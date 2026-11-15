# Sade yol, gorunum: yalniz saca dokunur. Cizimdeki sac (golge tonu ve tutam cizgileri) dort gorunusten modelin sacina
# kopyalanir; yuze, gozluge ve govdeye hicbir sey yazilmaz. Oyunun maskesi (ten / sac / yuz) de burada uretilir.
# python Scripts/simple_look.py <giris surumu> <cikis surumu> <geo npz> <cikti klasoru>     (Raicon calisma klasorunden)
import json, sys, os, types
import numpy as np, cv2
from PIL import Image, ImageFilter
Image.MAX_IMAGE_PIXELS = None
sys.path.insert(0, "D:/Game Projects/PaceBorn-3D/arena3d/Tools/characterlab/cizimden-modele/arac")
try:
    import s2m
except Exception:
    s2m = None          # yalniz sac kopyalama yolunda gerekir
vin, vout, geo_path, out = sys.argv[1:5]; os.makedirs(out, exist_ok=True)
E = lambda k, d: float(os.environ.get(k, d))
L = json.load(open("Textures/work/graft/atlas_layout.json")); S = L["size"]; MS = json.load(open("Textures/work/simple_measure.json"))
hx, hy, hw, hh = L["tiles"][0]["rect"]
FAST = os.environ.get("HAIR_COPY", "1") == "0"
atlas = None if FAST else np.asarray(Image.open("Textures/Model_BaseColor_%s.png" % vin).convert("RGB")).astype(np.float32).copy()
if os.environ.get("HAIR_COPY", "1") == "0":
    # Dokuya dokunulmaz: yalniz oyunun dokulari uretilir. Sac maskesi doku renginden (bas karosundaki acik lavanta / beyaz).
    import shutil
    p = "Textures/Model_BaseColor_%s.png" % vout; shutil.copyfile("Textures/Model_BaseColor_%s.png" % vin, p)      # dokuya dokunulmaz: birebir kopya
    base = Image.open(p).convert("RGB"); jq = int(E("BASE_QUALITY", 95))
    if os.environ.get("BASE_PNG", "0") == "1": base.save(os.path.join(out, "base.png"))
    else: base.save(os.path.join(out, "base.jpg"), quality=jq, subsampling=0)
    M = 2048; k = M / S
    small = np.asarray(base.resize((M, M), Image.LANCZOS)).astype(np.float32); sr, sg, sb = small[..., 0], small[..., 1], small[..., 2]
    top, low = small.max(2), small.min(2); sat = (top - low) / np.maximum(top, 1)
    skin = (sr > 140) & (sr > sg * 1.12) & (sg > sb * 1.05) & (sat > 0.18) & (sat < 0.66) & (sb > 60)
    ht = np.zeros((M, M), bool); ht[int(hy * k):int((hy + hh) * k), int(hx * k):int((hx + hw) * k)] = True
    hairm = ht & (low > 150) & (sb >= sr - 6) & (np.abs(sr - sg) < 30)
    hairm = cv2.morphologyEx(hairm.astype(np.uint8), cv2.MORPH_OPEN, np.ones((7, 7), np.uint8)).astype(bool)
    mask = np.zeros((M, M, 3), np.float32); mask[..., 0] = skin; mask[..., 1] = hairm; mask[..., 2] = skin & ht
    Image.fromarray((mask * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.6)).save(os.path.join(out, "mask.png"))
    Image.new("RGBA", (64, 64), (235, 235, 250, 0)).save(os.path.join(out, "highlight.png"))
    lk = os.path.join(out, "look.json")
    if os.path.exists(lk): os.remove(lk)
    print("saved", p, "(texture untouched) and game textures ->", out); raise SystemExit
g = np.load(geo_path); V, TV, TU, N = g["verts"].astype(np.float64), g["tri_vert"], g["tri_uv"].astype(np.float64), g["tri_n"].astype(np.float64)
cu = TU.mean(1); pxc, pyc = cu[:, 0] * S, (1 - cu[:, 1]) * S; cen = V[TV].mean(1)
in_head = (pxc >= hx) & (pxc < hx + hw) & (pyc >= hy) & (pyc < hy + hh)
fc = atlas[np.clip(pyc.astype(int), 0, S - 1), np.clip(pxc.astype(int), 0, S - 1)]; r, g_, b = fc[:, 0], fc[:, 1], fc[:, 2]
# sac: acik lavanta / beyaz dokulu bas ucgenleri; yuzdeki kucuk beyaz adalar (goz aki) ve ceket kalintilari ayiklanir
light = in_head & (fc.min(1) > 150) & (b >= r - 6) & (np.abs(r - g_) < 30)
_, wid = np.unique(np.round(V, 5), axis=0, return_inverse=True); wid = wid.reshape(-1); WT = wid[TV]
parent = {}
def find(a):
    while parent.setdefault(a, a) != a:
        parent[a] = parent[parent[a]]; a = parent[a]
    return a
for f in np.where(light)[0]:
    ra = find(WT[f, 0])
    for o in WT[f, 1:]:
        ro = find(o)
        if ro != ra: parent[ro] = ra
comp = np.array([find(WT[f, 0]) for f in np.where(light)[0]]); ids, cnt = np.unique(comp, return_counts=True)
big = set(ids[cnt >= E("HAIR_ISLAND_MIN", 250)].tolist())
hair = np.zeros(len(TV), bool); hair[np.where(light)[0][np.array([c in big for c in comp])]] = True
print("hair: %d triangles (%d islands kept of %d)" % (int(hair.sum()), len(big), len(ids)))
hm = np.zeros((S, S), np.uint8)
for f in np.where(hair)[0]:
    cv2.fillConvexPoly(hm, np.stack([TU[f][:, 0] * S, (1 - TU[f][:, 1]) * S], 1).round().astype(np.int32), 1)
# sac maskesi doku duzeyinde de renkle sinirlanir: sac ucgenlerinin kenarinda kalan ten / gozluk pikselleri korunur
ar, ag, ab = atlas[..., 0], atlas[..., 1], atlas[..., 2]
hm = (hm.astype(bool) & (atlas.min(-1) > 135) & (ab >= ar - 8) & (np.abs(ar - ag) < 34)).astype(np.float32)

# ---- cizimden sac: golge tonu ve tutam cizgileri (on, capraz, yan, arka)
sheet = Image.open("References/head_turnaround.png").convert("RGB"); sheet = sheet.resize((sheet.width * 2, sheet.height * 2), Image.LANCZOS)
geo = types.SimpleNamespace(V=V, TV=TV, TU=TU, N=N, cen=cen, H=V[:, 2].max())
HAIR_RULE = "((B > 170) & (B - R > 8) & (R > 110)) | ((R > 238) & (G > 238) & (B > 244))"
def project(rule_, blur):
    cfg = {"highlight": {"sheet_hair_rule": HAIR_RULE, "sheet_shine_rule": rule_, "shine_rows": 0.64, "box_rows": 0.64}}
    return np.clip(cv2.GaussianBlur(s2m.highlight_from_sheet(cfg, geo, {"hair": hair}, sheet, S, S).astype(np.float32), (0, 0), blur), 0, 1)
shade = project("(R < 170) & (R > 95) & (B > 160) & (B - R > 35)", E("SHADE_BLUR", 1.6))
# cizgiler: cizimden degil modelin kendi tutam aralarindan (cizimdeki cizgiler modelin tutamlariyla ortusmuyor, karalama
# gibi cikiyordu). Girintiler uclara dogru incelen cizgilerle cizilir.
import heapq
first = {}
for i, w in enumerate(wid): first.setdefault(w, i)
P3 = V[TV]; Cn = P3.mean(1); edges = {}
for f in np.where(hair)[0]:
    for i in range(3):
        a_, b_ = WT[f, i], WT[f, (i + 1) % 3]; edges.setdefault((min(a_, b_), max(a_, b_)), []).append((f, i))
ANG, WEAK, MINLEN = E("VALLEY_ANGLE", 42), E("VALLEY_WEAK", 22), E("VALLEY_MIN_MM", 24) / 1000
elen = lambda a_, b_: float(np.linalg.norm(V[first[a_]] - V[first[b_]]))
cand = []
for key, fl in edges.items():
    if len(fl) != 2: continue
    (f1, i1), (f2, i2) = fl; ang = np.degrees(np.arccos(np.clip(N[f1] @ N[f2], -1, 1)))
    if ang > WEAK and (Cn[f2] - Cn[f1]) @ N[f1] > 0: cand.append((key, fl, ang))
par2 = {}
def find2(a_):
    while par2.setdefault(a_, a_) != a_:
        par2[a_] = par2[par2[a_]]; a_ = par2[a_]
    return a_
for (a_, b_), fl, ang in cand:
    ra, rb = find2(a_), find2(b_)
    if ra != rb: par2[ra] = rb
length = {}
for (a_, b_), fl, ang in cand:
    if ang > ANG: length[find2(a_)] = length.get(find2(a_), 0.0) + elen(a_, b_)
keepe = [((a_, b_), fl) for (a_, b_), fl, ang in cand if length.get(find2(a_), 0.0) >= MINLEN]
adj = {}
for (a_, b_), fl in keepe:
    l_ = elen(a_, b_); adj.setdefault(a_, []).append((b_, l_)); adj.setdefault(b_, []).append((a_, l_))
dist = {v: (0.0 if len(n_) == 1 else 1e9) for v, n_ in adj.items()}
pq = [(0.0, v) for v, dd in dist.items() if dd == 0.0]; heapq.heapify(pq)
while pq:
    dd, v = heapq.heappop(pq)
    if dd > dist[v]: continue
    for o, l_ in adj[v]:
        if dd + l_ < dist[o]: dist[o] = dd + l_; heapq.heappush(pq, (dd + l_, o))
sm = lambda x: max(0.0, min(1.0, x)) ** 2 * (3 - 2 * max(0.0, min(1.0, x)))
taper = lambda v: 0.2 + 0.8 * sm(min(dist.get(v, 1e9), 1.0) / 0.010)
SS = 2; TS = S * SS; SH = 4; F = 1 << SH; canvas = np.zeros((TS, TS), np.uint8); WMM = E("VALLEY_MM", 1.0)
for (a_, b_), fl in keepe:
    for f, i in fl:
        p0 = np.array([TU[f, i][0] * TS, (1 - TU[f, i][1]) * TS]); p1 = np.array([TU[f, (i + 1) % 3][0] * TS, (1 - TU[f, (i + 1) % 3][1]) * TS]); dv_ = p1 - p0; Ln = np.linalg.norm(dv_)
        if Ln < 1e-6: continue
        dens = Ln / max(np.linalg.norm(P3[f, i] - P3[f, (i + 1) % 3]), 1e-9)
        h0 = max(0.35, WMM * taper(WT[f, i]) / 2000 * dens); h1 = max(0.35, WMM * taper(WT[f, (i + 1) % 3]) / 2000 * dens); nr = np.array([-dv_[1], dv_[0]]) / Ln
        cv2.fillConvexPoly(canvas, (np.array([p0 + nr * h0, p1 + nr * h1, p1 - nr * h1, p0 - nr * h0]) * F).round().astype(np.int32), 255, cv2.LINE_AA, SH)
lines = cv2.GaussianBlur(cv2.resize(canvas, (S, S), interpolation=cv2.INTER_AREA).astype(np.float32) / 255, (0, 0), 0.6)
print("hair lines from the model: %d crease edges kept of %d" % (len(keepe), len(cand)))
base_col = np.array([float(v) for v in os.environ.get("HAIR_BASE", "232,231,246").split(",")], np.float32)
shade_col = np.array([float(v) for v in os.environ.get("HAIR_SHADE", "150,157,205").split(",")], np.float32)
line_col = np.array([float(v) for v in os.environ.get("HAIR_LINE", "44,46,74").split(",")], np.float32)
m3 = hm[..., None]
hair_tex = base_col[None, None] * (1 - shade[..., None] * E("SHADE_STRENGTH", 0.9)) + shade_col * shade[..., None] * E("SHADE_STRENGTH", 0.9)
la = np.clip(lines, 0, 1)[..., None] * E("LINE_STRENGTH", 0.9)
hair_tex = hair_tex * (1 - la) + line_col * la
if os.environ.get("HAIR_COPY", "1") == "1":            # 0: sac dokusu Tripo'nun verdigi gibi kalir (hicbir sey yazilmaz)
    atlas = atlas * (1 - m3) + hair_tex * m3
print("drawing hair copied: shade covers %.1f%% and lines %.1f%% of the hair texels" % (100 * (shade * hm > 0.4).sum() / max(1, hm.sum()), 100 * (lines * hm > 0.4).sum() / max(1, hm.sum())))
p = "Textures/Model_BaseColor_%s.png" % vout; Image.fromarray(np.clip(atlas, 0, 255).astype(np.uint8)).save(p)

# ---- oyunun dokulari
base = Image.open(p).convert("RGB"); base.save(os.path.join(out, "base.jpg"), quality=93)
M = 1024; k = M / S
small = np.asarray(base.resize((M, M), Image.LANCZOS)).astype(np.float32); sr, sg, sb = small[..., 0], small[..., 1], small[..., 2]
top, low = small.max(2), small.min(2); sat = (top - low) / np.maximum(top, 1)
skin = (sr > 140) & (sr > sg * 1.12) & (sg > sb * 1.05) & (sat > 0.18) & (sat < 0.66) & (sb > 60)
mask = np.zeros((M, M, 3), np.float32); mask[..., 0] = skin
mask[..., 1] = cv2.resize(hm, (M, M), interpolation=cv2.INTER_AREA) > 0.5
ht = np.zeros((M, M), bool); ht[int(hy * k):int((hy + hh) * k), int(hx * k):int((hx + hw) * k)] = True
mask[..., 2] = skin & ht                                       # yuz ve boyun: golge yumusatilir
Image.fromarray((mask * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.6)).save(os.path.join(out, "mask.png"))
Image.new("RGBA", (64, 64), (235, 235, 250, 0)).save(os.path.join(out, "highlight.png"))
lk = os.path.join(out, "look.json")
if os.environ.get("HAIR_COPY", "1") == "1":
    json.dump({"outlineHairScale": 1.4, "rimHairScale": 0.15, "hairShadowColor": [0.72, 0.74, 0.93]}, open(lk, "w"), indent=1)
elif os.path.exists(lk): os.remove(lk)
print("saved", p, "and game textures ->", out)
