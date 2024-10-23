import bpy
import bmesh
import mathutils

def _process_curvature(obj, attribute_name):
    mesh = obj.data
    bm = bmesh.new()
    bm.from_mesh(mesh)

    if bm.verts.layers.float.get(attribute_name):
        curvature_layer = bm.verts.layers.float[attribute_name]
    else:
        curvature_layer = bm.verts.layers.float.new(attribute_name)
    
    for vert in bm.verts:
        if len(vert.link_edges) == 0:
            continue
        angle_sum = 0.0
        for edge in vert.link_edges:
            faces = edge.link_faces
            if len(faces) == 2:
                normal1 = faces[0].normal
                normal2 = faces[1].normal
                angle = normal1.angle(normal2)
                angle_sum += angle

        avg_curvature = angle_sum / len(vert.link_edges)
        vert[curvature_layer] = avg_curvature
    
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()

def process_curvature():
    attribute_name = "vertex_curvature"
    bpy.ops.object.mode_set(mode='OBJECT')
    for obj in bpy.data.collections['Nuclei'].objects:
        if obj.type != 'MESH':
            continue
        _process_curvature(obj, attribute_name)


if __name__ == "__main__":
    process_curvature()