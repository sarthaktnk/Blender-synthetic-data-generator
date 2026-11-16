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
    bl_description = "Render the whole dataset. Press Esc to cancel between images"

    running = False
    _timer = None
    _index = 0

    @classmethod
    def poll(cls, context):
        if cls.running:
            cls.poll_message_set("A run is already in progress")
            return False
        blocking, warnings = get_problems(context.scene.sdg_settings)
        if blocking:
            cls.poll_message_set(blocking[0])
            return False
        return True

    def invoke(self, context, event):
        settings = context.scene.sdg_settings
        wm = context.window_manager

        self.index = 0
        self._timer = wm.event_timer_add(0.1, window=context.window)
        wm.progress_begin(0, settings.num_images)
        wm.modal_handler_add(self)
        SDG_OT_generate.running = True
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        settings = context.scene.sdg_settings

        if event.type == 'ESC' and event.value == 'PRESS':
            return self.finish(context, f"Cancelled after {self._index} image(s)", cancelled=True)

        if event.type != 'TIMER':
            return {'PASS_THROUGH'}

        if self._index >= settings.num_images:
            return self.finish(context, f"Done: {self._index} image(s) rendered")

        try:
            apply_scene(context, settings, self._index)
            render_still(context, settings, image_base(settings, self._index))
        except Exception as error:
            return self.finish(context, f"Stopped by an error: {error}", cancelled=True, level='ERROR')

        self._index += 1
        context.window_manager.progress_update(self._index)
        return {'RUNNING_MODAL'}

    def finish(self, context, message, cancelled=False, level='INFO'):
        wm = context.window_manager
        wm.event_timer_remove(self._timer)
        wm.progress_end()
        reset_scene()
        SDG_OT_generate.running = False
        self.report({level}, message)
        return {'CANCELLED'} if cancelled else {'FINISHED'}
    

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
    SDG_OT_refresh_lights,
    SDG_OT_refresh_classes,
    SDG_OT_preview,
    SDG_OT_clear_preview,
    SDG_OT_generate,
    SDG_OT_new_seed,
)