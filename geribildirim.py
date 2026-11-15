# BÖRÜ'nün rızalı, anonim geri bildirimi. Yalnız kullanıcı açıkça izin verdiyse (ayar.json: "geribildirim": true) çalışır.
# Haftada en çok bir kez, son gönderimden bu yana günlükteki kayıtlardan bir ÖZET çıkarır, önce Belgeler\BORU\gonderilenler
# altına yazar (kullanıcı neyin gittiğini görür), sonra sunucuya gönderir.
# Gönderilmeyenler: dosya/klasör adları, kişi adları, model notları, BÖRÜ'nün tam yanıt metinleri, görseller, sınama kayıtları.
# Gönderilenler: sürüm, dil, işletim sistemi sürümü, rastgele kurulum kimliği, araç başına çağrı/hata/süre, onay sonuçları,
# ders adayları (başlık, dosya yolları ve tırnak içi metinler silinerek; sayı yerine <n>).
import os, json, time, uuid, platform, threading, urllib.request, re
import dersler

ADRES = os.environ.get("BORU_GERI_ADRES", "https://boru-geribildirim.anilcan-dagci.workers.dev/gonder")
SIKLIK = 7 * 86400
KLASOR = os.path.join(dersler.KOK, "gonderilenler")


def _ayar():
    try:
        return json.load(open(os.path.join(dersler.KOK, "ayar.json"), encoding="utf-8"))
    except Exception:
        return {}


def _ayar_yaz(d):
    os.makedirs(dersler.KOK, exist_ok=True)
    json.dump(d, open(os.path.join(dersler.KOK, "ayar.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)


def izin():
    """True: izin verildi; False: reddedildi; None: henüz sorulmadı."""
    return _ayar().get("geribildirim")


def izin_yaz(deger):
    d = _ayar(); d["geribildirim"] = bool(deger); d.setdefault("kurulum", uuid.uuid4().hex); _ayar_yaz(d)


def _temizle(metin):
    m = dersler._sade(metin)
    m = re.sub(r"'[^']*'", "'…'", m)        # tek tırnak içi (karakter adı, kullanıcının sözü) gitmez; çift tırnaktaki temizlenmiş neden kalır
    return m[:140]


def ozet(surum, dil):
    """Gönderilecek paketi hazırlar (göndermez). Son gönderimden bu yana, sınama olmayan kayıtlardan."""
    a = _ayar(); son = a.get("geribildirim_son", "")
    K = [k for k in dersler.kayitlar() if (k.get("zaman") or "") > son and not k.get("sinama")]
    araclar = {}
    for k in K:
        if k.get("arac"):
            x = araclar.setdefault(k["arac"], {"cagri": 0, "hata": 0, "sure": []})
            x["cagri"] += 1; x["hata"] += 1 if k.get("hata") else 0; x["sure"].append(k.get("sure") or 0)
    for x in araclar.values():
        s = sorted(x.pop("sure")); x["ortanca_sure"] = s[len(s) // 2] if s else 0
    onaylar = {}
    for k in K:
        if "onay" in k:
            t = dersler._onay_tur(k); c = k.get("cevap"); sec = k.get("secenekler") or []
            sonuc = "yanitsiz" if c is None else ("kabul" if sec and c == sec[0] else "ret")
            onaylar.setdefault(t, {"kabul": 0, "ret": 0, "yanitsiz": 0})[sonuc] += 1
    ders = [{"tur": x["tur"], "baslik": _temizle(x["baslik"]), "kanit": len(x["kanit"])} for x in dersler.adaylar(K) if x["tur"] != "not"]
    zamanlar = [k.get("zaman") for k in K if k.get("zaman")]
    return {"sema": 1, "surum": surum, "dil": dil, "os": "%s %s" % (platform.system(), platform.release()),
            "kurulum": a.get("kurulum") or uuid.uuid4().hex, "donem": {"bas": min(zamanlar, default=""), "son": max(zamanlar, default="")},
            "araclar": araclar, "onaylar": onaylar, "dersler": ders[:50]}


def gonder(surum, dil, zorla=False):
    """İzin varsa ve zamanı geldiyse özeti yazar ve gönderir. Döner: (durum, dosya yolu ya da None)."""
    a = _ayar()
    if a.get("geribildirim") is not True:
        return "izin yok", None
    if not zorla and time.time() - a.get("geribildirim_zaman", 0) < SIKLIK:
        return "zamanı gelmedi", None
    p = ozet(surum, dil)
    if not p["araclar"] and not p["dersler"] and not zorla:
        return "yeni kayıt yok", None
    os.makedirs(KLASOR, exist_ok=True)
    yol = os.path.join(KLASOR, time.strftime("%Y-%m-%d_%H%M%S") + ".json")
    json.dump(p, open(yol, "w", encoding="utf-8"), indent=1, ensure_ascii=False)       # önce kullanıcının görebileceği yere
    try:
        istek = urllib.request.Request(ADRES, data=json.dumps(p).encode("utf-8"), headers={"content-type": "application/json", "user-agent": "BORU/" + surum})
        cevap = json.loads(urllib.request.urlopen(istek, timeout=15).read().decode("utf-8"))
        durum = "gönderildi" if cevap.get("tamam") else "sunucu reddetti: %s" % cevap.get("hata")
    except Exception as ex:
        durum = "gönderilemedi: %s" % ex
    a = _ayar(); a["kurulum"] = p["kurulum"]
    if durum == "gönderildi":
        a["geribildirim_zaman"] = time.time(); a["geribildirim_son"] = p["donem"]["son"] or a.get("geribildirim_son", "")
    _ayar_yaz(a)
    with open(os.path.join(KLASOR, "_gunluk.txt"), "a", encoding="utf-8") as f:
        f.write("%s  %s  %s\n" % (time.strftime("%Y-%m-%d %H:%M:%S"), os.path.basename(yol), durum))
    return durum, yol


def arka_planda(surum, dil):
    threading.Thread(target=lambda: gonder(surum, dil), daemon=True).start()
