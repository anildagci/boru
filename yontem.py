# BÖRÜ'nün asistan bilgisi: kurallar.json'dan yöntem kuralı bulma, kontrol listeleri, plan için risk taraması.
# Ağ yok, model yok: anahtar kelime ve kategori eşleşmesi. (Faz 5'te yerel küçük model bu dosyanın yerine değil, yanına gelecek.)
import os, re, json, sys
from dil import DIL, KOK

BASE = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
PROFIL = os.path.join(KOK, "ozel", "PROFIL.md")         # yalnız bu bilgisayarda; hiçbir yere gönderilmez


def kurallar():
    try:
        return json.load(open(os.path.join(BASE, "bilgi", "kurallar.json"), encoding="utf-8"))["kurallar"]
    except Exception:
        return []


def _kucuk(s):
    return s.replace("I", "ı").replace("İ", "i").lower()


def _kelimeler(s):
    return set(w for w in re.findall(r"[\wçğıöşüâî]+", _kucuk(s)) if len(w) > 2)


def _kok(w):
    # Kaba kök: Türkçe ekleri ve İngilizce çekimleri atmak için uzun sözcüklerin ilk 5 harfi ("silmeyin" ~ "silme", "deleted" ~ "delet").
    return w[:5] if len(w) > 5 else w


def _kokler(s):
    return set(_kok(w) for w in _kelimeler(s))


_DIZIN = None


def _dizin():
    """Her kural için alan alan kök kümeleri ve kökün kaç kuralda geçtiğine göre ağırlık (nadir kök daha ayırt edici)."""
    global _DIZIN
    if _DIZIN is None:
        import math
        kk = kurallar(); alanlar = []
        for k in kk:
            def m(*ad):
                p = [k[a][d] for a in ad if isinstance(k.get(a), dict) for d in ("tr", "en")]
                return " ".join(" ".join(x) if isinstance(x, list) else str(x) for x in p)
            alanlar.append({"ust": _kokler(m("baslik", "ne_zaman") + " " + " ".join(k["anahtar"])),
                            "alt": _kokler(" ".join(k.get("tetik", [])) + " " + m("yap", "yapma"))})
        sayi = {}
        for a in alanlar:
            for w in a["ust"] | a["alt"]:
                sayi[w] = sayi.get(w, 0) + 1
        idf = {w: math.log((len(kk) + 1) / c) for w, c in sayi.items()}
        _DIZIN = (kk, alanlar, idf)
    return _DIZIN


def bul(soru, n=3, dil=None):
    """Soruyla en çok örtüşen kurallar (puan, kural)."""
    dil = dil or DIL; q = _kucuk(soru); qk = _kokler(soru); sonuc = []
    kk, alanlar, idf = _dizin()
    for k, a in zip(kk, alanlar):
        puan = 0.0
        for an in k["anahtar"]:
            if _kucuk(an) in q:
                puan += 3 + len(an) // 5          # uzun, özgül anahtar daha ağır basar
        puan += sum(idf.get(w, 0) for w in qk & a["ust"])            # başlık, ne zaman, anahtar
        puan += 0.6 * sum(idf.get(w, 0) for w in qk & (a["alt"] - a["ust"]))  # tetikler, yap/yapma
        if k["id"].lower() == q.strip() or k["kategori"] == q.strip():
            puan += 10
        if puan > 0:
            sonuc.append((round(puan, 2), k))
    sonuc.sort(key=lambda x: -x[0])
    return sonuc[:n]


def yaz(k, dil=None, kisa=False):
    dil = dil or DIL; en = dil == "en"
    s = ["%s · %s" % (k["id"], k["baslik"][dil]), ("When: " if en else "Ne zaman: ") + k["ne_zaman"][dil]]
    s += [("Do:" if en else "Yap:")] + ["  - " + x for x in k["yap"][dil]]
    if not kisa:
        s += [("Don't:" if en else "Yapma:")] + ["  - " + x for x in k["yapma"][dil]]
        s += [("Why: " if en else "Neden: ") + k["neden"][dil]]
    return "\n".join(s)


def katalog(dil=None):
    dil = dil or DIL
    return "\n".join("%s [%s] %s" % (k["id"], k["kategori"], k["baslik"][dil]) for k in kurallar())


LISTELER = {
    "baslangic": {
        "tr": ("Proje başlangıcı", ["Hedef ve kalite çıtası tek cümlede yazıldı mı? (referans örneklerle)",
               "Roller belli mi: kim karar verir, model hangi rolde?", "Bağlayıcı kurallar yazıldı mı: neye onay gerekir, ne asla yapılmaz, bütçe?",
               "İş kapılara bölündü mü; her kapıda neyi deneyip onaylayacaksın?", "Hedef platform ve öncelik (ör. PC önce, telefon sonra)?",
               "Yaratıcı kararlarda modelin önce senin fikrini sorması istendi mi?", "Belgeler nerede (GDD, AGENTS.md, devir teslim)? Model önce onları okuyacak mı?",
               "Yedek ve sürüm adlandırması belli mi?", "Ücretli araç/kredi gerekirse model durup soracak mı?"]),
        "en": ("Project start", ["Are the goal and quality bar written in one sentence (with reference examples)?",
               "Are roles clear: who decides, which role does the model play?", "Are binding rules written: what needs approval, what is never done, budget?",
               "Is the work split into gates; what will you try and approve at each?", "Target platform and priority (e.g. PC first, phone later)?",
               "Is the model required to ask for your ideas before creative decisions?", "Where are the docs (GDD, AGENTS.md, handover)? Will the model read them first?",
               "Are backups and version naming decided?", "Will the model stop and ask before paid tools/credits?"])},
    "teslim": {
        "tr": ("Teslim öncesi kalite", ["Sınananlar ve sınanmayanlar ayrı yazıldı mı?", "Sayılar ölçüldü mü, tahmin mi? (üçgen, süre, oran)",
               "Kullanıcının gerçek ortamında denendi mi (onun açtığı yoldan)?", "Önceki onaylı sürüm yedekte mi; hiçbir deneme silinmedi mi?",
               "Korunacak dendiği şeyler korundu mu (karşılaştırma görseliyle)?", "Testler ve build geçiyor mu; hiçbir test gevşetilmedi mi?",
               "Rapor kısa mı: ne oldu, ne sınandı, ne sınanmadı, senden ne bekleniyor?"]),
        "en": ("Pre-delivery quality", ["Are tested and untested items listed separately?", "Were numbers measured or guessed? (triangles, time, rates)",
               "Was it tried in the user's real environment (the way they launch it)?", "Is the previous approved version backed up; was no attempt deleted?",
               "Were the 'keep' items kept (shown with a comparison image)?", "Do tests and the build pass; was no test loosened?",
               "Is the report short: what happened, what was tested, what wasn't, what is needed from you?"])},
    "yardimci": {
        "tr": ("Yardımcı ajana (ör. Codex) iş verme istemi", ["Önce şunları oku: AGENTS.md, <belge §bölüm>.", "Amaç: <tek cümle>.",
               "Dokunacağın dosyalar: <liste>. Dokunmayacakların: <liste>.", "Kabul ölçütleri: <ölçülebilir maddeler>.",
               "Önce kabul testini ekle ve şimdiki hâliyle başarısız olduğunu göster; sonra düzelt.", "Var olan testleri gevşetme; build ve testler geçmeli.",
               "Dal: <görev/ad>. PR açıklaması <dil> ve önce/sonra ölçümleriyle. Ana dala birleştirme.", "Belirsiz bir kural ya da karar olursa tahmin etme, dur ve sor."]),
        "en": ("Prompt for a helper agent (e.g. Codex)", ["First read: AGENTS.md, <doc §section>.", "Goal: <one sentence>.",
               "Files you may touch: <list>. Files you must not: <list>.", "Acceptance criteria: <measurable items>.",
               "Add the acceptance test first and show it failing as things are; then fix.", "Don't loosen existing tests; build and tests must pass.",
               "Branch: <task/name>. PR description in <language> with before/after measurements. Don't merge to main.", "If a rule or decision is unclear, don't guess: stop and ask."])},
    "gorsel": {
        "tr": ("Görsel inceleme", ["Görseli kayıpsız ve büyütmeden göster.", "Kusurları renkli oklarla numarala: yeşil = koru, kırmızı = sorun.",
               "Her maddeye ayrı cevap ver; önce korunacakları koru.", "Yeni sürümü yeni adla kaydet; karşılaştırmayı yan yana göster.",
               "Mükemmel yoksa en kabul edilebilir sürümü yazıyla seç."]),
        "en": ("Visual review", ["Show images lossless and not upscaled.", "Number the defects with coloured arrows: green = keep, red = problem.",
               "Answer each item separately; protect the 'keep' items first.", "Save the new version under a new name; show the comparison side by side.",
               "If nothing is flawless, choose the most acceptable version in writing."])},
}

# Plan metninde dikkat isteyen işaretler: (desen, kural, Türkçe uyarı, İngilizce uyarı)
RISKLER = [
    (r"\b(sil|silin|delete|remove|rm )", "G01", "Silme var: neyin silineceği, geri alınıp alınamayacağı netleşmeli; önce yedek.", "Deletion: what gets deleted and whether it's reversible must be clear; back up first."),
    (r"üstüne yaz|overwrite|replace|değiştir", "K04", "Üstüne yazma: onaylı sürüm korunacak mı? Yeni adla yazmak daha güvenli.", "Overwrite: will the approved version be kept? Writing under a new name is safer."),
    (r"para|ücret|kredi|abonelik|satın|paid|credit|subscription|buy|pricing", "G03", "Para/kredi harcaması: maliyet ve ücretsiz alternatif kullanıcıya sorulmalı.", "Money/credits: the cost and a free alternative must be put to the user."),
    (r"yayınla|paylaş|herkese açık|publish|post |release|public", "G03", "Yayın: kullanıcının açık onayı gerekli; kişisel ve telifli içerik ayıklanmalı.", "Publishing: needs the user's explicit approval; personal and copyrighted content must be filtered out."),
    (r"push|merge|birleştir|main|master|force", "G02", "Ana dala/uzak depoya gönderme: ayrı dal + PR ve kullanıcı onayı.", "Pushing/merging to main: separate branch + PR and the user's approval."),
    (r"sanırım|galiba|herhalde|belki|tahmin|probably|maybe|guess|i think|assume", "N01", "Tahmin var: bu karar ölçülmeli ya da kullanıcıya sorulmalı.", "There's a guess: measure it or ask the user."),
    (r"hepsi|tamamı|her şeyi|tüm |everything|all of|entire|whole", "B01", "Kapsam geniş: kapılara bölünmeli; her kapıda neyin onaylanacağı belli olmalı.", "Wide scope: split into gates with a clear approval at each."),
    (r"azalt|küçült|sıkıştır|decimate|reduce|compress|downscale|optimi", "P01", "Kalite azaltma: hedef platform belli mi? Optimizasyon sonraya bırakılabilir.", "Quality reduction: is the target platform decided? Optimisation can come later."),
    (r"yapılamaz|imkansız|mümkün değil|impossible|can't be done|not possible", "A01", "Kestirip atma riski: engeli adlandırıp 3–4 alternatif sunulmalı.", "Dismissal risk: name the obstacle and offer 3–4 alternatives."),
    (r"çalışıyor|bitti|tamamlandı|works|done|finished|complete", "K05", "'Çalışıyor/bitti' iddiası: neyin sınandığı, neyin sınanmadığı ayrı yazılmalı.", "A 'works/done' claim: list what was tested and what wasn't."),
]
TEST_YOK = ("K02", "Planda sınama/kabul ölçütü görünmüyor: neyle 'oldu' diyeceğiz?", "No test or acceptance criterion in the plan: how will we know it worked?")
ONAY_YOK = ("B01", "Planda bir onay kapısı görünmüyor: kullanıcı nerede deneyip karar verecek?", "No approval gate in the plan: where does the user try and decide?")


def risk(plan, dil=None):
    dil = dil or DIL; q = _kucuk(plan); i = 2 if dil == "tr" else 3; bulgu = []
    for desen, kid, tr, en in RISKLER:
        if re.search(desen, q):
            bulgu.append((kid, (tr, en)[i - 2]))
    if not re.search(r"test|sına|dene|ölç|kabul|doğrula|verify|measure|accept|check", q):
        bulgu.append((TEST_YOK[0], TEST_YOK[1 if dil == "tr" else 2]))
    if not re.search(r"onay|sor|kullanıcı|approv|ask|user|review", q):
        bulgu.append((ONAY_YOK[0], ONAY_YOK[1 if dil == "tr" else 2]))
    return bulgu
