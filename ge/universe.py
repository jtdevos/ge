"""Lazy universe generation: port of getsector/xgetsector (GEPLANET.C).

Sectors exist only once something needs them. Generating a wormhole
also generates its destination sector (with wormhole creation
suppressed there to prevent cascades) and back-links a return wormhole
if the destination has a free slot. See salvage/spec/universe.md.
"""

from __future__ import annotations

from random import Random

from .data import (GameData, I_DECOYS, I_FIGHTER, I_FLUXPOD, I_FOOD,
                   I_IONCANNON, I_JAMMERS, I_MEN, I_MINE, I_MISSILE,
                   I_TORPEDO, I_TROOPS, I_ZIPPERS, NUMITEMS)
from .geometry import Coord, cdistance, coord1
from .models import Planet, Sector, Wormhole

# Zygor's shipyard shelves (build_plan_1): items stocked at 32000 each
ZYGOR_STOCK = [I_MISSILE, I_TORPEDO, I_IONCANNON, I_FLUXPOD, I_FIGHTER,
               I_DECOYS, I_MINE, I_JAMMERS, I_ZIPPERS]
STATION_STOCK = [I_TROOPS, I_MEN, I_FOOD]   # build_plan_2, 1032000 each


class Universe:
    def __init__(self, data: GameData, rng: Random):
        self.d = data
        self.rng = rng
        self.sectors: dict[tuple[int, int], Sector] = {}

    # rndm() in GELIB.C: uniform [0, mod]
    def _rndm(self, mod: float) -> float:
        return mod * self.rng.random()

    def _rnd(self) -> int:
        return self.rng.randrange(0, 2**15)   # gernd(): rand()

    def get_sector(self, coord: Coord) -> Sector:
        return self.get_sector_xy(coord1(coord.x), coord1(coord.y))

    def get_sector_xy(self, sx: int, sy: int) -> Sector:
        sect = self.sectors.get((sx, sy))
        if sect is None:
            sect = self._generate(sx, sy, suppress_worms=False)
        return sect

    def neutral(self, coord: Coord) -> bool:
        return coord1(coord.x) == 0 and coord1(coord.y) == 0

    # -- generation ------------------------------------------------------

    def _generate(self, sx: int, sy: int, suppress_worms: bool) -> Sector:
        sect = Sector(sx, sy)
        self.sectors[(sx, sy)] = sect   # register first: worm gen may recurse

        if sx == 0 and sy == 0:
            self._build_neutral(sect)
            return sect

        nplan = (self._rnd() % self.d.cfg.MAXPLSE
                 if self._rnd() % self.d.cfg.PLODDS == 0 else 0)

        coords: list[Coord] = []
        kinds: list[bool] = []          # True = wormhole
        for _ in range(nplan):
            wormy = (not suppress_worms
                     and self._rnd() % self.d.cfg.WORMODDS == 0)
            while True:
                c = Coord(sx + self._rndm(0.800) + 0.1,
                          sy + self._rndm(0.800) + 0.1)
                if all(cdistance(c, other) >= 0.0700 for other in coords):
                    break
            coords.append(c)
            kinds.append(wormy)

        for i, (c, wormy) in enumerate(zip(coords, kinds)):
            if wormy:
                sect.objects.append(self._build_wormhole(i + 1, c))
            else:
                sect.objects.append(self._build_planet(i + 1, c))
        return sect

    def _build_planet(self, plnum: int, c: Coord) -> Planet:
        pl = Planet(plnum=plnum, coord=c,
                    environ=int(self._rndm(3.999)),
                    resource=int(self._rndm(3.999)))
        if self._rndm(3.99) > 3:        # ~25%: spawns already populated
            for item in pl.items:
                item.rate = int(self._rndm(5.1))
            pl.items[I_MEN].qty = int(self._rndm(50000.0))
            pl.items[I_MEN].rate = 5 + int(self._rndm(25.0))
            pl.items[I_FOOD].qty = int(self._rndm(3200.0))
            pl.items[I_FOOD].rate = 15 + int(self._rndm(15.0))
        return pl

    def _build_wormhole(self, plnum: int, c: Coord, dest: Coord | None = None,
                        name: str = "") -> Wormhole:
        um = self.d.cfg.UNIVMAX
        if dest is None:
            dest = Coord(self._rndm(um * 2) - um, self._rndm(um * 2) - um)
        worm = Wormhole(plnum=plnum, coord=c, destination=dest, name=name)
        self._backlink(worm)
        return worm

    def _backlink(self, worm: Wormhole) -> None:
        """Generate the destination sector; add a return wormhole if room."""
        dx, dy = coord1(worm.destination.x), coord1(worm.destination.y)
        dsect = self.sectors.get((dx, dy))
        if dsect is None:
            dsect = self._generate(dx, dy, suppress_worms=True)
        if len(dsect.objects) < 9 and (dx, dy) != (0, 0):
            dsect.objects.append(Wormhole(
                plnum=len(dsect.objects) + 1,
                coord=worm.destination.copy(),
                destination=worm.coord.copy()))

    def _build_neutral(self, sect: Sector) -> None:
        """Sector 0,0 from the S00 config table (Zygor, station, portals)."""
        for np in self.d.neutral_planets:
            c = Coord(np.x / 10000.0, np.y / 10000.0)
            if np.type == 3:
                sect.objects.append(
                    self._build_wormhole(np.plnum, c, name=np.name))
                continue
            pl = Planet(plnum=np.plnum, coord=c, name=np.name,
                        userid=np.owner, environ=np.environment,
                        resource=np.resource)
            if np.type == 1:
                for i in ZYGOR_STOCK:
                    pl.items[i].qty = 32000
                    pl.items[i].sell = True
                    pl.items[i].markup2a = self.d.baseprice[i] * 2
            elif np.type == 2:
                for i in STATION_STOCK:
                    pl.items[i].qty = 1_032_000
                    pl.items[i].sell = True
                    pl.items[i].markup2a = self.d.baseprice[i] * 2
            sect.objects.append(pl)
