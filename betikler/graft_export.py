# Birlestirilmis Blaze modelini FBX ve GLB olarak disa aktarir (iskelet yok; Mixamo'ya ve Unity onizlemesine gider).
# blender -b <asilama .blend> --python Scripts/graft_export.py -- <karakter klasoru mutlak yol> <surum>
import bpy, sys, os
a = sys.argv[sys.argv.index("--") + 1:]; ROOT, VER = a[0], a[1]
J = lambda *p: os.path.join(ROOT, *p)
obj = bpy.data.objects["Model"]
for im in bpy.data.images:
    if im.source == "FILE" and im.filepath: im.reload()
bpy.ops.object.select_all(action="DESELECT"); obj.select_set(True); bpy.context.view_layer.objects.active = obj
fbx = J("Exports", "Model_Graft_%s.fbx" % VER)
bpy.ops.export_scene.fbx(filepath=fbx, use_selection=True, object_types={"MESH"}, apply_scale_options="FBX_SCALE_ALL",
                         path_mode="COPY", embed_textures=True, mesh_smooth_type="OFF", use_mesh_modifiers=False,
                         add_leaf_bones=False, bake_anim=False)
glb = J("Exports", "Model_Graft_%s.glb" % VER)
bpy.ops.export_scene.gltf(filepath=glb, use_selection=True, export_format="GLB", export_apply=False, export_animations=False)
print("exported", fbx, os.path.getsize(fbx), glb, os.path.getsize(glb), "| triangles", len(obj.data.polygons))
