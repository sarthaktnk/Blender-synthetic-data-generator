import bpy
import gpu
import blf
from gpu_extras.batch import batch_for_shader
from bpy_extras.view3d_utils import location_3d_to_region_2d
from mathutils import Vector

from .annotations import PALETTE
from .spawn import SPAWN_COLLECTION

_handle = None
_failed = False


def _draw():
    context = bpy.context
    settings = context.scene.sdg_settings
    region = context.region
    rv3d = context.region_data
    holder = bpy.data.collections.get(SPAWN_COLLECTION)

    if not settings.show_overlay or holder is None or rv3d is None:
        return


    by_class = {}
    labels = []

    for obj in holder.objects:
        corners = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
        points = [location_3d_to_region_2d(region, rv3d, p) for p in corners]
        if any(p is None for p in points):
            continue

        x0 = min(p.x for p in points)
        x1 = max(p.x for p in points)
        y0 = min(p.y for p in points)
        y1 = max(p.y for p in points)

        class_id = obj.get("sdg_class_id", 0)
        lines = by_class.setdefault(class_id, [])
        labels.append((class_id, x0, y1))

        for dx, dy in ((0, 0), (1, 0), (0, 1), (1, 1)):
            a = (x0 + dx, y0 + dy)
            b = (x1 + dx, y0 + dy)
            c = (x1 + dx, y1 + dy)
            d = (x0 + dx, y1 + dy)
            lines += [a, b, b, c, c, d, d, a]

    shader = gpu.shader.from_builtin('UNIFORM_COLOR')
    for class_id, coords in by_class.items():
        batch = batch_for_shader(shader, 'LINES', {"pos": coords})
        shader.uniform_float("color", PALETTE[class_id % len(PALETTE)])
        batch.draw(shader)

    if not settings.show_labels:
        return

    names = {entry.class_id: entry.name for entry in settings.class_list}
    font_id = 0
    blf.size(font_id, 14 * context.preferences.system.ui_scale)
    pad = 3

    for class_id, x, y in labels:
        text = names.get(class_id, f"class {class_id}")
        w, h = blf.dimensions(font_id, text)

        ly = y + 2
        if ly + h + 2 * pad > region.height:
            ly = y - h - 2 * pad -2

        verts = (
            (x, ly), (x + w + 2 * pad, ly),
            (x, ly + h + 2 *pad), (x + w + 2 * pad, ly + h + 2 * pad),
        )
        batch = batch_for_shader(shader, 'TRIS', {"pos": verts}, indices=((0, 1, 2), (2, 1, 3)))
        shader.uniform_float("color", PALETTE[class_id % len(PALETTE)])
        batch.draw(shader)

        blf.color(font_id, 0, 0, 0, 1)
        blf.position(font_id, x + pad, ly + pad, 0)
        blf.draw(font_id, text)


def draw_boxes():
    global _failed
    if _failed:
        return
    try:
        _draw()
    except Exception as error:
        _failed = True
        print("Synthetic Data overlay turned off after an error:", error)


def register_overlay():
    global _handle
    _handle = bpy.types.SpaceView3D.draw_handler_add(
        draw_boxes, (), 'WINDOW', 'POST_PIXEL'
    )


def unregister_overlay():
    global _handle
    if _handle is not None:
        bpy.types.SpaceView3D.draw_handler_remove(_handle, 'WINDOW')
        _handle = None


def redraw_viewports(context):
    for window in context.window_manager.windows:
        for area in window.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()