# Universe, Sectors, and Navigation

Mechanics salvaged from `GEMAIN.C` (tick loop), `GEFUNCS.C` (movement),
`GEPLANET.C` (sector/planet generation), `GELIB.C` (geometry),
`GECMDS.C` (`coord1`/`coord2`). Config names refer to
`salvage/data/config.toml`; constants to `salvage/data/constants.toml`.

## Coordinate system

- Positions are a pair of doubles `(x, y)`. **1.0 coordinate unit = one
  sector.** The fractional part of a coordinate is the position within
  the sector, displayed as an integer 0–9999 (fraction × `SSMAX`
  = 10000). Lore-wise a sector is 10000×10000 parsecs.
- `coord1(c) = floor(c)` → the sector number (int, can be negative).
  `coord2(c) = frac(c) * 10000` → position within sector.
- The navigable universe spans sector −`UNIVMAX`..+`UNIVMAX` on both
  axes (config `UNIVMAX`, shipped default 300 → the documented
  "6000×6000 sector" galaxy is actually 600×600 by default; docs
  describe ±300).
- Heading is degrees 0–359, **0 = north (−y), 90 = east (+x)**:
  movement is `x += speed·sin(heading)`, `y −= speed·cos(heading)`.
- Distance is plain Euclidean on coords. Bearing to a target is
  reported relative to ship's heading as −180..+180 (negative = port).

### Universe edge

Checked every movement tick (config `UNIVWRAP` selects behavior):

- **Wrap on**: coordinate crossing +max flips to −max (torus).
- **Wrap off**: ship is stopped 2 sectors inside the edge
  (`coord = ±(univmax−2)`), speed zeroed, and takes flat `TELEDAM`
  (17%) hull damage ("teleport" jolt).

## Sectors and generation

Sectors are created lazily, the first time any ship's position (or a
wormhole destination) needs one. Generation (`xgetsector`):

- A new sector gets planets only if `rand % PLODDS == 0` (default 3 →
  1 in 3 sectors is non-empty). If so, it holds `rand % MAXPLSE`
  planetary objects (config default 5, hard max 9).
- Each object is a **wormhole** if `rand % WORMODDS == 0` (default 50),
  otherwise a **planet**.
- Objects are placed uniformly in the sector interior
  (offset 0.1–0.9 on each axis) with a minimum spacing of 0.07 sectors
  from each other (rejection-sampled).

### Planets

New planets get:

- `environment` and `resource` factors: each random 0–3.
- Unowned (`userid` empty), password `"none"`, no name until claimed.
- ~25% of new planets (`rndm(3.99) > 3`) spawn *populated*: all item
  production rates random 0–5%, plus 0–50,000 men (rate 5–30%) and
  0–3200 food (rate 15–30%). These are the colonizable finds.

### Wormholes

- A wormhole's destination is a uniformly random coordinate anywhere in
  the universe. Generating a wormhole immediately also generates its
  destination sector (with wormhole creation suppressed there, to
  prevent runaway cascades — see the delightful comment at
  `GEPLANET.C:392`). If the destination sector exists and has a free
  planet slot, a **return wormhole** is inserted there pointing back;
  if the sector is full (9 objects), the wormhole is one-way.
- Wormholes have a `visible` flag (always 1 as generated).
- Flying within 25/10000 sector of a wormhole teleports the ship to the
  destination, adds 5.5% damage, and clears any locked torpedoes and
  missiles chasing it. Warnings print at <250 and <50 range
  (approach messages differ from planets').

### The neutral zone (sector 0,0)

Sector 0,0 is special-cased everywhere (`neutral()`):

- On first generation it is built from the `S00PLNUM` (default 3)
  configured objects in the MSG file's S00 table: **Zygor**
  (planet 1, the shipyard world), **T-Station** (planet 2), and others.
  Zygor sells weapons/equipment (32,000 of each, markup 2× base);
  T-Station sells men, troops, and food (1,032,000 each).
- Every planet-update pass restocks Zygor (all 14 items to 1,032,000,
  sell=Y, markup `2×base + rand%base`) and T-Station (men/troops/food
  same treatment).
- Mines do not detonate in the neutral zone; self-destruct blast
  damage doesn't apply there; a running self-destruct countdown is
  cancelled on entering it; hostility flags clear on any sector change.
- Hostile acts in neutral space are penalized (config `SE100DAM`,
  "amt of damage when hostile in Neutral", default 10).
- A warning broadcast (message `ZAPHIM2`) is sent to the neutral zone
  every 120 seconds.

## Movement model

All rates below are per **1-second tick**; each ship is processed every
3rd tick (the 1s handler processes channels `n mod 3 == clicker`, so
effective per-ship cadence is 3 s — a remake porting per-tick rates
must keep this ×3 stagger or renormalize).

### Speed and warp

- Speed is stored in units where **1000 = warp 1**. Warp N = N×1000.
- Player sets a target (`speed2b`); actual speed converges at
  `acceleration` (ship class `max_accel`) per tick when accelerating,
  and 2× that when decelerating.
- Accelerating above warp 1 costs `ACCENGAMT` (120) energy per tick;
  below warp 1 acceleration is free. If energy runs out mid-accel,
  target speed drops to 0.
- While cruising above warp 1: `MOVENGUSE` (10) energy per movement
  tick; if energy falls below `MOVENGMIN` (3000) the ship is forced to
  decelerate to stop.
- Position advances `speed/65000` coordinate units per tick — warp 10
  ≈ 0.15 sectors/s; crossing a sector at warp 36 takes ~5 s.

### Hyperspace

Crossing warp 1 upward enters hyperspace (`where = 1`); dropping below
warp 1 returns to normal space (`where = 0`). Entering hyperspace:

- Forces shields down and cloak off.
- Clears all locked torpedoes and all deployed decoys.
- Announces entry/exit to the sector.

While in hyperspace, gravity is ignored and phasers become
hyper-phasers (see combat.md).

### Exceeding rated warp

Each ship class has `max_warp` (`topspeed`). Holding speed above it
rolls dice each tick: chance scales with how far over you are (factor
60 down to 5; `rand % factor == 0` triggers). First 5 triggers are
escalating warnings; the 6th **blows the engines**: topspeed → 0,
forced stop, +0–19 damage. If you slow down after warnings, your
engines are permanently derated to `topspeed / warnings` until repaired
(maintenance resets `topspeed` to class max).

Missiles chasing a ship die when it exceeds warp 4–7 (random per
occasion: `4 + rand%4`).

### Rotation

`rotateship` (1s tick, per-ship every 3s): heading converges to target
at `max_accel/10` degrees per tick, turning whichever direction is
shorter. (The `ROTAMT`/`ROTENGUSE` constants exist but the per-tick
rotation rate actually used is class acceleration ÷ 10; the `rot`
command charges energy at command time — see commands.md.)

### Gravity

Every movement tick in normal space (users only — cyborgs are immune),
distance to each object in the current sector is checked
(units of 1/10000 sector):

- < 250: "entering gravity" warning; < 50: stronger warning.
- < 25 of a **planet**: ship is destroyed (damage set to 101). You
  cannot fly into a planet; you must `orbit` it.
- < 25 of a **wormhole**: teleport (see above).

### Sector transitions

On crossing a sector boundary the game announces departure/arrival to
both sectors — but only if the ship's speed is below 21000 (warp 21+
moves you too fast to be noticed). Hostility flags reset, and an active
self-destruct cancels if the new sector is neutral.

### Beacons

Planets can carry a beacon message (75 chars). While a ship is in a
sector with a beacon, each movement tick has a 1-in-10 chance of
displaying it.

## Energy

- Pool max `ENGYMAX` (65000); trickle-recharge `ENGRECHG` (1) per 6s
  tick.
- When energy drops below `ENGYMIN` (5000), a **flux pod** (cargo item)
  is consumed automatically to refill to max, with a warning when the
  last pod is used.
- Spending checks keep a 500-energy floor ("fudge") — a ship can never
  quite drain itself to zero by acting.
- Consumers: acceleration/cruise (above), shields (`type×SHENGUSE`
  = type×100 per 6s tick), cloak (`CLENGUSE` config, default per tick),
  phaser charging, rotation, and weapon fire (see combat.md).

## Repairs and damage bookkeeping

- Hull damage is a double 0–100%; ≥100 = destroyed (see combat.md for
  death handling).
- `maintenance`-initiated repairs tick on the 6s handler: −3% damage
  per tick until clear, then phasers/tactical/helm/fire-control reset,
  shields forced down, and `topspeed` restored to class max. Repair is
  cancelled if battle-locked (`cantexit`).
- Random system damage (tactical, helm, shields, phasers, cloak, fire
  control) accrues from hits once hull damage > 20% — see combat.md.
