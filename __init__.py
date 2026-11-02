import bpy # type: ignore
from bpy.props import FloatProperty , PointerProperty, BoolProperty # type: ignore

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

class SDG_PanelBase:
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Synthetic Data'
    
class SDG_PT_setup(SDG_PanelBase, bpy.types.Panel):
    bl_label = "Setup"
    bl_idname = "SDG_PT_setup"

    def draw(self, context):
        settings = context.scene.sdg_settings
        layout = self.layout
        layout.prop(settings, "subjects")
        layout.prop(settings, "environment")
        layout.prop(settings, "camera")

class SDG_PT_placement(SDG_PanelBase, bpy.types.Panel):
    bl_label = "Object Placement"
    bl_idname = "SDG_PT_placement"
    bl_options = {'DEFAULT_CLOSED'}

    def draw_header(self, context):
        self.layout.prop(context.scene.sdg_settings, "use_placement", text="")

    def draw(self, context):
        settings = context.scene.sdg_settings
        layout = self.layout
        layout.active = settings.use_placement
        layout.prop(settings, "pos_range")

classes = (
    SDG_Settings,
    SDG_PT_setup,
    SDG_PT_placement,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.sdg_settings = PointerProperty(type=SDG_Settings)

def unregister():
    del bpy.types.Scene.sdg_settings
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)