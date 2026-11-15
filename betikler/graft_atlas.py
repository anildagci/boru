# Asilanmis sahneyi tek dokulu tek modele cevirir: bas parcalarinin dokularini ve govde dokusunu tek atlasa yerlestirir,
# UV'leri yeniden esler, iki nesneyi birlestirir. Atlas goruntusunu graft_atlas_compose.py olusturur.
# blender -b <asilama .blend> --python Scripts/graft_atlas.py -- <karakter klasoru mutlak yol> <surum>
import bpy, sys, os, json
import numpy as np
a = sys.argv[sys.argv.index("--") + 1:]; ROOT, VER = a[0], a[1]
J = lambda *p: os.path.join(ROOT, *p)
SIZE = int(os.environ.get("ATLAS_SIZE", "4096")); BODY = int(os.environ.get("ATLAS_BODY", "2560")); GAP = 6
work = J("Textures", "work", "graft", "parts"); os.makedirs(work, exist_ok=True)
head = bpy.data.objects["HeadNew"]; body = bpy.data.objects["Body"]
print("uv layers: head %s body %s" % ([l.name for l in head.data.uv_layers], [l.name for l in body.data.uv_layers]))

# ---- bas parcalarinin dokulari diske
tiles = []
for mi, slot in enumerate(head.material_slots):
    img = None
    for nd in slot.material.node_tree.nodes:
        if nd.type == "TEX_IMAGE" and nd.image and "basecolor" in nd.image.name.lower():
            img = nd.image
    assert img is not None, slot.material.name
    path = os.path.join(work, "m%02d.png" % mi)
    img.filepath_raw = path; img.file_format = "PNG"; img.save()
    tiles.append({"mat": mi, "name": slot.material.name, "src": path, "w0": img.size[0], "h0": img.size[1]})

# ---- yerlesim: govde sol ustte BODY x BODY; bas karolari sagdaki ve alttaki seritlere raf raf dizilir
def pack(f):
    regions = [[BODY + GAP, 0, SIZE - BODY - GAP, SIZE], [0, BODY + GAP, BODY, SIZE - BODY - GAP]]
    out = []; cur = [(r[0], r[1], 0) for r in regions]                 # her bolgede: x, y, raf yuksekligi
    for t in sorted(tiles, key=lambda t: -t["h0"]):
        w, h = max(16, int(t["w0"] * f)), max(16, int(t["h0"] * f)); placed = False
        for ri, r in enumerate(regions):
            x, y, sh = cur[ri]
            if x + w > r[0] + r[2]:
                x, y, sh = r[0], y + sh + GAP, 0
            if y + h <= r[1] + r[3] and x + w <= r[0] + r[2]:
                out.append((t["mat"], x, y, w, h)); cur[ri] = (x + w + GAP, y, max(sh, h)); placed = True; break
            cur[ri] = (x, y, sh)
        if not placed:
            return None
    return out
f = 1.0
while True:
    lay = pack(f)
    if lay: break
    f -= 0.03
print("atlas: head tiles scaled by %.2f, body at %d px" % (f, BODY))
rect = {m: (x, y, w, h) for m, x, y, w, h in lay}
for t in tiles: t["rect"] = rect[t["mat"]]
json.dump({"size": SIZE, "body": [0, 0, BODY, BODY], "body_src": J("Textures", os.environ.get("ATLAS_BODY_SRC", "Model_BaseColor_v09.png")), "tiles": tiles},
          open(J("Textures", "work", "graft", "atlas_layout.json"), "w"), indent=1)

# ---- UV'ler
def remap(me, fn):
    n = len(me.loops); uv = np.empty(n * 2, np.float32); me.uv_layers[0].data.foreach_get("uv", uv); uv = uv.reshape(-1, 2)
    fn(me, uv); me.uv_layers[0].data.foreach_set("uv", uv.reshape(-1))
def head_fn(me, uv):
    npoly = len(me.polygons)
    mi = np.empty(npoly, np.int32); me.polygons.foreach_get("material_index", mi)
    ls = np.empty(npoly, np.int32); me.polygons.foreach_get("loop_start", ls)
    lt = np.empty(npoly, np.int32); me.polygons.foreach_get("loop_total", lt)
    loop_mat = np.repeat(mi, lt)
    out_of = int(((uv < -0.001) | (uv > 1.001)).any(1).sum())
    print("head uv: %d of %d corners outside 0..1" % (out_of, len(uv)))
    R = np.array([rect[m] for m in range(len(tiles))], np.float32)[loop_mat]
    u = np.clip(uv[:, 0], 0, 1); v = np.clip(uv[:, 1], 0, 1)
    uv[:, 0] = (R[:, 0] + u * R[:, 2]) / SIZE
    uv[:, 1] = 1 - (R[:, 1] + (1 - v) * R[:, 3]) / SIZE
def body_fn(me, uv):
    k = BODY / SIZE
    uv[:, 0] = uv[:, 0] * k; uv[:, 1] = 1 - (1 - uv[:, 1]) * k
remap(head.data, head_fn); remap(body.data, body_fn)
head.data.uv_layers[0].name = "UVMap"; body.data.uv_layers[0].name = "UVMap"

# ---- tek nesne, tek malzeme
bpy.ops.object.select_all(action="DESELECT"); body.select_set(True); head.select_set(True)
bpy.context.view_layer.objects.active = body; bpy.ops.object.join()
obj = bpy.context.view_layer.objects.active; obj.name = "Model"; me = obj.data; me.name = "Model"
while len(me.uv_layers) > 1: me.uv_layers.remove(me.uv_layers[-1])
me.materials.clear()
mat = bpy.data.materials.new("BlazeAtlas"); mat.use_nodes = True; nt = mat.node_tree
tex = nt.nodes.new("ShaderNodeTexImage")
atlas = J("Textures", "Model_BaseColor_%s.png" % VER)
img = bpy.data.images.new("atlas", 8, 8); img.filepath = atlas; img.source = "FILE"; tex.image = img
nt.links.new(tex.outputs["Color"], nt.nodes["Principled BSDF"].inputs["Base Color"]); nt.nodes.active = tex
me.materials.append(mat)
for p in me.polygons: p.material_index = 0; p.use_smooth = True
print("custom normals kept:", me.has_custom_normals)
print("merged: %d vertices, %d triangles, %d uv layer(s), %d material(s)" % (len(me.vertices), len(me.polygons), len(me.uv_layers), len(me.materials)))
out = J("Blender", "Model_Graft_%s.blend" % VER); bpy.ops.wm.save_as_mainfile(filepath=out); print("saved", out)
