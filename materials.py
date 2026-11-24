from .rng import make_rng
from .pools import find_pool


def class_id_of(settings, collection):
    """The class ID that belongs to a class collection, or None."""
    for entry in settings.class_list:
        if entry.collection == collection:
            return entry.class_id
    return None


def assign_material(obj, material, slot_mode):
    """Give ONE object its own material. Returns false if it has no slot."""
    slots = list(obj.material_slots)
    if not slots:
        return False
    if slot_mode == 'FIRST':
        slots = slots[:1]
    for slot in slots:
        slot.link = 'OBJECT'
        slot.material = material
    return True


def apply_material_rules(settings, spawned, image_index):
    """Apply the class rules to this image's spawned objects.
    Returns how many objects got a new material."""
    if not settings.use_materials or not settings.rules:
        return 0

    rng = make_rng(settings.seed, image_index, "materials")
    changed = 0

    for rule in settings.rules:
        if rule.target_type != 'CLASS':
            continue

        pool = find_pool(settings, rule.pool_name)
        materials = [item.material for item in pool.materials if item.material] if pool else []
        class_id = class_id_of(settings, rule.target_class)
        if not materials or class_id is None:
            continue

        for obj in spawned:
            if obj.get("sdg_class_id") != class_id:
                continue

            roll = rng.uniform(0, 100)
            material = rng.choice(materials)
            if roll >= rule.chance:
                continue

            if assign_material(obj, material, rule.slot_mode):
                changed += 1

    return changed