"""Geometry: port of GELIB.C and the coord1/coord2 helpers in GECMDS.C.

Coordinate system (see salvage/spec/universe.md):
1.0 coordinate unit = one sector. Heading 0 = north (-y), 90 = east
(+x); a ship at heading h moves along (sin h, -cos h).
"""

from __future__ import annotations

import math
from dataclasses import dataclass

SSMAX = 10000  # display units within one sector


@dataclass
class Coord:
    x: float = 0.0
    y: float = 0.0

    def copy(self) -> "Coord":
        return Coord(self.x, self.y)


def coord1(c: float) -> int:
    """Sector number of a coordinate."""
    return math.floor(c)


def coord2(c: float) -> int:
    """Position within the sector, 0-9999."""
    return int((c - math.floor(c)) * SSMAX)


def sector_of(p: Coord) -> tuple[int, int]:
    return (coord1(p.x), coord1(p.y))


def samesect(a: Coord, b: Coord) -> bool:
    return sector_of(a) == sector_of(b)


def normal(angle: float) -> float:
    """Bring an angle into [0, 360)."""
    a = math.fmod(angle, 360.0)
    return a + 360.0 if a < 0 else a


def smallest(a1: float, a2: float) -> float:
    """Smallest difference between two angles in [0, 360)."""
    a = abs(a1 - a2)
    return 360.0 - a if a > 180.0 else a


def cdistance(a: Coord, b: Coord) -> float:
    return math.hypot(a.x - b.x, a.y - b.y)


def vector(frm: Coord, to: Coord) -> float:
    """Compass heading from one point toward another.

    Closed form of GELIB.C's four-quadrant angleb/anglec construction:
    heading h satisfies (sin h, -cos h) ∝ (dx, dy).
    """
    dx = to.x - frm.x
    dy = to.y - frm.y
    if dx == 0.0 and dy == 0.0:
        return 0.0
    return normal(math.degrees(math.atan2(dx, -dy)))


def cbearing(frm: Coord, to: Coord, heading: float) -> float:
    """Bearing to a target relative to own heading, -180..+180."""
    b = normal(360.0 - heading + vector(frm, to))
    return b - 360.0 if b > 180.0 else b
