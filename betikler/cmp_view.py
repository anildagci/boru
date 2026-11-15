# Bir sahneyi ya da GLB'yi ayni kadrajla, duz doku rengiyle (golgelendirici yok) render alir: bas onden ve arkadan.
import bpy, sys, math
from mathutils import Vector
a = sys.argv[sys.argv.index("--") + 1:]; out = a[0]; glb = a[1] if len(a) > 1 and a[1].lower().endswith(".glb") else None
if glb:
    bpy.ops.wm.read_factory_settings(use_empty=True); bpy.ops.import_scene.gltf(filepath=glb)
ms = [o for o in bpy.context.scene.objects if o.type == "MESH"]
pts = [o.matrix_world @ Vector(c) for o in ms for c in o.bound_box]
top = max(p.z for p in pts); h = top - min(p.z for p in pts); cx = sum(p.x for p in pts) / len(pts)
sc = bpy.context.scene; sc.render.engine = "BLENDER_WORKBENCH"; sh = sc.display.shading; sh.light = "FLAT"; sh.color_type = "TEXTURE"; sc.display.render_aa = "8"
cam = bpy.data.objects.new("c", bpy.data.cameras.new("c")); sc.collection.objects.link(cam); sc.camera = cam; cam.data.type = "ORTHO"; cam.data.clip_end = 50
span = float(a[2]) * h if len(a) > 2 else 0.27 * h
sc.render.resolution_x = sc.render.resolution_y = 1400; cam.data.ortho_scale = span; cc = Vector((cx, 0, top - span * 0.48))
print("TRIS", sum(len(o.data.polygons) for o in ms), "IMG", [(i.name, tuple(i.size)) for i in bpy.data.images if i.size[0] > 64][:3])
for tag, d in (("front", Vector((0, -1, 0))), ("back", Vector((0, 1, 0)))):
    cam.location = cc + d * 20; cam.rotation_euler = (cc - cam.location).to_track_quat("-Z", "Y").to_euler()
    sc.render.filepath = out + "_" + tag + ".png"; bpy.ops.render.render(write_still=True)
