def new_stats():
    return {"images": 0, "train": 0, "val": 0, "empty": 0,
            "dropped": 0, "spawned": 0, "objects": {}}


def add_image(stats, boxes, spawned, failed, part):
    stats["images"] += 1
    stats[part] += 1
    if not boxes:
        stats["empty"] += 1
    stats["dropped"] += failed
    stats["spawned"] += spawned
    for box in boxes:
        key = str(box[0])
        stats["objects"][key] = stats["objects"].get(key, 0) + 1
    return stats


def balance_ratio(counts):
    values = list(counts.values())
    if len(values) < 2 or max(values) == 0:
        return None
    return min(values) / max(values)
