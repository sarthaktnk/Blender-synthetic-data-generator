import os
import bpy
from .split import count_val
from .files import has_dataset_files
from .pools import find_pool, rule_target

def once(messages, text):
    if text not in messages:
        messages.append(text)


def get_problems(settings):
    blocking = []
    warnings = []

    if settings.subjects is None:
        blocking.append("Pick a Subjects collection")
    elif len(settings.class_list) == 0:
        blocking.append("Subjects has no child collections")
    else:
        for entry in settings.class_list:
            if entry.collection is None or len(entry.collection.all_objects) == 0:
                blocking.append(f"Class '{entry.name}' is empty")
            if entry.count_min > entry.count_max:
                blocking.append(f"Class '{entry.name}': Min is above Max")
            if (settings.use_placement and entry.use_override and entry.scale_min > entry.scale_max):
                blocking.append(f"Class '{entry.name}': Scale Min is above Max")

        if all(entry.count_max == 0 for entry in settings.class_list):
            blocking.append("All class counts are 0")

    if settings.camera is None:
        blocking.append("Pick a Camera")

    if settings.environment is None:
        warnings.append("No Environment picked")
    else:
        has_light = any(obj.type == 'LIGHT' for obj in settings.environment.all_objects)
        if not has_light:
            warnings.append("Environment has no lights")
            
    if settings.use_placement and settings.scale_min > settings.scale_max:
        blocking.append("Scale: Min is above Max")

    if settings.use_lights:
        for light in settings.light_list:
            if not light.use:
                continue
            if light.intensity_min > light.intensity_max:
                blocking.append(f"Light '{light.name}': intensity Min is above Max")
            if light.temp_min > light.temp_max:
                blocking.append(f"Light '{light.name}': temperature Min is above Max")

    if settings.use_camera:
        ranges = [
            ("Distance", settings.distance_min, settings.distance_max),
            ("Azimuth", settings.azimuth_min, settings.azimuth_max),
            ("Elevation", settings.elevation_min, settings.elevation_max),
            ("Focal length", settings.focal_min, settings.focal_max),
        ]
        if settings.use_dof:
            ranges.append(("Aperture", settings.aperture_min, settings.aperture_max))

        for label, low, high in ranges:
            if low > high:
                blocking.append(f"Camera {label}: Min is above Max")

        if settings.camera_target is not None and settings.camera_target == settings.camera:
            blocking.append("Camera target can't be the camera itself")

    folder = settings.output_dir.strip()
    if not folder:
        blocking.append("Pick an output folder")
    elif folder.startswith("//") and not bpy.data.filepath:
        blocking.append("Save the .blend file first, or pick a full path")
    else:
        full = bpy.path.abspath(folder)
        if os.path.isdir(full) and not os.access(full, os.W_OK):
            blocking.append("Output folder is not writable")
        if has_dataset_files(full):
            if settings.clear_old:
                warnings.append("Folder has an old dataset: it will be replaced")
            else:
                warnings.append("Folder has old files: new ones will mix with them")

    if settings.num_images >= 2000:
        warnings.append("Large batch: this may take a long time")

    if count_val(settings.num_images, settings.val_split) == 0:
        warnings.append("No validation images (split too small or 0%)")

    # --- Materials ---
    if settings.use_materials:
        names = [pool.name for pool in settings.pools]
        for name in set(names):
            if names.count(name) > 1:
                once(blocking, f"Two pools are named '{name}'")

        class_collections = [entry.collection for entry in settings.class_list]
        seen = []

        for rule in settings.rules:
            target = rule_target(rule)
            if target is None:
                once(blocking, "A material rule has no target")
                continue

            label = target.name

            if rule.target_type == 'OBJECT':
                candidates = [target]
            elif rule.target_type == 'COLLECTION':
                candidates = list(target.all_objects)
            else:
                candidates = list(target.objects)
            bare = [o for o in candidates if o.type == 'MESH' and len(o.material_slots) == 0]

            if bare:
                once(warnings, f"'{label}': {len(bare)} object(s) have no material slot")

            if rule.target_type == 'CLASS' and target not in class_collections:
                once(blocking, f"Rule '{label}': not a class any more")

            pool = find_pool(settings, rule.pool_name)
            if pool is None:
                if rule.pool_name:
                    once(blocking, f"Rule '{label}': pool '{rule.pool_name}' not found")
                else:
                    once(blocking, f"Rule '{label}': pick a pool")
            elif len(pool.materials) == 0:
                once(blocking, f"Pool '{pool.name}' is empty")
            else:
                if any(item.material is None for item in pool.materials):
                    once(blocking, f"Pool '{pool.name}' has a missing material")
                if len(pool.materials) == 1:
                    once(warnings, f"Pool '{pool.name}' has only one material")

            if target in seen:
                once(warnings, f"Two rules target '{label}'")
            seen.append(target)

    return blocking, warnings