import bpy
from .rng import make_rng
from .colortemp import kelvin_to_linear

ORIG_ENERGY = "sdg_orig_energy"
ORIG_COLOR = "sdg_orig_color"


def randomize_lights(settings, image_index):
    """Randomize every included light for ONE image. Returns how many changed."""
    if not settings.use_lights:
        restore_lights()
        return 0

    rng = make_rng(settings.seed, image_index, "lights")
    changed = 0

    for entry in settings.light_list:
        off_roll = rng.uniform(0,100)
        factor = rng.uniform(entry.intensity_min, entry.intensity_max)
        temperature = rng.uniform(entry.temp_min, entry.temp_max)

        if not entry.use or entry.obj is None:
            continue

        light =entry.obj.data

        if ORIG_ENERGY not in light:
            light[ORIG_ENERGY] = light.energy
            light[ORIG_COLOR] = tuple(light.color)

        base = light[ORIG_ENERGY]
        light.energy = 0.0 if off_roll < entry.off_chance else base * factor
        light.color = kelvin_to_linear(temperature)
        changed += 1

    return changed


def restore_lights():
    """Put back every light we changed, and remove the markers."""
    for light in bpy.data.lights:
        if ORIG_ENERGY in light:
            light.energy = light[ORIG_ENERGY]
            light.color = tuple(light[ORIG_COLOR])
            del light[ORIG_ENERGY]
            del light[ORIG_COLOR]