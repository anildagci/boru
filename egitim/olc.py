# Faz 6 ölçümü: olcum_seti.json'daki 60 soruyu verilen Ollama modellerine BÖRÜ'nün çalışma bağlamıyla sorar ve puanlar.
# Kabul ölçütü: soru diliyle yanıt %100, doğru kural kimliği >= %80 (konu dışı hariç), döngü 0, kuralı ters uygulama 0.
# Kullanım: python egitim/olc.py <cikti.json> model1 [model2 ...]
import sys, os, json, re, time
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
os.environ.setdefault("BORU_DIL", "tr")
import model
from veri_uret import dil_bul, dongu_var

SET = json.load(open(os.environ.get("BORU_OLCUM_SET") or os.path.join(os.path.dirname(os.path.abspath(__file__)), "olcum_seti.json"), encoding="utf-8"))["sorular"]


def sor(ad, soru, dil):
    bilgi, kim = model.baglam(soru, profil=False, dil=dil)
    govde = {"model": ad, "stream": False, "keep_alive": "10m",
             "messages": [{"role": "system", "content": model.SISTEM[dil] + "\n\n" + bilgi}, {"role": "user", "content": soru}],
             "options": {"temperature": 0.2, "num_ctx": 8192}}
    if model.hizli_mi(ad) or ad.startswith("boru"):
        govde["options"].update(repeat_penalty=1.15, num_predict=350)
    else:
        govde["think"] = True
    t0 = time.time(); d = model._istek("/api/chat", govde, sure=300)
    return model._temizle(d["message"]["content"]), round(time.time() - t0, 1), kim


def puanla(s, y):
    anilan = set(re.findall(r"\b([A-Z]\d{2})\b", y))
    p = {"dil": dil_bul(y) == s["dil"], "dongu": dongu_var(y),
         "ters": any(re.search(r, y.lower()) for r in s["yasak"])}
    if s.get("konu_disi"):
        p["kural"] = None
    else:
        p["kural"] = bool(anilan & set(s["kural"]))
    return p


def ozet(sonuc):
    n = len(sonuc); konu = [x for x in sonuc if x["p"]["kural"] is not None]
    return {"dil_%": round(100 * sum(x["p"]["dil"] for x in sonuc) / n), "kural_%": round(100 * sum(x["p"]["kural"] for x in konu) / len(konu)),
            "dongu": sum(x["p"]["dongu"] for x in sonuc), "ters": sum(x["p"]["ters"] for x in sonuc),
            "ort_sn": round(sum(x["sn"] for x in sonuc) / n, 1)}


def gecti(o):
    return o["dil_%"] == 100 and o["kural_%"] >= 80 and o["dongu"] == 0 and o["ters"] == 0


if __name__ == "__main__":
    cikti, modeller = sys.argv[1], sys.argv[2:]; hepsi = {}
    for ad in modeller:
        sonuc = []
        sor(ad, "ısınma", "tr")
        for s in SET:
            y, sn, kim = sor(ad, s["soru"], s["dil"])
            sonuc.append({"soru": s["soru"], "yanit": y, "sn": sn, "baglam": kim, "p": puanla(s, y)})
        o = ozet(sonuc); o["gecti"] = gecti(o); hepsi[ad] = {"ozet": o, "sonuc": sonuc}
        print(ad, json.dumps(o, ensure_ascii=False), flush=True)
    json.dump(hepsi, open(cikti, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
