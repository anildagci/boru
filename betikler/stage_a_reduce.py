# Asama A: iki Tripo modelini ice aktarir, koseleri birlestirir, ucgen sayisini indirir ve ara sahne olarak kaydeder.
# Uzun suren adim budur; sonraki asamalar bu sahneden baslar. Kaynak dosyalara dokunmaz.
# blender -b --factory-startup --python Scripts/stage_a_reduce.py -- <karakter klasoru mutlak yol>
import bpy, sys, os
import numpy as np
ROOT = sys.argv[sys.argv.index("--") + 1]
J = lambda *p: os.path.join(ROOT, *p)
E = lambda k, d: float(os.environ.get(k, d))
bpy.ops.wm.read_factory_settings(use_empty=True)

def decimate(o, tris):
    n = len(o.data.polygons)
    if n <= tris: return
    bpy.ops.object.select_all(action="DESELECT"); o.select_set(True); bpy.context.view_layer.objects.active = o
    m = o.modifiers.new("d", "DECIMATE"); m.ratio = tris / n; bpy.ops.object.modifier_apply(modifier="d")

# ---- govde (tek parca). merge_vertices: glTF doku adasi kenarlarinda koseleri cogaltir; birlestirilmezse adalar ayrilir.
bpy.ops.import_scene.gltf(filepath=J("Source", os.environ.get("BORU_BODY", "body.glb")), merge_vertices=True)
body = [o for o in bpy.context.scene.objects if o.type == "MESH"][0]; body.name = "BodySrc"
bpy.ops.object.select_all(action="DESELECT"); body.select_set(True); bpy.context.view_layer.objects.active = body
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
n0 = len(body.data.polygons); decimate(body, E("BODY_TRIS", 30000))
for mat in body.data.materials:
    for nd in mat.node_tree.nodes:
        if nd.type == "TEX_IMAGE" and nd.image and "basecolor" in nd.image.name.lower():
            p = J("Textures", "original", "body_basecolor.png"); nd.image.filepath_raw = p; nd.image.file_format = "PNG"; nd.image.save()
print("body: %d -> %d triangles" % (n0, len(body.data.polygons)))

# ---- bas (parcali)
before = set(bpy.context.scene.objects)
if os.environ.get("BODY_ONLY", "0") == "1":             # tam cozunurluklu yol: yalniz govde (bas, simple_graft.py'de ice aktarilir)
    bpy.ops.file.pack_all(); out = J("Blender", os.environ.get("STAGE_A_NAME", "Model_StageA") + ".blend")
    bpy.ops.wm.save_as_mainfile(filepath=out); print("saved", out); raise SystemExit
bpy.ops.import_scene.gltf(filepath=J("Source", os.environ.get("BORU_HEAD_PARTS", "head_parts.glb")), merge_vertices=True)
parts = [o for o in bpy.context.scene.objects if o not in before and o.type == "MESH"]
DROP = {0, 8, 9, 17, 25, 26}                                # ceket ve omuzlar: govde modelinden gelir
BOOST = {6: 2.2, 15: 1.8, 16: 1.8, 27: 2.5, 29: 2.5, 32: 2.0, 35: 2.0, 37: 2.0, 39: 2.0, 10: 1.4, 14: 1.4, 30: 1.2, 31: 1.2, 34: 1.4}
keep = []
for o in parts:
    i = int(o.name.split("_")[-1])
    if i in DROP: bpy.data.objects.remove(o, do_unlink=True); continue
    bpy.ops.object.select_all(action="DESELECT"); o.select_set(True); bpy.context.view_layer.objects.active = o
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True); keep.append(o)
total = sum(len(o.data.polygons) * BOOST.get(int(o.name.split("_")[-1]), 1.0) for o in keep); T = E("HEAD_TRIS", 26000)
for o in keep:
    i = int(o.name.split("_")[-1]); n = len(o.data.polygons)
    decimate(o, max(E("PART_MIN", 160), n * BOOST.get(i, 1.0) * T / total))
    o.name = "H%02d" % i
print("head: %d parts kept, %d triangles" % (len(keep), sum(len(o.data.polygons) for o in keep)))
bpy.ops.file.pack_all()
out = J("Blender", os.environ.get("STAGE_A_NAME", "Model_StageA") + ".blend"); bpy.ops.wm.save_as_mainfile(filepath=out); print("saved", out)
