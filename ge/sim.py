"""Simulation core and tick loop.

Faithful port of the original's real-time handlers (see
docs/spec/universe.md and combat.md for the mechanics, and
docs/salvage.md for the cadence model):

    warrti2 (1 s)  -> Sim.tick(): rotation, acceleration, movement,
                      self-destruct; each ship processed every 3rd tick
    warrti  (6 s)  -> systems: flux autoload, repair, shields, cloak,
                      incoming ordnance/decoys/jammer, recharge, death

Deliberately synchronous and deterministic: the caller (an asyncio
runner, a test) calls tick() once per game second. All randomness goes
through the injected RNG.

Not yet ported (next milestones): torpedo/missile launch commands
(the lock-on roll they share is ported as `_lockon`), mines/zippers,
scanning, planet economy tick, cyborg AI, scoring/killem loot.
"""

from __future__ import annotations

import math
from random import Random

from .data import GameData, I_FLUXPOD
from .events import Event, Scope, Visibility
from .geometry import (Coord, cbearing, cdistance, normal, samesect,
                       sector_of, smallest, vector)
from .models import (ShieldStat, Ship, Status, Wormhole, WHERE_HYPER,
                     WHERE_NORMAL, WHERE_ORBIT_BASE)
from .universe import Universe

ALWAYS = Visibility.ALWAYS
FILTER = Visibility.FILTER

# lockon() weapon kind
LOCKON_TORPEDO = 0
LOCKON_MISSILE = 1


class Sim:
    def __init__(self, data: GameData | None = None, rng: Random | None = None,
                 universe: Universe | None = None):
        self.d = data or GameData()
        self.rng = rng or Random()
        self.universe = universe or Universe(self.d, self.rng)
        self.ships: dict[int, Ship] = {}
        self.events: list[Event] = []
        self.t = 0
        self._clicker = 0
        self._next_id = 0

    # -- helpers ---------------------------------------------------------

    def _rndm(self, mod: float) -> float:
        return mod * self.rng.random()

    def _rnd(self) -> int:
        return self.rng.randrange(0, 2**15)

    def cls(self, ship: Ship):
        return self.d.classes[ship.shpclass]

    def _emit(self, key: str, scope: Scope, vis: Visibility, *,
              ship: int | None = None, coord: Coord | None = None,
              exclude: int | None = None, **params) -> None:
        self.events.append(Event(self.t, key, scope, vis, ship=ship,
                                 coord=coord.copy() if coord else None,
                                 exclude=exclude, params=params))

    def drain_events(self) -> list[Event]:
        out, self.events = self.events, []
        return out

    def receivers_of(self, ev: Event) -> list[int]:
        """Resolve an event to receiving ship ids (original out* semantics)."""
        if ev.scope is Scope.SELF:
            return [ev.ship] if ev.ship is not None else []
        out = []
        for s in self.ships.values():
            if not s.in_game() or s.id == ev.exclude:
                continue
            if ev.scope is Scope.GAME:
                out.append(s.id)
            elif ev.scope is Scope.SECTOR:
                if ev.coord is not None and samesect(s.coord, ev.coord):
                    out.append(s.id)
            elif ev.scope is Scope.RANGE:
                if ev.coord is not None and self.cls(s).type == "USER":
                    dist = cdistance(ev.coord, s.coord) * 10000
                    if 1 < dist < self.cls(s).scan_range:
                        out.append(s.id)
        return out

    # -- lifecycle -------------------------------------------------------

    def spawn_ship(self, userid: str, shpclass: int = 1,
                   shipname: str = " <NO NAME> ") -> Ship:
        """Port of initshp(): new ship in the neutral sector."""
        cls = self.d.classes[shpclass]
        neutral = self.universe.get_sector_xy(0, 0)
        while True:
            c = Coord(self._rndm(0.9999), self._rndm(0.9999))
            if all(cdistance(c, o.coord) * 10000 >= 1000
                   for o in neutral.objects):
                break
        ship = Ship(id=self._next_id, userid=userid, shipname=shipname,
                    shpclass=shpclass, coord=c, status=Status.USER,
                    topspeed=cls.max_warp)
        ship.heading = ship.head2b = self._rndm(359.99)
        ship.items[I_FLUXPOD] = 3
        self._next_id += 1
        self.ships[ship.id] = ship
        return ship

    # -- player orders (sim-facing verbs behind the helm commands) --------

    def order_warp(self, ship: Ship, warp: int, degrees: int = 0) -> str | None:
        """cmd_warp(). Returns an error message key, or None on success."""
        cls = self.cls(ship)
        if cls.max_warp == 0:
            return "WARP01"
        if ship.topspeed == 0:
            return "WARPSPD2"
        if warp < 0:
            return "WARP02"
        if warp > ship.topspeed + ship.topspeed // 2:
            return "WARP03"
        if ship.helm != 0:
            return "HLBROKE"
        if warp > ship.topspeed:
            self._emit("WARP04", Scope.SELF, ALWAYS, ship=ship.id,
                       topspeed=ship.topspeed)
        self._leave_orbit(ship)
        deg = normal(ship.heading + degrees)
        self._emit("ENGFIRE", Scope.SELF, ALWAYS, ship=ship.id, deg=int(deg))
        ship.speed2b = 1000.0 * warp
        ship.head2b = deg
        return None

    def order_impulse(self, ship: Ship, percent: int, degrees: int = 0) -> str | None:
        """cmd_impulse(): sub-warp speed as a percent of warp 1."""
        if ship.where == WHERE_HYPER:
            return "IMPULSE1"
        if not 0 <= percent <= 99:
            return "NUMOOR"
        if ship.helm != 0:
            return "HLBROKE"
        self._leave_orbit(ship)
        deg = normal(ship.heading + degrees)
        self._emit("ENGFIRE", Scope.SELF, ALWAYS, ship=ship.id, deg=int(deg))
        ship.speed2b = 1000.0 * (percent / 100.0)
        ship.head2b = deg
        # a hard burn while cloaked leaks a fuzzy bearing (GECMDS.C:525)
        if ship.cloak == 10 and ship.speed2b > (self._rndm(200.0) + 10.0):
            for other in self.ships.values():
                if other.in_game() and other.id != ship.id and other.jammer == 0:
                    dist = cdistance(ship.coord, other.coord) * 10000
                    if dist < self.cls(other).scan_range / 2:
                        bearing = int(cbearing(other.coord, ship.coord,
                                               other.heading) + .5)
                        bearing += (self._rnd() % 20) - 10
                        self._emit("CLOK3", Scope.SELF, ALWAYS,
                                   ship=other.id, bearing=bearing)
        return None

    def order_rotate(self, ship: Ship, degrees: float,
                     absolute: bool = False) -> str | None:
        """cmd_rotate(). Relative -180..180, or absolute 0..359 ('@deg')."""
        if ship.helm != 0:
            return "HLBROKE"
        if absolute and not 0 <= degrees < 360:
            return "NUMOOR"
        if not self._useenergy(ship, self.d.const.ROTENGUSE):
            return "NOROTPW"
        deg = degrees if absolute else normal(ship.heading + degrees)
        self._emit("NOWTURN", Scope.SELF, ALWAYS, ship=ship.id, deg=int(deg))
        ship.head2b = float(deg)
        return None

    def order_flux(self, ship: Ship) -> str | None:
        """cmd_flux(): manually burn a flux pod."""
        if ship.items[I_FLUXPOD] == 0:
            return "NOFLUX"
        ship.items[I_FLUXPOD] -= 1
        ship.energy = float(self.d.const.ENGYMAX)
        self._emit("FLUXLOAD", Scope.SELF, ALWAYS, ship=ship.id)
        if ship.items[I_FLUXPOD] == 0:
            self._emit("LASTFLUX", Scope.SELF, ALWAYS, ship=ship.id)
        return None

    def order_orbit(self, ship: Ship, plnum: int) -> str | None:
        """cmd_orbit(): enter orbit of planet plnum in this sector."""
        if ship.where == WHERE_HYPER:
            return "ORBIT4"
        if ship.where >= WHERE_ORBIT_BASE:
            return "ORBIT3"
        sect = self.universe.get_sector(ship.coord)
        obj = sect.object_at(plnum)
        if obj is None:
            return "FOOLISH"
        if isinstance(obj, Wormhole):
            return "ORBIT0"
        if cdistance(ship.coord, obj.coord) * 10000 > 250:
            return "ORBIT2"
        self._emit("ORBIT1", Scope.SELF, ALWAYS, ship=ship.id,
                   plnum=plnum, name=obj.name)
        ship.where = WHERE_ORBIT_BASE + plnum
        ship.speed = ship.speed2b = 0.0
        return None

    def order_destruct(self, ship: Ship) -> str | None:
        """cmd_destruct(): start the self-destruct countdown."""
        if self.universe.neutral(ship.coord):
            return "SELFD1A"
        self._emit("SELFD1", Scope.SELF, ALWAYS, ship=ship.id)
        ship.destruct = self.d.const.COUNTDOWN
        return None

    def order_phaser(self, ship: Ship, degrees: int, focus: int = 1) -> str | None:
        """firep(): fire phasers in normal space, relative bearing, focus
        0-5. Mirrors GECMDS.C's firep() only — the where==1 dispatch to
        hyper-phasers (firehp) and margv validation both live in
        cmd_phas(), a session-layer concern not yet built."""
        if self.cls(ship).max_phaser_type == 0:
            return "PHASER0"
        if ship.phasrtype <= 0:
            return "PHA01"
        if ship.cloak > 0:
            return "PCLOKUP"
        # a fire attempt always drops shields, even if this shot then
        # fizzles for lack of charge — and per GEFUNCS.C:2419 they are
        # never re-raised afterwards (see docs/spec/combat.md)
        if ship.shieldstat == ShieldStat.UP:
            self._emit("SHLDDN", Scope.SELF, FILTER, ship=ship.id)
            ship.shieldstat = ShieldStat.DOWN
        if ship.phasr < self.d.const.PMINFIRE:
            self._emit("NOFIREP", Scope.SELF, ALWAYS, ship=ship.id)
            return None
        if self.universe.neutral(ship.coord):
            self._zaphim(ship)
            return None
        self._firephasers(ship, degrees, focus)
        ship.phasr = 0.0
        return None

    def order_hyperphaser(self, ship: Ship, degrees: int) -> str | None:
        """firehp(): fire hyper-phasers, relative bearing. Mirrors
        GECMDS.C's firehp() only — the where==1 dispatch and the
        hypha==0 ("still cooling down") gate both live in cmd_phas(), a
        session-layer concern not yet built."""
        C, cfg = self.d.const, self.d.cfg
        if ship.energy < C.HPMINFIR:
            self._emit("HNOFIRP", Scope.SELF, ALWAYS, ship=ship.id)
            return None
        if self.universe.neutral(ship.coord):
            self._zaphim(ship)
            return None
        self._firehyperphasers(ship, degrees)
        return None

    def order_abort(self, ship: Ship) -> str | None:
        """cmd_abort(): cancel self-destruct."""
        if ship.destruct <= 0:
            return "SELFD5"
        if ship.destruct < 10:
            self._emit("SELFD4A", Scope.RANGE, ALWAYS, coord=ship.coord,
                       shipname=ship.shipname)
        self._emit("SELFD4", Scope.SELF, ALWAYS, ship=ship.id)
        ship.destruct = 0
        return None

    def _leave_orbit(self, ship: Ship) -> None:
        if ship.where >= WHERE_ORBIT_BASE:
            self._emit("LEAVEORB", Scope.SELF, ALWAYS, ship=ship.id)
            ship.where = WHERE_NORMAL
            ship.repair = 0

    # -- firing (GECMDS.C) --------------------------------------------------

    def _zaphim(self, ship: Ship) -> None:
        """zaphim(): firing from the neutral zone zaps the firer instead."""
        self._emit("ZAPHIM1", Scope.SELF, ALWAYS, ship=ship.id)
        ship.damage += self.d.cfg.SE100DAM

    def _firephasers(self, ship: Ship, degrees: int, focus: int) -> None:
        """The beam sweep in firep(): every ship within focus+PHABIAS
        degrees of the fire direction is a potential hit."""
        C, cfg = self.d.const, self.d.cfg
        deg = normal(ship.heading + degrees)
        self._emit("PFIRED", Scope.SELF, FILTER, ship=ship.id,
                   charge=int(ship.phasr), focus=focus)
        ship.cantexit = C.FIRETICKS
        for target in self.ships.values():
            if target.id == ship.id or not target.in_game():
                continue
            if target.where == WHERE_HYPER and ship.phasrtype < cfg.PHATOWRP:
                continue
            if self.universe.neutral(target.coord):
                continue
            bearing = vector(ship.coord, target.coord)
            if smallest(bearing, deg) >= focus + C.PHABIAS:
                continue
            dam = self._phaser_damage(ship, target, focus)
            if dam < 1:
                continue
            target.lastfired = ship.id
            target.cantexit = C.FIRETICKS
            ship.cantexit = C.FIRETICKS
            if target.shieldstat != ShieldStat.UP:
                target.damage += dam
                self._emit("PHITHIM", Scope.SELF, ALWAYS, ship=ship.id,
                           dam=dam, shipname=target.shipname)
                self._emit("PHITYOU", Scope.SELF, ALWAYS, ship=target.id,
                           dam=dam, shipname=ship.shipname)
            else:
                self._shieldhit(target, dam)
                self._emit("PDEFLECT", Scope.SELF, ALWAYS, ship=ship.id,
                           shipname=target.shipname)
                self._emit("PHITDEF", Scope.SELF, ALWAYS, ship=target.id,
                           dam=dam, shipname=ship.shipname)
            self._randamage(target)

    def _phaser_damage(self, ship: Ship, target: Ship, focus: int) -> int:
        """pdamage() + firep()'s post-scaling: falloff by distance/focus/
        charge, then by shooter mark, target tonnage, and hyperspace."""
        C, cfg = self.d.const, self.d.cfg
        dist = cdistance(ship.coord, target.coord) * 10000.0
        reach = 20000.0 + ship.phasrtype * 4000.0
        dd = max(1.0 - dist / reach, 0.0)
        fd = 1.0 - focus / 11.0
        dam = int(cfg.PDAMMAX * (dd ** cfg.PFIRDST) * (fd * fd)
                  * (ship.phasr / 100.0))
        factor = (dam * ((1 + ship.phasrtype) / 2.5)
                  / (1.0 + self.cls(target).max_tonnage / C.TONFACT))
        if target.where == WHERE_HYPER:
            factor /= 2.0
        dam = int(factor)
        if ship.phasrtype == 20:      # sysop weapon: instant kill
            dam = 101
        return dam

    def _firehyperphasers(self, ship: Ship, degrees: int) -> None:
        """The beam sweep in firehp(): fixed HPBEAMW-degree beam, hits only
        ships also in hyperspace and within the shooter's scan range.
        Unlike firep(), there's no cloak check, no shield interaction, and
        no minimum-damage gate — any target caught in beam and range takes
        a hit, even a 0-damage one."""
        C, cfg = self.d.const, self.d.cfg
        deg = normal(ship.heading + degrees)
        self._emit("HPFIRED", Scope.SELF, FILTER, ship=ship.id, degrees=deg)
        ship.energy -= C.HPFIRAMT
        ship.hypha = 1
        ship.cantexit = C.FIRETICKS
        scan_range = self.cls(ship).scan_range
        for target in self.ships.values():
            if target.id == ship.id or not target.in_game():
                continue
            if target.where != WHERE_HYPER:
                continue
            if self.universe.neutral(target.coord):
                continue
            bearing = vector(ship.coord, target.coord)
            if smallest(bearing, deg) >= C.HPBEAMW:
                continue
            dist = cdistance(ship.coord, target.coord) * 10000.0
            if dist >= scan_range:
                continue
            dam = self._hyperphaser_damage(ship, target, dist)
            target.lastfired = ship.id
            target.cantexit = C.FIRETICKS
            ship.cantexit = C.FIRETICKS
            target.damage += dam
            self._emit("HPHITM", Scope.SELF, ALWAYS, ship=ship.id,
                       dam=dam, shipname=target.shipname)
            self._emit("HPHITU", Scope.SELF, ALWAYS, ship=target.id,
                       dam=dam, shipname=ship.shipname)
            self._randamage(target)

    def _hyperphaser_damage(self, ship: Ship, target: Ship, dist: float) -> int:
        """pdamage()'s where==1 branch + firehp()'s post-scaling: falloff
        over a fixed 40000-unit range, scaled by shooter mark and divided
        by target tonnage. No focus term, no charge term, no /2.5 shift."""
        C, cfg = self.d.const, self.d.cfg
        dd = max(1.0 - dist / 40000.0, 0.0)
        dam = int(cfg.HPDAMMAX * (dd ** cfg.HPFIRDST))
        factor = (dam * ship.phasrtype
                  / (1.0 + self.cls(target).max_tonnage / C.TONFACT))
        dam = int(factor)
        if ship.phasrtype == 20:      # sysop weapon: instant kill
            dam = 101
        return dam

    def _lockon(self, ship: Ship, target: Ship, kind: int) -> bool:
        """lockon(): the fire-control roll shared by torpedo and missile
        launch (GECMDS.C's torp()/cmd_missl() dispatch here before
        spawning a chaser — those launch commands themselves aren't
        ported yet). `kind` is LOCKON_TORPEDO or LOCKON_MISSILE.

        Fails outright (no battle-lock either side) if fire control is
        damaged, the shooter is jammed, or the target is in the neutral
        zone. Otherwise rolls a lock factor from range (and, for
        torpedoes, combined speed) and always battle-locks both ships,
        win or lose, once the target is found in scan range."""
        C, cfg = self.d.const, self.d.cfg
        if ship.firecntl > 0:
            self._emit("FCBROKE", Scope.SELF, ALWAYS, ship=ship.id)
            return False
        if ship.jammer > 0:
            self._emit("JAMMER4", Scope.SELF, ALWAYS, ship=ship.id)
            return False
        if self.universe.neutral(target.coord):
            self._emit("FCNONO", Scope.SELF, ALWAYS, ship=ship.id)
            return False
        dist = cdistance(ship.coord, target.coord)
        if target.cloak >= 10 or dist * 10000.0 >= self.cls(ship).scan_range:
            self._emit("LOCK5", Scope.SELF, ALWAYS, ship=ship.id,
                       shipname=target.shipname)
            return False
        if kind == LOCKON_TORPEDO:
            if target.speed > 999:
                fact = 0.0
            else:
                speed = ship.speed + target.speed
                fact = (1.2 - speed / 5000.0) * ((5.0 - dist) / (cfg.TORFACT / 10.0))
        else:
            fact = (5.0 - dist) / (cfg.MISFACT / 10.0)
        target.cantexit = C.FIRETICKS
        ship.cantexit = C.FIRETICKS
        if fact > 0.7:
            self._emit("LOCK2", Scope.SELF, FILTER, ship=target.id,
                       shipname=ship.shipname)
            return True
        self._emit("LOCK3", Scope.SELF, FILTER, ship=ship.id,
                   shipname=target.shipname)
        self._emit("LOCK4", Scope.SELF, FILTER, ship=target.id,
                   shipname=ship.shipname)
        return False

    def _phasrstat(self, ship: Ship) -> None:
        """Phaser reload each systems tick (the preload block in
        checkdam()); self-repairs from a damaged (negative) state first."""
        C = self.d.const
        if ship.phasr < 0:
            ship.phasr += 1
            if ship.phasr == 0:
                self._emit("PHREPR", Scope.SELF, ALWAYS, ship=ship.id)
        elif ship.phasr < 100:
            if self._useenergy(ship, C.PENGUSE):
                preload = ship.phasrtype * C.PRELOAD
                if ship.phasr < C.PMINFIRE <= ship.phasr + preload:
                    self._emit("PHSRUP", Scope.SELF, ALWAYS, ship=ship.id)
                ship.phasr += preload
                if ship.phasr >= 100:
                    ship.phasr = 100.0
                    self._emit("PHSRMAX", Scope.SELF, ALWAYS, ship=ship.id)

    # -- the tick loop -----------------------------------------------------

    def tick(self) -> None:
        """Advance one game second."""
        self.t += 1

        # 1 s handler (warrti2): each ship every 3rd tick
        for ship in list(self.ships.values()):
            if ship.in_game() and ship.id % 3 == self._clicker:
                self._rotateship(ship)
                self._accel(ship)
                self._moveship(ship)
                self._destruct_tick(ship)
        self._clicker = (self._clicker + 1) % 3

        # 6 s handler (warrti): ship systems
        if self.t % 6 == 0:
            for ship in list(self.ships.values()):
                if ship.in_game():
                    self._fluxstat(ship)
                    self._repairship(ship)
                    self._shieldstat(ship)
                    self._cloakstat(ship)
                    self._phasrstat(ship)
                    self._checktm(ship)
                    self._recharge(ship)
                    self._checkdam(ship)

    # -- movement (GEFUNCS.C) ---------------------------------------------

    def _rotateship(self, ship: Ship) -> None:
        rotamt = self.cls(ship).acceleration / 10.0
        if ship.heading == ship.head2b:
            return
        diff = normal(ship.heading - ship.head2b)
        if diff >= 360.0 - rotamt or diff <= rotamt:
            ship.heading = ship.head2b
            self._emit("NOWTHER", Scope.SELF, FILTER, ship=ship.id,
                       deg=int(ship.heading))
        elif diff < 180:
            ship.heading = normal(ship.heading - rotamt)
        else:
            ship.heading = normal(ship.heading + rotamt)

    def _accel(self, ship: Ship) -> None:
        C = self.d.const
        if ship.speed < ship.speed2b:
            rate = float(self.cls(ship).acceleration)
            if (ship.speed2b >= 1000 and ship.speed // 1000 < 1
                    and (ship.speed + rate) // 1000 >= 1):
                self._hyperspace(ship, entering=True)
            if abs(ship.speed - ship.speed2b) <= rate:
                ship.speed = ship.speed2b
                self._emit("SPEEDIS", Scope.SELF, FILTER, ship=ship.id,
                           warp=self._showarp(ship.speed))
            else:
                usage = 0 if ship.speed < 1000 else C.ACCENGAMT
                if self._useenergy(ship, usage):
                    if int(ship.speed / 1000) != int((ship.speed + rate) / 1000):
                        self._emit("WARP", Scope.SELF, FILTER, ship=ship.id,
                                   warp=int((ship.speed + rate) / 1000))
                        # crossing warp 4-7 sheds pursuing missiles
                        if (ship.speed + rate) / 1000 >= 4 + self._rnd() % 4:
                            shed = False
                            for m in ship.lmissl:
                                if m.distance > 0:
                                    m.distance = 0
                                    shed = True
                            if shed:
                                self._emit("MISSL2", Scope.SELF, FILTER,
                                           ship=ship.id)
                    ship.speed += rate
                else:
                    self._emit("NOACCEL", Scope.SELF, ALWAYS, ship=ship.id,
                               speed=int(ship.speed))
                    ship.speed2b = 0.0
        elif ship.speed > ship.speed2b:
            rate = float(self.cls(ship).acceleration) * 2.0
            if (ship.speed2b < 1000 and ship.speed // 1000 >= 1
                    and (ship.speed - rate) // 1000 < 1):
                self._hyperspace(ship, entering=False)
            if abs(ship.speed - ship.speed2b) <= rate:
                ship.speed = ship.speed2b
                if ship.speed > 0:
                    self._emit("SPEEDIS", Scope.SELF, FILTER, ship=ship.id,
                               warp=self._showarp(ship.speed))
                else:
                    self._emit("SPEED0", Scope.SELF, FILTER, ship=ship.id)
            else:
                if int(ship.speed / 1000) != int((ship.speed - rate) / 1000):
                    if ship.speed > 0:
                        self._emit("WARP", Scope.SELF, FILTER, ship=ship.id,
                                   warp=int((ship.speed - rate) / 1000) + 1)
                    else:
                        self._emit("DEADSTOP", Scope.SELF, FILTER, ship=ship.id)
                ship.speed -= rate

    def _hyperspace(self, ship: Ship, entering: bool) -> None:
        if entering:
            if ship.shieldstat == ShieldStat.UP:
                self._emit("HYSHDN", Scope.SELF, FILTER, ship=ship.id)
                ship.shieldstat = ShieldStat.DOWN
            if ship.cloak > 0:
                self._emit("HYCLDN", Scope.SELF, FILTER, ship=ship.id)
                ship.cloak = 0
            self._emit("HYPERIN", Scope.SELF, FILTER, ship=ship.id)
            ship.where = WHERE_HYPER
            self._emit("HYPERIN2", Scope.SECTOR, FILTER, coord=ship.coord,
                       exclude=ship.id, shipname=ship.shipname)
            for t in ship.ltorps:
                t.distance = 0
            ship.decout = [0] * len(ship.decout)
        else:
            self._emit("HYPEROUT", Scope.SELF, FILTER, ship=ship.id)
            ship.where = WHERE_NORMAL
            self._emit("HYPEROU2", Scope.SECTOR, FILTER, coord=ship.coord,
                       exclude=ship.id, shipname=ship.shipname)

    def _moveship(self, ship: Ship) -> None:
        C = self.d.const
        if ship.speed <= 0:
            if ship.where == WHERE_HYPER:   # fix stuck users
                ship.where = WHERE_NORMAL
            return

        oldpos = ship.coord.copy()
        ship.coord.x += ship.speed * math.sin(math.radians(ship.heading)) / 65000.0
        ship.coord.y -= ship.speed * math.cos(math.radians(ship.heading)) / 65000.0

        # universe edge
        um = self.d.cfg.UNIVMAX
        if ship.where <= WHERE_HYPER:
            for axis in ("x", "y"):
                v = getattr(ship.coord, axis)
                if v > um:
                    if self.d.cfg.UNIVWRAP:
                        setattr(ship.coord, axis, v - um * 2)
                    else:
                        setattr(ship.coord, axis, float(um - 2))
                        self._telezip(ship)
                elif v < -um:
                    if self.d.cfg.UNIVWRAP:
                        setattr(ship.coord, axis, v + um * 2)
                    else:
                        setattr(ship.coord, axis, float(-(um - 2)))
                        self._telezip(ship)

        if not samesect(oldpos, ship.coord):
            ox, oy = sector_of(oldpos)
            nx, ny = sector_of(ship.coord)
            self._emit("MOVE1", Scope.SELF, FILTER, ship=ship.id,
                       from_x=ox, from_y=oy, to_x=nx, to_y=ny)
            if ship.speed < 21000.0:      # warp 21+ transits go unnoticed
                self._emit("MOVE2", Scope.SECTOR, FILTER, coord=oldpos,
                           exclude=ship.id, shipname=ship.shipname)
                self._emit("MOVE3", Scope.SECTOR, FILTER, coord=ship.coord,
                           exclude=ship.id, shipname=ship.shipname)
            ship.hostile = 0
            if ship.destruct > 0 and self.universe.neutral(ship.coord):
                self._emit("SELFD4", Scope.SELF, ALWAYS, ship=ship.id)
                ship.destruct = 0

        if ship.speed > 1000.0 and ship.status == Status.USER:
            self._overspeed_check(ship)
            self._useenergy(ship, C.MOVENGUSE)
            if ship.energy < C.MOVENGMIN:
                ship.speed2b = 0.0
                self._emit("MOVE4", Scope.SELF, FILTER, ship=ship.id)

        # Cybertrons ignore gravity
        if ship.where == WHERE_NORMAL and ship.status == Status.USER:
            self._gravity(ship)

        if ship.hostile > 0:
            self._checkdist(ship)
        # TODO: beacon display roll (needs planet beacons wired to sessions)

    def _overspeed_check(self, ship: Ship) -> None:
        """Engine abuse above rated warp: warnings, then a blowout."""
        intspeed = int(ship.speed / 1000.0)
        if intspeed > ship.topspeed and ship.speed <= ship.speed2b:
            diff = intspeed - ship.topspeed
            diff = (diff * 100) // intspeed
            diff = 60 - diff
            if diff < 0:
                diff = 5
            if self._rnd() % diff == 0:
                if ship.warncntr > 4:
                    self._emit("WARPBRK", Scope.SELF, ALWAYS, ship=ship.id)
                    ship.topspeed = 0
                    ship.speed2b = 0.0
                    ship.damage += self._rnd() % 20
                else:
                    self._emit("WARPFAST", Scope.SELF, FILTER, ship=ship.id,
                               warning=ship.warncntr)
                    ship.warncntr += 1
        elif ship.warncntr > 0:
            ship.topspeed = ship.topspeed // ship.warncntr
            ship.speed2b = ship.topspeed * 1000.0
            self._emit("WARPSPD", Scope.SELF, FILTER, ship=ship.id,
                       topspeed=ship.topspeed)
            ship.warncntr = 0

    def _telezip(self, ship: Ship) -> None:
        ship.speed = ship.speed2b = 0.0
        ship.damage += self.d.const.TELEDAM
        self._emit("TELEPORT", Scope.SELF, ALWAYS, ship=ship.id)

    def _gravity(self, ship: Ship) -> None:
        sect = self.universe.get_sector(ship.coord)
        for obj in sect.objects:
            dist = cdistance(ship.coord, obj.coord) * 10000
            if dist >= 250:
                continue
            is_worm = isinstance(obj, Wormhole)
            if dist >= 50:
                key = "GRAVWRM1" if is_worm else "GRAVITY1"
            elif dist >= 25:
                key = "GRAVWRM2" if is_worm else "GRAVITY2"
            else:
                key = "GRAVWRM3" if is_worm else "GRAVITY3"
            self._emit(key, Scope.SELF, ALWAYS, ship=ship.id, plnum=obj.plnum)
            if dist < 25:
                if is_worm:
                    ship.coord = obj.destination.copy()
                    ship.damage += 5.5
                    self._cleartm(ship.id)
                else:
                    ship.damage = 101.0   # flew into a planet

    def _checkdist(self, ship: Ship) -> None:
        """Hostility toward a planet lapses beyond 1000 units."""
        sect = self.universe.get_sector(ship.coord)
        obj = sect.object_at(ship.hostile - WHERE_ORBIT_BASE)
        if obj is not None:
            if cdistance(ship.coord, obj.coord) * 10000 > 1000:
                ship.hostile = 0

    def _destruct_tick(self, ship: Ship) -> None:
        C = self.d.const
        if ship.destruct <= 0:
            return
        ship.destruct -= 1
        if ship.destruct > 0:
            if ship.destruct in (10, 5, 2):
                key = {10: "SELFD2A", 5: "SELFD2B", 2: "SELFD2C"}[ship.destruct]
                self._emit(key, Scope.RANGE, ALWAYS, coord=ship.coord,
                           shipname=ship.shipname)
            self._emit("SELFD2", Scope.SELF, ALWAYS, ship=ship.id,
                       count=ship.destruct)
            return
        # boom
        self._emit("SELFD3", Scope.SELF, ALWAYS, ship=ship.id)
        ship.damage = 101.0
        self._emit("SELFD3A", Scope.RANGE, ALWAYS, coord=ship.coord,
                   shipname=ship.shipname)
        for other in self.ships.values():
            if not other.in_game() or other.id == ship.id:
                continue
            dist = cdistance(ship.coord, other.coord) * 10000
            if dist >= C.MINERANGE or self.universe.neutral(other.coord):
                continue
            dd = 1.0 - (dist / C.DESTRUCTRANGE)
            dd = max(dd, 0.0) ** 3
            dam = int(dd * self.d.cfg.MNDAMMAX) * ((ship.shpclass // 2) + 1)
            if other.shieldstat == ShieldStat.UP:
                dam = dam // (self._rnd() % 5 + other.shieldtype)
                self._emit("SELFD6", Scope.SELF, ALWAYS, ship=other.id, dam=dam)
                self._shieldhit(other, dam + 20)
            else:
                self._emit("SELFD7", Scope.SELF, ALWAYS, ship=other.id, dam=dam)
            other.damage += dam
            other.lastfired = -1   # self-destruct credits no one

    # -- 6 s systems tick (GEFUNCS.C) ---------------------------------------

    def _recharge(self, ship: Ship) -> None:
        C = self.d.const
        ship.energy = min(ship.energy + C.ENGRECHG, float(C.ENGYMAX))

    def _fluxstat(self, ship: Ship) -> None:
        C = self.d.const
        if ship.energy < C.ENGYMIN and ship.items[I_FLUXPOD] > 0:
            ship.energy = float(C.ENGYMAX)
            ship.items[I_FLUXPOD] -= 1
            self._emit("FLUXLOAD", Scope.SELF, ALWAYS, ship=ship.id)
            if ship.items[I_FLUXPOD] == 0:
                self._emit("LASTFLUX", Scope.SELF, ALWAYS, ship=ship.id)

    def _repairship(self, ship: Ship) -> None:
        if ship.repair <= 0:
            return
        if ship.cantexit > 0:
            self._emit("MAINT10", Scope.SELF, ALWAYS, ship=ship.id)
            ship.repair = 0
            return
        ship.damage = max(ship.damage - 3.0, 0.0)
        ship.repair = int(ship.damage / 3.0)
        if ship.repair <= 1:
            ship.repair = 0
            ship.damage = 0.0
            ship.phasr = 100.0
            ship.tactical = ship.helm = ship.firecntl = 0
            ship.shieldstat = ShieldStat.DOWN
            ship.shield = 0
            ship.topspeed = self.cls(ship).max_warp
            self._emit("MAINT7", Scope.SELF, ALWAYS, ship=ship.id)

    # shields (marks 1-19; 20 = sysop gear)

    def _charge_limits(self, ship: Ship) -> tuple[int, int]:
        maxcharge = 40 + ship.shieldtype * 10
        pcnt = (ship.shield * 100) // maxcharge
        return maxcharge, pcnt

    def _shieldstat(self, ship: Ship) -> None:
        C = self.d.const
        if ship.shieldstat == ShieldStat.UP:
            if ship.energy < C.SHMINPWR:
                ship.shieldstat = ShieldStat.DOWN
                ship.shield = 0
                self._emit("SHDNNOP", Scope.SELF, ALWAYS, ship=ship.id)
            else:
                self._shieldchg(ship)
        elif ship.shieldstat == ShieldStat.DAMAGED:
            self._shieldrep(ship)

    def _shieldchg(self, ship: Ship) -> None:
        C = self.d.const
        if ship.shieldtype < 20:
            ship.energy -= ship.shieldtype * C.SHENGUSE
        maxcharge, _ = self._charge_limits(ship)
        if ship.shieldtype == 20 and ship.shield < maxcharge:
            ship.shield = maxcharge - 1
        if ship.shield < maxcharge:
            ship.shield += ship.shieldtype * 3
            if ship.shield >= maxcharge:
                ship.shield = maxcharge
                self._emit("SHLDUP", Scope.SELF, FILTER, ship=ship.id)
            else:
                _, pcnt = self._charge_limits(ship)
                self._emit("SHLDAT", Scope.SELF, FILTER, ship=ship.id, pcnt=pcnt)

    def _shieldrep(self, ship: Ship) -> None:
        ship.shield += ship.shieldtype
        if ship.shieldtype == 20:
            ship.shield = 1
        if ship.shield > 0:
            ship.shieldstat = ShieldStat.DOWN
            ship.shield = 0
            self._emit("SHREPR", Scope.SELF, ALWAYS, ship=ship.id)

    def _shieldhit(self, ship: Ship, dam: int) -> int:
        """Knock charge off the shields; may knock them out entirely."""
        C = self.d.const
        dmax = 80 - ship.shieldtype * C.SHIELD_FACTOR
        if ship.shieldtype == 20 or dmax < 0:
            dmax = 0
        knock = int(dmax * (dam / 100.0))
        ship.shield -= knock
        if ship.shield <= 2:
            self._emit("SHDAMAG", Scope.SELF, ALWAYS, ship=ship.id)
            ship.shieldstat = ShieldStat.DAMAGED
            ship.shield -= knock * 3
        elif ship.shield < C.SHMINCHG:
            self._emit("SHKNKDN", Scope.SELF, ALWAYS, ship=ship.id)
        return knock

    def _cloakstat(self, ship: Ship) -> None:
        clenguse = self.d.cfg.CLENGUSE
        if ship.cloak > 0:
            if ship.energy < clenguse:
                ship.cloak = 0
                self._emit("CLOKNOP", Scope.SELF, ALWAYS, ship=ship.id)
                self._emit("CLOK2", Scope.RANGE, FILTER, coord=ship.coord)
            else:
                ship.energy -= clenguse
        elif ship.cloak < 0:
            ship.cloak += 1
            if ship.cloak == 0:
                self._emit("CLREPR", Scope.SELF, ALWAYS, ship=ship.id)

    def _ton_fact(self, ship: Ship, damfact: float) -> float:
        """Damage adjusted by the class damage factor (higher = tougher)."""
        return damfact / (self.cls(ship).damage_factor / 100.0)

    def _checktm(self, ship: Ship) -> None:
        """Incoming torpedoes/missiles, decoy/jammer/cloak countdowns."""
        cfg = self.d.cfg
        if ship.hypha > 0:
            ship.hypha -= 1
        if ship.cantexit > 0:
            ship.cantexit -= 1

        # torpedoes
        announced = False
        for torp in ship.ltorps:
            if torp.distance <= 1:
                continue
            if torp.distance <= cfg.TORPSPED:
                torp.distance = 0
                if ship.shieldstat == ShieldStat.UP:
                    damfact = self._ton_fact(ship, cfg.TDAMMAX * self._rndm(.5))
                    ship.damage += damfact
                    ship.lastfired = torp.channel
                    self._emit("THIT1", Scope.SELF, ALWAYS, ship=ship.id)
                    self._acctm(ship, "MTACC1", torp.channel)
                    self._shieldhit(ship, (self._rnd() % 20) + 10)
                else:
                    self._emit("THIT2", Scope.SELF, ALWAYS, ship=ship.id)
                    damfact = self._ton_fact(
                        ship, cfg.TDAMMAX * (self._rndm(.5) + .5))
                    ship.damage += damfact
                    self._acctm(ship, "MTACC1", torp.channel)
                self._randamage(ship)
            else:
                if self._decoy_eats(ship, torp, limit=5000):
                    self._emit("TORDEST", Scope.SELF, FILTER, ship=ship.id)
                    continue
                torp.distance -= cfg.TORPSPED
                if not announced:
                    self._emit("TORP1", Scope.SELF, FILTER, ship=ship.id)
                    announced = True

        # missiles
        announced = False
        for mis in ship.lmissl:
            if mis.distance <= 0:
                continue
            if mis.distance < cfg.MISLSPED:
                mis.distance = 0
                energy = self._ton_fact(ship, float(mis.energy))
                size = ("very small" if energy < 1000 else
                        "light" if energy < 5000 else
                        "moderate" if energy < 20000 else
                        "strong" if energy < 40000 else "devastating")
                if ship.shieldstat == ShieldStat.UP:
                    ship.damage += cfg.MDAMMAX * (energy / 50000.0) * self._rndm(.1)
                    self._emit("MHIT1", Scope.SELF, ALWAYS, ship=ship.id, size=size)
                    self._acctm(ship, "MTACC2", mis.channel)
                    power = int((energy / 999) * (self._rndm(.5) + .5))
                    self._shieldhit(ship, power)
                else:
                    self._emit("MHIT2", Scope.SELF, ALWAYS, ship=ship.id, size=size)
                    ship.damage += (cfg.MDAMMAX * (energy / 50000.0)
                                    * (self._rndm(.5) + .5))
                    self._acctm(ship, "MTACC2", mis.channel)
                self._randamage(ship)
            else:
                if self._decoy_eats(ship, mis, limit=3000):
                    self._emit("MISDEST", Scope.SELF, FILTER, ship=ship.id)
                    continue
                mis.distance -= cfg.MISLSPED
                if not announced:
                    self._emit("MISSL1", Scope.SELF, FILTER, ship=ship.id)
                    announced = True

        # decoys age out
        for i, life in enumerate(ship.decout):
            if life > 0:
                ship.decout[i] = life - 1
                if ship.decout[i] == 0:
                    self._emit("DECGONE", Scope.SELF, FILTER, ship=ship.id)

        # jammer wears off
        if ship.jammer > 0:
            ship.jammer -= 1
            if ship.jammer == 0:
                self._emit("JAMMER5", Scope.SELF, FILTER, ship=ship.id)

        # cloak staging: 1 -> 2 -> 10 (fully cloaked)
        if ship.cloak == 1:
            ship.cloak = 2
        elif ship.cloak == 2:
            ship.cloak = 10
            self._emit("CLOKUP", Scope.SELF, ALWAYS, ship=ship.id)

    def _decoy_eats(self, ship: Ship, ordnance, limit: int) -> bool:
        for i, life in enumerate(ship.decout):
            if life > 0 and ordnance.distance < limit:
                if self._rnd() % self.d.cfg.DECODDS == 0:
                    ship.decout[i] = 0
                    ordnance.distance = 0
                    return True
        return False

    def _acctm(self, ship: Ship, key: str, channel: int) -> None:
        """Credit an ordnance hit to its firing channel."""
        if channel != 255:
            self._emit(key, Scope.SELF, ALWAYS, ship=channel,
                       shipname=ship.shipname)
            ship.lastfired = channel
        else:
            ship.lastfired = -1

    def _cleartm(self, channel: int) -> None:
        """Orphan all ordnance fired by a channel (owner left/died)."""
        for other in self.ships.values():
            if other.id == channel or not other.in_game():
                continue
            for t in other.ltorps:
                if t.channel == channel:
                    t.channel = 255
            for m in other.lmissl:
                if m.channel == channel:
                    m.channel = 255

    def _randamage(self, ship: Ship) -> None:
        """Random system damage roll after a hit (damage > 20%)."""
        cls = self.cls(ship)
        if ship.shieldtype == 20 or ship.damage <= 20.0:
            return
        if int(self._rndm((101.0 - ship.damage) / 1.5)) != 0:
            return
        system = self._rnd() % 6
        hit_timer = -int(self._rndm(ship.damage + 10.0))
        if system == 0:
            if cls.max_shield_type > 0:
                self._emit("RNDSHLD", Scope.SELF, ALWAYS, ship=ship.id)
                ship.shield = hit_timer
                ship.shieldstat = ShieldStat.DAMAGED
            else:
                self._emit("RNDXX1", Scope.SELF, ALWAYS, ship=ship.id)
        elif system == 1:
            if cls.max_phaser_type > 0:
                self._emit("RNDPHSR", Scope.SELF, ALWAYS, ship=ship.id)
                ship.phasr = float(hit_timer)
            else:
                self._emit("RNDXX2", Scope.SELF, ALWAYS, ship=ship.id)
        elif system == 2:
            if cls.has_torpedoes or cls.has_missiles:
                self._emit("RNDFCNT", Scope.SELF, ALWAYS, ship=ship.id)
                ship.firecntl = self._rnd() % 20
            else:
                self._emit("RNDXX3", Scope.SELF, ALWAYS, ship=ship.id)
        elif system == 3:
            if cls.has_cloak:
                self._emit("RNDCLOK", Scope.SELF, ALWAYS, ship=ship.id)
                ship.cloak = hit_timer
            else:
                self._emit("RNDXX4", Scope.SELF, ALWAYS, ship=ship.id)
        elif system == 4:
            self._emit("RNDTACT", Scope.SELF, ALWAYS, ship=ship.id)
            ship.tactical = hit_timer
        elif system == 5:
            self._emit("RNDNAVG", Scope.SELF, ALWAYS, ship=ship.id)
            ship.helm = hit_timer

    def _checkdam(self, ship: Ship) -> None:
        """Death check. Full killem() (loot, scoring) is a later milestone."""
        if ship.damage < 100.0:
            return
        ship.damage = 0.0
        self._emit("YOURDEAD", Scope.SELF, ALWAYS, ship=ship.id)
        self._emit("DIED", Scope.GAME, ALWAYS, exclude=ship.id,
                   shipname=ship.shipname, userid=ship.userid)
        self._cleartm(ship.id)
        ship.status = Status.AVAIL
        ship.where = -1
        # TODO killem(): kill credit via lastfired, loot transfer, score
        # award/deduction, planet-map capture, cash transfer (combat.md)

    # -- misc ---------------------------------------------------------------

    def _useenergy(self, ship: Ship, amount: float) -> bool:
        if ship.energy >= amount + 500:   # the original's 500 fudge floor
            ship.energy -= amount
            return True
        return False

    @staticmethod
    def _showarp(speed: float) -> str:
        if speed == 0.0:
            return "0.00"
        if speed / 1000.0 > 99.999:
            return "Hyper"
        return f"{speed / 1000.0:.2f}"
