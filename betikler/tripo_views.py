# Bir donus sayfasindan Tripo'ya verilecek gorselleri keser. Figurler bos sutunlardan ayrilir (sabit bolme el ve sac ucu
# kesiyordu); hepsi ayni olcekte ve ayni dikey hizada, kare beyaz zemine yerlestirilir. Bas ve tam boy sayfalar icin ayni.
# Kullanim (Characters klasorunden):
#   python tripo_views.py Raicon head_sides.png front,left,right,back tripo_head raicon_head
#   python tripo_views.py Raicon full_body_turnaround.png front,right,back tripo_body raicon_body
import sys, os
import numpy as np, cv2
from PIL import Image, ImageOps
Image.MAX_IMAGE_PIXELS = None
name, sheet_file, views, sub, prefix = sys.argv[1:6]; views = views.split(","); S = int(sys.argv[6]) if len(sys.argv) > 6 else 2048
src = os.path.join(name, "References", sheet_file); out = os.path.join(name, "References", sub); os.makedirs(out, exist_ok=True)
im = Image.open(src).convert("RGB"); A = np.asarray(im).astype(np.int32); H, W = A.shape[:2]
bg = np.median(np.concatenate([A[:10].reshape(-1, 3), A[:, :10].reshape(-1, 3)]), axis=0)
fig = (np.abs(A - bg).sum(2) > 45).astype(np.uint8)
fig = cv2.morphologyEx(fig, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
cols = fig.sum(0) > max(2, H * 0.004)
runs, start = [], None
for x in range(W + 1):
    on = x < W and cols[x]
    if on and start is None: start = x
    if not on and start is not None: runs.append((start, x)); start = None
runs = sorted(sorted(runs, key=lambda r: r[0] - r[1])[:len(views)])
assert len(runs) == len(views), "found %d figures, expected %d" % (len(runs), len(views))
rows = np.where(fig.sum(1) > 0)[0]; y0, y1 = rows.min(), rows.max() + 1
side = max(y1 - y0, max(b - a for a, b in runs)); pad = int(side * 0.05); canvas = side + 2 * pad
print("%s %s: figures at columns %s, rows %d..%d, scale %.2fx" % (src, im.size, runs, y0, y1, S / canvas))
res = {}
for v, (a, b) in zip(views, runs):
    crop = A[y0:y1, a:b].astype(np.float32); m = fig[y0:y1, a:b]
    # zemin: figurun disinda kalan ve zemin renginde olan her sey (figurun icindeki zemin cepleri dahil)
    near = (np.abs(crop - bg).sum(2) < 45)
    alpha = cv2.GaussianBlur(near.astype(np.float32), (0, 0), 0.6)[..., None]
    crop = crop * (1 - alpha) + 255 * alpha
    sq = np.full((canvas, canvas, 3), 255, np.float32)
    ox = (canvas - (b - a)) // 2; oy = pad + (side - (y1 - y0))          # alt hizali: ayaklar / omuzlar ayni satirda
    sq[oy:oy + (y1 - y0), ox:ox + (b - a)] = crop
    res[v] = Image.fromarray(sq.clip(0, 255).astype(np.uint8)).resize((S, S), Image.LANCZOS)
    res[v].save(os.path.join(out, "%s_%s.png" % (prefix, v)))
if "right" in res and "left" not in res:
    ImageOps.mirror(res["right"]).save(os.path.join(out, "%s_left_mirrored.png" % prefix))
c = Image.new("RGB", (S * len(views), S))
for i, v in enumerate(views): c.paste(res[v], (i * S, 0))
c.thumbnail((2000, 2000)); c.save(os.path.join(out, "_contact.png"))
