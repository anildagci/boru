# Bir GLB'nin yuzunu onden, ortografik ve duz doku rengiyle (golgelendirici yok) render alir; gozleri bulmak icin.
# Kadraj bilgisi (pikselden dunya x,z'ye donusum) yanina JSON olarak yazilir. Modele dokunmaz.
# blender -b --factory-startup --python yuz_onden.py -- <glb> <cikti.png>
import bpy, sys, json
from mathutils import Vector
glb, out = sys.argv[sys.argv.index("--") + 1:][:2]
bpy.ops.wm.read_factory_settings(use_empty=True); bpy.ops.import_scene.gltf(filepath=glb)
ms = [o for o in bpy.context.scene.objects if o.type == "MESH"]
pts = [o.matrix_world @ Vector(c) for o in ms for c in o.bound_box]
lo = Vector([min(p[i] for p in pts) for i in range(3)]); hi = Vector([max(p[i] for p in pts) for i in range(3)])
h = hi.z - lo.z; w = max(hi.x - lo.x, hi.y - lo.y)
govde = h / w > 1.5                     # boyu eninden cok buyuk: tam govde; degilse bas ve omuz
span = 0.24 * h if govde else 0.8 * h   # bas, kadrajin ust kismina sigacak kadar
cx = (lo.x + hi.x) / 2; cz = hi.z - span * 0.5
sc = bpy.context.scene; sc.render.engine = "BLENDER_WORKBENCH"; sh = sc.display.shading; sh.light = "FLAT"; sh.color_type = "TEXTURE"
sc.display.render_aa = "8"; R = 2000; sc.render.resolution_x = sc.render.resolution_y = R
wd = bpy.data.worlds.new("w"); sc.world = wd; wd.color = (1.0, 0.0, 1.0)          # mor zemin: modelde olmayan bir renk
sc.view_settings.view_transform = "Standard"
cam = bpy.data.objects.new("c", bpy.data.cameras.new("c")); sc.collection.objects.link(cam); sc.camera = cam
cam.data.type = "ORTHO"; cam.data.ortho_scale = span; cam.data.clip_end = 50
cam.location = Vector((cx, lo.y - 10, cz)); cam.rotation_euler = (Vector((cx, 0, cz)) - cam.location).to_track_quat("-Z", "Y").to_euler()
sc.render.filepath = out; bpy.ops.render.render(write_still=True)
# piksel (px, py) -> dunya: x = cx + (px / R - 0.5) * span ; z = cz - (py / R - 0.5) * span   (py yukaridan asagi)
json.dump({"cx": cx, "cz": cz, "span": span, "res": R, "govde": govde, "height": h, "top": hi.z}, open(out[:-4] + ".json", "w"), indent=1)
print("YUZ", out, "govde" if govde else "bas", "span %.4f" % span)
