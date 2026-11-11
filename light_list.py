def refresh_lights(settings):
    """Sync settings.light_list with the lights inside Environment. Returns (added, removed)."""
    if settings.environment is None:
        return 0,0

    lights = sorted(
        [o for o in settings.environment.all_objects if o.type == 'LIGHT'],
        key=lambda o: o.name,
    )
    added = 0
    removed = 0

    for i in reversed(range(len(settings.light_list))):
        if settings.light_list[i].obj not in lights:
            settings.light_list.remove(i)
            removed += 1

    existing = [entry.obj for entry in settings.light_list]
    for light in lights:
        if light not in existing:
            entry = settings.light_list.add()
            entry.obj = light
            added += 1

    for entry in settings.light_list:
        entry.name = entry.obj.name
    settings.light_index = min(settings.light_index, max(0, len(settings.light_list) - 1))

    return added, removed