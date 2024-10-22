bl_info = {
    "name": "My Custom Add-on",
    "blender": (2, 80, 0),  # Assure-toi que ta version est correcte
    "category": "Object",
    "description": "Un add-on avec quatre boutons qui exécutent des fonctions",
}

import bpy

# Fonction 1
def fonction_1():
    print("Fonction 1 exécutée")

# Fonction 2
def fonction_2():
    print("Fonction 2 exécutée")

# Fonction 3
def fonction_3():
    print("Fonction 3 exécutée")

# Fonction 4
def fonction_4():
    print("Fonction 4 exécutée")

# Panneau UI
class OBJECT_PT_CustomPanel(bpy.types.Panel):
    bl_label = "Custom Add-on Panel"
    bl_idname = "OBJECT_PT_custom_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Custom Panel'

    def draw(self, context):
        layout = self.layout

        # Boutons
        row = layout.row()
        row.operator("object.fonction_1_op", text="Lancer Fonction 1")
        
        row = layout.row()
        row.operator("object.fonction_2_op", text="Lancer Fonction 2")
        
        row = layout.row()
        row.operator("object.fonction_3_op", text="Lancer Fonction 3")
        
        row = layout.row()
        row.operator("object.fonction_4_op", text="Lancer Fonction 4")

# Opérateurs
class OBJECT_OT_Fonction1(bpy.types.Operator):
    bl_label = "Fonction 1"
    bl_idname = "object.fonction_1_op"

    def execute(self, context):
        fonction_1()
        return {'FINISHED'}

class OBJECT_OT_Fonction2(bpy.types.Operator):
    bl_label = "Fonction 2"
    bl_idname = "object.fonction_2_op"

    def execute(self, context):
        fonction_2()
        return {'FINISHED'}

class OBJECT_OT_Fonction3(bpy.types.Operator):
    bl_label = "Fonction 3"
    bl_idname = "object.fonction_3_op"

    def execute(self, context):
        fonction_3()
        return {'FINISHED'}

class OBJECT_OT_Fonction4(bpy.types.Operator):
    bl_label = "Fonction 4"
    bl_idname = "object.fonction_4_op"

    def execute(self, context):
        fonction_4()
        return {'FINISHED'}

# Enregistrement des classes
classes = [
    OBJECT_PT_CustomPanel,
    OBJECT_OT_Fonction1,
    OBJECT_OT_Fonction2,
    OBJECT_OT_Fonction3,
    OBJECT_OT_Fonction4
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
