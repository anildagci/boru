# Atlas goruntusunu kurar: govde dokusu + bas parcalarinin dokulari, graft_atlas.py'nin yazdigi yerlesime gore.
# python Scripts/graft_atlas_compose.py <surum>     (Blaze calisma klasorunden)
import json, sys, os
import numpy as np, cv2
from PIL import Image
Image.MAX_IMAGE_PIXELS = None
ver = sys.argv[1]
L = json.load(open("Textures/work/graft/atlas_layout.json"))
S = L["size"]; atlas = Image.new("RGB", (S, S), (60, 35, 30))
bx, by, bw, bh = L["body"]
atlas.paste(Image.open(L["body_src"]).convert("RGB").resize((bw, bh), Image.LANCZOS), (bx, by))
for t in L["tiles"]:
    x, y, w, h = t["rect"]
    src = np.asarray(Image.open(t["src"]).convert("RGB")).astype(np.float32); full = src.max(-1) >= 6
    for _ in range(32):                                  # karonun bos (siyah) bolgeleri komsu renkle: ada kenarlarinda koyu cizgi olmasin
        grown = cv2.dilate(np.where(full[..., None], src, 0).astype(np.float32), np.ones((3, 3), np.uint8))
        gm = cv2.dilate(full.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
        new = gm & ~full; src[new] = grown[new]; full |= new
    if os.environ.get("BAND_CLEAN", "1") == "1" and int(t["name"].split("_")[2]) in (5, 45, 6, 26):   # bandana, dugum, kuyruklar
        # Tripo bu dokulara ustlerine dusen sac tutamlarini da boyamis (koyu ve turuncu lekeler). Kirmizi olmayan her piksel
        # karonun kirmizi ortancasina cekilir; kumasin koyu kirmizi kivrim golgeleri kirmizi oldugu icin kalir.
        r_, g_, b_ = src[..., 0], src[..., 1], src[..., 2]
        isred = (r_ >= 95) & (g_ < 0.38 * r_) & (b_ < 0.45 * r_)
        if isred.any():
            med = np.median(src[isred & (r_ > 150)] if (isred & (r_ > 150)).any() else src[isred], axis=0)
            a = cv2.GaussianBlur((~isred).astype(np.float32), (0, 0), 1.5)[..., None]
            a = np.clip(a * 2.2, 0, 1); src = src * (1 - a) + med * a
    tile = Image.fromarray(np.clip(src, 0, 255).astype(np.uint8)).resize((w, h), Image.LANCZOS)
    # karonun cevresine kendi kenar pikselleri tasirilir (kucuk doku duzeylerinde komsu karo sizmasin)
    grown = tile.resize((w + 4, h + 4), Image.NEAREST); atlas.paste(grown, (x - 2, y - 2)); atlas.paste(tile, (x, y))
out = "Textures/Model_BaseColor_%s.png" % ver; atlas.save(out); print("saved", out, atlas.size, "tiles", len(L["tiles"]))
