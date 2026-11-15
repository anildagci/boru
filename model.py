# BÖRÜ'nün yerel küçük modeli (Faz 5). Model bu bilgisayarda Ollama ile çalışır; BÖRÜ ona yalnız 127.0.0.1 üzerinden konuşur.
# - Model kendiliğinden indirilmez: kullanıcı BÖRÜ penceresinde "Evet" demeden indirme yok (bkz. boru.py yerel_model, boru_mcp _model).
# - Ekran kartı yalnız gerektiğinde: her istekte keep_alive=5m; 5 dakika boşta kalınca Ollama modeli bellekten indirir.
# - Model, kural dosyasına (bilgi/kurallar.json) ve varsa kullanıcının özel profiline dayanarak yanıtlar; ikisi de bu bilgisayardan çıkmaz.
# - Ağ kütüphanesi yok (urllib); model kapalı ya da yoksa çağıran anahtar kelime eşlemesine (yontem.py) döner.
import json, os, re, time, urllib.request, urllib.error
from dil import DIL, KOK
import yontem

AYAR = os.path.join(KOK, "ayar.json")
VARSAYILAN = {"acik": False, "adres": "http://127.0.0.1:11434", "ad": "qwen3:4b"}
# Önerilen modeller: (görünen ad, yaklaşık indirme boyutu GB, lisans)
MODELLER = {"qwen3:4b": ("Qwen3 4B", 2.5, "Apache-2.0"), "qwen3:1.7b": ("Qwen3 1.7B", 1.4, "Apache-2.0"),
            "qwen3:8b": ("Qwen3 8B", 5.2, "Apache-2.0"),
            "qwen3:4b-instruct-2507-q4_K_M": ("Qwen3 4B Instruct", 2.5, "Apache-2.0")}
# İki kip (2026-11-16, aynı 6 soruyla ölçüldü): doğru = düşünen qwen3:4b (ort. 32 sn, Türkçede isabetli);
# hızlı = qwen3:4b-instruct (ort. ~3 sn; İngilizcesi iyi, Türkçesi zayıf; profille papağanlaşır, profilsiz ve tekrar cezasıyla çalışır).
KIPLER = {"dogru": "qwen3:4b", "hizli": "qwen3:4b-instruct-2507-q4_K_M"}


def hizli_mi(ad):
    return "instruct" in ad
OLLAMA_INDIR = "https://ollama.com/download"


def ayar():
    try:
        a = json.load(open(AYAR, encoding="utf-8")).get("model") or {}
    except Exception:
        a = {}
    return dict(VARSAYILAN, **{k: v for k, v in a.items() if k in VARSAYILAN})


def ayar_yaz(**k):
    try:
        d = json.load(open(AYAR, encoding="utf-8"))
    except Exception:
        d = {}
    d["model"] = dict(ayar(), **k)
    os.makedirs(KOK, exist_ok=True)
    gecici = AYAR + ".yeni"
    json.dump(d, open(gecici, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    os.replace(gecici, AYAR)


def _istek(yol, veri=None, sure=5, adres=None):
    url = (adres or ayar()["adres"]).rstrip("/") + yol
    govde = json.dumps(veri).encode("utf-8") if veri is not None else None
    r = urllib.request.Request(url, data=govde, headers={"Content-Type": "application/json"} if govde else {})
    with urllib.request.urlopen(r, timeout=sure) as y:
        return json.loads(y.read().decode("utf-8"))


def sunucu():
    """Ollama sürümü ya da None (çalışmıyor / kurulu değil)."""
    try:
        return _istek("/api/version", sure=2).get("version")
    except Exception:
        return None


def yuklu():
    try:
        return [m["name"] for m in _istek("/api/tags", sure=3).get("models", [])]
    except Exception:
        return []


def _var(ad, liste):
    return ad in liste or (":" not in ad and ad + ":latest" in liste)


def durum():
    """{'sunucu': sürüm|None, 'model': ad, 'indirilmis': bool, 'acik': bool, 'hazir': bool}"""
    a = ayar(); s = sunucu(); ind = bool(s) and _var(a["ad"], yuklu())
    return {"sunucu": s, "model": a["ad"], "indirilmis": ind, "acik": a["acik"], "hazir": bool(s and ind and a["acik"])}


def indir(cb=None, ad=None):
    """Modeli Ollama ile indirir. cb(yuzde|None, durum_metni) ara haber verir. Başarıda True."""
    ad = ad or ayar()["ad"]
    url = ayar()["adres"].rstrip("/") + "/api/pull"
    r = urllib.request.Request(url, data=json.dumps({"model": ad, "stream": True}).encode("utf-8"),
                               headers={"Content-Type": "application/json"})
    son, son_t = None, 0.0
    with urllib.request.urlopen(r, timeout=60) as y:
        for satir in y:
            try:
                d = json.loads(satir.decode("utf-8"))
            except Exception:
                continue
            if d.get("error"):
                raise RuntimeError(d["error"])
            yuzde = int(100 * d["completed"] / d["total"]) if d.get("total") and d.get("completed") else None
            if cb and (yuzde != son or time.time() - son_t > 5):
                son, son_t = yuzde, time.time(); cb(yuzde, d.get("status", ""))
            if d.get("status") == "success":
                return True
    return _var(ad, yuklu())


def bosalt():
    """Modeli ekran kartı belleğinden hemen indirir."""
    try:
        _istek("/api/generate", {"model": ayar()["ad"], "keep_alive": 0}, sure=10)
    except Exception:
        pass


SISTEM = {
 "tr": ("Sen BÖRÜ'sün: kullanıcının yapay zekâ ile çalışma yöntemine göre kısa, karar odaklı öneri veren yerel yardımcı.\n"
        "Kurallar:\n- Yalnız aşağıdaki KURALLAR'a ve varsa KULLANICI PROFİLİ'ne dayan. Dayandığın kuralın kimliğini parantezle an, ör. (N01).\n"
        "- İlk cümle doğrudan cevap olsun. En çok 6 madde. Süreç anlatma.\n- Kurallarda karşılığı yoksa bunu açıkça söyle; uydurma.\n"
        "- Silme, para, yayın, kalıcı iş varsa önce kullanıcının onayını almayı öner.\n- Kullanıcı hangi dilde yazdıysa o dilde yanıtla."),
 "en": ("You are BÖRÜ: a local assistant giving short, decision-focused advice based on the user's method of working with AI.\n"
        "Rules:\n- Rely only on the RULES below and the USER PROFILE if given. Cite the rule id you rely on in brackets, e.g. (N01).\n"
        "- The first sentence is the direct answer. At most 6 bullet points. No process narration.\n- If the rules don't cover it, say so plainly; don't invent.\n"
        "- If deletion, money, publishing or permanent work is involved, suggest getting the user's approval first.\n- Answer in the language the user wrote in."),
}


def baglam(soru, profil=True, dil=None, n=4):
    """Modele verilecek bilgi: soruya en uygun kurallar (yetmezse katalog) + varsa özel profil. (metin, kural kimlikleri)"""
    dil = dil or DIL; b = yontem.bul(soru, n=n)
    parca = ["KURALLAR / RULES:"] + [yontem.yaz(k, dil=dil) for _p, k in b]
    if len(b) < 2:
        parca += ["", "Katalog / Catalogue:", yontem.katalog(dil)]
    if profil and os.path.isfile(yontem.PROFIL):
        parca += ["", "KULLANICI PROFİLİ / USER PROFILE:", open(yontem.PROFIL, encoding="utf-8").read()[:3000]]
    return "\n\n".join(parca), [k["id"] for _p, k in b]


def _temizle(t):
    t = re.sub(r"<think>.*?</think>", "", t, flags=re.S)
    return t.strip()


def sor(soru, profil=True, dil=None, sure=180, ek=""):
    """Yerel modele sorar. (yanıt, kullanılan kural kimlikleri, saniye). Hazır değilse RuntimeError."""
    a = ayar(); dil = dil or DIL; t0 = time.time(); hizli = hizli_mi(a["ad"])
    bilgi, kimlikler = baglam(soru, profil and not hizli, dil)
    mesajlar = [{"role": "system", "content": SISTEM[dil] + "\n\n" + bilgi},
                {"role": "user", "content": (ek + "\n\n" if ek else "") + soru}]
    govde = {"model": a["ad"], "messages": mesajlar, "stream": False, "keep_alive": "5m",
             "options": {"temperature": 0.3, "num_ctx": 8192}}
    if hizli:                            # düşünmeyen model: döngüye girmesin, uzamasın
        govde["options"].update(temperature=0.2, repeat_penalty=1.15, num_predict=350)
        return _temizle((_istek("/api/chat", govde, sure=sure).get("message") or {}).get("content", "")), kimlikler, round(time.time() - t0, 1)
    # Ollama'daki qwen3:4b "düşünen" sürümdür ve think:false'u yok sayıp düşünmesini yanıta karıştırır.
    # think:true ile düşünme ayrı alana gider (atılır), yanıt temiz gelir. Düşünmeyen modeller think'i reddederse (400) onsuz dene.
    try:
        d = _istek("/api/chat", dict(govde, think=True), sure=sure)
    except urllib.error.HTTPError as ex:
        if ex.code != 400:
            raise
        d = _istek("/api/chat", govde, sure=sure)
    return _temizle((d.get("message") or {}).get("content", "")), kimlikler, round(time.time() - t0, 1)
