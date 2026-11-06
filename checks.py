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
                blocking.append(f"class '{entry.name}' is empty")
            if entry.count_min > entry.count_max:
                blocking.append(f"Class '{entry.name}': Min is above Max")

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
    return blocking, warnings