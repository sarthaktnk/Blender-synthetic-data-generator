import os
import bpy
from contextlib import contextmanager
from .split import split_of


def image_base(settings, index):
    """The file path WITHOUT an extension. Blender adds .png or .jpg itself."""
    folder = bpy.path.abspath(settings.output_dir)
    part = split_of(index, settings.val_split)
    return os.path.join(folder, "images", part, f"image_{index:05d}")


def image_path(settings, index):
    """The full path of the rendered file, with its extension."""
    ext = ".png" if settings.image_format == 'PNG' else ".jpg"
    return image_base(settings, index) + ext


def debug_path(settings, index):
    folder = bpy.path.abspath(settings.output_dir)
    return os.path.join(folder, "debug", f"debug_{index:05d}.png")


def label_path(settings, index):
     folder = bpy.path.abspath(settings.output_dir)
     part = split_of(index, settings.val_split)
     return os.path.join(folder, "labels", part, f"image_{index:05d}.txt")


@contextmanager
def render_settings(context, settings):
    """Apply the add-on's render settings, and put the user's back afterwards."""
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
    try:
            render.resolution_x = settings.res_x
            render.resolution_y = settings.res_y
            render.resolution_percentage = 100
            render.image_settings.file_format = settings.image_format
            scene.camera = settings.camera
            yield
    finally:
            render.filepath = saved["filepath"]
            render.resolution_x = saved["x"]
            render.resolution_y = saved["y"]
            render.resolution_percentage = saved["percent"]
            render.image_settings.file_format = saved["format"]
            scene.camera = saved["camera"]
    

def render_still(context, settings, base_path):
    """Render the current scene to base_path"""
    os.makedirs(os.path.dirname(base_path), exist_ok=True)
    with render_settings(context, settings):
         context.scene.render.filepath = base_path
         bpy.ops.render.render(write_still=True)