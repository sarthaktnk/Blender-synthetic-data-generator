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


class SDG_UL_overrides(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row(align=True)
        row.label(text=item.name, icon='OUTLINER_COLLECTION')
        side = row.row()
        side.alignment = 'RIGHT'
        side.label(text="Custom" if item.use_override else "Default")


class SDG_UL_lights(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row(align=True)
        row.prop(item, "use", text="")
        row.label(text=item.name, icon='LIGHT')
        side = row.row()
        side.alignment = 'RIGHT'
        side.label(text=item.obj.data.type.title() if item.obj else "?")

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
        layout.label(text="Class overrrides")
        layout.template_list(
            "SDG_UL_overrides", "",
            settings, "class_list",
            settings, "class_index",
            rows=3,
        )

        if settings.class_list:
            entry = settings.class_list[settings.class_index]
            layout.prop(entry, "use_override", text=f"Override defaults for '{entry.name}'")
            if entry.use_override:
                row = layout.row(align=True)
                row.prop(entry, "area_length")
                row.prop(entry, "area_width")
                layout.prop(entry, "rotation_mode")
                row = layout.row(align=True)
                row.prop(entry, "scale_min")
                row.prop(entry, "scale_max")


class SDG_PT_lights(SDG_PanelBase, bpy.types.Panel):
    bl_label = "Lights"
    bl_idname = "SDG_PT_lights"
    bl_options = {'DEFAULT_CLOSED'}

    def draw_header(self, context):
        self.layout.prop(context.scene.sdg_settings, "use_lights", text="")

    def draw(self, context):
        settings = context.scene.sdg_settings
        layout = self.layout
        layout.active = settings.use_lights

        layout.label(text="Found in Environment")
        rows = max(2, min(len(settings.light_list), 6))
        layout.template_list(
            "SDG_UL_lights", "",
            settings, "light_list",
            settings, "light_index",
            rows=rows,
        )
        layout.operator("sdg.refresh_lights", icon='FILE_REFRESH')

        if settings.light_list:
            light = settings.light_list[settings.light_index]
            layout.separator()
            layout.label(text=f"Settings for '{light.name}'")

            col = layout.column()
            col.active = light.use
            col.label(text="Intensity x")
            row = col.row(align=True)
            row.prop(light, "intensity_min")
            row.prop(light, "intensity_max")
            col.label(text="Color temperature (K)")
            row = col.row(align=True)
            row.prop(light, "temp_min")
            row.prop(light, "temp_max")
            col.prop(light, "off_chance", slider=True)


class SDG_PT_camera(SDG_PanelBase, bpy.types.Panel):
    bl_label = "Camera"
    bl_idname = "SDG_PT_camera"
    bl_options = {'DEFAULT_CLOSED'}

    def draw_header(self, context):
        self.layout.prop(context.scene.sdg_settings, "use_camera", text="")

    def draw(self, context):
        settings = context.scene.sdg_settings
        layout = self.layout
        layout.active = settings.use_camera

        layout.prop(settings, "camera_target")
        layout.label(text="Blank = world origin. any object works, even an Empty.")

        def pair(title, low, high):
            layout.label(text=title)
            row = layout.row(align=True)
            row.prop(settings, low)
            row.prop(settings, high)

        pair("Distance", "distance_min", "distance_max")
        pair("Azimuth", "azimuth_min", "azimuth_max")
        pair("Elevation", "elevation_min", "elevation_max")
        pair("Focal length", "focal_min", "focal_max")

        layout.prop(settings, "use_dof")
        col = layout.column()
        col.active = settings.use_dof
        row = col.row(align=True)
        row.prop(settings, "aperture_min")
        row.prop(settings, "aperture_max")


class SDG_PT_output(SDG_PanelBase, bpy.types.Panel):
    bl_label = "Output"
    bl_idname = "SDG_PT_output"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        settings = context.scene.sdg_settings
        layout = self.layout

        layout.prop(settings, "num_images")

        row = layout.row(align=True)
        row.prop(settings, "seed")
        row.operator("sdg.new_seed", text="", icon='FILE_REFRESH')

        row = layout.row(align=True)
        row.prop(settings, "res_x")
        row.prop(settings, "res_y")

        layout.prop(settings, "image_format")
        layout.prop(settings, "output_dir")


class SDG_PT_run(SDG_PanelBase, bpy.types.Panel):
    bl_label = "Run"
    bl_idname = "SDG_PT_run"

    def draw(self, context):
        layout = self.layout
        settings = context.scene.sdg_settings
        blocking, warnings = get_problems(settings)

        for message in blocking:
            layout.label(text=message, icon='ERROR')
        for message in warnings:
            layout.label(text=message, icon='INFO')

        layout.label(text=f"Next preview: image {settings.preview_index}")
        row = layout.row(align=True)
        row.operator("sdg.preview", icon='FILE_REFRESH')
        row.operator("sdg.clear_preview", icon='X')
        layout.operator("sdg.render_test", icon='RENDER_STILL')

        row = layout.row()
        row.scale_y = 1.8
        row.operator("sdg.generate", icon='RENDER_ANIMATION')

classes = (
    SDG_UL_classes,
    SDG_UL_overrides,
    SDG_UL_lights,
    SDG_PT_setup,
    SDG_PT_placement,
    SDG_PT_lights,
    SDG_PT_camera,
    SDG_PT_output,
    SDG_PT_run,
)