import bpy # type: ignore
from bpy.props import FloatProperty, PointerProperty

class SDG_Settings(bpy.types.PropertyGroup):
    pos_range: FloatProperty(
        name="Position Range",
        default=2.0,
        min=0.0,
        max=10.0
    )

class SDG_PT_main(bpy.types.Panel):
    bl_label = "Synthetic Data"
    bl_idname = "SDG_PT_main"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Synthetic Data"

    def draw(self, context):
        settings = context.scene.sdg_settings
        self.layout.prop(settings, "pos_range")

def register():
    bpy.utils.register_class(SDG_Settings)
    bpy.utils.register_class(SDG_PT_main)
    bpy.types.Scene.sdg_settings = PointerProperty(type=SDG_Settings)

def unregister():
    del bpy.types.Scene.sdg_settings
    bpy.utils.unregister_class(SDG_PT_main)
    bpy.utils.unregister_class(SDG_Settings)