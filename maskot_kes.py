# Maskot sayfasını (3 sütun x 2 satır, aynı kurdun altı hali) karelere keser ve kurt penceresine hazırlar.
# - Zemin: şeffafsa alfadan; düz beyazsa KENARDAN doldurularak bulunur (kurdun içindeki beyaz göğüs yelesi silinmez).
# - Altı kare aynı ölçekle küçültülür ve ayak çizgisi + yatay orta noktaya hizalanır (geçişte zıplama olmaz).
# - Pencerenin saydamlığı tek renkli (tam saydam ya da tam opak): yarı saydam kenarlar dış hat rengine karıştırılıp keskinleşir.
# python maskot_kes.py <sayfa.png> <çıktı klasörü> [kare yüksekliği=280]
from dil import _
import sys, os
import numpy as np, cv2

HALLER = ["bos", "kirp", "calisiyor", "sevincli", "endiseli", "soruyor"]
DIS_HAT = (21, 24, 30)                        # #15181e: kenar karışım rengi (kurdun dış hattına yakın)

# "Kendi maskotunu oluştur" için görüntü üretici prompt'u. Kullanıcının tarifi olduğu gibi girer (Türkçe de olur).
# Düzen kuralları kesicinin beklediğiyle aynı: tek sayfa, 3x2, hücreler birbirine değmez, düz zemin, aynı ölçek.
PROMPT = """Create a character sheet of ONE original mascot character, shown 6 times in a 3 columns x 2 rows grid.
Transparent background (if not possible: plain flat white background). No text, no labels, no scenery, no props except those listed.
Every cell: the SAME character, same size, same camera angle (front, very slightly three-quarter), whole body visible,
centered in its cell with plenty of empty space around it. Cells must not touch or overlap.
Style: polished, cute anime/cartoon illustration with soft cel shading and a thin dark outline around the whole figure.

The character: {tarif}

Cells, left to right, top to bottom:
1. Calm: gentle confident look, slight closed-mouth smile.
2. Blink: EXACTLY the same pose and expression as cell 1, only the eyes closed.
3. Working: focused eyes looking at a small glowing blue wireframe cube floating in front of its chest, one hand or paw raised toward it.
4. Happy: eyes closed in a happy smile, mouth open, arms or tail raised.
5. Worried: brows raised, small frown, slightly shrunk posture.
6. Asking: head tilted, one hand or paw slightly raised, curious open eyes, as if asking a question.

Keep proportions, colors and details identical across all six cells. The character must be original: do not copy or imitate any existing character, brand or artist.
Square image, high resolution."""


def prompt(tarif):
    return PROMPT.format(tarif=" ".join((tarif or "").split()) or "a friendly little wolf with dark fur and ice-blue eyes")


def on_plan(img):
    """Döner: 0..1 alfa. Şeffaf PNG'de alfadan; değilse kenardan bağlı açık zemin doldurularak."""
    if img.shape[2] == 4 and img[..., 3].min() < 250:
        return img[..., 3].astype(np.float32) / 255
    bgr = img[..., :3]; acik = (bgr.min(2) > 235) & (bgr.max(2).astype(int) - bgr.min(2) < 18)
    h, w = acik.shape; zemin = np.zeros((h, w), bool)
    a = acik.astype(np.uint8)
    n, lab = cv2.connectedComponents(a, connectivity=4)
    kenar = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    for k in kenar:
        zemin |= lab == k
    alfa = (~zemin).astype(np.float32)
    return cv2.GaussianBlur(alfa, (3, 3), 0)                   # kenarda yumuşak geçiş: aşağıda karışım için


def yaz(yol, img):
    cv2.imencode(".png", img)[1].tofile(yol)


def kes(sayfa, cikti, yuk=280):
    img = cv2.imdecode(np.fromfile(sayfa, np.uint8), cv2.IMREAD_UNCHANGED)   # Türkçe/Kiril yollar için (cv2.imread okuyamıyor)
    if img is None:
        raise SystemExit(_("okunamadı: %s") % sayfa)
    if img.ndim == 2:
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    alfa = on_plan(img); bgr = img[..., :3].astype(np.float32)
    H, W = alfa.shape; parcalar = []
    for i in range(6):
        r, c = divmod(i, 3); y0, y1, x0, x1 = r * H // 2, (r + 1) * H // 2, c * W // 3, (c + 1) * W // 3
        a = alfa[y0:y1, x0:x1]
        n, lab, st, _x = cv2.connectedComponentsWithStats((a > 0.5).astype(np.uint8), 8)
        if n < 2:
            raise SystemExit(_("%d. hücrede kurt bulunamadı") % (i + 1))
        en = 1 + int(np.argmax(st[1:, 4])); tut = st[1:, 4] > st[en, 4] * 0.02     # ana gövde + ona göre anlamlı parçalar (küp, kuyruk ucu)
        m = np.isin(lab, [j + 1 for j in np.where(tut)[0]])
        ys, xs = np.where(m); bx0, bx1, by0, by1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
        aa = a[by0:by1, bx0:bx1] * cv2.dilate(m[by0:by1, bx0:bx1].astype(np.uint8), np.ones((5, 5), np.uint8))
        parcalar.append((bgr[y0 + by0:y0 + by1, x0 + bx0:x0 + bx1], aa, (bx1 - bx0) / 2.0))
    olcek = yuk / max(p[1].shape[0] for p in parcalar)               # tek ölçek: hallerin birbirine göre boyu korunur
    gen = int(max(p[1].shape[1] for p in parcalar) * olcek) + 8
    os.makedirs(cikti, exist_ok=True); kare = []
    for ad, (b, a, orta) in zip(HALLER, parcalar):
        h, w = int(round(a.shape[0] * olcek)), int(round(a.shape[1] * olcek))
        b2 = cv2.resize(b, (w, h), interpolation=cv2.INTER_AREA); a2 = cv2.resize(a, (w, h), interpolation=cv2.INTER_AREA)[..., None]
        renk = b2 * a2 + np.array(DIS_HAT, np.float32) * (1 - a2)         # yarı saydam kenar dış hat rengine karışır
        tam = np.zeros((yuk, gen, 4), np.uint8); ox = gen // 2 - int(round(orta * olcek)); oy = yuk - h   # ayak çizgisi alta
        tam[oy:oy + h, ox:ox + w, :3] = np.clip(renk, 0, 255).astype(np.uint8)
        tam[oy:oy + h, ox:ox + w, 3] = np.where(a2[..., 0] > 0.35, 255, 0).astype(np.uint8)
        yaz(os.path.join(cikti, ad + ".png"), tam); kare.append(tam)
    onz = np.hstack([np.where(k[..., 3:] > 0, k[..., :3], np.array([1, 255, 0], np.uint8)) for k in kare])   # pencerenin saydam yeşili üstünde
    yaz(os.path.join(cikti, "_onizleme.png"), onz)
    print(_("MASKOT %d kare, %dx%d, ölçek %.3f -> %s") % (len(kare), gen, yuk, olcek, cikti))
    return cikti


if __name__ == "__main__":
    kes(sys.argv[1], sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 280)
