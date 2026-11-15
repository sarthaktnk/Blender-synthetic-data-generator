import bpy
import random
from .class_list import refresh_classes
from .checks import get_problems
from .spawn import (spawn_instances, clear_spawned, hide_originals, restore_originals)
from .light_list import refresh_lights
from .lights import randomize_lights, restore_lights
from .camera import randomize_camera, restore_camera
from .pipeline import apply_scene, reset_scene
from .render import image_base, render_still


class SDG_OT_render_test(bpy.types.Operator):
    bl_idname = "sdg.render_test"
    bl_label = "Render Test"
    bl_description = "Temporary: render image 0 to the output folder"

    @classmethod
    def poll(cls, context):
        blocking, warnings = get_problems(context.scene.sdg_settings)
        if blocking:
            cls.poll_message_set(blocking[0])
            return False
        return True

    def execute(self, context):
        settings = context.scene.sdg_settings
        apply_scene(context, settings, 0)
        base = image_base(settings, 0)
        render_still(context, settings, base)
        self.report({'INFO'}, f"Rendered to {base}")
        return {'FINISHED'}

class SDG_OT_refresh_lights(bpy.types.Operator):
    bl_idname = "sdg.refresh_lights"
    bl_label = "Refresh"
    bl_description = "Read the lights inside the Environment collection"

    def execute(self, context):
        settings = context.scene.sdg_settings
        if settings.environment is None:
            self.report({'WARNING'}, "Pick an Environment collection first")
            return {'CANCELLED'}
        added, removed = refresh_lights(settings)
        self.report({'INFO'}, f"{added} added, {removed} removed")
        return {'FINISHED'}

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

class SDG_OT_preview(bpy.types.Operator):
    bl_idname = "sdg.preview"
    bl_label = "preview"
    bl_description = "Show the next randomized scene (same seed, same images)"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        blocking, warnings = get_problems(context.scene.sdg_settings)
        if blocking:
            cls.poll_message_set(blocking[0])
            return False
        return True

    def execute(self, context):
        settings = context.scene.sdg_settings
        image = settings.preview_index

        spawned, failed, lights_changed = apply_scene(context, settings, image)
        settings.preview_index += 1

        message = f"Image {image}: {len(spawned)} object(s), {lights_changed} light(s)"
        if failed:
            message += f", {failed} did not fit"
        self.report({'WARNING' if failed else 'INFO'}, message)
        return {'FINISHED'}

class SDG_OT_clear_preview(bpy.types.Operator):
    bl_idname = "sdg.clear_preview"
    bl_label = "Clear"
    bl_description = "TRemove the preview objects and show the originals again"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        reset_scene()
        context.scene.sdg_settings.preview_index = 0
        return {'FINISHED'}


class SDG_OT_new_seed(bpy.types.Operator):
    bl_idname = "sdg.new_seed"
    bl_label = "New Seed"
    bl_description = "Pick a random seed"

    def execute(self, context):
        context.scene.sdg_settings.seed = random.randint(0, 999999)
        return {'FINISHED'}

classes = (
    SDG_OT_render_test,
    SDG_OT_refresh_lights,
    SDG_OT_refresh_classes,
    SDG_OT_preview,
    SDG_OT_clear_preview,
    SDG_OT_generate,
    SDG_OT_new_seed,

)