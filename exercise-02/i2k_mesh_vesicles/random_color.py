import bpy
import random

def random_color():
    return (random.random(), random.random(), random.random(), 1)

def random_lut(collection):
    if collection is None:
        return
    used_mats = set()
    for obj in collection.objects:
        if obj.type != 'MESH':
            continue
        mat, principled_node = None, None
        # No material OR two objects sharing the same material
        if (len(obj.material_slots) == 0) or (obj.material_slots[0].material.name in used_mats):
            mat = bpy.data.materials.new(name="RandomMaterial") # New material
            mat.use_nodes = True
            nodes = mat.node_tree.nodes
            for node in nodes:
                nodes.remove(node)
            principled_node = nodes.new(type="ShaderNodeBsdfPrincipled")
            output_node = nodes.new(type="ShaderNodeOutputMaterial")
            mat.node_tree.links.new(principled_node.outputs['BSDF'], output_node.inputs['Surface'])
            # Bind the material to the object
            if obj.data.materials:
                obj.data.materials[0] = mat
            else:
                obj.data.materials.append(mat)
        else:
            mat = obj.material_slots[0].material
            principled_node = mat.node_tree.nodes.get("Principled BSDF")
        
        if (mat is None) or (principled_node is None):
            return
        
        principled_node.inputs['Base Color'].default_value = random_color()
        used_mats.add(mat.name)


if __name__ == "__main__":
    collection = bpy.context.collection
    random_lut(collection)