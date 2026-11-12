import bpy
from .rng import make_rng
from .orbit import orbit_position, look_rotation

ORIG = "sdg_orig_camera"


def _restore_dof(cam, saved):
    cam.dof.use_dof = bool(saved["use_dof"])
    name = saved["focus_object"]
    cam.dof.focus_object = bpy.data.objects.get(name) if name else None
    cam.dof.focus_distance = saved["focus_distance"]
    cam.dof.aperture_fstop = saved["f_stop"]


def randomize_camera(settings, image_index):
    cam_obj = settings.camera
    if cam_obj is None or cam_obj.type != 'CAMERA':
        return False
    if not settings.use_camera:
        restore_camera()
        return False


    rng = make_rng(settings.seed, image_index, "camera")
    distance = rng.uniform(settings.distance_min, settings.distance_max)
    azimuth = rng.uniform(settings.azimuth_min, settings.azimuth_max)
    elevation = rng.uniform(settings.elevation_min, settings.elevation_max)
    focal = rng.uniform(settings.focal_min, settings.focal_max)
    f_stop = rng.uniform(settings.aperture_min, settings.aperture_max)

    cam = cam_obj.data


    if ORIG not in cam_obj:
        focus = cam.dof.focus_object
        cam_obj[ORIG] = {
            "loc": list(cam_obj.location),
            "rot": list(cam_obj.rotation_euler),
            "rot_mode": cam_obj.rotation_mode,
            "lens": cam.lens,
            "use_dof": cam.dof.use_dof,
            "focus_object": focus.name if focus else "",
            "focus_distance": cam.dof.focus_distance,
            "f_stop": cam.dof.aperture_fstop,
        }
    saved = cam_obj[ORIG]


    target = settings.camera_target
    center = tuple(target.matrix_world.translation) if target else (0.0, 0.0, 0.0)

    cam_obj.rotation_mode = 'XYZ'
    cam_obj.location = orbit_position(center, distance, azimuth, elevation)
    cam_obj.rotation_euler = look_rotation(azimuth, elevation)
    cam.lens = focal

    if settings.use_dof:
        cam.dof.use_dof = True
        cam.dof.focus_object = None
        cam.dof.focus_distance = distance
        cam.dof.aperture_fstop = f_stop
    else:
        _restore_dof(cam, saved)

    return True


def restore_camera():
    for obj in bpy.data.objects:
        if ORIG in obj:
            saved = obj[ORIG]
            cam = obj.data
            obj.rotation_mode = saved["rot_mode"]
            obj.location = tuple(saved["loc"])
            obj.rotation_euler = tuple(saved["rot"])
            cam.lens = saved["lens"]
            _restore_dof(cam, saved)
            del obj[ORIG]