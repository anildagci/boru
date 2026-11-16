# Faz 6: ince ayar verisini yerel "doğru kip" modeliyle (düşünen qwen3:4b) üretir: damıtma.
# 1) her kural için çeşitli, gerçekçi kullanıcı soruları (TR + EN)  2) BÖRÜ'nün çalışma bağlamıyla yanıtlar  3) otomatik elek.
# Claude'un yazdığı metin eğitim verisine girmez. Yarıda kalırsa kaldığı yerden sürer (çıktı dosyalarına ekler).
# Kullanım: python egitim/veri_uret.py <cikti_klasoru> [--soru-basina 6] [--is 3]
import sys, os, json, re, time, random, threading, argparse
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
os.environ.setdefault("BORU_DIL", "tr")
import model, yontem

OGRETMEN = "qwen3:4b"
ALANLAR = {"tr": ["mobil oyun geliştirme", "YouTube video üretimi", "web sitesi kodlama", "3B karakter modelleme", "kitap yazma",
                  "küçük işletme muhasebesi", "üniversite ödevi", "veri analizi", "müzik prodüksiyonu", "sosyal medya içerik takvimi",
                  "masaüstü uygulama", "logo ve marka tasarımı"],
          # v2: BÖRÜ'nün asıl kitlesi yapay zekâyla kod yazanlar; soruların çoğu yine İngilizce üretilip çevrildiği için "en" listesi asıl olandır
          "en2": ["a TypeScript browser racing game with simulation tests", "an Android release of a Unity game", "a Git repo where two AI agents open PRs",
                  "a game character art pipeline (concept, 3D model, game export)", "game balance and ability tuning", "a release build and its release notes",
                  "a Python desktop app installer", "a web API with a CI pipeline", "replacing assets and music in a game before launch"],
          "en": ["indie game development", "YouTube video production", "web app coding", "3D character modelling", "novel writing",
                 "small business bookkeeping", "university assignment", "data analysis", "music production", "social media calendar",
                 "desktop tool", "logo and brand design"]}
ALANLAR["en"] = ALANLAR["en"] + ALANLAR.pop("en2")   # 21 alan; 9'u yapay zekâyla kod/oyun işi
USLUP = {"tr": ["samimi, 'kanka' diye başlayan kısa bir mesaj", "resmî ve ayrıntılı bir soru", "aceleyle yazılmış, yazım hatalı tek cümle",
                "modelin az önce söylediği bir şeye tepki", "bir plan anlatıp onay isteyen mesaj"],
         "en": ["a casual, short message", "a formal, detailed question", "a hurried one-liner with typos",
                "a reaction to something the AI just said", "a message describing a plan and asking for a go-ahead"]}


def _json_liste(t):
    t = re.sub(r"<think>.*?</think>", "", t, flags=re.S)
    m = re.search(r"\[.*\]", t, flags=re.S)
    try:
        return [x.strip() for x in json.loads(m.group(0)) if isinstance(x, str) and 10 < len(x.strip()) < 600] if m else []
    except Exception:
        return []


SORUCU = "qwen3:4b-instruct-2507-q4_K_M"     # soruları ve çevirileri hızlı model yazar (saniyeler); yanıtları düşünen model


def ogretmen(mesajlar, sure=300, dusun=True):
    d = model._istek("/api/chat", {"model": OGRETMEN, "messages": mesajlar, "stream": False, "think": dusun, "keep_alive": "10m",
                                   "options": {"temperature": 0.8 if not dusun else 0.6, "num_ctx": 8192}}, sure=sure)
    return model._temizle((d.get("message") or {}).get("content", ""))


def sorucu(istem, sicaklik=0.9, uzunluk=300):
    d = model._istek("/api/chat", {"model": SORUCU, "messages": [{"role": "user", "content": istem}], "stream": False, "keep_alive": "10m",
                                   "options": {"temperature": sicaklik, "repeat_penalty": 1.1, "num_predict": uzunluk}}, sure=120)
    return model._temizle((d.get("message") or {}).get("content", ""))


def _kopya_mi(soru, k):
    """Soru kuralın kendi cümlelerinden 4 kelimelik parça taşıyorsa ya da kimliği anıyorsa: gerçek kullanıcı böyle yazmaz."""
    if re.search(r"\b[A-Z]\d{2}\b", soru):
        return True
    kural = " ".join(k["baslik"][d] + " " + " ".join(k["yap"][d]) + " " + " ".join(k["yapma"][d]) for d in ("tr", "en")).lower()
    w = re.findall(r"[\wçğıöşü']+", soru.lower())
    return any(" ".join(w[i:i + 4]) in kural for i in range(len(w) - 3))


def _sade(t):
    return t.strip().strip('"“”').strip()


def soru_uret(k, dil):
    """Tek bir kullanıcı mesajı. Soru önce İngilizce üretilir (4B model burada daha iyi: Türkçe istemde kural adlarını ve ipuçlarını
    soruya kopyalıyordu); Türkçe soru bunun doğal Türkçeye çevirisidir. Kuralın metni modele verilmez, yalnız durumu."""
    alan = random.choice(ALANLAR["en"]); uslup = random.choice(USLUP["en"]); durum = random.choice(k.get("tetik") or [k["ne_zaman"]["en"]])
    istem = ("A person is working with an AI assistant (Claude, ChatGPT or Codex) on this project: %s.\n"
             "This just happened: %s.\n"
             "Write the 1-3 sentence message they now send to a helper called BÖRÜ, reacting to exactly that event and asking what to do. "
             "Mention one concrete detail of their project. Style: %s. They don't know any rules or principles. "
             "Output only the message itself, no quotes, no title, no notes.") % (alan, durum, uslup)
    t = _sade(sorucu(istem, uzunluk=160))
    if not 15 < len(t) < 500 or re.search(r"\b(rule|principle)s?\b", t, re.I):
        return None
    # durum sınaması: mesaj gerçekten bu olayı anlatıyor mu? Kararı isabetli olan düşünen model verir.
    karar = ogretmen([{"role": "user", "content": "Event: %s\n\nMessage: %s\n\nIs the message clearly about this event? Answer only YES or NO."
                       % (durum, t)}], sure=200)
    if not karar.strip().upper().startswith("YES"):
        return None
    if dil == "tr":
        t = _sade(sorucu("Şu mesajı günlük, doğal Türkçeye çevir; çeviri olduğu belli olmasın, üslubu koru. Yalnız çeviriyi yaz.\n\n" + t, sicaklik=0.3, uzunluk=400))
    if not 15 < len(t) < 800 or dil_bul(t) != dil or _kopya_mi(t, k) or re.search(r"\b(ANMA|kural(ı|ına|a)?)\b", t):
        return None
    return t


def sorular_uret(k, dil, n):
    out = []
    for _ in range(n + 3):                           # birkaçı elenebilir
        q = soru_uret(k, dil)
        if q and q not in out:
            out.append(q)
        if len(out) >= n:
            break
    return out


TR_HARF = set("çğıöşüÇĞİÖŞÜ")
TR_SOZ = {"ve", "bir", "bu", "için", "ile", "değil", "önce", "ama", "mı", "mi", "ne", "nasıl", "şu", "olarak"}
EN_SOZ = {"the", "and", "you", "to", "of", "is", "for", "with", "before", "what", "how", "it", "this", "don't", "your"}


def dil_bul(t):
    w = re.findall(r"[a-zçğıöşü']+", t.lower())
    tr = sum(x in TR_SOZ for x in w) + 2 * sum(c in TR_HARF for c in t) / max(1, len(t) / 40)
    en = sum(x in EN_SOZ for x in w)
    return "tr" if tr > en else "en"


def dongu_var(t):
    w = t.split()
    for n in (3, 4, 6):
        gram = [" ".join(w[i:i + n]) for i in range(len(w) - n)]
        if gram and max(gram.count(g) for g in set(gram)) >= 4:
            return True
    return False


def elek(ornek, kid, baglam_kim):
    y = ornek["messages"][-1]["content"]; s = ornek["messages"][-2]["content"]
    if not 60 <= len(y) <= 1400: return "uzunluk"
    if dil_bul(y) != dil_bul(s): return "dil"
    if dongu_var(y): return "dongu"
    anilan = set(re.findall(r"\b([A-Z]\d{2})\b", y))
    if not anilan: return "kural_yok"
    if anilan - set(baglam_kim) - {kid}: return "olmayan_kural"
    if kid not in anilan: return "hedef_yok"
    if "<think>" in y or "Okay," in y[:20]: return "dusunce_sizdi"
    return None


def yanit_uret(soru, dil, k):
    bilgi, kim = model.baglam(soru, profil=False, dil=dil)
    if k["id"] not in kim:
        # v2: hedef kural bağlama girmediyse rastgele bir sıraya konur (v1 hep başa koyuyordu; model "ilk kuralı an" öğrenebilirdi).
        # Bağlam yine 4 kural: model, ilgisiz kurallar arasından doğrusunu seçmeyi öğrenir.
        kural = {x["id"]: x for x in yontem.kurallar()}
        kim = kim[:3]; kim.insert(random.randint(0, len(kim)), k["id"])
        bilgi = "\n\n".join(["KURALLAR / RULES:"] + [yontem.yaz(kural[i], dil=dil) for i in kim])
    sistem = model.SISTEM[dil] + "\n\n" + bilgi
    y = ogretmen([{"role": "system", "content": sistem}, {"role": "user", "content": soru}])
    return {"kural": k["id"], "dil": dil, "kaynak": "damitma:" + OGRETMEN,
            "messages": [{"role": "system", "content": sistem}, {"role": "user", "content": soru}, {"role": "assistant", "content": y}]}, kim


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("cikti"); ap.add_argument("--soru-basina", type=int, default=6); ap.add_argument("--is", type=int, default=3)
    ap.add_argument("--kurallar", default="", help="yalnız bu kimlikler (deneme için), ör. A01,K05")
    a = ap.parse_args(); os.makedirs(a.cikti, exist_ok=True)
    SORU, KABUL, RED = [os.path.join(a.cikti, f) for f in ("sorular.jsonl", "egitim.jsonl", "elenen.jsonl")]
    kilit = threading.Lock(); K = yontem.kurallar(); random.seed(6)
    if a.kurallar:
        K = [k for k in K if k["id"] in a.kurallar.split(",")]

    # 1) sorular (kaldığı yerden)
    var = {}
    if os.path.exists(SORU):
        for l in open(SORU, encoding="utf-8"):
            d = json.loads(l); var[(d["kural"], d["dil"])] = 1
    isler = [(k, dil) for k in K for dil in ("tr", "en") if (k["id"], dil) not in var]

    def s_is(kd):
        k, dil = kd
        for _deneme in range(3):
            try:
                q = sorular_uret(k, dil, a.soru_basina)
                if len(q) >= 3: break
            except Exception as ex:
                q = []; print("soru hatası", k["id"], dil, ex, flush=True)
        with kilit:
            with open(SORU, "a", encoding="utf-8") as f:
                f.write(json.dumps({"kural": k["id"], "dil": dil, "sorular": q}, ensure_ascii=False) + "\n")
            print("sorular", k["id"], dil, len(q), flush=True)
    with ThreadPoolExecutor(getattr(a, "is")) as ex:
        list(ex.map(s_is, isler))

    # 2) yanıtlar + elek (kaldığı yerden: yapılan sorular atlanır)
    yapilan = set()
    for f in (KABUL, RED):
        if os.path.exists(f):
            for l in open(f, encoding="utf-8"):
                yapilan.add(json.loads(l)["messages"][1]["content"])
    kural = {k["id"]: k for k in K}; isler = []
    for l in open(SORU, encoding="utf-8"):
        d = json.loads(l)
        for q in d["sorular"]:
            if q not in yapilan:
                isler.append((q, d["dil"], kural[d["kural"]]))
    print("yanıtlanacak", len(isler), flush=True); t0 = time.time(); sayac = {"ok": 0, "red": 0}

    def y_is(x):
        q, dil, k = x
        try:
            o, kim = yanit_uret(q, dil, k)
        except Exception as ex:
            print("yanıt hatası", ex, flush=True); return
        neden = elek(o, k["id"], kim)
        with kilit:
            if neden:
                o["elenme"] = neden; sayac["red"] += 1
            else:
                sayac["ok"] += 1
            with open(RED if neden else KABUL, "a", encoding="utf-8") as f:
                f.write(json.dumps(o, ensure_ascii=False) + "\n")
            n = sayac["ok"] + sayac["red"]
            if n % 10 == 0:
                print("%d/%d  kabul %d  red %d  %.0f sn" % (n, len(isler), sayac["ok"], sayac["red"], time.time() - t0), flush=True)
    with ThreadPoolExecutor(getattr(a, "is")) as ex:
        list(ex.map(y_is, isler))
    print("BİTTİ kabul", sayac["ok"], "red", sayac["red"], flush=True)


if __name__ == "__main__":
    main()
