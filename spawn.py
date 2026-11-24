import bpy
from math import pi, hypot
from .rng import make_rng
from .physics import settle

SPAWN_COLLECTION = "SDG_Spawned"
MAX_TRIES = 50
HIDDEN_MARK = "sdg_preview_hidden"
RENDER_MARK = "sdg_render_hidden"
MAX_LAYERS = 6


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
        for obj in list(entry.collection.all_objects):
            if not obj.hide_render:
                obj.hide_render = True
                obj[RENDER_MARK] = True
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

    for obj in bpy.data.objects:
        if obj.get(RENDER_MARK):
            obj.hide_render = False
            del obj[RENDER_MARK]


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


def find_position(rng, placed, radius, area_length, area_width, spacing):
    """Try to find a free spot. Returns (x,y), or None if nothing fits.
    "placed" is a list of (x, y, radius) tuples for objects already down."""
    half_x = area_length / 2
    half_y = area_width / 2

    for _ in range(MAX_TRIES):
        x = rng.uniform(-half_x, half_x)
        y = rng.uniform(-half_y, half_y)

        if all(hypot(x - px, y-py) >= radius + pr + spacing for px, py, pr in placed):
            return x, y
    return None


def find_start(rng, layers, radius, area_l, area_w, settings, max_radius):

    length = max(0.01, min(area_l, settings.area_length) - 2 * radius)
    width = max(0.01, min(area_w, settings.area_width) -2 * radius)

    for layer in range(MAX_LAYERS):
        while len(layers) <= layer:
            layers.append([])

        position = find_position(rng, layers[layer], radius, length, width, 0.0)
        if position is not None:
            x, y = position
            layers[layer].append((x, y, radius))
            z = (settings.ground_height + settings.drop_height + layer * (2 * max_radius + 0.02) + radius)
            return x, y, z
    return None


def spawn_instances(context, settings, image_index):
    """Create the instances for ONE image.
    Returns (spawned objects, number that did not fit)."""
    clear_spawned()

    holder = bpy.data.collections.new(SPAWN_COLLECTION)
    context.scene.collection.children.link(holder)

    rng = make_rng(settings.seed, image_index, "objects")

    # ---- Phase-1: decide what to place
    requests = []
    for entry in settings.class_list:
        if entry.collection is None:
            continue
        templates = sorted(entry.collection.objects, key=lambda o: o.name)
        if not templates:
            continue

        count = rng.randint(entry.count_min, entry.count_max)

        if entry.use_override:
            area_l, area_w = entry.area_length, entry.area_width
            rot_mode = entry.rotation_mode
            s_min, s_max = entry.scale_min, entry.scale_max
        else:
            area_l, area_w = settings.area_length, settings.area_width
            rot_mode = settings.rotation_mode
            s_min, s_max = settings.scale_min, settings.scale_max

        for n in range(count):
            template = rng.choice(templates)

            requests.append({
                "entry": entry,
                "template": template,
                "required": n < entry.count_min,
                "factor": rng.uniform(s_min, s_max),
                "rotation": pick_rotation(rng, template, rot_mode),
                "area_l": area_l,
                "area_w": area_w,
            })

    # ---- Phase-2: Mixing of objects
    required = [r for r in requests if r["required"]]
    optional = [r for r in requests if not r["required"]]
    rng.shuffle(required)
    rng.shuffle(optional)
    ordered = required + optional

    # ---- Phase-3: placing objects

    physics = settings.use_placement and settings.placement_mode == 'PHYSICS'
    layers = []

    max_radius = max(
        (max(r["template"].dimensions) * r["factor"] / 2 for r in ordered),
        default=0.0,
    )

    spawned = []
    placed = []
    failed = 0

    for req in ordered:
        entry = req["entry"]
        template = req["template"]

        obj = template.copy()
        obj.name = f"{entry.name}_inst"
        obj["sdg_class_id"] = entry.class_id

        if HIDDEN_MARK in obj:
            del obj[HIDDEN_MARK]
        if RENDER_MARK in obj:
            obj.hide_render = False
            del obj[RENDER_MARK]

        if settings.use_placement:
            obj.scale = template.scale * req["factor"]
            obj.rotation_euler = req["rotation"]

            radius = max(obj.dimensions) / 2
            if physics:
                position = find_start(rng, layers, radius, req["area_l"], req["area_w"], settings, max_radius)
            else:
                position = find_position(rng, placed, radius, req["area_l"], req["area_w"], settings.spacing)

            if position is None:
                bpy.data.objects.remove(obj)
                failed += 1
                continue

            if physics:
                obj.location = position
            else:
                x, y = position
                obj.location = (x, y, template.location.z)
                placed.append((x, y, radius))

        holder.objects.link(obj)
        spawned.append(obj)

    if physics and spawned:
        settle(context, settings, spawned)

    return spawned, failed