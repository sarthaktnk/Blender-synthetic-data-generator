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

        children = list(settings.subjects.children)
        removed = 0
        added = 0

        for i in reversed(range(len(settings.class_list))):
            entry = settings.class_list[i]
            if entry.collection not in children:
                settings.class_list.remove(i)
                removed += 1

        existing = [entry.collection for entry in settings.class_list]
        for child in children:
            if child not in existing:
                entry = settings.class_list.add()
                entry.collection = child
                entry.class_id = settings.next_class_id
                settings.next_class_id += 1
                added += 1

        for entry in settings.class_list:
            entry.name = entry.collection.name

        last = max(0, len(settings.class_list)-1)
        settings.class_index = min(settings.class_index, last)

        self.report({'INFO'}, f"{added} added, {removed} removed")
        return {'FINISHED'}


classes = (
    SDG_OT_refresh_classes,
)