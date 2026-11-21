import os
import json


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


def names_list(names):
    last = max(names) if names else -1
    return [names.get(i, f"unused_{i}") for i in range(last + 1)]


def write_classes(path, names):
    """classes.txt: line number = class ID. If IDs have gaps (a class was deleted),
    the gap gets a placeholder so the numbers still line up."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for name in names_list(names):
            f.write(name + "\n")


def write_yaml(path, names, has_val):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    lines = ["train: images/train"]
    if has_val:
        lines.append("val: images/val")
    else:
        lines.append("# No validation images in this run, so the training images are used.")
        lines.append("val: images/train")
    lines.append("names:")
    for i, name in enumerate(names_list(names)):
        lines.append(f" {i}: {json.dumps(name)}")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    names = {0: "bolt", 2: "big washer"}
    write_yaml("test_out/dataset.yaml", names, True)
    print(open("test_out/dataset.yaml").read())
    write_yaml("test_out/dataset2.yaml", names, False)
    print(open("test_out/dataset2.yaml").read())

