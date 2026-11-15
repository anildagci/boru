# Yuzun onden duz render'inda (yuz_onden.py) iki gozun irisini bulur; merkezlerinin dunya x,z'sini JSON'a yazar.
# Iris: doymus renkli, toplu, yuvarlaga yakin bir leke; kenari cogunlukla koyu (kirpik cizgisi); icinde ondan koyu bir bebek;
# karsi tarafta benzer bir esi. Kural renk bilmez: sari, mavi goz ayni sekilde bulunur.
# Esikler 2026-11-15'te dort goruntuyle olculdu (Raicon ve Bolt; govde ve bas). Gozluk cami (icinde bebek yok, 0,01-0,02),
# kas (doluluk 0,36-0,38) ve kayis tokasi (boy/en 4) bu esiklerle elenir. Baska karakterde yanilabilir: sonuc goruntusune bakilir.
# python goz_bul.py <yuz.png> ...   (yanindaki yuz.json okunur; sonuc yuz_goz.json ve isaretli yuz_goz.png)
import sys, json
import numpy as np, cv2

DOLULUK, ORAN, KENAR_KOYU, BEBEK = 0.45, (0.6, 1.8), 0.30, 0.10

def bul(png):
    k = json.load(open(png[:-4] + ".json")); R = k["res"]
    bgr = cv2.imread(png); hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV).astype(np.float32)
    S, V = hsv[..., 1] / 255, hsv[..., 2] / 255
    zemin = (bgr[..., 0] > 215) & (bgr[..., 1] < 60) & (bgr[..., 2] > 215)          # mor zemin
    koyu = (V < 0.35) & ~zemin
    renkli = ((S > 0.45) & (V > 0.45) & ~zemin).astype(np.uint8)
    renkli = cv2.morphologyEx(renkli, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)))
    n, lab, st, mer = cv2.connectedComponentsWithStats(renkli, 8)
    aday, elenen = [], 0
    for i in range(1, n):
        x, y, w, h, a = st[i]
        if a < R * R * 1e-4 or a > R * R * 0.01: continue
        m = (lab == i).astype(np.uint8); r = max(3, int(0.08 * max(w, h)))
        kenar = (cv2.dilate(m, np.ones((2 * r + 1,) * 2, np.uint8)) > 0) & (m == 0)
        hm = np.zeros_like(m); cv2.fillConvexPoly(hm, cv2.convexHull(cv2.findNonZero(m)), 1)
        ic = (hm > 0) & (m == 0)
        d = dict(px=float(mer[i][0]), py=float(mer[i][1]), alan=int(a), dolu=a / float(w * h), oran=h / float(w),
                 kenar_koyu=float(koyu[kenar].mean()), bebek=float(((V < V[m > 0].mean() * 0.7) & ic).sum() / a))
        if d["dolu"] > DOLULUK and ORAN[0] < d["oran"] < ORAN[1] and d["kenar_koyu"] > KENAR_KOYU and d["bebek"] > BEBEK:
            aday.append(d)
        else:
            elenen += 1
    en, eniyi = -9, None                       # en iyi es: ayni hizada, benzer buyuklukte, kadrajin ortasina gore karsilikli
    for i in range(len(aday)):
        for j in range(i + 1, len(aday)):
            a, b = sorted((aday[i], aday[j]), key=lambda d: d["px"])
            ara = b["px"] - a["px"]
            if ara < R * 0.02: continue
            dy = abs(a["py"] - b["py"]) / ara; oran = min(a["alan"], b["alan"]) / max(a["alan"], b["alan"])
            orta = abs((a["px"] + b["px"]) / 2 - R / 2) / ara
            if dy > 0.25 or orta > 0.5 or oran < 0.4: continue
            puan = oran - dy - orta + (a["bebek"] + b["bebek"]) / 2
            if puan > en: en, eniyi = puan, (a, b)
    sonuc = {"bulundu": eniyi is not None, "aday": len(aday), "elenen": elenen, "_aday": aday}
    if eniyi:
        dunya = lambda d: [k["cx"] + (d["px"] / R - 0.5) * k["span"], k["cz"] - (d["py"] / R - 0.5) * k["span"]]
        sonuc.update(sol=dunya(eniyi[0]), sag=dunya(eniyi[1]), piksel=[[d["px"], d["py"]] for d in eniyi], puan=en,
                     baska_aday=len(aday) > 2)
    return sonuc

def kaydet(png):
    s = bul(png); bgr = cv2.imread(png)
    for d in s.pop("_aday"): cv2.circle(bgr, (int(d["px"]), int(d["py"])), 10, (255, 128, 0), 3)
    for p in s.get("piksel", []): cv2.circle(bgr, (int(p[0]), int(p[1])), 30, (0, 255, 0), 5)
    cv2.imwrite(png[:-4] + "_goz.png", bgr); json.dump(s, open(png[:-4] + "_goz.json", "w"), indent=1)
    return s

if __name__ == "__main__":
    for p in sys.argv[1:]:
        s = kaydet(p); print(p.replace("\\", "/").split("/")[-1], "BULDU" if s["bulundu"] else "BULAMADI", "aday", s["aday"], s.get("piksel"), s.get("sol"), s.get("sag"))
