# -*- coding: utf-8 -*-
"""BÖRÜ: yapay zekâyla çalışırken emeğini koruyan kurt.

Masaüstünde duran bir kurt. Kitin ana yolunu kurulu Blender'ı çağırarak yürütür ve her adımda ne bulduğunu,
neye dokunmadığını yazıyla söyler. Kaynak dosyalara dokunmaz, hiçbir denemeyi silmez.

  python boru.py                         kurt ve panel
  python boru.py --run <adım> --work <klasör> [--body f] [--head f] [--glb f] [--sheet f --views a,b,c] [--log f]
  python boru.py --shot <png>            pencerenin ekran görüntüsünü alıp çıkar (deneme için)
  python boru.py --mcp                   Claude Code / Codex'e bağlanan MCP sunucusu (stdio); bkz. boru_mcp.py
  python boru.py --maskot <sayfa.png> [--ad kimlik] [--isim "Ad"] [--kisisel]
                                         maskot sayfasını (3x2, altı hal) bu bilgisayarın maskot setlerine keser
                                         (Belgeler\\BORU\\maskot; exe'ye ve depoya girmez). Kurda sağ tık > Maskot ile seçilir.
  python boru.py --dersler [--rapor f]   günlükten ders adayları raporu (Belgeler\\BORU\\DERS_ADAYLARI.md)
Kullanıcı verisi (ayar, günlük, kişisel maskotlar, dersler): Belgeler\\BORU (BORU_VERI ile değişir); bkz. dersler.KOK.
Adımlar: kes, incele, oturt, birlestir, teslim
"""
from dil import _
import os, sys, json, glob, time, shutil, threading, subprocess, queue, runpy, contextlib, traceback, math, re

APP, SLOGAN, SURUM = _("BÖRÜ"), _("yapay zekâyla çalışırken emeğini koruyan kurt"), "0.6.2"
BASE = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
SCR = os.path.join(BASE, "betikler")
import dersler                                       # kullanıcı verisinin yeri: dersler.KOK (Belgeler\BORU)
AYAR = os.path.join(dersler.KOK, "ayar.json")
TAM = {"BODY_TRIS": "999999999", "BODY_ONLY": "1", "STAGE_A_NAME": "Model_StageA_full", "PRE_TRIS": "999999999",
       "HEAD_TRIS": "999999999", "NECK_OVERLAP": "0.012", "ATLAS_SIZE": "8192", "ATLAS_BODY": "4096",
       "ATLAS_BODY_SRC": "original/body_basecolor.png", "BAND_CLEAN": "0", "HAIR_COPY": "0", "BASE_QUALITY": "97"}


def _paket():
    """Çağrılmaz. Derleyicinin, betikler/ altındaki dosyaların kullandığı kütüphaneleri exe'ye koyması için."""
    import numpy, cv2, heapq, types, shutil, json                                   # noqa: F401
    import PIL.Image, PIL.ImageOps, PIL.ImageFilter, PIL.ImageDraw, PIL.ImageGrab   # noqa: F401


def ayar_oku():
    try:
        return json.load(open(AYAR, encoding="utf-8"))
    except Exception:
        return {}


def ayar_yaz(d):
    os.makedirs(os.path.dirname(AYAR), exist_ok=True)
    json.dump(d, open(AYAR, "w", encoding="utf-8"), indent=1, ensure_ascii=False)


def blender_bul():
    adaylar = [ayar_oku().get("blender"), os.environ.get("BLENDER")]
    adaylar += sorted(glob.glob(r"C:\Program Files\Blender Foundation\Blender *\blender.exe"), reverse=True)
    for p in adaylar:
        if p and os.path.isfile(p):
            return p
    return None


class Dur(Exception):
    """Adım tamamlanamadı; mesajı kullanıcıya söylenir."""


class Yazici:
    def __init__(self, soyle):
        self.soyle, self.kalan, self.satirlar = soyle, "", []

    def write(self, s):
        self.kalan += s
        while "\n" in self.kalan:
            satir, self.kalan = self.kalan.split("\n", 1)
            self.satirlar.append(satir.rstrip()); self.soyle("log", satir.rstrip())
        return len(s)

    def flush(self):
        pass


class Motor:
    """Adımları yürütür. soyle(tur, metin): tur = log | kurt | mod."""

    def __init__(self, soyle):
        self.soyle, self.hata = soyle, {}

    # ---- çalıştırıcılar
    def blender(self, blend, betik, args, env=None):
        exe = blender_bul()
        if not exe:
            raise Dur(_("Blender'ı bulamadım. Panelden blender.exe yolunu göster."))
        komut = [exe, "-b"] + ([blend] if blend else ["--factory-startup"]) + ["--python", os.path.join(SCR, betik), "--"] + list(args)
        e = dict(os.environ); e.update(env or {})
        p = subprocess.Popen(komut, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=e, text=True, encoding="utf-8",
                             errors="replace", creationflags=0x08000000 if os.name == "nt" else 0)
        satirlar = []
        for ln in p.stdout:
            ln = ln.rstrip(); satirlar.append(ln)
            if ln and len(ln) < 400 and "| INFO" not in ln and not ln.lstrip().startswith(("Fra:", "Saved:", "Blender ", "Read ", "Time:", "Import ", "Export ")):
                self.soyle("log", ln)
        p.wait()
        if any("Traceback (most recent call last)" in l for l in satirlar):
            son = [l for l in satirlar if l.strip()][-3:]
            raise Dur(_("Blender betiği hata verdi (%s): %s") % (betik, " | ".join(son)))
        return satirlar

    def py(self, betik, args, env=None, cwd=None):
        eski_cwd, eski_argv = os.getcwd(), sys.argv[:]
        eski_env = {k: os.environ.get(k) for k in (env or {})}
        y = Yazici(self.soyle)
        try:
            os.environ.update(env or {}); os.chdir(cwd or eski_cwd); sys.argv = [betik] + list(args)
            with contextlib.redirect_stdout(y), contextlib.redirect_stderr(y):
                try:
                    runpy.run_path(os.path.join(SCR, betik), run_name="__main__")
                except SystemExit:
                    pass
        except Exception as ex:
            raise Dur(_("%s hata verdi: %s") % (betik, ex))
        finally:
            os.chdir(eski_cwd); sys.argv = eski_argv
            for k, v in eski_env.items():
                if v is None:
                    os.environ.pop(k, None)
                else:
                    os.environ[k] = v
        return y.satirlar

    # ---- yardımcılar
    @staticmethod
    def hazirla(work):
        for d in ("Source", "References", "Textures/original", "Textures/work/graft", "Blender", "Exports", "Renders/kontrol", "Backups"):
            os.makedirs(os.path.join(work, d), exist_ok=True)

    @staticmethod
    def durum(work, yeni=None):
        p = os.path.join(work, "boru_durum.json")
        try:
            d = json.load(open(p, encoding="utf-8"))
        except Exception:
            d = {}
        if yeni:
            d.update(yeni); json.dump(d, open(p, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
        return d

    @staticmethod
    def kaynaga_al(work, yol):
        """Dosyayı Source/ altına kopyalar; var olanın üstüne asla yazmaz. Source içindeki adını döner."""
        hedef = os.path.join(work, "Source", os.path.basename(yol))
        if os.path.abspath(yol) == os.path.abspath(hedef):
            return os.path.basename(hedef)
        if os.path.exists(hedef) and os.path.getsize(hedef) != os.path.getsize(yol):
            kok, uz = os.path.splitext(os.path.basename(yol)); hedef = os.path.join(work, "Source", "%s_%s%s" % (kok, time.strftime("%H%M%S"), uz))
        if not os.path.exists(hedef):
            shutil.copy2(yol, hedef)
        return os.path.basename(hedef)

    # ---- adımlar
    def kes(self, work, sayfa, gorunusler):
        self.hazirla(work)
        ad = os.path.basename(work.rstrip("/\\")); ref = os.path.join(work, "References")
        if os.path.abspath(os.path.dirname(sayfa)) != os.path.abspath(ref):
            shutil.copy2(sayfa, os.path.join(ref, os.path.basename(sayfa)))
        kok = os.path.splitext(os.path.basename(sayfa))[0]; alt = "tripo_" + kok
        self.py("tripo_views.py", [ad, os.path.basename(sayfa), gorunusler, alt, "%s_%s" % (ad.lower(), kok)], cwd=os.path.dirname(work.rstrip("/\\")))
        cikti = os.path.join(ref, alt); dosyalar = sorted(f for f in os.listdir(cikti) if f.endswith(".png") and not f.startswith("_")) if os.path.isdir(cikti) else []
        if not dosyalar:
            raise Dur(_("Sayfadan görünüş kesemedim. Görünüş sayısı sayfadaki figür sayısıyla aynı mı?"))
        self.soyle("kurt", _("Çizimi kestim.\n1. %d görsel hazır, hepsi aynı ölçekte ve hizada, beyaz zeminli.\n2. Sayfanın kendisine dokunmadım.\n"
                           "3. Tripo'ya vermeden önce önizlemeye bak: saç ucu ya da el kesilmiş mi?\nKlasör: References/%s") % (len(dosyalar), alt))
        return os.path.join(cikti, "_contact.png")

    def incele(self, work, glb):
        self.hazirla(work)
        kok = os.path.splitext(os.path.basename(glb))[0]; cikti = os.path.join(work, "Renders", "incele", kok)
        satirlar = self.blender(None, "render_glb.py", [glb, cikti, "m"])
        m = next((re.search(r"objects (\d+) verts (\d+) tris (\d+)", l) for l in satirlar if "INFO m objects" in l), None)
        if not m:
            raise Dur(_("Modeli okuyamadım: %s") % os.path.basename(glb))
        parca, ucgen = int(m.group(1)), int(m.group(3)); bulgu = [_("%s üçgen, %d parça.") % (format(ucgen, ",").replace(",", "."), parca)]
        if ucgen < 200000:
            bulgu.append(_("Üçgen sayısı düşük. Kalite için Tripo'da HD Model ile (yaklaşık 2 milyon üçgen) üretilmiş halini öneririm."))
        else:
            bulgu.append(_("Üçgen sayısı yüksek; azaltmayacağım."))
        bulgu.append(_("Parçalı model: saç, yüz ve aksesuar ayrı seçilebilir.") if parca > 1 else _("Tek parça: bölgeleri renkle ayırırım."))
        bulgu.append(_("Sekiz açıdan renkli ve kil renderlarını aldım. Önce kil renderlara bak: biçim doğruysa doku işi kolaydır."))
        self.soyle("kurt", _("Modele baktım, dokunmadım.\n") + "\n".join("%d. %s" % (i + 1, b) for i, b in enumerate(bulgu)))
        return cikti

    def gozler(self, work, glb):
        """Modelin yüzünü önden düz render alır, iki irisi bulur. Göz dosyasının yolunu döner."""
        kok = os.path.splitext(os.path.basename(glb))[0]; png = os.path.join(work, "Renders", "gozler", kok + ".png")
        os.makedirs(os.path.dirname(png), exist_ok=True)
        self.blender(None, "yuz_onden.py", [os.path.join(work, "Source", glb), png])
        self.py("goz_bul.py", [png])
        sonuc = os.path.join(work, "Renders", "gozler", kok + "_goz.json")
        try:
            g = json.load(open(sonuc, encoding="utf-8"))
        except Exception:
            g = {}
        if not g.get("bulundu"):
            raise Dur(_("%s modelinde iki gözü bulamadım. Yüzün önden görüntüsü: Renders/gozler/%s.png. "
                      "Gözler saçla kapalı ya da çok küçük olabilir.") % (kok, kok))
        return sonuc

    def oturt(self, work, govde, bas):
        self.hazirla(work)
        b, h = self.kaynaga_al(work, govde), self.kaynaga_al(work, bas)
        self.soyle("kurt", _("Hizalama için iki modelde de gözleri arıyorum."))
        goz = {"BORU_EYES_BODY": self.gozler(work, b), "BORU_EYES_HEAD": self.gozler(work, h)}
        renk = self.durum(work).get("renk")              # "raicon": eski, elle ölçülmüş renk kuralları; yoksa otomatik
        if renk:
            goz["BORU_RENK"] = renk
        rid = time.strftime("%m%d_%H%M"); tag = rid + "g"; d = self.durum(work)
        temel = os.path.join(work, "Blender", "Model_StageA_full.blend")
        if not os.path.exists(temel) or d.get("govde") != b:
            self.soyle("kurt", _("Gövdeyi içe aktarıyorum. Üçgen sayısını azaltmıyorum; birkaç dakika sürer."))
            self.blender(None, "stage_a_reduce.py", [work], env=dict(TAM, BORU_BODY=b))
            if not os.path.exists(temel):
                raise Dur(_("Gövdeyi içe aktaramadım."))
        self.soyle("kurt", _("Başı gövdeye oturtuyorum. Yüze, saça ve dokulara dokunmayacağım."))
        satirlar = self.blender(temel, "simple_graft.py", [work, tag], env=dict(TAM, BORU_HEAD=h, **goz))
        sahne = os.path.join(work, "Blender", "Model_Graft_%s.blend" % tag)
        if not os.path.exists(sahne):
            neden = next((l for l in satirlar if "bulunamadi" in l or "degil" in l), "")
            raise Dur(_("Başı oturtamadım. %s Hizalamayı gözlerden, ten ve yaka rengini yüzün ortasından aşağı inerek buluyorum; "
                      "yakada tenden belirgin farklı bir giysi rengi olmalı.") % neden)
        self.blender(sahne, "who3.py", [os.path.join(work, "Renders", "kontrol", tag)])
        olcek = next((re.search(r"scale ([\d.]+)", l).group(1) for l in satirlar if l.startswith("head: scale")), "?")
        m = next((re.search(r"kept (\d+) triangles; head: kept (\d+)", l) for l in satirlar if l.startswith("body: collar top")), None)
        self.durum(work, {"govde": b, "bas": h, "graft": tag, "govde_ucgen": int(m.group(1)) if m else None, "bas_ucgen": int(m.group(2)) if m else None})
        nokta = lambda n: format(int(n), ",").replace(",", ".")
        self.soyle("kurt", _("Başı gövdeye oturttum (deneme %s).\n1. Ölçek: %s.\n2. Gövde %s, baş %s üçgen; hiç azaltmadım.\n"
                           "3. Dokunmadıklarım: yüz, saç, dokular, kaynak dosyalar.\n4. Kontrol görseli: kırmızı gövde, yeşil baş.\n"
                           "Yakaya, enseye ve boyna bak. Bozuk bir yer varsa birleştirmeden önce söyle.") % (tag, olcek, nokta(m.group(1)) if m else "?", nokta(m.group(2)) if m else "?"))
        return os.path.join(work, "Renders", "kontrol", tag + "_front.png")

    def birlestir(self, work):
        d = self.durum(work); g = d.get("graft")
        if not g:
            raise Dur(_("Önce başı gövdeye oturtmam gerekiyor."))
        ad = os.path.basename(work.rstrip("/\\")); rid = time.strftime("%m%d_%H%M"); a, t = rid + "a", rid + "t"
        self.soyle("kurt", _("Baş ve gövdeyi tek modelde, tek dokuda topluyorum. Dokuları küçültmüyorum."))
        self.blender(os.path.join(work, "Blender", "Model_Graft_%s.blend" % g), "graft_atlas.py", [work, a], env=TAM)
        self.py("graft_atlas_compose.py", [a], env=TAM, cwd=work)
        self.py("simple_look.py", [a, t, "none", os.path.join(work, "Exports", "Unity", ad + "Anime")], env=TAM, cwd=work)
        sahne = os.path.join(work, "Blender", "Model_Graft_%s.blend" % a)
        if not os.path.exists(sahne) or not os.path.exists(os.path.join(work, "Textures", "Model_BaseColor_%s.png" % t)):
            raise Dur(_("Tek dokuya toplayamadım."))
        self.blender(sahne, "graft_export.py", [work, a])
        fbx = os.path.join(work, "Exports", "Model_Graft_%s.fbx" % a)
        if not os.path.exists(fbx):
            raise Dur(_("Dışa aktaramadım."))
        v = next((l for l in self.blender(None, "verify_fbx.py", [fbx]) if l.startswith("VERIFY")), "")
        m = re.search(r"objects (\d+) .*tris (\d+) uv layers (\d+) materials (\d+)", v)
        if not m:
            raise Dur(_("Dışa aktardığım dosyayı yeniden açıp doğrulayamadım."))
        self.durum(work, {"atlas": a, "doku": t, "birlesik_ucgen": int(m.group(2))})
        self.soyle("kurt", _("Tek model, tek doku hazır (deneme %s).\n1. Yeniden içe aktarıp saydım: %s parça, %s üçgen, %s doku katmanı, %s malzeme.\n"
                           "2. Doku birleştirilmiş haliyle aynı; üstüne hiçbir şey yazmadım.\n3. Oyun dokuları: Exports/Unity/%sAnime.\n"
                           "Teslim etmedim. Önce bak; beğenirsen 'Teslim et' de.") % (a, m.group(1), format(int(m.group(2)), ",").replace(",", "."), m.group(3), m.group(4), ad))
        return fbx

    def teslim(self, work):
        d = self.durum(work); a, t = d.get("atlas"), d.get("doku")
        if not a:
            raise Dur(_("Teslim edilecek birleştirilmiş model yok."))
        ad = os.path.basename(work.rstrip("/\\"))
        cift = [("Blender/Model_Graft_%s.blend" % a, "Blender/%s_Final_Master.blend" % ad), ("Exports/Model_Graft_%s.fbx" % a, "Exports/%s_Mixamo_Upload.fbx" % ad),
                ("Exports/Model_Graft_%s.glb" % a, "Exports/%s_Preview.glb" % ad), ("Textures/Model_BaseColor_%s.png" % t, "Textures/%s_BaseColor_Final.png" % ad)]
        eski = [h for _x, h in cift if os.path.exists(os.path.join(work, h))]
        if eski:
            yedek = os.path.join(work, "Backups", "teslim_" + time.strftime("%Y-%m-%d_%H%M%S")); os.makedirs(yedek)
            for h in eski:
                shutil.copy2(os.path.join(work, h), yedek)
        for k, h in cift:
            shutil.copy2(os.path.join(work, k), os.path.join(work, h))
        self.durum(work, {"teslim": a})
        self.soyle("kurt", _("Teslim ettim (deneme %s).\n1. Ana dosya, iskelet aracına gidecek FBX, önizleme ve doku hazır.\n2. %s\n3. Denemelerin hepsi duruyor; hiçbirini silmedim.\n"
                           "Sıradaki iş senin: FBX'i iskelet aracına yükle.") % (a, _("Önceki teslimi Backups altına yedekledim.") if eski else _("Önceki teslim yoktu.")))
        return os.path.join(work, cift[1][1])

    def calistir(self, ad, fn, *args):
        """Adımı çalıştırır; üç kez üst üste tutmazsa bırakır ve elde kalan en iyi sürümü söyler."""
        self.soyle("mod", "calisiyor")
        try:
            sonuc = fn(*args); self.hata[ad] = 0; self.soyle("mod", "sevincli"); return sonuc
        except Exception as ex:
            n = self.hata[ad] = self.hata.get(ad, 0) + 1
            neden = str(ex) if isinstance(ex, Dur) else "%s: %s" % (type(ex).__name__, ex)
            if not isinstance(ex, Dur):
                self.soyle("log", traceback.format_exc())
            if n >= 3:
                d = self.durum(args[0]) if args and os.path.isdir(str(args[0])) else {}
                iyi = d.get("teslim") or d.get("atlas") or d.get("graft") or _("henüz yok")
                self.soyle("kurt", _("Üç kez denedim, tutmadı. Burada bırakıyorum.\nSon neden: %s\nEldeki son sağlam deneme: %s. Hiçbir şeyi silmedim.") % (neden, iyi))
            else:
                self.soyle("kurt", _("Olmadı (deneme %d/3).\nNeden: %s\nHiçbir şeyi silmedim; kaynaklar ve önceki denemeler yerinde.") % (n, neden))
            self.soyle("mod", "endiseli"); return None


# ---------------------------------------------------------------------------------------------- komut satırı
def komut_satiri(argv):
    al = lambda k, v=None: argv[argv.index(k) + 1] if k in argv else v
    gunluk = open(al("--log"), "a", encoding="utf-8") if al("--log") else None
    ekran = sys.stdout                       # betikler çalışırken stdout yönlendirilir; gerçek çıkış burada tutulur

    def soyle(tur, metin):
        if tur == "mod":
            return
        satir = (_("\n[BÖRÜ] ") + metin + "\n") if tur == "kurt" else metin
        if gunluk:
            gunluk.write(satir + "\n"); gunluk.flush()
        elif ekran:
            try:
                ekran.write(satir + "\n"); ekran.flush()
            except Exception:
                pass
    m = Motor(soyle); adim, work = al("--run"), al("--work")
    is_ = {"kes": lambda: m.calistir("kes", m.kes, work, al("--sheet"), al("--views", "front,right,back")),
           "incele": lambda: m.calistir("incele", m.incele, work, al("--glb")),
           "oturt": lambda: m.calistir("oturt", m.oturt, work, al("--body"), al("--head")),
           "birlestir": lambda: m.calistir("birlestir", m.birlestir, work),
           "teslim": lambda: m.calistir("teslim", m.teslim, work)}
    sonuc = is_[adim]()
    soyle("log", "SONUC %s %s" % (adim, sonuc))
    return 0 if sonuc else 1


# ---------------------------------------------------------------------------------------------- pencere
MASKOT_HALLER = ("bos", "kirp", "calisiyor", "sevincli", "endiseli", "soruyor")


# Maskot setleri iki yerde durur:
#  - BASE/maskot/<kimlik>: kitle birlikte dağıtılan (exe'ye gömülü) setler. Yalnız dağıtılabilir olanlar buraya konur.
#  - Belgeler\BORU\maskot\<kimlik>: yalnız bu bilgisayardaki setler (kişisel ya da kullanıcının kendi ürettiği).
#    Bunlar ne exe'ye ne depoya girer.
# Her setin klasöründe altı kare (bos, kirp, ...) ve bilgi.json ({"ad", "lisans": dagitilabilir | kisisel | kendi}) bulunur.
KISISEL_MASKOT = os.path.join(dersler.KOK, "maskot")


def maskotlar():
    """[(kimlik, ad, lisans, klasör)]: önce gömülü setler, sonra bu bilgisayardakiler."""
    out = []
    for kok, varsayilan in ((os.path.join(BASE, "maskot"), "dagitilabilir"), (KISISEL_MASKOT, "kisisel")):
        if not os.path.isdir(kok):
            continue
        for k in sorted(os.listdir(kok)):
            d = os.path.join(kok, k)
            if os.path.isfile(os.path.join(d, "bos.png")):
                try:
                    b = json.load(open(os.path.join(d, "bilgi.json"), encoding="utf-8"))
                except Exception:
                    b = {}
                out.append((k, b.get("ad", k), b.get("lisans", varsayilan), d))
    e = os.environ.get("BORU_MASKOT")
    if e and os.path.isfile(os.path.join(e, "bos.png")):
        out.insert(0, ("_ortam", "BORU_MASKOT", "kisisel", e))
    return out


def maskot_yukle(tk, kimlik=None):
    """Seçili setin kareleri {hal: PhotoImage}. kimlik "cizim" ya da set yoksa boş sözlük: vektör kurt çizilir."""
    if kimlik == "cizim":
        return {}
    setler = maskotlar()
    s = next((x for x in setler if x[0] == kimlik), None) or (setler[0] if setler else None)
    if not s:
        return {}
    try:
        return {h: tk.PhotoImage(file=os.path.join(s[3], h + ".png")) for h in MASKOT_HALLER if os.path.isfile(os.path.join(s[3], h + ".png"))}
    except Exception:
        return {}


def pencere(shot=None, mcp=None, sinama=None):
    """mcp verilirse: MCP kipinin kurdu. Panel açılmaz (iş modelden gelir); mesajlar ve onay soruları mcp["kuyruk"]tan okunur.
    sinama (yalnız kaynaktan çalışırken): "evet|hayir:<bekle sn>:<ekran.png>" soru gelince ekran görüntüsü alır, sonra düğmeye basar."""
    import tkinter as tk
    from tkinter import filedialog, ttk
    SAYDAM, W, H = "#00ff01", 340, 580
    kok = tk.Tk(); kok.title(APP); kok.overrideredirect(True); kok.attributes("-topmost", True)
    kok.config(bg=SAYDAM)
    try:
        kok.attributes("-transparentcolor", SAYDAM)
    except tk.TclError:
        pass
    kok.geometry("%dx%d+%d+%d" % (W, H, kok.winfo_screenwidth() - W - 40, kok.winfo_screenheight() - H - 80))
    cv = tk.Canvas(kok, width=W, height=H, bg=SAYDAM, highlightthickness=0); cv.pack()
    S = {"mod": "bos", "metin": _("Selam, ben BÖRÜ.\nYapay zekâyla çalışırken yanındayım. Claude Code'u izlememi istersen bana sağ tıkla > Canlı kurt.\n(3B paketi için bana tıkla: panel açılır.)"),
         "t0": time.time(), "kirp": 0.0, "mesgul": False, "panel": None, "gunluk": None, "dug": [], "soru": None}
    if mcp:
        S["metin"] = (_("Selam, ben BÖRÜ. Yapay zekâ modeline bağlandım.\nO çalışırken ne yaptığını burada söylerim. "
                      "Teslim gibi kalıcı bir iş olursa sana burada sorarım; sen 'Evet' demeden yapmam."))
    kuyruk = mcp["kuyruk"] if mcp else queue.Queue(); motor = Motor(lambda tur, metin: kuyruk.put((tur, metin)))
    import kanca
    kanca_sunucu = kanca.dinle(kuyruk)                  # canlı kurt: Claude Code kancaları buraya haber verir (yalnız izler)
    a = ayar_oku()
    KARE = maskot_yukle(tk, a.get("maskot"))

    def maskot_degistir(kimlik):
        a["maskot"] = kimlik; ayar_yaz(a); KARE.clear(); KARE.update(maskot_yukle(tk, kimlik))
        # önceki mesaj (ör. "Yeni maskotun hazır: ...") ekranda kalmasın: değişimi söyle, kurdu sakin hale getir
        ad = _("Çizim kurt") if kimlik == "cizim" else next((m[1] for m in maskotlar() if m[0] == kimlik), kimlik)
        S["metin"] = _("Maskot: %s. Sağ tık > Maskot ile istediğin zaman değiştirebilirsin.") % ad; S["mod"] = "bos"

    def ciz():
        t = time.time() - S["t0"]; mod = S["mod"]; cv.delete("all")
        KOYU, ORTA, ACIK, GOZ = "#2c313c", "#3d4452", "#d9dde6", "#7fd8ff"
        # konuşma balonu (soru varsa: soru ve altında düğmeler; soru metni kısaltılmaz)
        soru = S["soru"]
        metin = soru["metin"] if soru else (S["metin"] if len(S["metin"]) < 420 else S["metin"][:417] + "...")
        yazi = cv.create_text(22, 18, text=metin, anchor="nw", width=W - 44, font=("Segoe UI", 9, "bold" if soru else "normal"), fill="#1c1f26")
        x0, y0, x1, y1 = cv.bbox(yazi); y1 = max(y1, 60)
        if soru:
            dy = y1 + 10; n = len(soru["secenekler"]); gen = (W - 44 - 10 * (n - 1)) // n
            for i, sec in enumerate(soru["secenekler"]):
                bx0 = 22 + i * (gen + 10); renk = "#2e7d4f" if i == 0 else "#a33a3a"
                cv.create_rectangle(bx0, dy, bx0 + gen, dy + 30, fill=renk, outline="#15181e", width=2, tags=("dug", "dug%d" % i))
                cv.create_text(bx0 + gen // 2, dy + 15, text=sec, fill="white", font=("Segoe UI", 10 if n < 3 else 8, "bold"), tags=("dug", "dug%d" % i))
            y1 = dy + 34
        cv.create_polygon(150, y1 + 8, 185, y1 + 8, 170, y1 + 30, fill="white", outline="#2c313c", width=2)
        cv.create_rectangle(10, 8, W - 10, y1 + 10, fill="#fff7e0" if soru else "white", outline="#c47f00" if soru else "#2c313c", width=3 if soru else 2)
        cv.tag_raise(yazi); cv.tag_raise("dug")
        cv.create_line(151, y1 + 10, 184, y1 + 10, fill="#fff7e0" if soru else "white", width=3)
        hiz = {"bos": 2.2, "calisiyor": 5.0, "sevincli": 9.0, "endiseli": 0.8}[mod]
        kuy = math.sin(t * hiz) * (26 if mod != "endiseli" else 6)
        nefes = math.sin(t * 1.6) * 1.5
        bx, by = 170, min(H - 28, max(392, y1 + 300))                 # balon uzarsa kurt aşağı iner (başı balona girmez)
        if KARE:                                                       # çizilmiş maskot kareleri varsa onlar oynar
            if t - S["kirp"] > 3.6:
                S["kirp"] = t
            ad = "soruyor" if soru else ("kirp" if mod == "bos" and (t - S["kirp"]) < 0.14 else mod)
            img = KARE.get(ad) or KARE.get("bos")
            ky = min(H - 4, max(by + 10, y1 + 34 + img.height()))      # başı balonun altında kalsın
            sallan = int(round(math.sin(t * (6.0 if mod == "calisiyor" else 1.6)) * (2 if mod == "calisiyor" else 1.5)))
            cv.create_image(bx, ky + sallan, image=img, anchor="s")
            return
        # kuyruk
        r = math.radians(-58 + kuy); tx, ty = bx + 52 + 70 * math.cos(r), by - 40 + 70 * math.sin(r)
        cv.create_polygon(bx + 40, by - 52, bx + 58, by - 30, tx + 8, ty + 10, tx, ty - 6, fill=KOYU, outline="#15181e", smooth=True)
        cv.create_oval(tx - 9, ty - 12, tx + 11, ty + 10, fill=ACIK, outline="")
        # gövde, göğüs, ayaklar
        cv.create_oval(bx - 62, by - 142 - nefes, bx + 62, by - 4, fill=KOYU, outline="#15181e", width=2)
        cv.create_oval(bx - 30, by - 112 - nefes, bx + 30, by - 10, fill=ACIK, outline="")
        for sx in (-34, 34):
            cv.create_oval(bx + sx - 20, by - 22, bx + sx + 20, by, fill=ORTA, outline="#15181e", width=2)
        # baş
        hy = by - 196 - nefes; egim = math.sin(t * 0.7) * 2 + (4 if mod == "endiseli" else 0)
        kulak = math.sin(t * 3.1) * 3 if (int(t) % 6 == 0 or mod == "sevincli") else 0
        for s_ in (-1, 1):
            cv.create_polygon(bx + s_ * 58, hy + 18, bx + s_ * (52 + kulak), hy - 62, bx + s_ * 14, hy - 6, fill=KOYU, outline="#15181e", width=2)
            cv.create_polygon(bx + s_ * 48, hy + 6, bx + s_ * (48 + kulak), hy - 40, bx + s_ * 26, hy - 2, fill="#8f98ab", outline="")
        cv.create_oval(bx - 68, hy - 30, bx + 68, hy + 82, fill=KOYU, outline="#15181e", width=2)
        cv.create_polygon(bx - 66, hy + 30, bx - 88, hy + 62, bx - 50, hy + 60, fill=KOYU, outline="#15181e", width=2)        # yanak tüyleri
        cv.create_polygon(bx + 66, hy + 30, bx + 88, hy + 62, bx + 50, hy + 60, fill=KOYU, outline="#15181e", width=2)
        cv.create_oval(bx - 34, hy + 26, bx + 34, hy + 84, fill=ACIK, outline="")                                             # burun bölgesi
        cv.create_polygon(bx - 34, hy + 34, bx, hy + 6, bx + 34, hy + 34, fill=ACIK, outline="")
        cv.create_oval(bx - 9, hy + 40, bx + 9, hy + 53, fill="#15181e", outline="")
        if mod == "sevincli":
            cv.create_arc(bx - 16, hy + 50, bx + 16, hy + 74, start=200, extent=140, style="arc", outline="#15181e", width=2)
        else:
            cv.create_line(bx, hy + 53, bx, hy + 62, fill="#15181e", width=2); cv.create_line(bx - 10, hy + 66, bx, hy + 62, bx + 10, hy + 66, fill="#15181e", width=2, smooth=True)
        # gözler
        if t - S["kirp"] > 3.6:
            S["kirp"] = t
        kirpiyor = (t - S["kirp"]) < 0.14
        bak = math.sin(t * 2.4) * 4 if mod == "calisiyor" else 0
        for s_ in (-1, 1):
            ex, ey = bx + s_ * 30, hy + 12
            if kirpiyor:
                cv.create_line(ex - 11, ey, ex + 11, ey, fill="#15181e", width=3)
            elif mod == "sevincli":
                cv.create_arc(ex - 11, ey - 8, ex + 11, ey + 12, start=20, extent=140, style="arc", outline=GOZ, width=4)
            else:
                cv.create_oval(ex - 12, ey - 10, ex + 12, ey + 10, fill=GOZ, outline="#15181e", width=2)
                cv.create_oval(ex - 4 + bak, ey - 5, ex + 4 + bak, ey + 5, fill="#15181e", outline="")
                cv.create_oval(ex - 2 + bak, ey - 5, ex + 1 + bak, ey - 2, fill="white", outline="")
            if mod == "endiseli":
                cv.create_line(ex - s_ * 14, ey - 20, ex + s_ * 10, ey - 14, fill="#15181e", width=3)
            elif mod == "calisiyor":
                cv.create_line(ex - s_ * 14, ey - 14, ex + s_ * 10, ey - 19, fill="#15181e", width=3)

    def gunluge(metin):
        g = S["gunluk"]
        if g is not None and g.winfo_exists():
            g.insert("end", metin + "\n"); g.see("end")

    def tik():
        try:
            while True:
                tur, metin = kuyruk.get_nowait()
                if tur == "sor":                                       # MCP: kullanıcıya soru (metin = soru sözlüğü)
                    S["soru"] = metin; S["mod"] = "bos"; kok.deiconify(); kok.lift(); kok.attributes("-topmost", True)
                    try:
                        kok.bell()
                    except Exception:
                        pass
                    if sinama:
                        sinama_tikla(metin)
                elif tur == "sor_iptal":
                    if S["soru"] is metin:
                        S["soru"] = None; S["metin"] = _("Soruya yanıt gelmedi; 'hayır' saydım ve modele söyledim."); S["mod"] = "endiseli"
                elif tur == "kapat":
                    kok.destroy(); return
                elif tur == "mod":
                    S["mod"] = metin
                elif tur == "kurt":
                    S["metin"] = metin; gunluge(_("\n[BÖRÜ] ") + metin + "\n")
                elif tur == "bitti":
                    S["mesgul"] = False
                    for b in S["dug"]:
                        if b.winfo_exists():
                            b.config(state="normal")
                    if metin and os.path.exists(metin):
                        try:
                            os.startfile(metin)
                        except Exception:
                            pass
                else:
                    gunluge(metin)
        except queue.Empty:
            pass
        ciz(); kok.after(70, tik)

    def baslat(ad, fn, *args):
        if S["mesgul"]:
            return
        S["mesgul"] = True
        for b in S["dug"]:
            if b.winfo_exists():
                b.config(state="disabled")
        threading.Thread(target=lambda: kuyruk.put(("bitti", motor.calistir(ad, fn, *args))), daemon=True).start()

    def panel_ac():
        if S["panel"] is not None and S["panel"].winfo_exists():
            S["panel"].lift(); return
        p = tk.Toplevel(kok); p.title("%s — %s" % (APP, SLOGAN)); p.geometry("760x560"); S["panel"] = p
        alan = {}

        def satir(r, etiket, anahtar, sec):
            ttk.Label(p, text=etiket).grid(row=r, column=0, sticky="w", padx=8, pady=3)
            v = tk.StringVar(value=a.get(anahtar, "") or (blender_bul() or "" if anahtar == "blender" else "")); alan[anahtar] = v
            ttk.Entry(p, textvariable=v, width=78).grid(row=r, column=1, sticky="we", pady=3)

            def tikla():
                yol = sec()
                if yol:
                    v.set(yol); kaydet()
            ttk.Button(p, text=_("Seç"), width=6, command=tikla).grid(row=r, column=2, padx=8)

        def kaydet():
            for k, v in alan.items():
                a[k] = v.get()
            ayar_yaz(a)
        glb = lambda: filedialog.askopenfilename(parent=p, filetypes=[("Model", "*.glb")])
        satir(0, _("Çalışma klasörü"), "work", lambda: filedialog.askdirectory(parent=p))
        satir(1, _("Gövde modeli (GLB)"), "govde", glb)
        satir(2, _("Baş modeli (GLB)"), "bas", glb)
        satir(3, "Blender", "blender", lambda: filedialog.askopenfilename(parent=p, filetypes=[("blender.exe", "blender.exe")]))
        p.columnconfigure(1, weight=1)
        cubuk = ttk.Frame(p); cubuk.grid(row=4, column=0, columnspan=3, sticky="we", padx=8, pady=6)
        gor = tk.StringVar(value=_("baş: ön, sol, sağ, arka"))
        secenek = {_("baş: ön, sol, sağ, arka"): "front,left,right,back", _("baş ya da tam boy: ön, sağ, arka"): "front,right,back", _("baş: ön, çapraz, sağ, arka"): "front,3q,right,back"}

        def gerek(*anahtarlar):
            kaydet()
            eksik = [k for k in anahtarlar if not alan[k].get() or not os.path.exists(alan[k].get())]
            if eksik:
                S["metin"] = _("Önce şunu göstermen gerekiyor: ") + ", ".join({"work": _("çalışma klasörü"), "govde": _("gövde modeli"), "bas": _("baş modeli")}[k] for k in eksik) + "."
                S["mod"] = "endiseli"; return False
            return True

        def d_kes():
            if gerek("work"):
                s = filedialog.askopenfilename(parent=p, title=_("Dönüş sayfası"), filetypes=[(_("Görsel"), "*.png *.jpg *.jpeg *.webp")])
                if s:
                    baslat("kes", motor.kes, alan["work"].get(), s, secenek[gor.get()])

        def d_incele():
            if gerek("work"):
                s = glb()
                if s:
                    baslat("incele", motor.incele, alan["work"].get(), s)
        dugmeler = [(_("1  Çizimi kes"), d_kes), (_("2  Modeli incele"), d_incele),
                    (_("3  Başı gövdeye oturt"), lambda: gerek("work", "govde", "bas") and baslat("oturt", motor.oturt, alan["work"].get(), alan["govde"].get(), alan["bas"].get())),
                    (_("4  Tek doku + dışa aktar"), lambda: gerek("work") and baslat("birlestir", motor.birlestir, alan["work"].get())),
                    (_("5  Teslim et"), lambda: gerek("work") and baslat("teslim", motor.teslim, alan["work"].get()))]
        S["dug"] = []
        for i, (ad, fn) in enumerate(dugmeler):
            b = ttk.Button(cubuk, text=ad, command=fn); b.grid(row=0, column=i, padx=3); S["dug"].append(b)
        ttk.Label(cubuk, text=_("1. adımdaki görünüşler:")).grid(row=1, column=0, columnspan=2, sticky="e", pady=6)
        ttk.Combobox(cubuk, textvariable=gor, values=list(secenek), state="readonly", width=34).grid(row=1, column=2, columnspan=3, sticky="w")
        g = tk.Text(p, wrap="word", font=("Consolas", 9)); g.grid(row=5, column=0, columnspan=3, sticky="nswe", padx=8, pady=6); p.rowconfigure(5, weight=1)
        S["gunluk"] = g
        g.insert("end", _("%s %s — %s\nKaynak dosyalara dokunmam, hiçbir denemeyi silmem, her adımda ne yaptığımı ve neye dokunmadığımı söylerim.\n"
                        "Başı gövdeye oturtma adımı gözlerden hizalar; iki yaka tipinde (tişört yakası, yüksek ceket yakası) sınandı.\n\n") % (APP, SURUM, SLOGAN))

    def yanitla(i):
        soru = S["soru"]
        if not soru:
            return
        soru["cevap"] = soru["secenekler"][i]; S["soru"] = None
        S["metin"] = _("Tamam, '%s' dedin. Modele ilettim.") % soru["cevap"]; S["mod"] = "sevincli" if i == 0 else "bos"
        if soru.get("geri"):                          # pencerenin kendi sorusu (ör. bağlantı): yanıtı kendisi işler
            soru["geri"](soru["cevap"])
        if soru.get("olay"):
            soru["olay"].set()

    # ---- Claude Code / Codex bağlantısı: açılışta bakar, bağlı değilse izin ister; hiçbiri yoksa yol gösterir
    def baglanti_kontrol(zorla=False):
        import baglanti
        d = baglanti.durum(); kurulu = [h for h in d if h["kurulu"]]; eksik = [h for h in kurulu if not (h["bagli"] and h["dogru"])]
        if not kurulu:
            S["metin"] = (_("Ben Claude Code ya da Codex'le çalışırım; ikisi de bu bilgisayarda görünmüyor.\n"
                          "1. Claude masaüstü uygulamasını (Code sekmesi) ya da Codex'i kur.\n2. Beni yeniden aç; bağlanmayı ben teklif ederim."))
            return
        if not eksik:
            S["metin"] = (_("Selam, ben BÖRÜ. %s bağlıyım.\nOrada şöyle yazabilirsin: \"BÖRÜ'yü kullanarak bu işe başlamadan önce planımı riskler için tara.\" Canlı kurt için bana sağ tıkla. "
                          "Kalıcı işlerde sana burada soracağım.\n(Bana tıkla: panel açılır.)") % " ve ".join(h["ad"] + "'a" for h in kurulu))
            return
        if a.get("baglanti_sorma") and not zorla:
            return
        satir = "\n".join("• " + s for s, h in zip(baglanti.ozet(d), d) if h in eksik)
        dosya = "\n".join("• %s" % h["dosya"].replace(os.path.expanduser("~"), "~") for h in eksik)

        def geri(cevap):
            if cevap == _("Bir daha sorma"):
                a["baglanti_sorma"] = True; ayar_yaz(a)
                S["metin"] = _("Peki, sormayacağım. Fikrin değişirse bana sağ tıkla > Bağlantılar."); return
            if cevap != _("Bağla"):
                S["metin"] = _("Peki. İstediğinde bana sağ tıkla > Bağlantılar."); return
            sonuc = []
            for h in eksik:
                try:
                    y = baglanti.baglan(h["kimlik"]); sonuc.append(_("%s: bağlandı%s") % (h["ad"], _(" (yedek: %s)") % os.path.basename(y) if y else ""))
                except Exception as ex:
                    sonuc.append(_("%s: OLMADI (%s); dosyaya dokunmadım") % (h["ad"], ex)); S["mod"] = "endiseli"
            S["metin"] = (_("Bağlantı:\n") + "\n".join("%d. %s" % (i + 1, s) for i, s in enumerate(sonuc)) +
                          _("\nŞimdi %s yeniden başlat; sonra orada \"BÖRÜ'yü kullanarak ...\" diye iste.") % " ve ".join(h["ad"] + "'i" for h in eksik))
            if any(h["kimlik"] == "claude" for h in eksik):          # açık Claude Code, ayar dosyasını kendi kopyasıyla ezebilir
                kok.after(8000, lambda: None if baglanti.durum()[0]["dogru"] else S.update(
                    metin=_("Claude Code ayar dosyasını yeniden yazmış, bağlantım silinmiş. Claude'u kapat, sonra bana sağ tıkla > Bağlantılar."), mod="endiseli"))
        S["soru"] = {"metin": _("Seni yapay zekâ ortamına bağlayayım mı?\n\n%s\n\nNe yapacağım: şu dosyalara yalnız 'boru' girdisini yazacağım, "
                              "önce yedeklerini alacağım; başka ayarına dokunmam:\n%s\nSonra o uygulamayı yeniden başlatman gerekir.") % (satir, dosya),
                     "secenekler": [_("Bağla"), _("Şimdi değil"), _("Bir daha sorma")], "geri": geri, "cevap": None}
        if sinama:
            sinama_tikla(S["soru"])

    # ---- Canlı kurt: Claude Code'un kancaları kurda her hareketi haber verir. Yalnız izler, hiçbir işlemi durdurmaz.
    def canli_kurt():
        kurulu = kanca.kurulu_mu(); dosya = kanca.ayar_dosyasi().replace(os.path.expanduser("~"), "~")

        def geri(cevap):
            try:
                if cevap == _("Aç"):
                    y = kanca.kur()
                    S["metin"] = (_("Canlı kurt açık. Claude Code'u yeniden başlat; o çalışırken ben de burada tepki veririm.%s") %
                                  (_(" (yedek: %s)") % os.path.basename(y) if y else "")); S["mod"] = "sevincli"
                    if kanca_sunucu is None:
                        S["metin"] += _("\nNot: başka bir BÖRÜ penceresi açık; haberler ona gidiyor.")
                elif cevap == _("Kapat"):
                    kanca.kaldir(); S["metin"] = _("Canlı kurt kapalı. Claude Code ayarından yalnız benim girdilerimi sildim.")
                else:
                    S["metin"] = _("Peki, hiçbir şeyi değiştirmedim.")
            except Exception as ex:
                S["metin"] = _("Olmadı (%s). Ayar dosyasına dokunmadım ya da yedeği geri koydum.") % ex; S["mod"] = "endiseli"
        if kurulu:
            S["soru"] = {"metin": _("Canlı kurt açık: Claude Code çalışırken her hareketini bana haber veriyor, ben de tepki veriyorum.\n\n"
                                    "Kapatayım mı? %s dosyasından yalnız benim girdilerimi silerim, önce yedek alırım.") % dosya,
                         "secenekler": [_("Kapat"), _("Açık kalsın")], "geri": geri, "cevap": None}
        else:
            S["soru"] = {"metin": _("Canlı kurdu açayım mı?\n\nClaude Code çalışırken (terminalde ya da Claude masaüstündeki Code sekmesinde) "
                                    "ne yaptığını bana haber verir: dosya düzenlerken çalışırım, riskli bir komutta endişelenip seni uyarırım, "
                                    "iş bitince sevinirim.\n\nBu sürüm yalnız izler, hiçbir işlemi durdurmaz. Haberler yalnız bu bilgisayarda kalır.\n"
                                    "Ne yapacağım: %s dosyasına yalnız benim girdilerimi eklerim, önce yedek alırım.") % dosya,
                         "secenekler": [_("Aç"), _("Şimdi değil")], "geri": geri, "cevap": None}

    def dug_tik(e):
        """Basılan yer bir onay düğmesiyse yanıtlar ve True döner."""
        for hedef in cv.find_overlapping(e.x, e.y, e.x, e.y):
            for tg in cv.gettags(hedef):
                if tg.startswith("dug") and tg[3:].isdigit():
                    yanitla(int(tg[3:])); return True
        return False

    def sinama_tikla(soru):
        sec, bekle, ekran = (sinama.split(":", 2) + ["", ""])[:3]

        def bas():
            if ekran:
                try:                                                   # görüntü alınamasa da düğmeye basılır
                    from PIL import ImageGrab
                    kok.update(); x, y = kok.winfo_rootx(), kok.winfo_rooty(); ImageGrab.grab(bbox=(x, y, x + W, y + H)).save(ekran)
                except Exception as ex:
                    sys.__stderr__ and sys.__stderr__.write("sinama ekran goruntusu alinamadi: %s\n" % ex)
            i = {"evet": 0, "hayir": 1}.get(sec, int(sec) if sec.isdigit() else None)
            if i is not None and S["soru"] is soru:              # düğmenin ortasına basılmış gibi: isabet denetimi de sınanır
                x0, y0, x1, y1 = cv.coords("dug%d" % i)[:4]
                class O: pass
                o = O(); o.x, o.y = (x0 + x1) / 2, (y0 + y1) / 2
                if not dug_tik(o):
                    S["metin"] = _("SINAMA: düğmeye basılamadı (isabet yok).")
        kok.after(int(float(bekle or 1) * 1000), bas)

    surukle = {}
    cv.bind("<ButtonPress-1>", lambda e: surukle.update(x=e.x_root, y=e.y_root, wx=kok.winfo_x(), wy=kok.winfo_y(), oynadi=False, dugme=dug_tik(e)))

    def tasi(e):
        dx, dy = e.x_root - surukle["x"], e.y_root - surukle["y"]
        if abs(dx) + abs(dy) > 4 and not surukle.get("dugme"):
            surukle["oynadi"] = True; kok.geometry("+%d+%d" % (surukle["wx"] + dx, surukle["wy"] + dy))
    cv.bind("<B1-Motion>", tasi)
    # MCP kipinde panel açılmaz: iş modelden gelir, elle başlatılan bir adım onunla çakışırdı. Çıkış da yok: bağlantıyı istemci kapatır.
    cv.bind("<ButtonRelease-1>", lambda e: None if (surukle.get("oynadi") or surukle.get("dugme") or mcp) else panel_ac())
    menu = tk.Menu(kok, tearoff=0)
    if not mcp:
        menu.add_command(label=_("Bağlantılar (Claude Code / Codex)"), command=lambda: baglanti_kontrol(zorla=True))
        menu.add_command(label=_("Canlı kurt (Claude Code)…"), command=canli_kurt)
        menu.add_command(label=_("Paneli aç"), command=panel_ac); menu.add_separator(); menu.add_command(label=_("Çıkış"), command=kok.destroy)
    else:
        menu.add_command(label=_("Küçült"), command=kok.iconify)
    alt = tk.Menu(menu, tearoff=0); secili = tk.StringVar(value=a.get("maskot") or (maskotlar()[0][0] if maskotlar() else "cizim"))

    def maskot_menusu():
        alt.delete(0, "end")
        for kimlik, ad, lisans, _x in maskotlar():
            alt.add_radiobutton(label=ad + {"kisisel": _("  (kişisel: yalnız bu bilgisayar)"), "kendi": _("  (senin)")}.get(lisans, ""),
                                variable=secili, value=kimlik, command=lambda k=kimlik: maskot_degistir(k))
        alt.add_radiobutton(label=_("Çizim kurt (yedek)"), variable=secili, value="cizim", command=lambda: maskot_degistir("cizim"))
        alt.add_separator(); alt.add_command(label=_("Kendi maskotunu oluştur…"), command=maskot_sihirbazi)

    def maskot_sihirbazi():
        """Kendi maskotunu oluştur: tarif > prompt > (kullanıcı görüntü üreticide üretir) > görsel seç > kes, önizle > kaydet."""
        import maskot_kes, webbrowser, tempfile
        if S.get("sihirbaz") is not None and S["sihirbaz"].winfo_exists():
            S["sihirbaz"].lift(); return
        w = tk.Toplevel(kok); S["sihirbaz"] = w; w.title(_("BÖRÜ — Kendi maskotunu oluştur")); w.geometry("620x700"); w.configure(bg="#f6f3ec")
        try:
            w.iconbitmap(os.path.join(BASE, "boru.ico"))
        except Exception:
            pass
        st = ttk.Style(w); st.configure("B.TLabel", background="#f6f3ec", font=("Segoe UI", 10)); st.configure("Bh.TLabel", background="#f6f3ec", font=("Segoe UI", 12, "bold"))
        st.configure("Bk.TLabel", background="#f6f3ec", foreground="#5b5f6a", font=("Segoe UI", 9))
        cer = tk.Frame(w, bg="#f6f3ec"); cer.pack(fill="both", expand=True, padx=18, pady=12)
        D = {"klasor": None}
        ttk.Label(cer, text=_("1. Maskotunu birkaç kelimeyle anlat"), style="Bh.TLabel").pack(anchor="w")
        ttk.Label(cer, text=_("Örnek: turuncu tüylü, yeşil atkılı, yuvarlak gözlüklü küçük bir tilki"), style="Bk.TLabel").pack(anchor="w")
        tarif = tk.Text(cer, height=3, wrap="word", font=("Segoe UI", 10), relief="solid", bd=1); tarif.pack(fill="x", pady=(4, 6))
        sat = tk.Frame(cer, bg="#f6f3ec"); sat.pack(anchor="w")
        bilgi1 = ttk.Label(cer, text="", style="Bk.TLabel", wraplength=570)

        def kopyala():
            w.clipboard_clear(); w.clipboard_append(maskot_kes.prompt(tarif.get("1.0", "end")))
            bilgi1.config(text=_("Prompt panoda. Görüntü üreticiye (ör. ChatGPT) yapıştır, çıkan görseli bilgisayarına kaydet."))
        ttk.Button(sat, text=_("Prompt'u kopyala"), command=kopyala).pack(side="left")
        ttk.Button(sat, text=_("ChatGPT'yi aç"), command=lambda: webbrowser.open("https://chatgpt.com/")).pack(side="left", padx=8)
        bilgi1.pack(anchor="w", pady=(4, 0))
        ttk.Label(cer, text=_("Altı hal tek görselde, 3 sütun × 2 satır gelir: sakin, göz kırpma, çalışıyor, sevinçli, endişeli, soru soruyor.\n"
                            "1. ve 2. kare aynı olmalı (yalnız gözler kapalı); figürler birbirine değmemeli."), style="Bk.TLabel").pack(anchor="w", pady=(6, 12))
        ttk.Label(cer, text=_("2. Üretilen görseli seç"), style="Bh.TLabel").pack(anchor="w")
        onz = tk.Label(cer, bg="#e9e4d8", text=_("(önizleme)"), height=9); bilgi2 = ttk.Label(cer, text="", style="B.TLabel", wraplength=570)

        def sec():
            yol = filedialog.askopenfilename(parent=w, title=_("Maskot görseli"), filetypes=[(_("Görsel"), "*.png *.jpg *.jpeg *.webp")])
            if not yol:
                return
            gecici = tempfile.mkdtemp(prefix="boru_maskot_", dir=dersler.KOK if os.path.isdir(dersler.KOK) else None)
            try:
                maskot_kes.kes(yol, gecici)
            except BaseException as ex:                      # kesici anlaşılır mesajla SystemExit fırlatır
                bilgi2.config(text=_("Kesemedim: %s\nGörselde altı figür 3 sütun × 2 satır olmalı, birbirine değmemeli; zemin düz ya da saydam olmalı.") % ex, foreground="#a33a3a")
                return
            D["klasor"], D["kaynak"] = gecici, os.path.basename(yol)
            from PIL import Image                            # önizleme pencerenin açık zemininde (kenar sınaması için olan yeşil değil)
            kar = [Image.open(os.path.join(gecici, h + ".png")).convert("RGBA") for h in MASKOT_HALLER]
            ac = Image.new("RGBA", (sum(k.width for k in kar) + 8 * 7, max(k.height for k in kar) + 16), (233, 228, 216, 255)); x = 8
            for k in kar:
                ac.alpha_composite(k, (x, 8)); x += k.width + 8
            ac.convert("RGB").save(os.path.join(gecici, "_onizleme_acik.png"))
            img = tk.PhotoImage(file=os.path.join(gecici, "_onizleme_acik.png")); k = max(1, -(-img.width() // 570))
            img = img.subsample(k, k); onz.config(image=img, text="", height=img.height()); onz.image = img
            bilgi2.config(text=_("Altı kareyi kestim, aynı ölçekte ve hizada. Beğendiysen ad ver ve kaydet."), foreground="#2e7d4f")
            if not ad.get():
                ad.set(os.path.splitext(os.path.basename(yol))[0][:30])
        ttk.Button(cer, text=_("Görsel seç…"), command=sec).pack(anchor="w", pady=(4, 6)); onz.pack(fill="x"); bilgi2.pack(anchor="w", pady=(6, 12))
        ttk.Label(cer, text=_("3. Adını koy ve kaydet"), style="Bh.TLabel").pack(anchor="w")
        ad = tk.StringVar(); ttk.Entry(cer, textvariable=ad, width=40).pack(anchor="w", pady=4)
        kisisel = tk.BooleanVar(value=False)
        ttk.Checkbutton(cer, variable=kisisel, text=_("Başkasının eserine benzeyebilir: 'kişisel' diye işaretle (yalnız bu bilgisayarda)")).pack(anchor="w")
        ttk.Label(cer, text=_("Kendi maskotların zaten yalnız bu bilgisayarda durur (Belgeler\\BORU\\maskot)."), style="Bk.TLabel").pack(anchor="w", pady=(2, 10))

        def kaydet():
            if not D["klasor"]:
                bilgi2.config(text=_("Önce görseli seç."), foreground="#a33a3a"); return
            isim = ad.get().strip() or _("Benim maskotum")
            kimlik = re.sub(r"[^a-z0-9_]+", "_", isim.lower().translate(str.maketrans("çğıöşüâî", "cgiosuai"))).strip("_") or "maskot"
            hedef, i = os.path.join(KISISEL_MASKOT, kimlik), 1
            while os.path.exists(hedef):                       # aynı adlı set varsa üstüne yazılmaz
                i += 1; hedef = os.path.join(KISISEL_MASKOT, "%s_%d" % (kimlik, i))
            os.makedirs(KISISEL_MASKOT, exist_ok=True); shutil.move(D["klasor"], hedef)
            json.dump({"ad": isim, "lisans": "kisisel" if kisisel.get() else "kendi", "kaynak": D["kaynak"]},
                      open(os.path.join(hedef, "bilgi.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
            k = os.path.basename(hedef); secili.set(k); maskot_degistir(k); maskot_menusu()
            S["metin"] = _("Yeni maskotun hazır: %s. Sağ tık > Maskot'tan istediğin zaman değiştirebilirsin.") % isim; S["mod"] = "sevincli"; w.destroy()
        alt_sat = tk.Frame(cer, bg="#f6f3ec"); alt_sat.pack(fill="x", side="bottom")
        ttk.Button(alt_sat, text=_("Kaydet ve kullan"), command=kaydet).pack(side="right")
        ttk.Button(alt_sat, text=_("Vazgeç"), command=w.destroy).pack(side="right", padx=8)
        if os.environ.get("BORU_SIHIRBAZ_SINA") and not getattr(sys, "frozen", False):   # sınama (yalnız kaynaktan): doldurur, görüntü alır, kaydeder
            t, g, e = os.environ["BORU_SIHIRBAZ_SINA"].split("|")
            tarif.insert("1.0", t); kopyala()
            filedialog.askopenfilename = lambda **k: g; sec()

            def cek():
                from PIL import ImageGrab
                w.update(); x, y = w.winfo_rootx(), w.winfo_rooty(); ImageGrab.grab(bbox=(x, y, x + w.winfo_width(), y + w.winfo_height())).save(e)
                kaydet()
            w.after(1500, cek)

    maskot_menusu()
    menu.insert_cascade(0, label=_("Maskot"), menu=alt)
    import dil as dil_mod
    dmenu = tk.Menu(menu, tearoff=0); dsec = tk.StringVar(value=dil_mod.DIL)

    def dil_degistir(d):
        a["dil"] = d; ayar_yaz(a)
        S["metin"] = ("Dil değişikliği BÖRÜ'yü yeniden açınca geçerli olur." if d == "tr" else "The language change takes effect after you restart BÖRÜ.")
    for kod, ad_ in dil_mod.DILLER.items():
        dmenu.add_radiobutton(label=ad_, variable=dsec, value=kod, command=lambda k=kod: dil_degistir(k))
    menu.add_separator(); menu.add_cascade(label="Dil / Language", menu=dmenu)
    # ---- rızalı, anonim geri bildirim (varsayılan kapalı; bkz. geribildirim.py ve PRIVACY.md)
    import geribildirim
    gb = tk.BooleanVar(value=geribildirim.izin() is True)

    def gb_degistir():
        geribildirim.izin_yaz(gb.get())
        S["metin"] = (_("Anonim geri bildirim açık. Haftada en çok bir kez, gönderdiklerimi önce Belgeler\\BORU\\gonderilenler'e yazarım.")
                      if gb.get() else _("Anonim geri bildirim kapalı. Hiçbir şey göndermem."))
        if gb.get():
            geribildirim.arka_planda(SURUM, dil_mod.DIL)

    def gonderilenler():
        os.makedirs(geribildirim.KLASOR, exist_ok=True)
        try:
            os.startfile(geribildirim.KLASOR)
        except Exception:
            pass
    menu.add_checkbutton(label=_("Anonim geri bildirim gönder"), variable=gb, command=gb_degistir)
    menu.add_command(label=_("Gönderilenleri göster"), command=gonderilenler)

    # ---- yerel küçük model (Faz 5; bkz. model.py). İndirme yalnız buradaki "Evet" ile.
    import model as model_mod

    def yerel_model():
        def is_(fn):                     # ağ işleri pencereyi dondurmasın
            threading.Thread(target=fn, daemon=True).start()

        def bak():
            d = model_mod.durum(); ad, gb_, lis = model_mod.MODELLER.get(d["model"], (d["model"], "?", "?"))
            if not d["sunucu"]:
                def geri(c):
                    if c == _("Sayfayı aç"):
                        import webbrowser; webbrowser.open(model_mod.OLLAMA_INDIR)
                        kuyruk.put(("kurt", _("Ollama'yı kurduktan sonra bana yeniden sağ tıkla > Yerel model.")))
                    else:
                        kuyruk.put(("kurt", _("Peki. İstediğinde sağ tık > Yerel model.")))
                kuyruk.put(("sor", {"metin": _("Yerel model için bu bilgisayarda Ollama gerekiyor (ücretsiz, açık kaynak; modeli ekran kartında çalıştırır). "
                                             "Ben program kurmam: indirme sayfasını açayım, sen kur.\n\n%s") % model_mod.OLLAMA_INDIR,
                                    "secenekler": [_("Sayfayı aç"), _("Şimdi değil")], "geri": geri, "cevap": None}))
                return
            if d["acik"] and d["indirilmis"]:
                def geri(c):
                    if c == _("Kapat"):
                        model_mod.ayar_yaz(acik=False); is_(model_mod.bosalt)
                        kuyruk.put(("kurt", _("Yerel modeli kapattım. Kurallarla (anahtar kelime) çalışmaya devam ederim.")))
                    elif c in (_("Hızlı kip"), _("Doğru kip")):
                        hedef = model_mod.KIPLER["hizli" if c == _("Hızlı kip") else "dogru"]
                        had, hgb, hlis = model_mod.MODELLER[hedef]

                        def gec():
                            model_mod.bosalt(); model_mod.ayar_yaz(ad=hedef)
                            kuyruk.put(("kurt", _("%s: %s. Sağ tık > Yerel model ile geri dönebilirsin.") % (c, had)))
                        if hedef in model_mod.yuklu():
                            is_(gec); return

                        def geri2(c2):
                            if c2 != _("Evet"):
                                kuyruk.put(("kurt", _("Peki, kipi değiştirmedim."))); return

                            def indir2():
                                try:
                                    kuyruk.put(("mod", "calisiyor"))
                                    model_mod.indir(lambda y, dr: kuyruk.put(("kurt", _("%s indiriliyor: %s%s") % (had, dr, " %%%d" % y if y is not None else ""))), ad=hedef)
                                    gec(); kuyruk.put(("mod", "sevincli"))
                                except Exception as ex:
                                    kuyruk.put(("kurt", _("İndirme olmadı: %s. Hiçbir şeyi açmadım.") % ex)); kuyruk.put(("mod", "endiseli"))
                            is_(indir2)
                        kuyruk.put(("sor", {"metin": _("%s için %s (lisans %s) Ollama ile indirilir (~%s GB). İndireyim mi?") % (c, had, hlis, hgb),
                                            "secenekler": [_("Evet"), _("Hayır")], "geri": geri2, "cevap": None}))
                    else:
                        kuyruk.put(("kurt", _("Tamam, yerel model açık kalıyor.")))
                hizli = model_mod.hizli_mi(d["model"])
                kuyruk.put(("sor", {"metin": _("Yerel model açık: %s (Ollama %s). Ekran kartını yalnız soru sorulunca kullanır; 5 dakika boşta kalınca bellekten iner.")
                                             % (ad, d["sunucu"]) + "\n\n" + (_("Şu an hızlı kip: birkaç saniyede yanıtlar; Türkçesi daha zayıf, özel profilini kullanmaz.") if hizli else
                                                                             _("Şu an doğru kip: daha isabetli ama bir yanıt yarım dakika sürebilir.")),
                                    "secenekler": [_("Açık kalsın"), _("Doğru kip") if hizli else _("Hızlı kip"), _("Kapat")], "geri": geri, "cevap": None}))
                return

            def geri(c):
                if c != _("Evet"):
                    kuyruk.put(("kurt", _("Peki, yerel modeli kurmadım."))); return

                def indir():
                    try:
                        kuyruk.put(("mod", "calisiyor"))
                        if not d["indirilmis"]:
                            model_mod.indir(lambda y, dr: kuyruk.put(("kurt", _("%s indiriliyor: %s%s") % (ad, dr, " %%%d" % y if y is not None else ""))))
                        model_mod.ayar_yaz(acik=True)
                        kuyruk.put(("kurt", _("Yerel model hazır: %s. Bana sağ tıkla > BÖRÜ'ye sor.") % ad)); kuyruk.put(("mod", "sevincli"))
                    except Exception as ex:
                        kuyruk.put(("kurt", _("İndirme olmadı: %s. Hiçbir şeyi açmadım.") % ex)); kuyruk.put(("mod", "endiseli"))
                is_(indir)
            kuyruk.put(("sor", {"metin": _("Yerel küçük modeli açayım mı?\n\n%s (lisans %s) %sbu bilgisayarda çalışır; ekran kartını yalnız soru sorulunca "
                                         "kullanır. Sorduğun hiçbir şey dışarı gönderilmez.") % (ad, lis, "" if d["indirilmis"] else _("Ollama ile indirilir (~%s GB), ") % gb_),
                                "secenekler": [_("Evet"), _("Hayır")], "geri": geri, "cevap": None}))
        is_(bak)

    def sor_penceresi():
        if S.get("sorp") is not None and S["sorp"].winfo_exists():
            S["sorp"].lift(); return
        w = tk.Toplevel(kok); S["sorp"] = w; w.title(_("BÖRÜ'ye sor")); w.geometry("620x520"); w.configure(bg="#f6f3ec")
        try:
            w.iconbitmap(os.path.join(BASE, "boru.ico"))
        except Exception:
            pass
        tk.Label(w, text=_("Yapay zekâyla çalışırken takıldığın şeyi yaz (ör. \"Codex'e nasıl iş vereyim?\", \"model yapılamaz diyor\")."),
                 bg="#f6f3ec", wraplength=590, justify="left").pack(anchor="w", padx=12, pady=(12, 4))
        giris = tk.Text(w, height=4, wrap="word", font=("Segoe UI", 10)); giris.pack(fill="x", padx=12)
        cikti = tk.Text(w, wrap="word", font=("Segoe UI", 10), bg="white"); cikti.pack(fill="both", expand=True, padx=12, pady=8)
        alt = tk.Frame(w, bg="#f6f3ec"); alt.pack(fill="x", padx=12, pady=(0, 10))
        prof = tk.BooleanVar(value=True)
        tk.Checkbutton(alt, text=_("Özel profilimi kullan (bu bilgisayardan çıkmaz)"), variable=prof, bg="#f6f3ec").pack(side="left")

        def yaz(t):
            try:
                if w.winfo_exists():
                    cikti.delete("1.0", "end"); cikti.insert("end", t)
            except Exception:
                pass

        def gonder(_e=None):
            soru = giris.get("1.0", "end").strip()
            if not soru:
                return "break"
            yaz(_("Düşünüyorum…")); kuyruk.put(("mod", "calisiyor"))

            def is_():
                d = model_mod.durum()
                if d["hazir"]:
                    try:
                        y, kim, sn = model_mod.sor(soru, profil=prof.get())
                        kok.after(0, yaz, y + "\n\n— " + _("Yerel model %s, %s sn. Dayandığı kurallar: %s. Küçük bir model; kendi yargınla kullan.") % (d["model"], sn, ", ".join(kim) or "-"))
                        kuyruk.put(("mod", "sevincli")); return
                    except Exception as ex:
                        not_ = _("Yerel model yanıt vermedi (%s).") % ex
                else:
                    not_ = _("Yerel model kapalı ya da kurulu değil (sağ tık > Yerel model). Şimdilik kurallardan buluyorum:")
                b = yontem_mod.bul(soru)
                kok.after(0, yaz, not_ + "\n\n" + ("\n\n".join(yontem_mod.yaz(k) for _p, k in b) if b else yontem_mod.katalog()))
                kuyruk.put(("mod", "bos"))
            threading.Thread(target=is_, daemon=True).start()
            return "break"
        ttk.Button(alt, text=_("Sor"), command=gonder).pack(side="right")
        giris.bind("<Control-Return>", gonder); giris.focus_set()
        if os.environ.get("BORU_SOR_SINA") and not getattr(sys, "frozen", False):     # sınama: soruyu yaz, gönder, yanıtı dosyaya yaz
            giris.insert("1.0", os.environ["BORU_SOR_SINA"]); gonder()

            def bekle():
                t = cikti.get("1.0", "end").strip()
                if t and t != _("Düşünüyorum…"):
                    open(os.environ["BORU_SOR_CIKTI"], "w", encoding="utf-8").write(t); kok.destroy()
                else:
                    kok.after(500, bekle)
            kok.after(500, bekle)
    import yontem as yontem_mod
    menu.add_separator()
    menu.add_command(label=_("BÖRÜ'ye sor…"), command=sor_penceresi)
    menu.add_command(label=_("Yerel model…"), command=yerel_model)
    if os.environ.get("BORU_SOR_SINA") and not getattr(sys, "frozen", False):
        kok.after(400, sor_penceresi)

    def gb_sor():
        """Bir kez sorar (yanıtsız kalırsa bir sonraki açılışta yeniden). Başka bir soru ekrandaysa bu açılışta sormaz."""
        if geribildirim.izin() is not None or S.get("soru") or (shot and not os.environ.get("BORU_GB_SINA")):
            if geribildirim.izin() is True:
                geribildirim.arka_planda(SURUM, dil_mod.DIL)
            return
        if mcp:                                  # model çalışırken sorma (onay sorularıyla çakışır); bir sonraki normal açılışta sorulur
            return

        def geri(cevap):
            evet = cevap == _("Evet, gönder")
            geribildirim.izin_yaz(evet); gb.set(evet)
            S["metin"] = (_("Teşekkürler! Haftada en çok bir kez anonim özet gönderirim; önce Belgeler\\BORU\\gonderilenler'e yazarım. Sağ tık menüsünden istediğin an kapatabilirsin.")
                          if evet else _("Peki, hiçbir şey göndermem. Fikrin değişirse sağ tık > Anonim geri bildirim gönder."))
        S["soru"] = {"metin": _("BÖRÜ'yü geliştirmemize yardım eder misin?\n\nHaftada en çok bir kez anonim bir kullanım özeti göndereyim: hangi adım kaç kez çalıştı ya da durdu, "
                                "hangi dersler çıktı. Dosya, klasör ve kişi adı, model notu, görsel GÖNDERİLMEZ. Gönderdiğim her şeyi önce Belgeler\\BORU\\gonderilenler'e "
                                "yazarım; istediğin an kapatırsın.\nAyrıntı: github.com/anildagci/boru → PRIVACY.md"),
                     "secenekler": [_("Evet, gönder"), _("Hayır")], "geri": geri, "cevap": None}
    if not os.environ.get("BORU_EV") or os.environ.get("BORU_GB_SINA"):
        kok.after(2500, gb_sor)
    if not mcp:
        menu.insert_command(1, label=_("Kendi maskotunu oluştur…"), command=maskot_sihirbazi)
    if os.environ.get("BORU_MENU_TANI"):     # tanı: gerçek pencerede kurulan menünün satırlarını yazar ve kapanır
        open(os.environ["BORU_MENU_TANI"], "w", encoding="utf-8").write(
            "\n".join("%s | %s" % (alt.entrycget(i, "label"), alt.entrycget(i, "value") if alt.type(i) == "radiobutton" else alt.type(i))
                      for i in range(alt.index("end") + 1) if alt.type(i) != "separator") + "\n")
        kok.after(300, kok.destroy)
    cv.bind("<Button-3>", lambda e: menu.tk_popup(e.x_root, e.y_root))
    try:
        kok.iconbitmap(os.path.join(BASE, "boru.ico"))
    except Exception:
        pass
    if os.environ.get("BORU_SIHIRBAZ_SINA") and not getattr(sys, "frozen", False):
        kok.after(500, maskot_sihirbazi)
    if not mcp and (not shot or os.environ.get("BORU_EV")):     # açılışta bağlantıya bak (deneme ekran görüntüsünde yalnız sahte evle)
        kok.after(700, baglanti_kontrol)
    if shot:
        def cek():
            from PIL import ImageGrab
            kok.update(); x, y = kok.winfo_rootx(), kok.winfo_rooty()
            ImageGrab.grab(bbox=(x, y, x + W, y + H)).save(shot); kok.destroy()
        kok.after(int(float(os.environ.get("BORU_SHOT_SN", "1.6")) * 1000), cek)
    tik(); kok.mainloop()


if __name__ == "__main__":
    if "--mcp" in sys.argv:                  # Claude Code / Codex bağlantısı (MCP, stdio)
        import boru_mcp
        sinama = sys.argv[sys.argv.index("--sinama") + 1] if ("--sinama" in sys.argv and not getattr(sys, "frozen", False)) else None
        sys.exit(boru_mcp.baslat(Motor, Dur, SURUM, pencere=None if os.environ.get("BORU_PENCERESIZ") == "1" else pencere, sinama=sinama))
    if "--maskotlar" in sys.argv:            # tanı: hangi maskot setlerini, nerede görüyorum
        satir = ["BASE=%s" % BASE, "KISISEL=%s (var: %s)" % (KISISEL_MASKOT, os.path.isdir(KISISEL_MASKOT)), "secili=%s" % ayar_oku().get("maskot")]
        satir += ["%s | %s | %s | %s" % m for m in maskotlar()]
        hedef = sys.argv[sys.argv.index("--maskotlar") + 1] if len(sys.argv) > sys.argv.index("--maskotlar") + 1 else None
        (open(hedef, "w", encoding="utf-8").write("\n".join(satir) + "\n") if hedef else print("\n".join(satir)))
        sys.exit(0)
    if "--maskot" in sys.argv:               # maskot sayfasını (3x2) bu bilgisayarın maskot setlerine keser
        import maskot_kes
        al = lambda k, v=None: sys.argv[sys.argv.index(k) + 1] if k in sys.argv else v
        kimlik = re.sub(r"[^a-z0-9_]+", "_", (al("--ad") or "benim_maskotum").lower()).strip("_")
        hedef = os.path.join(KISISEL_MASKOT, kimlik); maskot_kes.kes(al("--maskot"), hedef)
        json.dump({"ad": al("--isim", kimlik), "lisans": "kisisel" if "--kisisel" in sys.argv else "kendi",
                   "kaynak": os.path.basename(al("--maskot"))}, open(os.path.join(hedef, "bilgi.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        sys.exit(0)
    if "--dersler" in sys.argv:              # ders adayları raporu (geliştirici ve kullanıcının birlikte değerlendirmesi için)
        import dersler
        yol, A = dersler.rapor(sys.argv[sys.argv.index("--rapor") + 1] if "--rapor" in sys.argv else dersler.RAPOR)
        sys.stdout and print(_("%d ders adayı (%d yeni). Rapor: %s") % (len(A), sum(a["karar"] == "yeni" for a in A), yol))
        sys.exit(0)
    if "--run" in sys.argv:
        sys.exit(komut_satiri(sys.argv))
    pencere(sys.argv[sys.argv.index("--shot") + 1] if "--shot" in sys.argv else None,
            sinama=sys.argv[sys.argv.index("--sinama") + 1] if ("--sinama" in sys.argv and not getattr(sys, "frozen", False)) else None)
