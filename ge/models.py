"""World-state models: ships, planets, wormholes, sectors.

Field names track the original structs (WARSHP, GALPLNT, GALWORM in
GEMAIN.H) so the salvage spec reads directly onto this code.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum

from .data import NUMITEMS
from .geometry import Coord

MAXTORPS = 3
MAXMISSL = 3
MAXDECOY = 10


class Status(IntEnum):        # GESTAT_*
    AVAIL = 0
    USER = 1
    AUTO = 2
    IDLE = 3


class ShieldStat(IntEnum):    # SHIELDUP/DN/DM
    UP = 1
    DOWN = 2
    DAMAGED = 3


# Ship.where encodes location mode (original int convention kept):
#   -1 dead/out, 0 normal space, 1 hyperspace, 10+n orbiting planet n.
WHERE_DEAD = -1
WHERE_NORMAL = 0
WHERE_HYPER = 1
WHERE_ORBIT_BASE = 10


@dataclass
class Torpedo:
    channel: int = 255      # firing ship id (255 = empty slot)
    distance: int = 0       # remaining flight distance; 0 = inert


@dataclass
class Missile:
    channel: int = 255
    distance: int = 0
    energy: int = 0         # warhead charge set at launch


@dataclass
class Mine:
    channel: int = 255      # owner ship id (255 = free slot)
    timer: int = 0
    coord: Coord = field(default_factory=Coord)


@dataclass
class Ship:
    id: int
    userid: str
    shipname: str = " <NO NAME> "
    shpclass: int = 1                    # slot in GameData.classes
    status: Status = Status.AVAIL

    coord: Coord = field(default_factory=Coord)
    heading: float = 0.0
    head2b: float = 0.0
    speed: float = 0.0                   # 1000.0 == warp 1
    speed2b: float = 0.0
    where: int = WHERE_NORMAL

    energy: float = 50000.0
    damage: float = 0.0
    topspeed: int = 0                    # rated warp; derated by abuse
    warncntr: int = 0

    phasr: float = 100.0                 # phaser charge 0-100%
    phasrtype: int = 1                   # mark
    shieldtype: int = 1                  # mark
    shieldstat: ShieldStat = ShieldStat.DOWN
    shield: int = 0                      # charge
    cloak: int = 0                       # -n damaged, 0 off, 1..2 engaging, 10 up
    jammer: int = 0                      # ticks of jam remaining

    tactical: int = 0                    # <0 = damaged (system timers)
    helm: int = 0
    firecntl: int = 0
    repair: int = 0
    cantexit: int = 0                    # battle-lock ticks
    destruct: int = 0                    # self-destruct countdown
    hostile: int = 0                     # 10+n while attacking planet n
    hypha: int = 0                       # hyper-phaser cooldown
    minesnear: bool = False
    lastfired: int = -1                  # ship id last to fire on us
    lock: int = -1                       # our locked target

    items: list[int] = field(default_factory=lambda: [0] * NUMITEMS)
    ltorps: list[Torpedo] = field(default_factory=lambda: [Torpedo() for _ in range(MAXTORPS)])
    lmissl: list[Missile] = field(default_factory=lambda: [Missile() for _ in range(MAXMISSL)])
    decout: list[int] = field(default_factory=lambda: [0] * MAXDECOY)

    def in_game(self) -> bool:
        return self.status in (Status.USER, Status.AUTO)


@dataclass
class ItemStock:                        # ITEM struct per planet item
    qty: int = 0
    rate: int = 0                        # production effort %
    sell: bool = False                   # sell to others?
    reserve: int = 0
    markup2a: int = 0                    # unit sale price to others
    sold2a: int = 0


@dataclass
class Planet:
    plnum: int                           # 1-based slot within sector
    coord: Coord
    name: str = ""
    userid: str = ""                     # owner ("" = unclaimed)
    environ: int = 0                     # 0-3
    resource: int = 0                    # 0-3
    cash: int = 0
    debt: int = 0
    tax: int = 0
    taxrate: int = 0
    password: str = "none"
    beacon: str = ""
    spyowner: str = ""
    teamcode: int = 0
    items: list[ItemStock] = field(default_factory=lambda: [ItemStock() for _ in range(NUMITEMS)])


@dataclass
class Wormhole:
    plnum: int
    coord: Coord
    destination: Coord
    name: str = ""
    visible: bool = True


@dataclass
class Sector:
    xsect: int
    ysect: int
    objects: list[Planet | Wormhole] = field(default_factory=list)

    def object_at(self, plnum: int) -> Planet | Wormhole | None:
        for o in self.objects:
            if o.plnum == plnum:
                return o
        return None
