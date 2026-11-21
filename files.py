import os
import re

NAME_RE = re.compile(r"^(image|debug)_\d{5}\.(png|jpg|txt)$")
TOP_FILES = ("classes.txt", "dataset.yaml")


def iter_dataset_files(folder):

    for sub in ("images", "labels", "debug"):
        for part in ("", "train", "val"):
            d = os.path.join(folder, sub, part)
            if not os.path.isdir(d):
                continue
            with os.scandir(d) as entries:
                for entry in entries:
                    if entry.is_file() and NAME_RE.match(entry.name):
                        yield entry.path
    for name in TOP_FILES:
        path = os.path.join(folder, name)
        if os.path.isfile(path):
            yield path


def has_dataset_files(folder):
    return next(iter_dataset_files(folder), None) is not None


def clear_dataset(folder):
    files = list(iter_dataset_files(folder))
    for path in files:
        os.remove(path)
    return len(files)
