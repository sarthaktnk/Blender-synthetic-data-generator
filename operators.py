import os
import bpy
import random
import json
from .class_list import refresh_classes
from .checks import get_problems
from .spawn import (spawn_instances, clear_spawned, hide_originals, restore_originals)
from .light_list import refresh_lights
from .lights import randomize_lights, restore_lights
from .camera import randomize_camera, restore_camera
from .pipeline import apply_scene, reset_scene
from .render import image_base, render_still, render_settings, image_path, debug_path, label_path
from .labels import write_yolo_file, write_classes, class_names, write_yaml
from .split import count_val, split_of
from .annotations import compute_boxes, save_debug_image
from .files import clear_dataset
from .stats import new_stats, add_image
from .pools import unique_pool_name

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

        try:
            folder = bpy.path.abspath(settings.output_dir)
            if settings.clear_old:
                removed = clear_dataset(folder)
                if removed:
                    self.report({'INFO'}, f"Removed {removed} old dataset file(s)")
            write_classes(os.path.join(folder, "classes.txt"), class_names(settings))
            has_val = count_val(settings.num_images, settings.val_split) > 0
            write_yaml(os.path.join(folder, "dataset.yaml"), class_names(settings), has_val)
        except OSError as error:
            self.report({'ERROR'}, f"Can't write to the output folder: {error}")
            return {'CANCELLED'}

        self._stats = new_stats()
        settings.last_stats = ""

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
            with render_settings(context, settings):
                spawned, failed, lights = apply_scene(context, settings, self._index)
                boxes = compute_boxes(context, settings, spawned)
                render_still(context, settings, image_base(settings, self._index))

            write_yolo_file(label_path(settings, self._index), boxes)
            add_image(self._stats, boxes, len(spawned), failed, split_of(self._index, settings.val_split))
            settings.last_stats = json.dumps(self._stats)
            if settings.save_debug:
                save_debug_image(
                    image_path(settings, self._index), boxes,
                    debug_path(settings, self._index)
                )
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


class SDG_OT_pool_add(bpy.types.Operator):
    bl_idname = "sdg.pool_add"
    bl_label = "Add Pool"
    bl_description = "Create a new, empty pool"

    def execute(self, context):
        settings = context.scene.sdg_settings
        pool = settings.pools.add()
        pool.name = unique_pool_name(settings)
        settings.pool_index = len(settings.pools) - 1
        return {'FINISHED'}


class SDG_OT_pool_remove(bpy.types.Operator):
    bl_idname = "sdg.pool_remove"
    bl_label = "Remove"
    bl_description = "Remove the selected pool"

    @classmethod
    def poll(cls, context):
        return len(context.scene.sdg_settings.pools) > 0

    def execute(self, context):
        settings = context.scene.sdg_settings
        index = settings.pool_index
        settings.pools.remove(index)
        settings.pool_index = max(0, min(index, len(settings.pools) - 1))
        return {'FINISHED'}


class SDG_OT_pool_material_remove(bpy.types.Operator):
    bl_idname = "sdg.pool_material_remove"
    bl_label = "Remove Material"
    bl_description = "Take the selected material out of this pool"

    @classmethod
    def poll(cls, context):
        settings = context.scene.sdg_settings
        return bool(settings.pools) and bool(settings.pools[settings.pool_index].materials)

    def execute(self, context):
        settings = context.scene.sdg_settings
        pool = settings.pools[settings.pool_index]
        index = pool.material_index
        pool.materials.remove(index)
        pool.material_index = max(0, min(index, len(pool.materials) - 1))
        return {'FINISHED'}


class SDG_OT_rule_add(bpy.types.Operator):
    bl_idname = "sdg.rule_add"
    bl_label = "Add Rule"
    bl_description = "Create a material rule"

    def execute(self, context):
        settings = context.scene.sdg_settings
        rule = settings.rules.add()

        if settings.class_list:
            rule.target_class = settings.class_list[0].collection
        if settings.pools:
            rule.pool_name = settings.pools[settings.pool_index].name
        settings.rule_index = len(settings.rules) - 1
        return {'FINISHED'}


class SDG_OT_rule_remove(bpy.types.Operator):
    bl_idname = "sdg.rule_remove"
    bl_label = "Remove"
    bl_description = "Remove the selected rule"

    @classmethod
    def poll(cls, context):
        return len(context.scene.sdg_settings.rules) > 0

    def execute(self, context):
        settings = context.scene.sdg_settings
        index = settings.rule_index
        settings.rules.remove(index)
        settings.rule_index = max(0, min(index, len(settings.rules) - 1))
        return {'FINISHED'}
    
classes = (
    SDG_OT_refresh_lights,
    SDG_OT_refresh_classes,
    SDG_OT_preview,
    SDG_OT_clear_preview,
    SDG_OT_generate,
    SDG_OT_new_seed,
    SDG_OT_pool_add,
    SDG_OT_pool_remove,
    SDG_OT_pool_material_remove,
    SDG_OT_rule_add,
    SDG_OT_rule_remove
)