from math import cos, sin, pi, radians, sqrt


def orbit_position(target, distance, azimuth, elevation):
     
     tx, ty, tz = target
     flat = distance * cos(elevation)
     return (
          tx + flat * cos(azimuth),
          ty + flat * sin(azimuth),
          tz + distance * sin(elevation),
     )


def look_rotation(azimuth, elevation):
     return (pi / 2 - elevation, 0.0, azimuth + pi / 2)


def _forward(rotation):
    """Self-test helper: where does a camera with this rotation point?
    Applies Blender's XYZ Euler order (X first, then Z) to the vector (0, 0, -1)."""
    rx, _, rz = rotation
    x, y, z = 0.0, 0.0, -1.0
    y, z = y * cos(rx) - z * sin(rx), y * sin(rx) + z * cos(rx)    # rotate around X
    x, y = x * cos(rz) - y * sin(rz), x * sin(rz) + y * cos(rz)    # rotate around Z
    return x, y, z

