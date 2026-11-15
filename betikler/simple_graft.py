# Sade yol: tek parca bas modeli (yuzu Tripo'nun urettigi haliyle) govdeye oturtulur. Yuze dokunulmaz.
# Hizalama iki modelde de belirgin olan gozluk camlarindan (mavi) yapilir; govdenin basi ve boynu cikar, basin ceketi cikar.
# blender -b Blender/Model_StageA.blend --python Scripts/simple_graft.py -- <karakter klasoru mutlak yol> <surum>
import bpy, bmesh, sys, os, math, json
import numpy as np
from mathutils import Vector, Matrix
a = sys.argv[sys.argv.index("--") + 1:]; ROOT, VER = a[0], a[1]
J = lambda *p: os.path.join(ROOT, *p)
E = lambda k, d: float(os.environ.get(k, d))
for o in [o for o in bpy.data.objects if o.type == "MESH" and o.name.startswith("H")]: bpy.data.objects.remove(o, do_unlink=True)
body = bpy.data.objects["BodySrc"]

def arrays(me):
    nl, nf = len(me.loops), len(me.polygons)
    co = np.empty(len(me.vertices) * 3, np.float32); me.vertices.foreach_get("co", co); co = co.reshape(-1, 3)
    lv = np.empty(nl, np.int32); me.loops.foreach_get("vertex_index", lv)
    uv = np.empty(nl * 2, np.float32); me.uv_layers[0].data.foreach_get("uv", uv); uv = uv.reshape(-1, 2)
    ls = np.empty(nf, np.int32); me.polygons.foreach_get("loop_start", ls)
    fn = np.empty(nf * 3, np.float32); me.polygons.foreach_get("normal", fn); fn = fn.reshape(-1, 3)
    return co, lv, uv, ls[:, None] + np.arange(3)[None], fn
def colours(me):
    img = None
    for mat in me.materials:
        for nd in mat.node_tree.nodes:
            if nd.type == "TEX_IMAGE" and nd.image and "basecolor" in nd.image.name.lower(): img = nd.image
    W_, H_ = img.size; px = np.array(img.pixels[:], np.float32).reshape(H_, W_, 4)[..., :3]
    co, lv, uv, tri, fn = arrays(me); u = uv[tri].mean(1)
    return co, lv, uv, tri, fn, px[np.clip((u[:, 1] % 1) * H_, 0, H_ - 1).astype(int), np.clip((u[:, 0] % 1) * W_, 0, W_ - 1).astype(int)]
skin_c = lambda c: (c[:, 0] > 0.55) & (c[:, 1] > 0.38) & (c[:, 2] > 0.25) & (c[:, 0] - c[:, 2] > 0.12) & (c[:, 0] > c[:, 1]) & (c[:, 1] > c[:, 2])
cyan_c = lambda c: (c[:, 2] > 0.55) & (c[:, 1] > 0.45) & (c[:, 0] < 0.5) & (c[:, 2] - c[:, 0] > 0.25)
navy_c = lambda c: (c[:, 2] > c[:, 0] + 0.06) & (c[:, 0] < 0.25) & (c[:, 2] < 0.55) & (c[:, 2] > 0.12)
def lenses(cen, m):
    xm = np.median(cen[m, 0]); l, r = cen[m & (cen[:, 0] < xm)].mean(0), cen[m & (cen[:, 0] >= xm)].mean(0)
    return l, r, float(cen[m, 1].min())
# Goz capasi: goz_bul.py iki irisin dunya x,z'sini onden render'dan bulur; burada onden atilan isinla yuzeydeki y bulunur.
# Cozunurlukten bagimsizdir (ucgenlerin agirlik merkezine degil, yuzeyin kendisine bakar). Dosya verilmezse eski yol: gozluk cami.
def eyes(obj, key):
    p = os.environ.get(key)
    if not p: return None
    g = json.load(open(p))
    if not g.get("bulundu"): raise SystemExit("goz bulunamadi: %s" % p)
    y0 = min((obj.matrix_world @ Vector(c)).y for c in obj.bound_box) - 1.0; inv = obj.matrix_world.inverted(); pts = []
    for x, z in (g["sol"], g["sag"]):
        ok, loc, nor, idx = obj.ray_cast(inv @ Vector((x, y0, z)), (inv.to_3x3() @ Vector((0, 1, 0))).normalized())
        if not ok: raise SystemExit("goz noktasi yuzeyde degil: %s %.4f %.4f" % (p, x, z))
        pts.append(np.array(obj.matrix_world @ loc))
    print("eyes %s: %s %s" % (key, pts[0].round(4), pts[1].round(4)))
    return pts[0], pts[1], float((pts[0][1] + pts[1][1]) / 2)

# ---- govde
bme = body.data; co, lv, uv, tri, fn, cc = colours(bme); cen = co[lv][tri].mean(1); Hb = co[:, 2].max()
bl, br, bfront = eyes(body, "BORU_EYES_BODY") or lenses(cen, cyan_c(cc) & (cen[:, 2] > 0.85 * Hb))
# Renk kurallari. "raicon": Raicon icin elle olculmus sabit kurallar (onayli sonuc bunlarla). "otomatik": ten ve yaka rengi
# modelin kendisinden okunur: gozlerin ortasindan asagi inen on orta sutunda ilk renk ten, tenden belirgin farkli ilk renk
# yakadaki giysidir (tisort yakasi gibi). Goz dosyasi verilmezse eski yol (raicon) kalir.
RENK = os.environ.get("BORU_RENK", "otomatik" if os.environ.get("BORU_EYES_BODY") else "raicon")
def sample(cen, cc, ex, ez, ed, name):
    col = (np.abs(cen[:, 0] - ex) < ed * 0.15); fy = cen[col & (np.abs(cen[:, 2] - ez) < ed), 1].min(); col &= cen[:, 1] < fy + 2 * ed
    seq = []
    for z in np.arange(ez - ed * 0.6, ez - ed * 6, -ed * 0.2):
        m = col & (np.abs(cen[:, 2] - z) < ed * 0.1)
        if m.sum(): seq.append((z, cc[m][np.argmin(cen[m, 1])]))
    sk = np.median([c for z, c in seq[:3]], 0); gi = next((i for i, (z, c) in enumerate(seq) if np.abs(c - sk).max() > 0.25), None)
    if gi is None: raise SystemExit("%s: yaka rengi bulunamadi (on orta sutunda tenden farkli renk yok)" % name)
    gm = np.median([c for z, c in seq[gi:gi + 3]], 0)
    zline = float((seq[gi][0] + seq[gi - 1][0]) / 2) if gi else float(seq[gi][0])     # ten ile giysi arasi: on yaka hizasi
    print("%s colours: skin %s, garment %s (neckline at front z %.3f)" % (name, sk.round(2), gm.round(2), zline))
    return sk, gm, zline
near = lambda ref, tol: (lambda c: np.abs(c - ref).max(1) < tol)
if RENK == "otomatik":
    bsk, bgm, bline = sample(cen, cc, (bl[0] + br[0]) / 2, (bl[2] + br[2]) / 2, abs(br[0] - bl[0]), "body")
    skin_b, navy_b = near(bsk, E("SKIN_TOL", 0.15)), near(bgm, E("GARMENT_TOL", 0.12))
else:
    skin_b, navy_b = skin_c, navy_c
skin = skin_b(cc); navy = navy_b(cc)

# ---- bas (tek parca)
before = set(bpy.context.scene.objects)
bpy.ops.import_scene.gltf(filepath=J("Source", os.environ.get("BORU_HEAD", "head.glb")), merge_vertices=True)
head = [o for o in bpy.context.scene.objects if o not in before and o.type == "MESH"][0]
bpy.ops.object.select_all(action="DESELECT"); head.select_set(True); bpy.context.view_layer.objects.active = head
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
if E("PRE_TRIS", 300000) < len(head.data.polygons):       # tam cozunurluklu yolda (PRE_TRIS cok buyuk) hic azaltma yapilmaz
    m = head.modifiers.new("d", "DECIMATE"); m.ratio = E("PRE_TRIS", 300000) / len(head.data.polygons); bpy.ops.object.modifier_apply(modifier="d")
hme = head.data; hco, hlv, huv, htri, hfn, hcc = colours(hme); hcen = hco[hlv][htri].mean(1)
hl, hr, hfront = eyes(head, "BORU_EYES_HEAD") or lenses(hcen, cyan_c(hcc) & (hcen[:, 2] > 0.5 * hco[:, 2].max()))
s = abs(br[0] - bl[0]) / abs(hr[0] - hl[0]) * E("HEAD_SCALE", 1.0)
src = np.array([(hl[0] + hr[0]) / 2, hfront, (hl[2] + hr[2]) / 2]); dst = np.array([(bl[0] + br[0]) / 2, bfront + E("HEAD_DY", 0), (bl[2] + br[2]) / 2 + E("HEAD_DZ", 0)])
head.matrix_world = Matrix.Translation(Vector(dst)) @ Matrix.Scale(s, 4) @ Matrix.Translation(Vector(-src))
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
hco, hlv, huv, htri, hfn, hcc = colours(hme); hcen = hco[hlv][htri].mean(1)
if RENK == "otomatik":
    hsk, hgm, hline = sample(hcen, hcc, dst[0], dst[2], abs(br[0] - bl[0]), "head")
    skin_h, navy_h = near(hsk, E("SKIN_TOL", 0.15)), near(hgm, E("GARMENT_TOL", 0.12))
else:
    skin_h, navy_h = skin_c, navy_c
hskin = skin_h(hcc)
if RENK == "otomatik":
    # boynun yakaya yakin kismi dokuda golgeli: sabit esigin disinda kaliyor ve "ten degil" diye siliniyordu (Bolt: tirtikli boyun
    # alti). Ten rengine giysi renginden daha yakin olan yuzler de ten sayilir.
    dsk = np.abs(hcc - hsk).max(1); hskin |= (dsk < np.abs(hcc - hgm).max(1)) & (dsk < E("SKIN_TOL_WIDE", 0.35))
fr = hco[np.unique(hlv[htri[hskin]])]; front = fr[fr[:, 1] < fr[:, 1].min() + 0.03]; chin = float(front[:, 2].min())
print("head: scale %.4f; lens anchor %s -> %s; top z %.4f (body %.4f); chin z %.4f" % (s, src.round(4), dst.round(4), hco[:, 2].max(), Hb, chin))

# ---- govdeden cikarilanlar: YALNIZ eski kucuk bas. Yakaya dokunulmaz.
# Yakanin ust kenari cevresinde degisir (arkada yuksek, onde alcak): boyun ekseni etrafinda aci dilimleri icin lacivert
# yuzeylerin en yuksek noktasi bulunur; onun ustunde beyaz serit icin pay birakilir, daha yukarisi eski bastir.
collar_top = float(np.percentile(cen[navy & (cen[:, 2] > 0.7 * Hb) & (cen[:, 2] < chin + 0.035), 2], 99.5)) + 0.012
fc = skin & (np.abs(cen[:, 0] - dst[0]) < 0.02) & (cen[:, 2] > 0.72 * Hb) & (cen[:, 2] < chin)
neck_base = float(cen[fc, 2].min()) if fc.any() else chin - 0.06
if RENK == "otomatik": neck_base = bline           # ic yuzlerdeki ten rengi yaniltiyor (Bolt: 0,721); on sutundaki gecis kullanilir
ax = np.array([dst[0], dst[1] + 0.09])
if RENK == "otomatik":
    # boyun ekseni ve yaricapi gövdenin kendi boyun teninden: yaka hizasinin biraz ustundeki ten halkasi.
    # (Raicon'un sabiti "gozlerin 9 cm arkasi"; Bolt'ta boyun one yakin, boynun onu "genis ten" sayilip siliniyordu.)
    ring = skin & (np.abs(cen[:, 2] - (neck_base + 0.012)) < 0.006) & (np.abs(cen[:, 0] - dst[0]) < 0.06) & (cen[:, 1] > dst[1] - 0.01) & (cen[:, 1] < dst[1] + 0.15)
    if ring.sum() >= 8:
        p = cen[ring][:, :2]; ax = np.array([dst[0], (p[:, 1].min() + p[:, 1].max()) / 2])
        nr = float(np.median(np.hypot(p[:, 0] - ax[0], p[:, 1] - ax[1])))
        os.environ.setdefault("NECK_RADIUS", str(nr * 1.15)); os.environ.setdefault("OLD_NECK_RADIUS", str(nr * 1.4))
        print("body: neck axis y %.4f (eyes %.4f), neck radius %.4f from %d skin faces" % (ax[1], dst[1], nr, ring.sum()))
rad = np.hypot(cen[:, 0] - ax[0], cen[:, 1] - ax[1])
ang = np.arctan2(cen[:, 1] - ax[1], cen[:, 0] - ax[0]); NB = 36; bi = ((ang + np.pi) / (2 * np.pi) * NB).astype(int) % NB
cn = navy & (cen[:, 2] > 0.7 * Hb) & (cen[:, 2] < chin + 0.035) & (rad < 0.14)      # eski basin kaslari da lacivert: cene hizasinin biraz ustune kadar aranir
rim = np.full(NB, np.nan)
for k in range(NB):
    m_ = cn & (bi == k)
    if m_.sum() >= 3: rim[k] = np.percentile(cen[m_, 2], 97)
for k in range(NB):                                     # bos dilimler komsulardan
    if np.isnan(rim[k]):
        nb_ = [rim[(k + d) % NB] for d in (-2, -1, 1, 2) if not np.isnan(rim[(k + d) % NB])]; rim[k] = np.mean(nb_) if nb_ else collar_top
# yaka onde acik: oradaki dilimlerde lacivert yuzey az ve alcakta, kenar oldugundan dusuk olculuyor ve yakanin ic astari
# ustten kesiliyordu. Her dilim, iki yanindaki dilimlerin en yuksegini alir (kenar aniden alcalmaz).
rim = np.array([max(rim[(k + d) % NB] for d in range(-int(E("RIM_SPREAD", 3)), int(E("RIM_SPREAD", 3)) + 1)) for k in range(NB)])
lim = rim[bi] + E("TRIM_ROOM", 0.012)
light_b = cc.min(1) > 0.55
drop = (cen[:, 2] > lim) & (rad < 0.16)                                    # yakanin ustunde kalan eski bas
drop |= skin & (cen[:, 2] > neck_base - 0.004) & (rad < 0.12)                # eski boyun, kulak, alt yuz teni
drop |= ~navy & ~light_b & ~skin & (cen[:, 2] > chin - 0.004) & (rad < 0.075)  # yakanin icinde kalan eski basin koyu parcalari
# yakanin icinde kalan eski bas (ense saci, kayis): her aci diliminde yakanin ic yaricapindan iceride olan, lacivert olmayan yuzler
rin = np.full(NB, np.nan)
for k in range(NB):
    m_ = cn & (bi == k) & (cen[:, 2] > rim[k] - 0.03)
    if m_.sum() >= 3: rin[k] = np.percentile(rad[m_], 10)
rin = np.where(np.isnan(rin), np.nanmedian(rin), rin)
drop |= ~navy & (cen[:, 2] > neck_base + 0.01) & (rad < rin[bi] - E("INNER_MARGIN", 0.012))
drop |= (cen[:, 2] > rim[bi] + 0.002) & (rad < rin[bi] + E("RIM_INNER", 0.003))        # yaka kenarinin ustunde ve icinde kalan eski ense saci
# eski boynun ten olmayan koyu kismi (cene alti golgesi): tisort yakasinin ustunde, boyun yaricapinda
# (yakanin ic yuzu de koyu lacivert: yalniz renksiz koyu yuzler alinir ve yakanin ic yaricapinin icinde kalanlar)
drop |= (cc.max(1) < 0.3) & ~navy & (np.abs(cc[:, 0] - cc[:, 2]) < 0.04) & (cen[:, 2] > neck_base + 0.004) & (rad < np.minimum(E("OLD_NECK_RADIUS", 0.060), rin[bi] - 0.006))
if RENK == "otomatik":
    # dusuk cozunurluklu govdede ucgenler buyuk: agirlik merkezi yaka altinda kalan ten ucgeni yukari, yeni boynun onune tasiyor
    # (Bolt: onde sagda kiriklar). Ten ucgenleri en yuksek koselerine gore alinir.
    vz = co[lv][tri][:, :, 2].max(1)
    drop |= skin & (vz > neck_base + 0.004) & (rad < 0.12)
    # yaka giysisi, yaka kenarinin hemen altinda hic silinmez (Bolt: sirtta tek ucgenlik delik)
    drop &= ~(navy & (cen[:, 2] < rim[bi] + E("TRIM_ROOM", 0.012)) & (cen[:, 2] < neck_base + 0.03))
print("body: collar rim z %.3f..%.3f around the neck; removing %d triangles of the old head" % (np.nanmin(rim), np.nanmax(rim), int(drop.sum())))
bm = bmesh.new(); bm.from_mesh(bme); bm.faces.ensure_lookup_table()
bmesh.ops.delete(bm, geom=[bm.faces[i] for i in np.where(drop)[0]], context="FACES"); bm.to_mesh(bme); bm.free(); bme.update()
body.name = "Body"; bme.uv_layers[0].name = "UVMap"

# ---- bastan cikarilanlar: YALNIZ kendi ceketi ve tisortu (govde modelinden geliyor). Saca, enseye, yuze dokunulmaz.
hrad = np.hypot(hcen[:, 0] - ax[0], hcen[:, 1] - ax[1])
hnavy = navy_h(hcc) &(hcen[:, 2] < chin + 0.075)
facebox = (np.abs(hcen[:, 0] - dst[0]) < 0.062) & (hcen[:, 1] < dst[1] + 0.045) & (hcen[:, 2] > chin - 0.004)
hnavy &= ~facebox                                          # yanak isareti ve kaslar da lacivert: yuzde aranmaz
# beyaz yaka seridi: lacivert yuzeye cok yakin (serit genisligi kadar), ten olmayan acik renkli yuzler
nv = hcen[hnavy]; lightc = ~hskin & (hcc.min(1) > 0.35) & (np.abs(hcc[:, 0] - hcc[:, 2]) < 0.2) & ~facebox & (hcen[:, 2] < chin + 0.06)
dmin = np.full(len(hcen), 9.0); li = np.where(lightc)[0]
if len(nv):
    nvs = nv[:: max(1, len(nv) // 4000)]
    for s0 in range(0, len(li), 4000):
        q = hcen[li[s0:s0 + 4000]]; dmin[li[s0:s0 + 4000]] = np.sqrt(((q[:, None, :] - nvs[None]) ** 2).sum(-1)).min(1)
trim = lightc & (dmin < E("TRIM_DIST", 0.010))
below = (hcen[:, 2] < neck_base - E("NECK_OVERLAP", 0.035))                                   # tisort ve omuzlar
panel = ~hskin & (hcen[:, 2] < chin - 0.012) & (hrad > 0.065)                                 # ceketin omuz panelleri
shirt = (hcc.max(1) < 0.3) & (hcen[:, 2] < chin - 0.008) & ~facebox                           # tisortun yaka kismi
# govdenin yakasinin icinde kalan, ten olmayan her sey (ceket kalintisi, tisort, yakanin altina inen sac ucu) gorunmez; orada
# birakilirsa govdenin yakasini delip disari cikiyor. Yaka kenari hizasinin altinda yalniz ten (boyun) ve yuz kalir.
hang = np.arctan2(hcen[:, 1] - ax[1], hcen[:, 0] - ax[0]); hbi = ((hang + np.pi) / (2 * np.pi) * NB).astype(int) % NB
under = ~hskin & ~facebox & (hcen[:, 2] < rim[hbi] + E("HEAD_RIM_CLEAR", 0.004)) & (hrad < 0.16)
# boynun dibi: bas modelinde yaka acik (kopruk kemigi teni gorunuyor), govdede orasi tisort. Tisort yakasi hizasinda yalniz
# boynun kendisi (dar yaricap) kalir; daha genis ten tisortun ustune tasiyordu.
wide = hskin & (hcen[:, 2] < neck_base + E("NECK_NARROW_Z", 0.012)) & (hrad > E("NECK_RADIUS", 0.046)) & ~facebox
# boynun alt kenari duz bir kesimle biter: bas modelinin kendi tisort siniri tirtikli (renkle ayrildigi icin); boyun, o sinirin
# hemen ustunden yatay kesilir. Govdenin tisortuyle arasinda kalan dar bosluk siyah tisortle ayni tonda gorunur.
# (cene altindaki golge de dokuda koyu: tisort yalniz cenenin belirgin altinda aranir ve kesim yuksekligi sinirlanir)
sh_front = shirt & (hrad < 0.055) & (hcen[:, 2] < chin - 0.025)
neck_cut = float(np.percentile(hcen[sh_front, 2], 97)) + E("NECK_CUT_ROOM", 0.003) if sh_front.sum() > 20 else neck_base
neck_cut = min(neck_cut, neck_base + E("NECK_CUT_MAX", 0.018))
if RENK == "otomatik":
    # tisort yakasi alcak ve acik: boyun yakanin altina inmezse yakanin ici bos gorunur (Bolt). Raicon'da yuksek ceket yakasi sakliyordu.
    neck_cut = neck_base - E("NECK_DEPTH", 0.02)
flat_cut = (hcen[:, 2] < neck_cut) & ~facebox
print("head: neck cut flat at z %.4f (body shirt neckline %.4f)" % (neck_cut, neck_base))
keep = ~(hnavy | trim | below | panel | shirt | under | wide | flat_cut)
if os.environ.get("BORU_DEBUG"):        # boynun on yuzunde, yaka hizasi civarinda hangi kural ne siliyor
    reg = (np.abs(hcen[:, 0] - dst[0]) < 0.02) & (hcen[:, 1] < dst[1] + 0.04) & (hcen[:, 2] > neck_base - 0.02) & (hcen[:, 2] < neck_base + 0.02)
    print("DEBUG neck front faces %d skin %d" % (reg.sum(), (reg & hskin).sum()), {k: int((v & reg).sum()) for k, v in dict(hnavy=hnavy, trim=trim, below=below, panel=panel, shirt=shirt, under=under, wide=wide, flat_cut=flat_cut).items()})
print("head: removed %d jacket, %d trim, %d below-neck, %d shoulder-panel triangles; nothing else" % (int(hnavy.sum()), int((trim & ~hnavy).sum()), int((below & ~hnavy & ~trim).sum()), int((panel & ~below & ~hnavy & ~trim).sum())))
bm = bmesh.new(); bm.from_mesh(hme); bm.faces.ensure_lookup_table()
bmesh.ops.delete(bm, geom=[bm.faces[i] for i in np.where(~keep)[0]], context="FACES")
bm.faces.ensure_lookup_table(); seen = set(); kill = []
for f in bm.faces:
    if f.index in seen: continue
    stack = [f]; seen.add(f.index); isl = []
    while stack:
        q = stack.pop(); isl.append(q)
        for e_ in q.edges:
            for o in e_.link_faces:
                if o.index not in seen: seen.add(o.index); stack.append(o)
    if len(isl) < 20: kill += isl
bmesh.ops.delete(bm, geom=kill, context="FACES"); bm.to_mesh(hme); bm.free(); hme.update()
n1 = len(hme.polygons)
if E("HEAD_TRIS", 40000) < n1:
    m = head.modifiers.new("d", "DECIMATE"); m.ratio = E("HEAD_TRIS", 40000) / n1; bpy.ops.object.modifier_apply(modifier="d")
m = head.modifiers.new("t", "TRIANGULATE"); bpy.ops.object.modifier_apply(modifier="t")
hme = head.data; hme.uv_layers[0].name = "UVMap"; head.name = "HeadNew"
for mat in hme.materials: mat.name = "tripo_part_0_material"
bpy.ops.object.shade_smooth()
for p in bme.polygons: p.use_smooth = True
print("body: collar top %.4f, neckline %.4f, kept %d triangles; head: kept %d, reduced to %d" % (collar_top, neck_base, len(bme.polygons), n1, len(hme.polygons)))
json.dump({"scale": float(s), "chin": chin, "collar_top": collar_top, "neck_base": neck_base, "height": float(Hb), "anchor": [float(v) for v in dst]}, open(J("Textures", "work", "simple_measure.json"), "w"), indent=1)
bpy.ops.file.pack_all()
out = J("Blender", "Model_Graft_%s.blend" % VER); bpy.ops.wm.save_as_mainfile(filepath=out); print("saved", out)
