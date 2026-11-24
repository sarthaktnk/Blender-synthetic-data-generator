import bpy # type: ignore
from bpy.props import (
    BoolProperty, FloatProperty, PointerProperty, CollectionProperty, IntProperty, StringProperty, EnumProperty
 ) # type: ignore
from .class_list import refresh_classes
from .light_list import refresh_lights
from math import pi, radians
from .overlay import redraw_viewports
from .pools import add_material

ROTATION_ITEMS = [
    ('ANY', "Any",  "Random rotation on every axis"),
    ('UPRIGHT', "Upright",  "Random turn around Z only"),
    ('FLAT', "Flat",  "Lying on its side, random turn around Z"),
    ('FIXED', "Fixed",  "Keep the original rotation"),
]

TARGET_ITEMS = [
    ('CLASS', "Class", "Spawned objects of one class"),
    ('COLLECTION', "Collection", "Every object in a collection"),
    ('OBJECT', "Object", "A single object"),
]

SLOT_ITEMS = [
    ('FIRST', "First", "Only the first material slot"),
    ('ALL', "All", "Every material slot")
]

PLACEMENT_MODES = [
    ('SCATTER', "Scatter", "Random positions on a flat area"),
    ('PHYSICS', "Physics", "Drop the objects and let them settle naturally"),
]


def poll_camera(self, obj):
    return obj.type == 'CAMERA'


def poll_class_collection(self, collection):
    settings = bpy.context.scene.sdg_settings
    return any(entry.collection == collection for entry in settings.class_list)


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


def update_overlay(self, context):
    redraw_viewports(context)


class SDG_PoolMaterial(bpy.types.PropertyGroup):
    material: PointerProperty(type=bpy.types.Material)


def update_pool_name(self, context):
    settings = context.scene.sdg_settings
    for rule in settings.rules:
        if self.prev_name and rule.pool_name == self.prev_name:
            rule.pool_name = self.name
    self.prev_name = self.name


class SDG_Pool(bpy.types.PropertyGroup):
    name: StringProperty(name="Pool", default="Pool", update=update_pool_name)
    prev_name: StringProperty(default="")
    materials: CollectionProperty(type=SDG_PoolMaterial)
    material_index: IntProperty(default=0)


class SDG_MaterialRule(bpy.types.PropertyGroup):
    target_type: EnumProperty(name="Target", items=TARGET_ITEMS, default='CLASS')
    target_class: PointerProperty(name="Class", type=bpy.types.Collection, poll=poll_class_collection)
    target_collection: PointerProperty(name="Collection", type=bpy.types.Collection)
    target_object: PointerProperty(name="Object", type=bpy.types.Object)
    pool_name: StringProperty(name="Pool")
    slot_mode: EnumProperty(name="Slot", items=SLOT_ITEMS, default='FIRST')
    chance: FloatProperty(
        name="Chance", default=100.0, min=0.0, max=100.0, subtype='PERCENTAGE',
        description="Share of the targeted objects that get a new material",
    )

def update_add_material(self, context):
    if self.add_material is None:
        return
    if self.pools:
        add_material(self.pools[self.pool_index], self.add_material)
    self.add_material = None


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

    placement_mode: EnumProperty(
        name="Mode", items=PLACEMENT_MODES, default='SCATTER',
    )
    # --- Physics ---
    ground_height: FloatProperty(
        name="Ground height", default=0.0,
        subtype='DISTANCE', unit='LENGTH',
        description="Height of the invisible ground the objects land on",
    )
    drop_height: FloatProperty(
        name="drop height", default=0.5, min=0.05,
        subtype='DISTANCE', unit='LENGTH',
        description="Objects start between a little above the ground and this height",
    )
    sim_frames: IntProperty(
        name="Settle frames", default=100, min=10, max=600,
        description="Simulation frames to run"
    )
    friction: FloatProperty(
        name="Friction", default=0.5, min=0.0, max=1.0,
        description="How much objects resist sliding",
    )
    bounciness: FloatProperty(
        name="Bounce", default=0.1, min=0.0, max=1.0,
        description="How much objects bounce when they land",
    )
    use_walls: BoolProperty(
        name="Walls", default=True,
        description="Invisible walls around the area keep objects from rolling out",
    )

    rules: CollectionProperty(type=SDG_MaterialRule)
    rule_index: IntProperty(default=0)
    scale_min: FloatProperty(name="Scale Min", default=0.8, min=0.01)
    scale_max: FloatProperty(name="Scale Max", default=1.2, min=0.01)
    num_images: IntProperty(name="Images", default=500, min=1, max=100000)
    seed: IntProperty(
        name="Seed", default=42, min=0,
        description="Same seed and same settings give the same dataset",
    )

    output_dir: StringProperty(
        name="Folder", subtype='DIR_PATH', default="//synthetic_data",
        description="Where the dataset is written. // means next to the .blend file"
    )
    clear_old: BoolProperty(
        name="Replace previous dataset", default=True,
        description="Before generating, delete old image_#####, debug_#####,"
                    "classes.txt and dataset.yaml files in the output folder."
                    "Other files are never touched",
    )
    res_x: IntProperty(name="Width", default=1280, min=64, max=8192, subtype='PIXEL')
    res_y: IntProperty(name="Height", default=720, min=64, max=8192, subtype='PIXEL')
    image_format: EnumProperty(
        name="Format",
        items=[
            ('PNG', "PNG", "Lossless, larger files"),
            ('JPEG', "JPEG", "Smaller files, slight quality loss"),
        ],
        default='PNG',
    )
    save_debug: BoolProperty(
        name="Save debug images", default=False,
        description="Also save a copy of each image with the boxes drawn on it",
    )
    val_split: IntProperty(
        name="Validation", default=20, min=0, max=50,
        subtype='PERCENTAGE',
        description="Share of images set aside for validation",
    )
    last_stats: StringProperty(default="")
    show_overlay: BoolProperty(
        name="Show boxes in viewport", default=True,
        update=update_overlay,
        description="Draw a box around every preview object, colored by class",
    )
    show_labels: BoolProperty(
        name="Show class names", default=True,
        update=update_overlay,
        description="Write the class name above each box"
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

    use_camera: BoolProperty(
        name="Camera", default=True,
        description="Randomize the camera",
    )
    camera_target: PointerProperty(
        name="Target", type=bpy.types.Object,
        description="The camera orbits and looks at this object (blank = world origin)"
    )
    distance_min: FloatProperty(
        name="Min", default=1.5, min=0.05,
        subtype='DISTANCE', unit='LENGTH',
    )
    distance_max: FloatProperty(
        name="Max", default=4.0, min=0.05,
        subtype='DISTANCE', unit='LENGTH',
    )
    azimuth_min: FloatProperty(
        name="Min", default=0.0, min=0.0, max=2 * pi,
        subtype='ANGLE', unit='ROTATION',
        description="Angle around the target, 0 = the +X side",
    )
    azimuth_max: FloatProperty(
        name="Max", default=2 * pi, min=0.0, max=2 * pi,
        subtype='ANGLE', unit='ROTATION',
    )
    elevation_min: FloatProperty(
        name="Min", default=radians(10), min=0.0, max=radians(89),
        subtype='ANGLE', unit='ROTATION',
        description="Height angle above the ground plane",
    )
    elevation_max: FloatProperty(
        name="Max", default=radians(60), min=0.0, max=radians(89),
        subtype='ANGLE', unit='ROTATION',
    )
    focal_min: FloatProperty(
        name="Min", default=35.0, min=1.0, unit='CAMERA',
        description="Shortest focal length (wider view)",
    )
    focal_max: FloatProperty(
        name="Max", default=85.0, min=1.0, unit='CAMERA',
        description="Longest focal length (narrower view)",
    )
    use_dof: BoolProperty(
        name="Depth of field", default=False,
        description="Blur things that are away from the target",
    )
    aperture_min: FloatProperty(name="Min", default=2.8, min=0.5)
    aperture_max: FloatProperty(name="Max", default=8.0, min=0.5)

    # --- Materials ---
    use_materials: BoolProperty(
        name="Materials", default=True,
        description="Randomize materials with the rules below",
    )
    pools: CollectionProperty(type=SDG_Pool)
    pool_index: IntProperty(default=0)
    add_material: PointerProperty(
        name="Add material", type=bpy.types.Material,
        update=update_add_material,
        description="Add a material from this file to the selected pool"
    )

classes = (
    SDG_ClassEntry,
    SDG_LightEntry,
    SDG_PoolMaterial,
    SDG_Pool,
    SDG_MaterialRule,
    SDG_Settings,
    
)