# 2. Navigation

Galactic Empire functions on a 360-degree compass and is strictly
two-dimensional.

```text
               315  0  45
                  \ | /
                   \|/
             270----*----90
                   /|\
                  / | \
               225 180 135
```

- **Galactic heading** — absolute direction; 0 is north, 90 east.
- **Bearing** — where something is relative to *your* nose, −180 to
  +180: negative to port (left), positive to starboard (right), 0
  dead ahead, ±180 astern.
- **Heading** (of a contact) — which way *it* faces relative to you:
  0 means it faces you, 180 means it's showing you its engines.

Positions within a sector read 0–9999 on each axis, measured from the
sector's top-left corner. `report nav` shows your sector, position,
heading and speed; `navigate <x> <y>` gives bearing and distance to
any sector (to its upper-left corner, so expect to fine-tune on
arrival).

## Turning

`rotate <deg>` turns you relative to your current heading (negative =
port), `rotate @<deg>` turns to an absolute galactic heading. The
ship always swings through the shorter arc. You can also steer while
under way by giving a second argument to `impulse` or `warp`.

> **Salvage note:** the guide says the ship "must be stationary
> first" to rotate. In the source the command works at any speed —
> what's true is that the *turn is not instant*: the helm converges
> on the ordered heading at a rate set by your class's acceleration
> (acceleration ÷ 10 degrees per movement tick — a Dreadnought
> out-turns a Freight Barge fifteen to one). Each `rotate` costs 30
> energy ([universe spec](../spec/universe.md)).

## Impulse and warp

Two drives, one speed scale: warp 1 = lightspeed = 1000 speed units.

- `impulse <n>` — sub-light, n = 0–99, as a percentage of lightspeed.
  Impulse acceleration is free of energy cost.
- `warp <n>` — n = 0–50, limited by your hull's rated maximum.
  Accelerating past warp 1 draws 120 energy per tick; cruising above
  warp 1 draws a steady trickle (10 per movement tick). If your
  energy pool runs low (below 3000) the ship forces itself to a stop
  — keep flux pods aboard (see [chapter 3](03-ships-and-equipment.md)).

Speed changes are not instant: actual speed converges on your ordered
speed at your class acceleration per tick (braking is twice as fast
as accelerating). At warp 10 you cross a sector in roughly twenty
seconds; at warp 36, about five.

### Hyperspace

Crossing warp 1 puts you **in hyperspace**; dropping back below warp
1 returns you to normal space. Entering hyperspace:

- forces your shields down and your cloak off,
- sheds every torpedo chasing you (but *not* missiles),
- abandons any decoys you had out,
- and is announced to the sector.

In hyperspace normal phasers are useless and torpedoes cannot be
fired; the hyper-phaser becomes your weapon (see
[chapter 5](05-combat.md)). Gravity does not touch you in hyperspace.

### Pushing the engines

You may push the warp engines up to half again past their rated
maximum. The farther and longer you overdrive, the more likely
trouble: the engines will warn you up to five times, each warning
permanently derating your top speed until repaired — and on the sixth
protest they **blow**, leaving you stopped, damaged, and limping at
impulse until a maintenance crew restores your rated warp
([universe spec](../spec/universe.md)).

## Gravity kills

In normal space, every planet and wormhole in your sector pulls at
you. You'll be warned entering the gravity well (range 250) and
warned again harder at range 50. **Within range 25 of a planet, your
ship is destroyed.** You cannot fly *to* a planet; you `orbit` it
(legal within range 250) — orbiting stops the ship and parks you
safely.

## Wormholes

Wormholes are rare galactic anomalies caused by a paired spatial
singularity, appearing on scans among a sector's planets. Fly within
range 25 of one and you are pulled through and ejected at its
terminal sector — which may be anywhere in the galaxy — taking about
5.5% hull damage in transit, and shedding any torpedoes or missiles
chasing you. Most wormholes are bidirectional; a return wormhole
usually waits at the far end. One-way wormholes have been speculated
to exist (they occur when the destination sector has no room for the
return portal).

> **Salvage note:** the guide's ritual — "approach directly at about
> 1/4 impulse" or you will "miss the event horizon" or "oscillate
> between terminal sectors" — is flavor. In the source, any approach
> within range 25 transits, at any speed; the damage and the lost
> weapon locks are real ([universe spec](../spec/universe.md)).
> Approaching slowly is still wise: the well announces itself at
> range 250, and at warp you can overshoot the window or blunder into
> a planet's kill radius in the same sector.

## Being seen

Crossing a sector boundary announces your departure and arrival to
ships in both sectors — unless you're moving faster than warp 21,
too quick to be noticed. Planets can carry an owner's **beacon
message**; while you loiter in the sector it will flash at you now
and then. Sector arrivals, beacons, taunts and battle noise are the
texture of travel; `set filter on` if you want quiet.
