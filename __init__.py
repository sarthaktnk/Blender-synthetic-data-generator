import bpy # type: ignore
from bpy.props import PointerProperty # type: ignore

from . import properties, operators, panels

classes = properties.classes + operators.classes + panels.classes

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.sdg_settings = PointerProperty(type=properties.SDG_Settings)

def unregister():
    del bpy.types.Scene.sdg_settings
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)