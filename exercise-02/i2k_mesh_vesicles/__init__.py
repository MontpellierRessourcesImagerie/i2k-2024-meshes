bl_info = {
    "name": "Vesicles Tools Panel",
    "blender": (4, 0, 0),
    "category": "3D View",
    "author": "I2K 2024",
    "version": (1, 0, 0),
    "description": "Addon allowing to process semantically segmented nuclei and spots to determine how many vesicles (spots) where absorbed, and from which nucleus each vesicle is.",
}

import bpy

from .random_color import random_lut
from .split_components import split_components
from .spots_to_empties import reset_locations, spots_as_empties
from .cut_and_close import cut_and_close
from .closest_nuclei import spot_to_closest_nucleus
from .filter_by_volume import find_objects_by_volume

### > Functions call have to be done wrapped in an operator.

class OBJECT_OT_split_connected_components(bpy.types.Operator):
    bl_idname = "object.split_connected_components"
    bl_label = "Split connected components"
    bl_description = "Split the selected mesh in connected components"
    
    def execute(self, context):
        # split_components()
        self.report({'INFO'}, "Splitting connected components")
        return {'FINISHED'}


class OBJECT_OT_random_color(bpy.types.Operator):
    bl_idname = "object.random_color"
    bl_label = "Random color"
    bl_description = "Apply a random color to the selected mesh"

    def execute(self, context):
        collection = bpy.context.collection
        # random_lut(collection)
        self.report({'INFO'}, "Applying random color")
        return {'FINISHED'}


class OBJECT_OT_close_cut(bpy.types.Operator):
    bl_idname = "object.close_cut"
    bl_label = "Close cut"
    bl_description = "Close the cut, triangulate faces and split new objects"

    def execute(self, context):
        # cut_and_close()
        self.report({'INFO'}, "Separating nuclei")
        return {'FINISHED'}

# Wrapper pour "Select by volume"
class OBJECT_OT_select_by_volume(bpy.types.Operator):
    bl_idname = "object.select_by_volume"
    bl_label = "Select by volume"
    bl_description = "Select objects by volume"

    volume_min: bpy.props.FloatProperty(name="Volume Min", default=0.0)
    volume_max: bpy.props.FloatProperty(name="Volume Max", default=100.0)

    def execute(self, context):
        bpy.ops.object.select_all(action='DESELECT')
        collection_name = bpy.context.collection.name
        # find_objects_by_volume(collection_name, self.volume_min, 'Smaller than')
        # find_objects_by_volume(collection_name, self.volume_max, 'Bigger than')
        self.report({'INFO'}, f"Selecting objects with volume between {self.volume_min} and {self.volume_max}")
        return {'FINISHED'}


class OBJECT_OT_spots_as_empties(bpy.types.Operator):
    bl_idname = "object.spots_as_empties"
    bl_label = "Spots as empties"
    bl_description = "Create empties at spots locations"

    def execute(self, context):
        # reset_locations()
        # spots_as_empties()
        self.report({'INFO'}, "Creating spots as empties")
        return {'FINISHED'}


class OBJECT_OT_spots_ownership(bpy.types.Operator):
    bl_idname = "object.spots_ownership"
    bl_label = "Spots ownership"
    bl_description = "Determine by which nucleus is owned each spot"

    def execute(self, context):
        # spot_to_closest_nucleus()
        self.report({'INFO'}, "Managing spots ownership")
        return {'FINISHED'}


# We make our panel (looking like a tab) in the viewer's side panel 
# (the one that you can open with N)
class VIEW3D_PT_vesicles_tools_panel(bpy.types.Panel):
    bl_label = "Vesicles tools"
    bl_idname = "VIEW3D_PT_vesicles_tools_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Vesicles Tools'
    
    def draw(self, context):
        layout = self.layout
        
        layout.operator("object.split_connected_components", text="Split connected components")
        layout.operator("object.random_color", text="Random color")
        layout.operator("object.close_cut", text="Close cut")
        
        layout.prop(context.scene, "volume_min", text="Volume Min")
        layout.prop(context.scene, "volume_max", text="Volume Max")
        op = layout.operator("object.select_by_volume", text="Select by volume")
        op.volume_min = context.scene.volume_min
        op.volume_max = context.scene.volume_max
        
        layout.operator("object.spots_as_empties", text="Spots as empties")
        layout.operator("object.spots_ownership", text="Spots ownership")


# In Blender, you need to register your classes if you want them to be loaded in the pool of operators.
def register_props():
    bpy.types.Scene.volume_min = bpy.props.FloatProperty(name="Volume Min", default=0.0)
    bpy.types.Scene.volume_max = bpy.props.FloatProperty(name="Volume Max", default=1.0)

def unregister_props():
    del bpy.types.Scene.volume_min
    del bpy.types.Scene.volume_max

# Enregistrement des classes
classes = (
    OBJECT_OT_split_connected_components,
    OBJECT_OT_random_color,
    OBJECT_OT_close_cut,
    OBJECT_OT_select_by_volume,
    OBJECT_OT_spots_as_empties,
    OBJECT_OT_spots_ownership,
    VIEW3D_PT_vesicles_tools_panel
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    register_props()

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    unregister_props()

if __name__ == "__main__":
    register()
