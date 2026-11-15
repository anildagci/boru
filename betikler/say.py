# Bir sahneyi (.blend) ya da modeli (.glb / .fbx) sayar ve onden/arkadan duz doku rengiyle render alir. Dosyayi kaydetmez, degistirmez.
# blender -b <sahne.blend> --python say.py -- <cikti oneki>      ya da      blender -b --python say.py -- <cikti oneki> <model.glb|fbx>
# SAY_RENDER=0: yalniz sayar (bekci olcumu icin).
import bpy, sys, os
from mathutils import Vector
a = sys.argv[sys.argv.index("--") + 1:]; out = a[0]
if len(a) > 1:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    if a[1].lower().endswith(".fbx"):
        bpy.ops.import_scene.fbx(filepath=a[1])
    else:
        bpy.ops.import_scene.gltf(filepath=a[1])
ms = [o for o in bpy.context.scene.objects if o.type == "MESH" and o.visible_get()]
tris = 0
for o in ms:
    o.data.calc_loop_triangles(); tris += len(o.data.loop_triangles)
imgs = sorted({(n.image.name, tuple(n.image.size)) for o in ms for m in o.data.materials if m and m.node_tree
               for n in m.node_tree.nodes if n.type == "TEX_IMAGE" and n.image})
renkli = [s for n, s in imgs if "basecolor" in n.lower() or "base_color" in n.lower() or "diffuse" in n.lower()] or [s for n, s in imgs]
print("SAYI parca %d ucgen %d uv %d malzeme %d doku %d" % (len(ms), tris, max([len(o.data.uv_layers) for o in ms] or [0]),
      len({m.name for o in ms for m in o.data.materials if m}), max([max(s) for s in renkli] or [0])))
if not ms:
    print("SAY model yok (gorunur bir mesh bulunamadi)"); raise SystemExit
pts = [o.matrix_world @ Vector(c) for o in ms for c in o.bound_box]
lo = Vector([min(p[i] for p in pts) for i in range(3)]); hi = Vector([max(p[i] for p in pts) for i in range(3)])
print("SAY %d parça: %s" % (len(ms), ", ".join("%s (%s üçgen)" % (o.name, format(len(o.data.loop_triangles), ",").replace(",", ".")) for o in ms[:8])))
print("SAY toplam %s üçgen" % format(tris, ",").replace(",", "."))
print("SAY UV katmanı: %s" % ", ".join("%s %d" % (o.name, len(o.data.uv_layers)) for o in ms[:8]))
print("SAY malzeme: %s" % ", ".join("%s %d" % (o.name, len([m for m in o.data.materials if m])) for o in ms[:8]))
print("SAY doku: %s" % (", ".join("%s %dx%d" % (n, s[0], s[1]) for n, s in imgs[:8]) or "yok"))
print("SAY boyut (en, derinlik, boy): %.3f, %.3f, %.3f" % tuple(hi - lo))
if os.environ.get("SAY_RENDER", "1") == "0":
    raise SystemExit
sc = bpy.context.scene; sc.render.engine = "BLENDER_WORKBENCH"; sh = sc.display.shading; sh.light = "FLAT"; sh.color_type = "TEXTURE"
sc.display.render_aa = "8"; sc.render.resolution_x = 900; sc.render.resolution_y = 1200
w = bpy.data.worlds.new("w"); sc.world = w; w.color = (0.75, 0.75, 0.75)
cam = bpy.data.objects.new("say_cam", bpy.data.cameras.new("say_cam")); sc.collection.objects.link(cam); sc.camera = cam
size = max(hi - lo); cen = (lo + hi) / 2; cam.data.type = "ORTHO"; cam.data.ortho_scale = (hi.z - lo.z) * 1.05; cam.data.clip_end = size * 20
for tag, d in (("front", Vector((0, -1, 0))), ("back", Vector((0, 1, 0)))):
    cam.location = cen + d * size * 5; cam.rotation_euler = (cen - cam.location).to_track_quat("-Z", "Y").to_euler()
    sc.render.filepath = out + "_" + tag + ".png"; bpy.ops.render.render(write_still=True)
