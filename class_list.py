def refresh_classes(settings):
    """Sync settings.class_list with the child collections of Subjects. Returns (added,removed) so the caller can report it """

    if settings.subjects is None:
        return 0,0

    children = list(settings.subjects.children)
    removed = 0
    added = 0

    for i in reversed(range(len(settings.class_list))):
        if settings.class_list[i].collection not in children:
            settings.class_list.remove(i)
            removed += 1

    existing = [entry.collection for entry in settings.class_list]
    for child in children:
        if child not in existing:
            entry = settings.class_list.add()
            entry.collection = child
            entry.class_id = settings.next_class_id
            settings.next_class_id += 1
            added += 1

    for entry in settings.class_list:
        entry.name = entry.collection.name

    last = max(0, len(settings.class_list) - 1)
    settings.class_index = min(settings.class_index, last)

    return added, removed