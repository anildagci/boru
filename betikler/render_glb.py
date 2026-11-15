# Bir GLB'yi sekiz yonden render alir: duz doku rengi ve kil. Modele dokunmaz.
# blender -b --factory-startup --python Scripts/render_glb.py -- <glb> <cikti klasoru> <etiket>
import bpy, sys, math, os
from mathutils import Vector
glb, outdir, tag = sys.argv[sys.argv.index("--") + 1:][:3]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=glb)
meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"]
pts = [o.matrix_world @ Vector(c) for o in meshes for c in o.bound_box]
lo = Vector([min(p[i] for p in pts) for i in range(3)]); hi = Vector([max(p[i] for p in pts) for i in range(3)])
cen = (lo + hi) / 2; size = max(hi - lo)
tris = 0
for o in meshes:
    o.data.calc_loop_triangles(); tris += len(o.data.loop_triangles)
print("INFO %s objects %d verts %d tris %d size %s" % (tag, len(meshes), sum(len(o.data.vertices) for o in meshes), tris, tuple(round(v, 3) for v in hi - lo)))
for o in meshes:
    print("INFO %s object %s verts %d materials %s" % (tag, o.name, len(o.data.vertices), [m.name for m in o.data.materials if m]))
    for m in o.data.materials:
        if m and m.node_tree:
            for n in m.node_tree.nodes:
                if n.type == "TEX_IMAGE" and n.image:
                    print("INFO %s image %s %s" % (tag, n.image.name, tuple(n.image.size)))
sc = bpy.context.scene
sc.render.engine = "BLENDER_WORKBENCH"; sh = sc.display.shading
sc.display.render_aa = "8"; sc.render.resolution_x = sc.render.resolution_y = 1000
w = bpy.data.worlds.new("w"); sc.world = w; w.color = (0.75, 0.75, 0.75)
cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); sc.collection.objects.link(cam); sc.camera = cam
cam.data.type = "ORTHO"; cam.data.ortho_scale = size * 1.08; cam.data.clip_end = size * 20
os.makedirs(outdir, exist_ok=True)
def shoot(prefix):
    for ang in (0, 22, 45, 68, 90, 135, 180, 270):
        a = math.radians(ang); d = Vector((-math.sin(a), -math.cos(a), 0))     # 0 = on, 90 = cizimdeki yan
        cam.location = cen + d * size * 5
        cam.rotation_euler = (cen - cam.location).to_track_quat("-Z", "Y").to_euler()
        sc.render.filepath = os.path.join(outdir, "%s_%s%03d.png" % (tag, prefix, ang)); bpy.ops.render.render(write_still=True)
sh.light = "FLAT"; sh.color_type = "TEXTURE"; shoot("a")
sh.light = "STUDIO"; sh.color_type = "SINGLE"; sh.single_color = (0.62, 0.55, 0.5); sh.show_cavity = True; shoot("clay")
