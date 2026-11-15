# kurallar.json'dan okunabilir yöntem notlarını (TR/EN) ve eğitim örneklerini (JSONL) üretir.
# Builds readable method notes (TR/EN) and training examples (JSONL) from kurallar.json.
import json, os

BURA = os.path.dirname(os.path.abspath(__file__))
KAT = {
    "baslangic": ("Başlangıç", "Getting started"), "netlestirme": ("Netleştirme", "Clarifying"),
    "kalite": ("Kalite", "Quality"), "alternatif": ("Alternatifler", "Alternatives"),
    "guvenlik": ("Güvenlik ve geri alınabilirlik", "Safety and reversibility"),
    "iletisim": ("İletişim", "Communication"), "ekip": ("Modellerle ekip", "Teaming with models"),
    "urun": ("Ürün", "Product"), "uretim": ("Üretim", "Production"),
}
ETIKET = {
    "tr": {"bas": "Yapay zekâ ile çalışma yöntemi", "giris": "Gerçek projelerden damıtılmış kurallar. BÖRÜ bunları `boru_yontem` aracıyla modele sunar. Bu dosya `derle_bilgi.py` ile `kurallar.json`'dan üretilir; elle düzenleme.",
           "ne": "Ne zaman", "yap": "Yap", "yapma": "Yapma", "neden": "Neden", "i": 0},
    "en": {"bas": "A method for working with AI", "giris": "Rules distilled from real projects. BÖRÜ serves them to the model through the `boru_yontem` tool. This file is generated from `kurallar.json` by `derle_bilgi.py`; don't edit by hand.",
           "ne": "When", "yap": "Do", "yapma": "Don't", "neden": "Why", "i": 1},
}


def yukle():
    return json.load(open(os.path.join(BURA, "kurallar.json"), encoding="utf-8"))["kurallar"]


def md(kurallar, dil):
    e = ETIKET[dil]; s = ["# " + e["bas"], "", e["giris"], ""]
    for kat, adlar in KAT.items():
        grup = [k for k in kurallar if k["kategori"] == kat]
        if not grup: continue
        s += ["## " + adlar[e["i"]], ""]
        for k in grup:
            s += ["### %s · %s" % (k["id"], k["baslik"][dil]), "", "**%s:** %s" % (e["ne"], k["ne_zaman"][dil]), ""]
            s += ["**%s:**" % e["yap"]] + ["- " + x for x in k["yap"][dil]] + [""]
            s += ["**%s:**" % e["yapma"]] + ["- " + x for x in k["yapma"][dil]] + [""]
            s += ["**%s:** %s" % (e["neden"], k["neden"][dil]), ""]
    return "\n".join(s)


def ornekler(kurallar):
    """Her kural için iki dilde soru-cevap örnekleri (ileride ince ayar için)."""
    S = {"tr": ["%s ne yapmalıyım?", "Şu durumdayım: %s. Yapay zekâyla nasıl ilerleyeyim?"],
         "en": ["What should I do %s?", "My situation: %s. How should I proceed with the AI?"]}
    SIS = {"tr": "Sen BÖRÜ'sün: kullanıcının yapay zekâ ile çalışma yöntemine göre kısa, karar odaklı öneri veren yardımcı.",
           "en": "You are BÖRÜ: an assistant giving short, decision-focused advice based on the user's method of working with AI."}
    for k in kurallar:
        for dil in ("tr", "en"):
            nz = k["ne_zaman"][dil]
            nz_kucuk = nz[0].lower() + nz[1:]
            cevap = "%s\n\n%s\n%s\n\n%s\n%s\n\n%s" % (
                k["baslik"][dil],
                ETIKET[dil]["yap"] + ":", "\n".join("- " + x for x in k["yap"][dil]),
                ETIKET[dil]["yapma"] + ":", "\n".join("- " + x for x in k["yapma"][dil]),
                ETIKET[dil]["neden"] + ": " + k["neden"][dil])
            for kalip in S[dil]:
                yield {"kural": k["id"], "dil": dil, "messages": [
                    {"role": "system", "content": SIS[dil]},
                    {"role": "user", "content": (lambda t: t[0].upper() + t[1:])(kalip % nz_kucuk)},
                    {"role": "assistant", "content": cevap}]}


if __name__ == "__main__":
    K = yukle()
    for dil in ("tr", "en"):
        open(os.path.join(BURA, "YONTEM.%s.md" % dil), "w", encoding="utf-8", newline="\n").write(md(K, dil))
    n = 0
    with open(os.path.join(BURA, "ornekler.jsonl"), "w", encoding="utf-8", newline="\n") as f:
        for o in ornekler(K):
            f.write(json.dumps(o, ensure_ascii=False) + "\n"); n += 1
    print(len(K), "kural,", n, "örnek")
