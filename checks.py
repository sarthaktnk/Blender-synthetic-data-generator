import os
import bpy


def get_problems(settings):
    blocking = []
    warnings = []

    if settings.subjects is None:
        blocking.append("Pick a Subjects collection")
    elif len(settings.class_list) == 0:
        blocking.append("Subjects has no child collections")
    else:
        for entry in settings.class_list:
            if entry.collection is None or len(entry.collection.all_objects) == 0:
                blocking.append(f"class '{entry.name}' is empty")
            if entry.count_min > entry.count_max:
                blocking.append(f"Class '{entry.name}': Min is above Max")
            if (settings.use_placement and entry.use_override and entry.scale_min > entry.scale_max):
                blocking.append(f"Class '{entry.name}': Scale Min is above Max")

        if all(entry.count_max == 0 for entry in settings.class_list):
            blocking.append("All class counts are 0")

    if settings.camera is None:
        blocking.append("Pick a Camera")

    if settings.environment is None:
        warnings.append("No Environment picked")
    else:
        has_light = any(obj.type == 'LIGHT' for obj in settings.environment.all_objects)
        if not has_light:
            warnings.append("Environment has no lights")
            
    if settings.use_placement and settings.scale_min > settings.scale_max:
        blocking.append("Scale: Min is above Max")

    if settings.use_lights:
        for light in settings.light_list:
            if not light.use:
                continue
            if light.intensity_min > light.intensity_max:
                blocking.append(f"Light '{light.name}': intensity Min is above Max")
            if light.temp_min > light.temp_max:
                blocking.append(f"Light '{light.name}': temperature Min is above Max")

    if settings.use_camera:
        ranges = [
            ("Distance", settings.distance_min, settings.distance_max),
            ("Azimuth", settings.azimuth_min, settings.azimuth_max),
            ("Elevation", settings.elevation_min, settings.elevation_max),
            ("Focal length", settings.focal_min, settings.focal_max),
        ]
        if settings.use_dof:
            ranges.append(("Aperture", settings.aperture_min, settings.aperture_max))

        for label, low, high in ranges:
            if low > high:
                blocking.append(f"Camera {label}: Min is above Max")

        if settings.camera_target is not None and settings.camera_target == settings.camera:
            blocking.append("Camera target can't be the camera itself")

    folder = settings.output_dir.strip()
    if not folder:
        blocking.append("Pick an output folder")
    elif folder.startswith("//") and not bpy.data.filepath:
        blocking.append("Save the .blend file first, or pick a full path")
    else:
        full = bpy.path.abspath(folder)
        if os.path.isdir(full) and not os.access(full, os.W_OK):
            blocking.append("Output folder is not writable")

    if settings.num_images >= 2000:
        warnings.append("Large batch: this may take a long time")  
    return blocking, warnings