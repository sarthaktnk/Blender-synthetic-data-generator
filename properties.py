import bpy # type: ignore
from bpy.props import BoolProperty, FloatProperty, PointerProperty # type: ignore

def poll_camera(self, obj):
    return obj.type == 'CAMERA'

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
        description="Collection whose child collections become Classes",
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

classes = (
    SDG_Settings,
)