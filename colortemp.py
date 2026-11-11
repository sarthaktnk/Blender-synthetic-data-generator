from math import log


def kelvin_to_srgb(kelvin):
    """Approximate display color (r, g, b, each 0-1) of a light at this color temperature. Valid roughly 1000-12000 K."""

    t = max(1000, min(kelvin, 12000)) / 100.0

    if t <= 66:
        red = 255.0
        green = 99.4708025861 * log(t) - 161.1195681661
    else:
        red = 329.698727446 * (t - 60) ** -0.1332047592
        green = 288.1221695283 * (t - 60) ** -0.0755148492

    if t >= 66:
        blue = 255.0
    elif t <= 19:
        blue = 0.0
    else:
        blue = 138.5177312231 * log(t - 10) - 305.0447927307


    def clamp(v):
        return max(0.0, min(v, 255.0)) / 255.0

    return clamp(red), clamp(green), clamp(blue)


def srgb_to_linear(c):
    """Convert one channel from display (sRGB) values to linear values."""
    if c <= 0.04045:
        return c / 12.92
    return ((c + 0.055) / 1.055) ** 2.4


def kelvin_to_linear(kelvin):
    """The one we will actually use on a blender light."""
    r, g, b = kelvin_to_srgb(kelvin)
    return srgb_to_linear(r), srgb_to_linear(g), srgb_to_linear(b)


if __name__ == "__main__":
    for k in (2700, 4000, 5500, 6500, 10000):
        r, g, b = kelvin_to_srgb(k)
        print(f"{k:>6} K  ->  {round(r*255)}, {round(g*255)}, {round(b*255)}")