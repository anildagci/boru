# Govde kirmizi, bas yesil: on yakin plan. Hangi yuzeyin hangi modelden geldigini gosterir. Sahneyi kaydetmez.
import bpy, sys
from mathutils import Vector
out = sys.argv[sys.argv.index("--") + 1]
for name, col in (("Body", (0.9, 0.1, 0.1, 1)), ("HeadNew", (0.1, 0.8, 0.2, 1))):
    for m in bpy.data.objects[name].data.materials: m.use_nodes = False; m.diffuse_color = col
sc = bpy.context.scene; sc.render.engine = "BLENDER_WORKBENCH"; sh = sc.display.shading; sh.light = "STUDIO"; sh.color_type = "MATERIAL"
cam = sc.camera
if cam is None:
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); sc.collection.objects.link(cam); sc.camera = cam; cam.data.type = "ORTHO"; cam.data.clip_end = 30
sc.render.resolution_x = 1200; sc.render.resolution_y = 1000; cam.data.ortho_scale = 0.24; cc = Vector((0, -0.05, 0.85))
for tag, d in (("front", Vector((0, -5, 0))), ("side", Vector((-5, 0, 0))), ("back", Vector((0, 5, 0)))):
    cam.location = cc + d; cam.rotation_euler = (cc - cam.location).to_track_quat("-Z", "Y").to_euler()
    sc.render.filepath = out + "_" + tag + ".png"; bpy.ops.render.render(write_still=True)
