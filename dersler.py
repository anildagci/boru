# BÖRÜ'nün ders adayları: günlükte tekrar eden durumları ayıklar, her adayı kanıtıyla yazar.
# Adaylar BÖRÜ'nün davranışını kendiliğinden DEĞİŞTİRMEZ. Kullanıcı (geliştiriciyle birlikte) değerlendirir; onaylananlar
# bir sonraki sürümde uygulanır. Kararlar Belgeler\BORU\dersler.json'da tutulur.
import os, re, json, time, hashlib, collections, statistics

# BÖRÜ'nün kullanıcı verisi (ayar, günlük, kişisel maskotlar, dersler) tek yerde: Belgeler\BORU (BORU_VERI ile değişir).
# %APPDATA% kullanılmaz: Claude masaüstü uygulaması (MSIX paketi) içinden açılan süreçlerin %APPDATA% yazıları paketin
# gizli kopyasına yönlenir; Gezgin'den açılan BÖRÜ onları göremez (2026-11-16: kişisel maskot menüde çıkmadı).
KOK = os.environ.get("BORU_VERI") or os.path.join(os.path.expanduser("~"), "Documents", "BORU")
GUNLUK = os.path.join(KOK, "gunluk")
KARAR = os.path.join(KOK, "dersler.json")
RAPOR = os.path.join(KOK, "DERS_ADAYLARI.md")
ESIK = 2                                                           # bir örüntü en az bu kadar tekrar edince aday olur


def kayitlar():
    k = []
    if os.path.isdir(GUNLUK):
        for f in sorted(os.listdir(GUNLUK)):
            if f.endswith(".jsonl"):
                for satir in open(os.path.join(GUNLUK, f), encoding="utf-8"):
                    try:
                        k.append(json.loads(satir))
                    except Exception:
                        pass
    return k


def _sade(metin):
    """Yolları, sayıları ve deneme etiketlerini ayıklar; aynı türden durumlar aynı anahtara düşsün."""
    m = metin.split("\n")[0]
    m = re.sub(r"[A-Za-z]:[\\/].*?(\.[A-Za-z0-9]{2,5}\b|$)", "<yol>", m)          # boşluklu yollar da (uzantıya ya da satır sonuna kadar)
    m = re.sub(r"\d{4}_\d{4}[a-z]", "<deneme>", m)
    m = re.sub(r"\(deneme \d/3\)", "(deneme n/3)", m)
    m = re.sub(r"\d[\d.,]*", "<n>", m)
    return m.strip()[:160]


def _neden(k):
    if k.get("neden"):
        return k["neden"]
    y = k.get("yanit", "")
    m = re.search(r"^(?:Neden|Reason): (.+)$", y, re.M)          # kayıt Türkçe ya da İngilizce olabilir
    return m.group(1) if m else y.split("\n")[0]


def _onay_tur(k):
    if k.get("onay_tur"):
        return k["onay_tur"]
    o = k.get("onay", "")
    return ("teslim" if ("teslim etmek istiyor" in o or "wants to deliver" in o) else "bekci" if o.startswith(("Bekçi", "Watchdog"))
            else "renk" if ("renk kuralını" in o or "colour rule" in o) else "diger")


def _kanit(k):
    return {"zaman": k.get("zaman"), "klasor": os.path.basename((k.get("klasor") or "").rstrip("\\/")) or None,
            "arac": k.get("arac"), "sinama": bool(k.get("sinama")), "surum": k.get("surum") or "sürüm kaydı yok (0.2-d öncesi)"}


def adaylar(K=None):
    K = kayitlar() if K is None else K
    out = {}

    def ekle(tur, anahtar, baslik, oneri, kanit):
        i = hashlib.sha1(("%s|%s" % (tur, anahtar)).encode("utf-8")).hexdigest()[:8]
        a = out.setdefault(i, {"id": i, "tur": tur, "baslik": baslik, "oneri": oneri, "kanit": []})
        a["kanit"].append(_kanit(kanit))

    # 1) aynı nedenle tekrar tekrar duran adımlar
    karar_kaynakli = ("kullanıcı 'Hayır' dedi", "Kullanıcı 'Dur' dedi", "yanıt vermedi", "Kullanıcı 'Hayır' dedi",
                      "said 'No'", "said 'Stop'", "didn't answer")
    for k in K:
        if k.get("arac") and k.get("hata"):
            if any(x in k.get("yanit", "") for x in karar_kaynakli):   # kullanıcının kararıyla duranlar 3. maddede sayılır
                continue
            n = _sade(_neden(k))
            ekle("tekrar_eden_durma", k["arac"] + "|" + n, "%s aynı nedenle duruyor: \"%s\"" % (k["arac"], n),
                 "Nedeni ortadan kaldır: araç talimatı mı yetersiz (model yanlış sırayla çağırıyor), girdi mi hatalı, yoksa adımın kendisi mi zayıf?", k)
    # 2) üç denemede tutmayan adımlar
    for k in K:
        if any(x in k.get("yanit", "") for x in ("Üç kez denedim", "I tried three times")):
            ekle("uc_deneme", k.get("arac"), "%s üç denemede tutmadı" % k.get("arac"), "Adımın bu durumdaki zayıflığını incele; kullanıcıdan hangi ek bilgi istenmeli?", k)
    # 3) kullanıcı kararları
    for k in K:
        if "onay" in k:
            t, c = _onay_tur(k), k.get("cevap")
            if c is None:
                ekle("onay_yanitsiz", t, "%s sorusu yanıtsız kaldı" % t, "Kullanıcı pencereyi görmüyor olabilir: bildirim, ses ya da sürenin uzunluğu gözden geçirilmeli.", k)
            elif c in ("Hayır", "Dur", "No", "Stop"):
                ekle("onay_red", t, "Kullanıcı %s sorusuna '%s' dedi" % (t, c), "Model bu işi neden erken ya da yanlış durumda istiyor? Talimat ya da öneri metni düzeltilmeli mi?", k)
            elif t == "bekci" and c in ("Devam", "Continue"):
                ekle("bekci_hep_devam", t, "Bekçi ihlal buldu, kullanıcı yine de 'Devam' dedi", "Kural bu durumda fazla katı olabilir; bu ihlal türü uyarıya mı inmeli?", k)
    # 4) tekrar eden bekçi ihlal türleri
    for k in K:
        for m in re.finditer(r"\[(?:İHLAL|VIOLATION)\] ([^:]+):", k.get("yanit", "")):
            ekle("bekci_ihlal", m.group(1), "Bekçi ihlali tekrar ediyor: %s" % m.group(1), "Bu değişikliği kim, neden yapıyor? Model talimatı ya da hibrit kip kuralı netleşmeli mi?", k)
    # 5) modelin ve kullanıcının notları (tek kayıt yeter)
    for k in K:
        if "not" in k and k.get("not"):
            ekle("not", k["not"], "Not: %s" % k["not"][:120], "Notu değerlendir.", k)
    # 6) yavaş adımlar
    sure = collections.defaultdict(list)
    for k in K:
        if k.get("arac") and not k.get("hata") and k.get("sure") is not None:
            sure[k["arac"]].append(k)
    for ad, ks in sure.items():
        if len(ks) >= 3:
            md = statistics.median(x["sure"] for x in ks)
            for x in ks:
                if x["sure"] > max(60, 3 * md):
                    ekle("yavas", ad, "%s bazen çok yavaş (ortanca %.0f sn)" % (ad, md), "Yavaş çağrıların klasörüne ve girdisine bak; ara haber yeterli mi?", x)
    return [a for a in out.values() if len(a["kanit"]) >= (1 if a["tur"] == "not" else ESIK)]


def kararlar():
    try:
        return json.load(open(KARAR, encoding="utf-8"))
    except Exception:
        return {}


def karar_yaz(i, karar, not_=""):
    d = kararlar(); d[i] = {"karar": karar, "not": not_, "zaman": time.strftime("%Y-%m-%d %H:%M:%S")}
    os.makedirs(KOK, exist_ok=True); json.dump(d, open(KARAR, "w", encoding="utf-8"), indent=1, ensure_ascii=False)


def rapor(yol=RAPOR):
    A = adaylar(); D = kararlar()
    for a in A:
        a["karar"] = D.get(a["id"], {}).get("karar", "yeni"); a["sinama_orani"] = sum(k["sinama"] for k in a["kanit"]) / len(a["kanit"])
    A.sort(key=lambda a: (a["karar"] != "yeni", -len(a["kanit"])))
    s = ["# BÖRÜ ders adayları", "", "Oluşturma: %s. Günlük: `%s` (%d kayıt). Eşik: en az %d tekrar (notlar için 1)." % (time.strftime("%Y-%m-%d %H:%M"), GUNLUK, len(kayitlar()), ESIK), "",
         "Adaylar BÖRÜ'nün davranışını değiştirmez. Kullanıcı ve geliştirici değerlendirir; onaylananlar bir sonraki sürümde uygulanır.", ""]
    for a in A:
        kl = sorted({k["klasor"] for k in a["kanit"] if k["klasor"]})
        s += ["## [%s] %s" % (a["id"], a["baslik"]), "",
              "- Tür: %s · Kanıt: %d kayıt · Karar: **%s**%s" % (a["tur"], len(a["kanit"]), a["karar"],
                                                                 " · sınama kaydı: %%%d" % round(100 * a["sinama_orani"]) if a["sinama_orani"] else ""),
              "- Klasörler: %s · Sürümler: %s" % (", ".join(kl) or "-", ", ".join(sorted({k["surum"] for k in a["kanit"]}))),
              "- İlk/son: %s / %s" % (a["kanit"][0]["zaman"], a["kanit"][-1]["zaman"]),
              "- Öneri: %s" % a["oneri"], ""]
    os.makedirs(os.path.dirname(yol), exist_ok=True); open(yol, "w", encoding="utf-8").write("\n".join(s))
    return yol, A
