import bpy

_LOCATIONS = "Spots-locations"
_SPOTS     = "Spots"

def reset_locations():
    collection = bpy.data.collections.get(_LOCATIONS)
    if collection is None:
        collection = bpy.data.collections.new(_LOCATIONS)
        bpy.context.scene.collection.children.link(collection)
        return
    for obj in collection.objects:
        bpy.data.objects.remove(obj, do_unlink=True)
    

def spots_as_empties():
    spots_locations_col = bpy.data.collections.get(_LOCATIONS)

    spots_col = bpy.data.collections.get(_SPOTS)
    if spots_col is None:
        return
    
    # Create empties where spots are.
    for obj in spots_col.objects:
        if obj.type == 'MESH':
            empty = bpy.data.objects.new(f"location-{obj.name}", None)
            empty.location = obj.location
            empty.empty_display_type = 'PLAIN_AXES'
            empty.empty_display_size = 1.0
            empty.color = (1.0, 0.5, 0.2, 1.0)
            spots_locations_col.objects.link(empty)


if __name__ == "__main__":
    reset_locations()
    spots_as_empties()
