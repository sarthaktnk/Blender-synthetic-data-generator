import os
import bpy


def image_base(settings, index):
    """The file path WITHOUT an extension. Blender adds .png or .jpg itself."""
    folder = bpy.path.abspath(settings.output_dir)
    return os.path.join(folder, "images", f"image_{index:05d}")


def render_still(context, settings, base_path):
    """Render the current scene to base_path, then restore the render settings."""
    scene = context.scene
    render = scene.render

    saved = {
        "filepath": render.filepath,
        "x": render.resolution_x,
        "y": render.resolution_y,
        "percent": render.resolution_percentage,
        "format": render.image_settings.file_format,
        "camera": scene.camera,
    }

    os.makedirs(os.path.dirname(base_path), exist_ok=True)

    try:
        render.filepath = base_path
        render.resolution_x = settings.res_x
        render.resolution_y = settings.res_y
        render.resolution_percentage = 100
        render.image_settings.file_format = settings.image_format
        scene.camera = settings.camera

        bpy.ops.render.render(write_still=True)
    finally:
        render.filepath = saved["filepath"]
        render.resolution_x = saved["x"]
        render.resolution_y = saved["y"]
        render.resolution_percentage = saved["percent"]
        render.image_settings.file_format = saved["format"]
        scene.camera = saved["camera"]