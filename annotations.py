import bpy
import numpy as np
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector

PALETTE = [
    (1, 0, 0, 1), (0, 1, 0, 1), (0, 0.4, 1, 1),
    (1, 1, 0, 1), (1, 0, 1, 1), (0, 1, 1, 1),
]


def compute_boxes(context, settings, objects):
    """2D box for each object, in the current camera view."""
    scene = context.scene
    camera = settings.camera

    context.view_layer.update()

    boxes = []
    for obj in objects:
        corners = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
        points = [world_to_camera_view(scene, camera, p) for p in corners]

        if any(p.z <= 0 for p in points):
            continue

        xs = [p.x for p in points]
        ys = [p.y for p in points]

        x0, x1 = max(0.0, min(xs)), min(1.0, max(xs))
        y0, y1 = max(0.0, min(ys)), min(1.0, max(ys))

        if x1 <= x0 or y1 <= y0 or (x1 -x0) * (y1 - y0) < 1e-5:
            continue

        boxes.append((obj["sdg_class_id"], x0, y0, x1, y1))
    return boxes


def save_debug_image(image_file, boxes, out_file):
    """Draw the boxes onto a copy of the rendered image, for checking."""
    img = bpy.data.images.load(image_file)
    try:
        w, h = img.size
        pixels = np.empty(w * h * 4, dtype=np.float32)
        img.pixels.foreach_get(pixels)
        pixels = pixels.reshape(h, w, 4)

        t = 2
        for class_id, x0, y0, x1, y1 in boxes:
            c0, c1 = int(x0 * (w - 1)), int(x1 * (w - 1))
            r0, r1 = int(y0 * (h - 1)), int(y1 * (h - 1))
            color = PALETTE[class_id % len(PALETTE)]

            pixels[r0:r0 + t, c0:c1 + 1] = color
            pixels[max(0, r1 - t + 1):r1 + 1, c0:c1 + 1] = color
            pixels[r0:r1 + 1, c0:c0 + t] = color
            pixels[r0:r1 + 1, max(0, c1 - t + 1):c1 + 1] = color

        img.pixels.foreach_set(pixels.ravel())
        img.filepath_raw = out_file
        img.file_format = 'PNG'
        img.save()
    finally:
        bpy.data.images.remove(img)