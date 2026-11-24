from .spawn import spawn_instances, hide_originals, restore_originals, clear_spawned
from .lights import randomize_lights, restore_lights
from .camera import randomize_camera, restore_camera
from .materials import apply_material_rules

def apply_scene(context, settings, image_index):
    """Build the scene for ONE image. Returns (spawned, failed, lights_changed)."""
    spawned, failed = spawn_instances(context, settings, image_index)
    apply_material_rules(settings, spawned, image_index)
    hide_originals(settings)
    lights_changed = randomize_lights(settings, image_index)
    randomize_camera(settings, image_index)
    return spawned, failed, lights_changed


def reset_scene():
    """Undo everything apply_scene did."""
    clear_spawned()
    restore_originals()
    restore_lights()
    restore_camera()