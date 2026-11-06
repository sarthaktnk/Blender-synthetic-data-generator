import bpy
from .rng import make_rng

SPAWN_COLLECTION = "SDG_Spawned"


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


def spawn_instances(context, settings, image_index):
    """Create the instances for ONE image. Returns the list of new objects."""
    clear_spawned()

    holder = bpy.data.collections.new(SPAWN_COLLECTION)
    context.scene.collection.children.link(holder)

    rng = make_rng(settings.seed, image_index, "objects")
    spawned = []
    x = 0.0

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
            holder.objects.link(obj)
            obj.location = (x, 3.0, 3.0)
            x += 0.5
            spawned.append(obj)

    return spawned