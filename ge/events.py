"""Events emitted by the sim core.

The sim never formats text. Each event carries a `key` naming the
original MSG-file message it corresponds to (MBMGEMSG.MSG), plus the
parameters that message interpolates; the presentation layer maps keys
to text/ANSI. Scope and visibility mirror the original's output
routines:

    SELF   -> outprfge(cls, usrnum)          one ship
    SECTOR -> outsect(cls, coord, exclude)   ships in a sector
    RANGE  -> outrange(cls, coord)           ships whose scan range covers coord
    GAME   -> outwar(cls, exclude, freq)     everyone in the game

Visibility FILTER events are suppressible by the user's `filter`
option; ALWAYS events are not.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto

from .geometry import Coord


class Scope(Enum):
    SELF = auto()
    SECTOR = auto()
    RANGE = auto()
    GAME = auto()


class Visibility(Enum):
    ALWAYS = auto()
    FILTER = auto()


@dataclass
class Event:
    t: int                       # sim time (seconds) when emitted
    key: str                     # original MSG name, e.g. "SPEEDIS"
    scope: Scope
    visibility: Visibility
    ship: int | None = None      # target ship for SELF scope
    coord: Coord | None = None   # anchor for SECTOR/RANGE scope
    exclude: int | None = None   # ship id excluded from broadcast
    params: dict = field(default_factory=dict)

    def __str__(self) -> str:  # debugging/demo aid only
        where = {
            Scope.SELF: f"ship {self.ship}",
            Scope.SECTOR: "sector",
            Scope.RANGE: "range",
            Scope.GAME: "game",
        }[self.scope]
        p = " ".join(f"{k}={v}" for k, v in self.params.items())
        return f"[t={self.t:>4}] {self.key:<10} -> {where:<8} {p}"
