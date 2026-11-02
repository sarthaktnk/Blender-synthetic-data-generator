import bpy

class SDG_PanelBase:
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Synthetic Data'

class SDG_PT_setup(SDG_PanelBase, bpy.types.Panel):
    bl_label = "Setup"
    bl_idname = "SDG_PT_setup"

    def draw(self, context):
        settings = context.scene.sdg_settings
        layout = self.layout
        layout.prop(settings, "subjects")
        layout.prop(settings, "environment")
        layout.prop(settings, "camera")

class SDG_PT_placement(SDG_PanelBase, bpy.types.Panel):
    bl_label = "Object Placement"
    bl_idname = "SDG_PT_placement"
    bl_options = {'DEFAULT_CLOSED'}

    def draw_header(self, context):
        self.layout.prop(context.scene.sdg_settings, "use_placement", text="")

    def draw(self, context):
        settings = context.scene.sdg_settings
        layout = self.layout
        layout.active = settings.use_placement
        layout.prop(settings, "pos_range")

classes = (
    SDG_PT_setup,
    SDG_PT_placement,
)