import dataclasses
from random import Random

import pytest

from ge.geometry import Coord
from ge.models import Sector, ShieldStat, WHERE_HYPER
from ge.sim import LOCKON_MISSILE, LOCKON_TORPEDO, Sim


@pytest.fixture
def sim():
    return Sim(rng=Random(42))


@pytest.fixture
def shooter(sim):
    s = sim.spawn_ship("shooter", shpclass=1, shipname="Shooter")
    for sx in range(95, 110):
        for sy in range(95, 110):
            sim.universe.sectors[(sx, sy)] = Sector(sx, sy)
    s.coord = Coord(100.5, 100.5)
    s.heading = s.head2b = 90.0   # facing east
    s.phasr = 100.0
    return s


@pytest.fixture
def target(sim, shooter):
    t = sim.spawn_ship("target", shpclass=1, shipname="Target")
    t.coord = Coord(100.51, 100.5)   # ~100 units due east of the shooter
    return t


def keys(events):
    return [e.key for e in events]


def test_phaser_hits_and_damages_unshielded_target(sim, shooter, target):
    assert sim.order_phaser(shooter, 0) is None
    evs = sim.drain_events()
    assert "PHITHIM" in keys(evs)
    assert "PHITYOU" in keys(evs)
    assert target.damage > 0
    assert target.lastfired == shooter.id
    assert shooter.cantexit == sim.d.const.FIRETICKS
    assert target.cantexit == sim.d.const.FIRETICKS
    assert shooter.phasr == 0.0


def test_phaser_deflected_by_shields_does_no_hull_damage(sim, shooter, target):
    target.shieldstat = ShieldStat.UP
    target.shield = 50
    assert sim.order_phaser(shooter, 0) is None
    evs = sim.drain_events()
    assert "PDEFLECT" in keys(evs)
    assert "PHITDEF" in keys(evs)
    assert target.damage == 0.0
    assert target.shield < 50


def test_phaser_misses_outside_beam_width(sim, shooter, target):
    target.coord = Coord(100.5, 100.49)   # north of the shooter, not east
    assert sim.order_phaser(shooter, 0) is None
    evs = sim.drain_events()
    assert "PHITHIM" not in keys(evs)
    assert target.damage == 0.0
    assert shooter.phasr == 0.0           # still fires, just hits nothing


def test_phaser_needs_minimum_charge(sim, shooter, target):
    shooter.phasr = 10.0
    assert sim.order_phaser(shooter, 0) is None
    evs = sim.drain_events()
    assert "NOFIREP" in keys(evs)
    assert target.damage == 0.0
    assert shooter.phasr == 10.0          # unlike a real shot, charge stays


def test_phaser_in_neutral_zone_zaps_the_shooter(sim, shooter, target):
    shooter.coord = sim.universe.get_sector_xy(0, 0).objects[0].coord.copy()
    assert sim.order_phaser(shooter, 0) is None
    evs = sim.drain_events()
    assert "ZAPHIM1" in keys(evs)
    assert shooter.damage == sim.d.cfg.SE100DAM
    assert shooter.phasr == 100.0         # early return: charge not spent


def test_firing_drops_shields_and_never_reraises(sim, shooter, target):
    shooter.shieldstat = ShieldStat.UP
    assert sim.order_phaser(shooter, 0) is None
    assert shooter.shieldstat == ShieldStat.DOWN
    assert "SHLDDN" in keys(sim.drain_events())


def test_no_phaser_system_refuses_to_fire(sim, shooter):
    cls = sim.d.classes[shooter.shpclass]
    sim.d.classes[shooter.shpclass] = dataclasses.replace(cls, max_phaser_type=0)
    assert sim.order_phaser(shooter, 0) == "PHASER0"


def test_phaser_recharges_after_firing(sim, shooter, target):
    sim.order_phaser(shooter, 0)
    sim.drain_events()
    assert shooter.phasr == 0.0
    for _ in range(6):
        sim.tick()
    assert shooter.phasr == pytest.approx(shooter.phasrtype * sim.d.const.PRELOAD)
    assert shooter.phasr > 0.0


def test_hyperphaser_hits_and_damages_target(sim, shooter, target):
    shooter.where = target.where = WHERE_HYPER
    assert sim.order_hyperphaser(shooter, 0) is None
    evs = sim.drain_events()
    assert "HPHITM" in keys(evs)
    assert "HPHITU" in keys(evs)
    assert target.damage > 0
    assert target.lastfired == shooter.id
    assert shooter.cantexit == sim.d.const.FIRETICKS
    assert target.cantexit == sim.d.const.FIRETICKS
    assert shooter.energy == 50000.0 - sim.d.const.HPFIRAMT
    assert shooter.hypha == 1


def test_hyperphaser_ignores_ship_in_normal_space(sim, shooter, target):
    shooter.where = WHERE_HYPER   # target stays in normal space
    assert sim.order_hyperphaser(shooter, 0) is None
    evs = sim.drain_events()
    assert "HPHITM" not in keys(evs)
    assert target.damage == 0.0


def test_hyperphaser_misses_outside_beam_width(sim, shooter, target):
    shooter.where = target.where = WHERE_HYPER
    target.coord = Coord(100.5, 100.49)   # north of the shooter, not east
    assert sim.order_hyperphaser(shooter, 0) is None
    evs = sim.drain_events()
    assert "HPHITM" not in keys(evs)
    assert target.damage == 0.0


def test_hyperphaser_misses_outside_scan_range(sim, shooter, target):
    shooter.where = target.where = WHERE_HYPER
    target.coord = Coord(120.5, 100.5)   # ~20 sector-units east: past scan range
    assert sim.order_hyperphaser(shooter, 0) is None
    evs = sim.drain_events()
    assert "HPHITM" not in keys(evs)
    assert target.damage == 0.0


def test_hyperphaser_needs_minimum_energy(sim, shooter, target):
    shooter.where = target.where = WHERE_HYPER
    shooter.energy = 1000.0
    assert sim.order_hyperphaser(shooter, 0) is None
    evs = sim.drain_events()
    assert "HNOFIRP" in keys(evs)
    assert target.damage == 0.0
    assert shooter.energy == 1000.0
    assert shooter.hypha == 0


def test_hyperphaser_in_neutral_zone_zaps_the_shooter(sim, shooter, target):
    shooter.where = WHERE_HYPER
    shooter.coord = sim.universe.get_sector_xy(0, 0).objects[0].coord.copy()
    assert sim.order_hyperphaser(shooter, 0) is None
    evs = sim.drain_events()
    assert "ZAPHIM1" in keys(evs)
    assert shooter.damage == sim.d.cfg.SE100DAM
    assert shooter.energy == 50000.0       # early return: energy not spent


def test_lockon_succeeds_at_close_range(sim, shooter, target):
    assert sim._lockon(shooter, target, LOCKON_TORPEDO) is True
    evs = sim.drain_events()
    assert "LOCK2" in keys(evs)
    assert shooter.cantexit == sim.d.const.FIRETICKS
    assert target.cantexit == sim.d.const.FIRETICKS


def test_lockon_fails_at_marginal_range_but_still_battle_locks(sim, shooter, target):
    target.coord = Coord(104.5, 100.5)   # 4 sectors out: in range, weak lock
    assert sim._lockon(shooter, target, LOCKON_TORPEDO) is False
    evs = sim.drain_events()
    assert "LOCK3" in keys(evs)
    assert "LOCK4" in keys(evs)
    assert shooter.cantexit == sim.d.const.FIRETICKS
    assert target.cantexit == sim.d.const.FIRETICKS


def test_lockon_missile_uses_its_own_factor(sim, shooter, target):
    target.coord = Coord(104.5, 100.5)   # fails missile lock too at this range
    assert sim._lockon(shooter, target, LOCKON_MISSILE) is False
    assert "LOCK3" in keys(sim.drain_events())


def test_lockon_torpedo_cannot_catch_a_fast_target(sim, shooter, target):
    target.speed = 1500.0                # above warp 1
    assert sim._lockon(shooter, target, LOCKON_TORPEDO) is False
    evs = sim.drain_events()
    assert "LOCK3" in keys(evs)
    assert shooter.cantexit == sim.d.const.FIRETICKS   # still battle-locked


def test_lockon_fails_outside_scan_range(sim, shooter, target):
    target.coord = Coord(111.5, 100.5)   # 11 sectors: past class-1 scan range
    assert sim._lockon(shooter, target, LOCKON_TORPEDO) is False
    evs = sim.drain_events()
    assert "LOCK5" in keys(evs)
    assert shooter.cantexit == 0         # no battle lock: never found the target
    assert target.cantexit == 0


def test_lockon_fails_against_fully_cloaked_target(sim, shooter, target):
    target.cloak = 10
    assert sim._lockon(shooter, target, LOCKON_TORPEDO) is False
    assert "LOCK5" in keys(sim.drain_events())


def test_lockon_refuses_target_in_neutral_zone(sim, shooter, target):
    target.coord = sim.universe.get_sector_xy(0, 0).objects[0].coord.copy()
    assert sim._lockon(shooter, target, LOCKON_TORPEDO) is False
    evs = sim.drain_events()
    assert "FCNONO" in keys(evs)
    assert shooter.cantexit == 0


def test_lockon_refuses_with_broken_fire_control(sim, shooter, target):
    shooter.firecntl = 1
    assert sim._lockon(shooter, target, LOCKON_TORPEDO) is False
    assert "FCBROKE" in keys(sim.drain_events())


def test_lockon_refuses_while_jammed(sim, shooter, target):
    shooter.jammer = 1
    assert sim._lockon(shooter, target, LOCKON_TORPEDO) is False
    assert "JAMMER4" in keys(sim.drain_events())
