import bpy

class SDG_PT_main(bpy.types.Panel):
    bl_label = "Synthetic Data"
    bl_idname = "SDG_PT_main"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Synthetic Data"

    def draw(self, context):
        self.layout.label(text="Hello from my add-on!")

def register():
    bpy.utils.register_class(SDG_PT_main)

def unregister():
    bpy.utils.unregister_class(SDG_PT_main)