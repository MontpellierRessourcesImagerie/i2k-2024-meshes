import bpy
import bmesh

###############################################

collection_name = "Collection"
smallest_volume = 120.0 # in µm³

###############################################

bpy.ops.object.select_all(action='DESELECT')
collection = bpy.data.collections[collection_name]
targets    = []

for obj in collection.objects:
    # The scene can contain meshes, lights, cameras, lattices, ...
    if obj.type != 'MESH':
        continue
    
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='EDIT')

    bm = bmesh.from_edit_mesh(obj.data)
    volume = bm.calc_volume()

    bpy.ops.object.mode_set(mode='OBJECT')
    
    if volume < smallest_volume:
        targets.append(obj.name)

bpy.ops.object.select_all(action='DESELECT')
for item in targets:
    obj = bpy.data.objects.get(item)
    if obj is None:
        continue
    obj.select_set(True)
