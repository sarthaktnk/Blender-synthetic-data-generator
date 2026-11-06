import bpy # type: ignore
from bpy.props import (
    BoolProperty, FloatProperty, PointerProperty, CollectionProperty, IntProperty, StringProperty, EnumProperty
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

    area_length: FloatProperty(
        name="Length", default=2.0, min=0.01,
        subtype='DISTANCE', unit='LENGTH',
        description="Size of the placement area alomg X",
    ) # type: ignore
    area_width: FloatProperty(
        name="Width", default=1.5, min=0.01,
        subtype='DISTANCE', unit='LENGTH',
        description="Size of the placement area alomg Y",
    ) # type: ignore
    spacing: FloatProperty(
        name="Min. gap", default=0.1, min=0.0, max=1.0,
        subtype='DISTANCE', unit='LENGTH',
        description="Smallest allowed gap between two objects",
    ) # type: ignore
    rotation_mode: EnumProperty(
        name="Rotation",
        items=[
            ('ANY', "Any",  "Random rotation on every axis"),
            ('UPRIGHT', "Upright",  "Random turn around Z only"),
            ('FLAT', "Flat",  "Lying on its side, random turn around Z"),
            ('FIXED', "Fixed",  "Keep the original rotation"),
        ],
        default='ANY',
    ) # type: ignore
    scale_min: FloatProperty(name="Min", default=0.8, min=0.01)
    scale_max: FloatProperty(name="Max", default=1.2, min=0.01)
    num_images: IntProperty(name="Images", default=500, min=1, max=100000)
    seed: IntProperty(
        name="Seed", default=42, min=0,
        description="Same seed and same settings give the same dataset",
    )
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