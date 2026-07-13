from random import Random

import pytest

from ge.data import I_FLUXPOD
from ge.geometry import Coord, sector_of
from ge.models import Sector, Status, WHERE_HYPER
from ge.sim import Sim


@pytest.fixture
def sim():
    return Sim(rng=Random(42))


@pytest.fixture
def ship(sim):
    """A ship parked in a hand-made empty region (no gravity surprises)."""
    s = sim.spawn_ship("test", shpclass=1, shipname="Testboat")
    for sx in range(95, 110):
        for sy in range(95, 110):
            sim.universe.sectors[(sx, sy)] = Sector(sx, sy)
    s.coord = Coord(100.5, 100.5)
    s.heading = s.head2b = 90.0   # due east
    return s


def keys(events):
    return [e.key for e in events]


def test_warp_accelerates_and_enters_hyperspace(sim, ship):
    assert sim.order_warp(ship, 5) is None
    sim.tick()
    evs = sim.drain_events()
    assert "HYPERIN" in keys(evs)          # crossed warp 1 on the way up
    assert "SPEEDIS" in keys(evs)
    assert ship.speed == 5000.0
    assert ship.where == WHERE_HYPER


def test_cruising_crosses_sectors_east(sim, ship):
    sim.order_warp(ship, 5)
    for _ in range(60):
        sim.tick()
    evs = sim.drain_events()
    sx, sy = sector_of(ship.coord)
    assert sy == 100                       # heading 90 = pure +x
    assert sx > 100
    moves = [e for e in evs if e.key == "MOVE1"]
    assert moves and moves[0].params["from_x"] == 100
    # warp 5 = 5000/65000 sectors per movement tick, ship moves every 3s
    assert ship.coord.x == pytest.approx(100.5 + 20 * 5000 / 65000.0)


def test_cruise_drains_energy(sim, ship):
    sim.order_warp(ship, 5)
    for _ in range(60):
        sim.tick()
    assert ship.energy < 50000.0


def test_universe_edge_telezip(sim, ship):
    ship.coord = Coord(299.99, 100.5)
    for sx in range(295, 301):
        sim.universe.sectors.setdefault((sx, 100), Sector(sx, 100))
    sim.order_warp(ship, 5)
    sim.tick()
    evs = sim.drain_events()
    assert "TELEPORT" in keys(evs)
    assert ship.coord.x == 298.0           # dumped 2 sectors inside the edge
    assert ship.speed == 0.0
    assert ship.damage == pytest.approx(17.0)   # TELEDAM


def test_rotate_snaps_at_high_accel(sim, ship):
    # Interceptor accel 5000 -> 500 deg/tick rotation: effectively instant
    assert sim.order_rotate(ship, -90) is None   # east -> north
    assert ship.energy == 50000.0 - 30           # ROTENGUSE
    sim.tick()
    assert ship.heading == 0.0
    assert "NOWTHER" in keys(sim.drain_events())


def test_flux_pod_autoloads_when_low(sim, ship):
    ship.energy = 4000.0                   # below ENGYMIN
    pods = ship.items[I_FLUXPOD]
    for _ in range(6):
        sim.tick()
    assert ship.items[I_FLUXPOD] == pods - 1
    assert ship.energy >= 60000.0
    assert "FLUXLOAD" in keys(sim.drain_events())


def test_destruction_at_full_damage(sim, ship):
    ship.damage = 101.0
    for _ in range(6):
        sim.tick()
    evs = sim.drain_events()
    assert "YOURDEAD" in keys(evs)
    assert ship.status == Status.AVAIL
    assert not ship.in_game()


def test_neutral_sector_has_configured_objects(sim):
    sect = sim.universe.get_sector_xy(0, 0)
    names = {getattr(o, "name", "") for o in sect.objects}
    assert "Zygor" in names
    assert "Tahanian Station" in names
    assert len(sect.objects) == 6
