import bpy
import mathutils
import json

def get_total_vertices():
    """
    Returns the total number of vertices in each nucleus.
    """
    collection = bpy.data.collections.get('Nuclei')
    if collection is None:
        print("No Nuclei collection")
        return None
    acc = 0
    n_vertices = [len(obj.data.vertices) for obj in collection.objects if obj.type == 'MESH']
    return sum(n_vertices)
    

def build_kd_tree():
    """
    Builds a KD-Tree containing the vertices of all nuclei present in the collection.
    Returns the KD Tree, and the array of correspondance with objects.
    """
    ttl_vertices = get_total_vertices()
    kd = mathutils.kdtree.KDTree(ttl_vertices)
    vertex_to_object_map = [] # So we can retrieve the closest object
    normals = [] # Vertices normals, for I/O test
    
    collection = bpy.data.collections.get('Nuclei')
    if collection is None:
        print("No Nuclei collection")
        return None
    
    for obj in collection.objects:
        if obj.type != 'MESH':
            continue
        mesh = obj.data
        matrix = obj.matrix_world
        for i, vert in enumerate(mesh.vertices):
            normals.append(vert.normal)
            kd.insert(matrix @ vert.co, len(vertex_to_object_map))
            vertex_to_object_map.append(obj)
    
    kd.balance()
    return kd, vertex_to_object_map, normals


def get_spots():
    collection = bpy.data.collections.get('Spots-locations')
    if collection is None:
        print("No Spots collection")
        return None
    return [(tuple(obj.location), obj) for obj in collection.objects if obj.type == 'EMPTY']


def counter_to_json(data_dict):
    json_str = json.dumps(data_dict, indent=4)
    text_name = "Results_JSON"
    # Remove prevouis attempt
    if text_name in bpy.data.texts:
        bpy.data.texts.remove(bpy.data.texts[text_name])
    text_block = bpy.data.texts.new(name=text_name)
    text_block.write(json_str)


def spot_to_closest_nucleus():
    """
    Loops through the spots (empties) and searches for the closest vertex.
    Sets the parent of each spot to its owner nuclei.
    Counts the number of spots per nuclei
    """
    kd, mapping, normals = build_kd_tree()
    spots = get_spots()
    counter = {}
    
    for rank, (s_co, empty) in enumerate(spots):
        co, index, dist = kd.find(s_co)
        closest_object = mapping[index]
        v1 = mathutils.Vector(co) - closest_object.location # origin to surface point
        v2 = empty.location - mathutils.Vector(co) # vertex to empty
        v1.normalize()
        v2.normalize()
        inside = v1.dot(v2) <= 0
        empty.name = closest_object.name + "-" + str(rank)
        empty.empty_display_type = "SPHERE" if inside else "CUBE"
        counter.setdefault(closest_object.name, {'in': 0, 'out': 0})
        counter[closest_object.name]['in' if inside else 'out'] += 1
    counter_to_json(counter)
    

if __name__ == "__main__":
    spot_to_closest_nucleus()

