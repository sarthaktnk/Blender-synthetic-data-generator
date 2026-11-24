import json
import bpy
from .rng import make_rng
from .pools import find_pool

MARK = "sdg_orig_materials"


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


def remember_materials(obj):
    """Save what every slot holds, the first time only."""
    if MARK in obj:
        return
    obj[MARK] = json.dumps({
        "links": [slot.link for slot in obj.material_slots],
        "names": [slot.material.name if slot.material else "" for slot in obj.material_slots],
    })


def restore_materials():
    """Put every slot back the way it was, and remove the markers."""
    for obj in bpy.data.objects:
        raw = obj.get(MARK)
        if raw is None:
            continue
        saved = json.loads(raw)
        for slot, link, name in zip(obj.material_slots, saved["links"], saved["names"]):
            material = bpy.data.materials.get(name) if name else None
            slot.link = 'OBJECT'
            slot.material = material if link == 'OBJECT' else None
            slot.link = link
        del obj[MARK]


def rule_objects(settings, rule, spawned):
    """The objects one rule should change."""
    if rule.target_type == 'CLASS':
        class_id = class_id_of(settings, rule.target_class)
        return [o for o in spawned
                if class_id is not None and o.get("sdg_class_id") == class_id]

    if rule.target_type == 'COLLECTION':
        target = rule.target_collection
        objects = list(target.all_objects) if target else []
    else:
        objects = [rule.target_object] if rule.target_object else []

    # Never touch our own spawned copies through these rules.
    return sorted((o for o in objects if "sdg_class_id" not in o),
                  key=lambda o: o.name)


def apply_material_rules(settings, spawned, image_index):
    """Apply the class rules to this image's spawned objects.
    Returns how many objects got a new material."""

    restore_materials()
    
    print("spawned:", len(spawned), sorted({o.get("sdg_class_id") for o in spawned}))

    if not settings.use_materials:
        return 0

    changed = 0

    for rule_index, rule in enumerate(settings.rules):
        pool = find_pool(settings, rule.pool_name)
        materials = [item.material for item in pool.materials if item.material] if pool else []
        print("  rule class id:", class_id_of(settings, rule.target_class) if rule.target_type == 'CLASS' else "-")
        objects = rule_objects(settings, rule, spawned)
        print(f"rule {rule_index}: {rule.target_type}, {len(materials)} material(s), {len(objects)} object(s)")
        if not materials or not objects:
            continue

        rng = make_rng(settings.seed, image_index, f"materials-{rule_index}")

        for obj in objects:
            roll = rng.uniform(0, 100)
            material = rng.choice(materials)
            if roll >= rule.chance:
                continue

            if rule.target_type != 'CLASS':
                remember_materials(obj)
            if assign_material(obj, material, rule.slot_mode):
                changed += 1

    return changed