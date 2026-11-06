import bpy
from .checks import get_problems

class SDG_UL_classes(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row(align=True)
        count = len(item.collection.all_objects) if item.collection else 0
        icon = 'OUTLINER_COLLECTION' if count > 0 else 'ERROR'

        row.label(text=item.name, icon=icon)
        row.label(text=f"ID {item.class_id}")
        row.label(text=f"{item.count_min}-{item.count_max}")

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
        layout.separator()
        layout.template_list(
            "SDG_UL_classes", "",
            settings, "class_list",
            settings, "class_index",
            rows=3,
        )
        layout.operator("sdg.refresh_classes", icon='FILE_REFRESH')
        if settings.class_list:
            entry = settings.class_list[settings.class_index]
            row = layout.row(align=True)
            row.prop(entry, "count_min")
            row.prop(entry, "count_max")
            if entry.collection:
                n = len(entry.collection.all_objects)
                layout.label(text=f"{n} object(s) in this class")

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
        layout.label(text="Defaults for all classes")

        row = layout.row(align=True)
        row.prop(settings, "area_length")
        row.prop(settings, "area_width")

        layout.prop(settings, "spacing", slider=True)
        layout.prop(settings, "rotation_mode")

        row = layout.row(align=True)
        row.prop(settings, "scale_min")
        row.prop(settings, "scale_max")

        layout.separator()
        layout.label(text="Temporary test buttons")
        layout.operator("sdg.spawn_test")
        layout.operator("sdg.clear_spawned")

class SDG_PT_output(SDG_PanelBase, bpy.types.Panel):
    bl_label = "Output"
    bl_idname = "SDG_PT_output"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        settings = context.scene.sdg_settings
        self.layout.prop(settings, "num_images")
        self.layout.prop(settings, "seed")


class SDG_PT_run(SDG_PanelBase, bpy.types.Panel):
    bl_label = "Run"
    bl_idname = "SDG_PT_run"

    def draw(self, context):
        layout = self.layout
        blocking, warnings = get_problems(context.scene.sdg_settings)

        for message in blocking:
            layout.label(text=message, icon='ERROR')
        for message in warnings:
            layout.label(text=message, icon='INFO')

        row = layout.row()
        row.scale_y = 1.8
        row.operator("sdg.generate", icon='RENDER_ANIMATION')

classes = (
    SDG_UL_classes,
    SDG_PT_setup,
    SDG_PT_placement,
    SDG_PT_output,
    SDG_PT_run,
)