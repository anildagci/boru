# BÖRÜ'nün bekçisi: karakter klasörünün bir "anını" tutar ve BÖRÜ dışında yapılan değişiklikleri kurallara göre sınıflandırır.
# Kurallar (kullanıcının): kaynak dosyalara dokunulmaz; onaylı sürümün (teslim) üstüne yazılmaz; hiçbir deneme silinmez;
# üçgen sayısı ve doku çözünürlüğü azaltılmaz. Bekçi dosyalara bakar; hiçbir şeyi değiştirmez, geri almaz, silmez.
from dil import _
import os, json, hashlib

DIZINLER = ("Source", "Blender", "Exports", "Textures", "Backups")
ATLA_DIZIN = ("Textures/work",)                                  # BÖRÜ'nün ara dosyaları
ATLA_UZANTI = (".blend1", ".blend2", ".tmp", ".log", ".pyc")
TESLIM = ("_Final_Master.blend", "_Mixamo_Upload.fbx", "_Preview.glb", "_BaseColor_Final.png")
MODEL = (".blend", ".fbx", ".glb")
AN = "boru_bekci.json"


def _sha1(yol):
    h = hashlib.sha1()
    with open(yol, "rb") as f:
        for parca in iter(lambda: f.read(1 << 20), b""):
            h.update(parca)
    return h.hexdigest()


def oku(work):
    try:
        return json.load(open(os.path.join(work, AN), encoding="utf-8"))
    except Exception:
        return None


def yaz(work, an):
    json.dump(an, open(os.path.join(work, AN), "w", encoding="utf-8"), indent=0, ensure_ascii=False)


def tara(work, eski=None):
    """{göreli yol: [boyut, değişme zamanı (ns), sha1 ya da None]}. Kaynak dosyaların içeriği özetlenir (yalnız değiştiyse yeniden)."""
    eski = eski or {}; an = {}
    for d in DIZINLER:
        kok = os.path.join(work, d)
        for kl, _x, dosyalar in os.walk(kok):
            for ad in dosyalar:
                tam = os.path.join(kl, ad); rel = os.path.relpath(tam, work).replace("\\", "/")
                if rel.lower().endswith(ATLA_UZANTI) or any(rel.startswith(a + "/") for a in ATLA_DIZIN):
                    continue
                try:
                    st = os.stat(tam)
                except OSError:
                    continue
                kayit = [st.st_size, st.st_mtime_ns, None]
                if d == "Source":
                    o = eski.get(rel)
                    kayit[2] = o[2] if (o and o[0] == kayit[0] and o[1] == kayit[1] and o[2]) else _sha1(tam)
                an[rel] = kayit
    return an


def fark(eski, yeni):
    eklenen = sorted(set(yeni) - set(eski)); silinen = sorted(set(eski) - set(yeni))
    degisen = []
    for r in sorted(set(eski) & set(yeni)):
        e, y = eski[r], yeni[r]
        if r.startswith("Source/"):
            if e[2] != y[2]:                                     # kaynakta yalnız içerik değişimi sayılır (dokunup kaydetmek değil)
                degisen.append(r)
        elif e[0] != y[0] or e[1] != y[1]:
            degisen.append(r)
    return eklenen, silinen, degisen


def siniflandir(f, kip):
    """[(seviye, metin)]; seviye: ihlal (kullanıcıya sorulur) | uyari | bilgi."""
    eklenen, silinen, degisen = f; b = []
    for r in silinen:
        b.append(("ihlal", _("Kaynak dosya silindi: %s") % r if r.startswith("Source/") else _("Silindi (hiçbir deneme silinmez): %s") % r))
    for r in degisen:
        if r.startswith("Source/"):
            b.append(("ihlal", _("Kaynak dosyanın içeriği değişti: %s") % r))
        elif r.endswith(TESLIM):
            b.append(("ihlal", _("Teslim dosyası BÖRÜ'nün teslimi dışında değişti (onaylı sürümün üstüne yazıldı): %s") % r))
        elif r.lower().endswith(MODEL) or r.lower().endswith(".png"):
            b.append(("ihlal", _("Var olan bir denemenin üstüne yazıldı: %s") % r))
        else:
            b.append(("uyari", _("Değişti: %s") % r))
    for r in eklenen:
        if r.startswith("Source/"):
            b.append(("uyari", _("Source altına BÖRÜ dışında yeni dosya eklendi: %s") % r))
        elif kip == "arac":
            b.append(("uyari", _("Araç kipindeyiz ama BÖRÜ dışında yeni dosya oluştu: %s") % r))
        else:
            b.append(("bilgi", _("Yeni dosya: %s") % r))
    return b


def olculecek(f):
    """Ölçülmesi gereken yeni ya da değişmiş model dosyaları (yedekler hariç)."""
    eklenen, _x, degisen = f
    return [r for r in eklenen + degisen if r.lower().endswith(MODEL) and r.startswith(("Blender/", "Exports/"))]
