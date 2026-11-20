import os


def box_to_yolo(box):
    """Convert (class_id, x0, y0. x1. y1) with y = 0 at the Bottom into a 
    YOLO LINE: 'class cx cy w h', all 0-1, with y=0 at the Top."""
    class_id, x0, y0, x1, y1 = box
    cx = (x0 + x1)/2
    cy = 1.0 - (y0 + y1) / 2
    w = x1 - x0
    h = y1 - y0
    return f"{class_id} {cx:.6f} {cy:.6f} {w:.6f} {h:.6f}"


def write_yolo_file(path, boxes):
    """One text file per image, onle line per object.
    An empty file is valid: it tells the trainer that this image has no objects."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for box in boxes:
            f.write(box_to_yolo(box) + "\n")


def class_names(settings):
    """A dictionary {class_id:name}, taken from the class list."""
    return {entry.class_id: entry.name for entry in settings.class_list}


def write_classes(path, names):
    """classes.txt: line number = class ID. If IDs have gaps (a class was deleted),
    the gap gets a placeholder so the numbers still line up."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    last = max(names) if names else -1
    with open(path, "w", encoding="utf-8") as f:
        for i in range(last + 1):
            f.write(names.get(i, f"unused_{i}") + "\n")

