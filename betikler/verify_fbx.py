# Teslim FBX'ini bos bir sahneye yeniden ice aktarip sayar: nesne, kose, ucgen, UV, doku, boyut.
# blender -b --factory-startup --python Scripts/verify_fbx.py -- <fbx>
import bpy, sys
from mathutils import Vector
f = sys.argv[sys.argv.index("--") + 1]
bpy.ops.wm.read_factory_settings(use_empty=True); bpy.ops.import_scene.fbx(filepath=f)
ms = [o for o in bpy.context.scene.objects if o.type == "MESH"]
arm = [o for o in bpy.context.scene.objects if o.type == "ARMATURE"]
for o in ms:
    me = o.data; me.calc_loop_triangles()
    pts = [o.matrix_world @ Vector(c) for c in o.bound_box]
    size = [max(p[i] for p in pts) - min(p[i] for p in pts) for i in range(3)]
    imgs = [n.image.name for m in me.materials if m and m.node_tree for n in m.node_tree.nodes if n.type == "TEX_IMAGE" and n.image]
    print("VERIFY objects %d armatures %d | %s: verts %d tris %d uv layers %d materials %d images %s | size m %.3f %.3f %.3f | shape keys %s | custom normals %s" % (
        len(ms), len(arm), o.name, len(me.vertices), len(me.loop_triangles), len(me.uv_layers), len(me.materials), imgs, size[0], size[1], size[2], me.shape_keys is not None, me.has_custom_normals))
