import bpy
import random

def random_color():
    return (random.random(), random.random(), random.random(), 1)

def random_lut(collection):
    if collection is None:
        return
    for obj in collection.objects:
        if obj.type != 'MESH':
            continue
        
        mat = bpy.data.materials.new(name="RandomMaterial") # New material
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        for node in nodes:
            nodes.remove(node)
        
        # Create a BSDF with a random color
        principled_node = nodes.new(type="ShaderNodeBsdfPrincipled")
        output_node = nodes.new(type="ShaderNodeOutputMaterial")
        mat.node_tree.links.new(principled_node.outputs['BSDF'], output_node.inputs['Surface'])
        principled_node.inputs['Base Color'].default_value = random_color()

        # Bind the material to the object
        if obj.data.materials:
            obj.data.materials[0] = mat
        else:
            obj.data.materials.append(mat)


collection = bpy.context.collection
random_lut(collection)