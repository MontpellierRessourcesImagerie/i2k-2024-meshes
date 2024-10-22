import bpy
import mathutils
from pprint import pprint

def get_total_vertices():
    """
    Returns the total number of vertices in the nuclei.
    """
    collection = bpy.data.collections.get('Nuclei')
    if collection is None:
        print("No Nuclei collection")
        return None
    acc = 0
    n_vertices = [len(obj.data.vertices) for obj in collection.objects if obj.type == 'MESH']
    return sum(n_vertices)
    

def build_kd_tree():
    ttl_vertices = get_total_vertices()
    # Structure to make position query on a points cloud
    kd = mathutils.kdtree.KDTree(ttl_vertices)
    # So we can retrieve the closest object
    vertex_to_object_map = []
    
    collection = bpy.data.collections.get('Nuclei')
    if collection is None:
        print("No Nuclei collection")
        return None
    
    for obj in collection.objects:
        if obj.type == 'MESH':
            mesh = obj.data
            matrix = obj.matrix_world
            for i, vert in enumerate(mesh.vertices):
                kd.insert(matrix @ vert.co, len(vertex_to_object_map))
                vertex_to_object_map.append(obj)
    
    kd.balance()
    return kd, vertex_to_object_map


def get_spots():
    collection = bpy.data.collections.get('Spots')
    if collection is None:
        print("No Spots collection")
        return None
    return [(tuple(obj.location), obj) for obj in collection.objects if obj.type == 'EMPTY']


def spot_to_closest_nucleus():
    kd, mapping = build_kd_tree()
    spots = get_spots()
    counter = {}
    
    for s_co, empty in spots:
        co, index, dist = kd.find(s_co)
        closest_object = mapping[index]
        empty.parent = closest_object
        counter.setdefault(closest_object.name, 0)
        counter[closest_object.name] += 1
    
    pprint(counter)
    
    
spot_to_closest_nucleus()

