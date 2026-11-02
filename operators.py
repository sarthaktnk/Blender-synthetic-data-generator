import bpy

class SDG_OT_refresh_classes(bpy.types.Operator):
    bl_idname = "sdg.refresh_classes"
    bl_label = "Refresh"
    bl_description = "Read the child collections of Subjects as classes"

    def execute(self, context):
        settings = context.scene.sdg_settings

        if settings.subjects is None:
            self.report({'WARNING'}, "Pick a Subjects collection first")
            return {'CANCELLED'}

        settings.class_list.clear()
        settings.class_index = 0

        for number, child in enumerate(settings.subjects.children):
            entry = settings.class_list.add()
            entry.name = child.name
            entry.class_id = number
            entry.collection = child

        return {'FINISHED'}


classes = (
    SDG_OT_refresh_classes,
)