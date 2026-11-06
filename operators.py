import bpy
from .class_list import refresh_classes
from .checks import get_problems
from .spawn import spawn_instances, clear_spawned

class SDG_OT_refresh_classes(bpy.types.Operator):
    bl_idname = "sdg.refresh_classes"
    bl_label = "Refresh"
    bl_description = "Read the child collections of Subjects as classes"

    def execute(self, context):
        settings = context.scene.sdg_settings

        if settings.subjects is None:
            self.report({'WARNING'}, "Pick a Subjects collection first")
            return {'CANCELLED'}

        added, removed = refresh_classes(settings)

        self.report({'INFO'}, f"{added} added, {removed} removed")
        return {'FINISHED'}

class SDG_OT_generate(bpy.types.Operator):
    bl_idname = "sdg.generate"
    bl_label = "Generate Dataset"
    bl_description = "Render the dataset"

    @classmethod
    def poll(cls, context):
        blocking, warnings =  get_problems(context.scene.sdg_settings)
        if blocking:
            cls.poll_message_set(blocking[0])
            return False
        return True

    def execute(self, context):
        self.report({'INFO'}, "Generate isn't built yet, but the button works")
        return {'FINISHED'}

class SDG_OT_spawn_test(bpy.types.Operator):
    bl_idname = "sdg.spawn_test"
    bl_label = "Spawn Test"
    bl_description = "Temporary: spawn instances for image 0"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        blocking, warnings = get_problems(context.scene.sdg_settings)
        return not blocking

    def execute(self, context):
        spawned = spawn_instances(context, context.scene.sdg_settings, 0)
        self.report({'INFO'}, f"Spawned {len(spawned)} objects(s)")
        return {'FINISHED'}

class SDG_OT_clear_spawned(bpy.types.Operator):
    bl_idname = "sdg.clear_spawned"
    bl_label = "Clear Spawned"
    bl_description = "Temporary: delete everything the add-on spawned"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        removed = clear_spawned()
        self.report({'INFO'}, f"Removed {removed} object(s)")
        return {'FINISHED'}

classes = (
    SDG_OT_refresh_classes,
    SDG_OT_generate,
    SDG_OT_spawn_test,
    SDG_OT_clear_spawned,
)