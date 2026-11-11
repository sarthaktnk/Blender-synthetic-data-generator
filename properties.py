import bpy # type: ignore
from bpy.props import (
    BoolProperty, FloatProperty, PointerProperty, CollectionProperty, IntProperty, StringProperty, EnumProperty
 ) # type: ignore
from .class_list import refresh_classes
from .light_list import refresh_lights

ROTATION_ITEMS = [
    ('ANY', "Any",  "Random rotation on every axis"),
    ('UPRIGHT', "Upright",  "Random turn around Z only"),
    ('FLAT', "Flat",  "Lying on its side, random turn around Z"),
    ('FIXED', "Fixed",  "Keep the original rotation"),
]

def poll_camera(self, obj):
    return obj.type == 'CAMERA'

def update_override(self, context):
    if self.use_override:
        s = context.scene.sdg_settings
        self.area_length = s.area_length
        self.area_width = s.area_width
        self.rotation_mode = s.rotation_mode
        self.scale_min = s.scale_min
        self.scale_max = s.scale_max

class SDG_ClassEntry(bpy.types.PropertyGroup):

    name: StringProperty(name="Class", default="class")
    class_id: IntProperty(name="ID", default=0, min=0)
    collection: PointerProperty(type=bpy.types.Collection)
    count_min: IntProperty(name="Min", default=1, min=0)
    count_max: IntProperty(name="Max", default=3, min=0)

    use_override: BoolProperty(
        name="Override",
        default=False,
        update=update_override,
        description="Use this calss's own placement settings instead of the defaults",
    )
    area_length: FloatProperty(
        name="Length", default=2.0, min=0.01,
        subtype='DISTANCE', unit='LENGTH',
    )
    area_width: FloatProperty(
        name="Width", default=1.5, min=0.01,
        subtype='DISTANCE', unit='LENGTH',
    )
    rotation_mode: EnumProperty(name="Rotation", items=ROTATION_ITEMS, default='ANY')
    scale_min: FloatProperty(name="Min", default=0.8, min=0.01)
    scale_max: FloatProperty(name="Max", default=1.2, min=0.01)


def update_subjects(self, context):
    refresh_classes(self)

class SDG_LightEntry(bpy.types.PropertyGroup):
    name: StringProperty(name="Light", default="light")
    obj: PointerProperty(type=bpy.types.Object)
    use: BoolProperty(
        name="Include", default=True,
        description="Randomize this light (Untick to keep it fixed)",
    )

    intensity_min: FloatProperty(name="Min", default=0.5, min=0.0)
    intensity_max: FloatProperty(name="Max", default=1.5, min=0.0)
    temp_min: IntProperty(name="Min", default=3500, min=1000, max=12000)
    temp_max: IntProperty(name="Max", default=7500, min=1000, max=12000)

    off_chance: FloatProperty(
        name="Off chance", default=0.0, min=0.0, max=100.0,
        subtype='PERCENTAGE',
        description="Chance that this light is switched off in an image",
    )


def update_environment(self, context):
    refresh_lights(self)


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
        items=ROTATION_ITEMS,
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
        description="Collection holding lights and other fixed objects", update=update_environment,
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

    use_lights: BoolProperty(
        name="Lights", default=True,
        description="Randomize the lights",
    )
    light_list: CollectionProperty(type=SDG_LightEntry)
    light_index: IntProperty(default=0)


    preview_index: IntProperty(default=0, min=0)

    class_list: CollectionProperty(type=SDG_ClassEntry)

    class_index: IntProperty(default=0)
    next_class_id: IntProperty(default=0)

classes = (
    SDG_ClassEntry,
    SDG_LightEntry,
    SDG_Settings,
)