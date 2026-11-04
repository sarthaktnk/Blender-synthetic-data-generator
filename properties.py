import bpy # type: ignore
from bpy.props import (
    BoolProperty, FloatProperty, PointerProperty, CollectionProperty, IntProperty, StringProperty,
 ) # type: ignore
from .class_list import refresh_classes

def poll_camera(self, obj):
    return obj.type == 'CAMERA'

class SDG_ClassEntry(bpy.types.PropertyGroup):

    name: StringProperty(name="Class", default="class")
    class_id: IntProperty(name="ID", default=0, min=0)
    collection: PointerProperty(type=bpy.types.Collection)
    count_min: IntProperty(name="Min", default=1, min=0)
    count_max: IntProperty(name="Max", default=3, min=0)


def update_subjects(self, context):
    refresh_classes(self)


class SDG_Settings(bpy.types.PropertyGroup):

    pos_range: FloatProperty(
        name="Position Range",
        default=2.0,
        min=0.0,
        max=10.0
    ) # type: ignore
    subjects: PointerProperty(
        name="Subjects",
        type=bpy.types.Collection,
        description="Collection whose child collections become Classes", update=update_subjects,
    ) # type: ignore
    environment: PointerProperty(
        name="Environment",
        type=bpy.types.Collection,
        description="Collection holding lights and other fixed objects",
    ) # type: ignore
    camera: PointerProperty(
        name="Camera",
        type=bpy.types.Object,
        poll=poll_camera,
        description="Camera that will be moved during generation",
    ) # type: ignore

    use_placement: BoolProperty(
        name="Object Placement",
        default=True,
        description="Randomize where the subjects are placed",
    ) # type: ignore

    class_list: CollectionProperty(type=SDG_ClassEntry)

    class_index: IntProperty(default=0)
    next_class_id: IntProperty(default=0)

classes = (
    SDG_ClassEntry,
    SDG_Settings,
)