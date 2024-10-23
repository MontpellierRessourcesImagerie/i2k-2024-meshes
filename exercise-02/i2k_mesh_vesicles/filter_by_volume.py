import bpy
import bmesh

###############################################

OPERATIONS = [
    "Bigger than",
    "Smaller than"
]

###############################################

def compare(operation, a, b):
    if operation == OPERATIONS[0]:
        return a > b
    elif operation == OPERATIONS[1]:
        return a < b
    else:
        return False

def select_items(targets):
    for item in targets:
        obj = bpy.data.objects.get(item)
        if obj is None:
            continue
        obj.select_set(True)

def find_objects_by_volume(collection_name, thr_volume, operation):
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
        
        if compare(operation, volume, thr_volume):
            targets.append(obj.name)
    
    select_items(targets)

if __name__ == "__main__":
    bpy.ops.object.select_all(action='DESELECT')
    find_objects_by_volume("Spots", 7.0, 'Smaller than')
    find_objects_by_volume("Spots", 34.0, 'Bigger than')