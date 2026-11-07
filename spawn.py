import bpy
from math import pi, hypot
from .rng import make_rng

SPAWN_COLLECTION = "SDG_Spawned"
MAX_TRIES = 50
HIDDEN_MARK = "sdg_preview_hidden"


def clear_spawned():
    """Delete every spawned object and the holder collection.
    Returns how many objects were removed."""
    holder = bpy.data.collections.get(SPAWN_COLLECTION)
    if holder is None:
        return 0

    objects = list(holder.objects)
    for obj in objects:
        bpy.data.objects.remove(obj, do_unlink=True)
    bpy.data.collections.remove(holder)
    return len(objects)

def hide_originals(settings):
    """Hide the template objects in the viewport, and mark the ones we hid."""
    for entry in settings.class_list:
        if entry.collection is None:
            continue
        for obj in entry.collection.all_objects:
            try:
                if obj.visible_get():
                    obj.hide_set(True)
                    obj[HIDDEN_MARK] = True
            except RuntimeError:
                pass


def restore_originals():
    """Unhide everything we hid, and remove the markers."""
    for obj in bpy.data.objects:
        if obj.get(HIDDEN_MARK):
            try:
                obj.hide_set(False)
            except RuntimeError:
                pass
            del obj[HIDDEN_MARK]


def pick_rotation(rng, template, mode):
    """Return (x, y, z) angles in radians for the chosen rotation mode."""
    tx, ty, tz = template.rotation_euler
    if mode == 'ANY':
        return (rng.uniform(0, 2*pi), rng.uniform(0, 2*pi), rng.uniform(0, 2*pi))
    if mode == 'UPRIGHT':
        return (tx, ty, rng.uniform(0, 2*pi))
    if mode == 'FLAT':
        return (tx + pi/2, ty, rng.uniform(0, 2*pi))
    return (tx, ty, tz)


def find_position(rng, placed, radius, settings):
    """Try to find a free spot. Returns (x,y), or None if nothing fits.
    "placed" is a list of (x, y, radius) tuples for objects already down."""
    half_x = settings.area_length / 2
    half_y = settings.area_width / 2

    for _ in range(MAX_TRIES):
        x = rng.uniform(-half_x, half_x)
        y = rng.uniform(-half_y, half_y)

        if all(hypot(x - px, y-py) >= radius + pr + settings.spacing for px, py, pr in placed):
            return x, y
    return None


def spawn_instances(context, settings, image_index):
    """Create the instances for ONE image.
    Returns (spawned objects, number that did not fit)."""
    clear_spawned()

    holder = bpy.data.collections.new(SPAWN_COLLECTION)
    context.scene.collection.children.link(holder)

    rng = make_rng(settings.seed, image_index, "objects")
    spawned = []
    placed = []
    failed = 0

    for entry in settings.class_list:
        if entry.collection is None:
            continue
        templates = sorted(entry.collection.objects, key=lambda o: o.name)
        if not templates:
            continue

        count = rng.randint(entry.count_min, entry.count_max)

        for _ in range(count):
            template = rng.choice(templates)
            obj = template.copy()
            obj.name = f"{entry.name}_inst"
            obj["sdg_class_id"] = entry.class_id

            if HIDDEN_MARK in obj:
                del obj[HIDDEN_MARK]

            if settings.use_placement:
                factor = rng.uniform(settings.scale_min, settings.scale_max)
                obj.scale = template.scale * factor
                obj.rotation_euler = pick_rotation(rng, template, settings.rotation_mode)

                radius = max(obj.dimensions) / 2
                position = find_position(rng, placed, radius, settings)

                if position is None:
                    bpy.data.objects.remove(obj)
                    failed += 1
                    continue

                x, y = position
                obj.location = (x, y, template.location.z)
                placed.append((x, y, radius))

            holder.objects.link(obj)
            spawned.append(obj)

    return spawned, failed  