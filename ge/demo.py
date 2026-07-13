"""Smoke-test the sim from a terminal: python3 -m ge.demo [seed].

Spawns a ship in the neutral sector, orders warp 5, and prints the
event stream for two minutes of game time. Not a game client — just a
way to watch the tick loop breathe.
"""

from __future__ import annotations

import sys
from random import Random

from .geometry import coord2, sector_of
from .sim import Sim


def main() -> None:
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    sim = Sim(rng=Random(seed))
    ship = sim.spawn_ship("demo", shpclass=1, shipname="Pathfinder")

    sx, sy = sector_of(ship.coord)
    print(f"Spawned {ship.shipname!r} ({sim.cls(ship).name}) in sector "
          f"{sx},{sy} at {coord2(ship.coord.x)},{coord2(ship.coord.y)}, "
          f"heading {ship.heading:.0f}")

    err = sim.order_warp(ship, 5, degrees=0)
    if err:
        print(f"warp order refused: {err}")
        return

    for _ in range(120):
        sim.tick()
        for ev in sim.drain_events():
            print(f"{ev}   (to ships {sim.receivers_of(ev)})")

    sx, sy = sector_of(ship.coord)
    print(f"\nAfter {sim.t}s: sector {sx},{sy} at "
          f"{coord2(ship.coord.x)},{coord2(ship.coord.y)}, "
          f"speed warp {ship.speed / 1000:.2f}, energy {ship.energy:.0f}, "
          f"damage {ship.damage:.1f}%")


if __name__ == "__main__":
    main()
