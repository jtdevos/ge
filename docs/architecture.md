# Remake Architecture

Design decisions and current state of the Galactic Empire remake.
This document (plus the [salvage docs](salvage.md) and the code
itself) is intended to be enough context to pick the project up cold.

## Goals and non-goals

- A hobby/exploration project. Success is "even a few people play it."
- **Faithful to the original's feel and numbers** for the first
  playable version: same mechanics, same balance constants, same
  terse command interface, same rhythm. Modernizing the *experience*
  comes later, deliberately, once the faithful baseline exists.
- Not nostalgic about the *implementation*: the original's C, Btrieve,
  and MajorBBS scaffolding are reference material, not templates.
- Simplicity of hosting beats scalability: one process, one SQLite
  file, a handful of players.

## Delivery: SSH-first

1. **SSH server** (AsyncSSH, planned) — `ssh play.example.com` from
   any terminal. This is the primary client.
2. **Native "embellished terminal" client** (maybe, later) — a
   terminal emulator wrapped in retro chrome (CRT phosphor,
   Alien-movie cockpit aesthetics), pointed at the same SSH server.
3. **Web client** (distant third) — xterm.js over a websocket bridge.

Because the server speaks plain ANSI/VT100, clients 2 and 3 require no
server changes. That's the point of choosing SSH first.

Identity plan: SSH public keys (first connection with a new key
creates a commander). No passwords.

## The load-bearing seam: sim vs. presentation

The original entangles game logic and output completely (`prf()`
calls inside physics code). The remake's one deliberate structural
divergence is a hard boundary:

- **The sim core (`ge/`) never formats text and never does I/O.** It
  mutates world state and emits `Event`s — keyed by the original MSG
  message names, scoped SELF/SECTOR/RANGE/GAME mirroring the
  original's output routines (`outprfge`/`outsect`/`outrange`/
  `outwar`).
- **The session layer (not yet built) never computes game rules.** It
  parses commands into sim orders and renders events into text —
  initially line-mode output faithful to the original, later possibly
  a full-screen mode consuming the very same event stream.

This is what keeps the door open for a hybrid/full-screen interface
without rewriting the sim.

## The sim core (`ge/`)

Synchronous and deterministic on purpose: `Sim.tick()` advances one
game second; all randomness flows through an injected `random.Random`;
there is no asyncio in the core. An asyncio runner (the future server)
will call `tick()` on a wall-clock cadence; tests call it directly.

| Module | Contents |
|---|---|
| `ge/data.py` | Typed loader for `salvage/data/*.toml` (ship classes, config, constants) |
| `ge/geometry.py` | Port of `GELIB.C`: bearings, vectors, sector coordinates |
| `ge/models.py` | `Ship`/`Planet`/`Wormhole`/`Sector` dataclasses, field names tracking the original structs |
| `ge/universe.py` | Lazy sector generation incl. wormhole back-links and the fixed neutral sector |
| `ge/events.py` | The sim→presentation event contract |
| `ge/sim.py` | Tick loop, movement/energy/shields/incoming-ordnance, player orders |
| `ge/demo.py` | `python -m ge.demo`: watch the tick loop run |

### Tick cadences (preserved from the original — the balance numbers
assume them)

- **1 s** (original `warrti2`): rotation, acceleration, movement,
  self-destruct countdown. Each ship is processed every **3rd** tick
  (the original staggered channels mod 3), so per-tick rates are
  effectively per-3-seconds per ship. Port numbers and stagger
  together or renormalize knowingly.
- **6 s** (original `warrti`): energy recharge, flux autoload, shield
  charge, cloak upkeep, repairs, incoming torpedo/missile resolution,
  decoy/jammer countdowns, death check.
- **Planet sweep** (not yet built): continuous walk of all planets,
  self-calibrated so one full pass ≈ `PLANTOCK` config minutes;
  production, spies, revolts.
- **Nightly** (not yet built): planet scoring, report mail, purges,
  team scores, roster.

### Status (July 2026)

Done and tested: data loading, geometry, universe generation, movement
(impulse/warp/rotate/orbit), hyperspace transitions, engine-overspeed
blowouts, universe edge, gravity and wormhole transit, energy/flux,
shields (charge/hit/repair), cloak, incoming torpedoes/missiles with
decoys, jammer/battle-lock countdowns, self-destruct, random system
damage, death (minus kill rewards).

Next milestones (in rough order; TODOs in `ge/sim.py`):

1. Firing side of combat: lock-on rolls, phasers/hyper-phasers,
   torpedo/missile launch, mines, zippers ([combat spec](spec/combat.md))
2. `killem()` kill rewards: loot, scoring, planet-map capture
3. Scanning (`sca se/ra/pl/sh`) and reports — first presentation-layer
   consumers
4. Session layer: command parser + line-mode renderer over stdin, then
   AsyncSSH
5. Persistence (SQLite), planet economy tick, cyborg AI, teams/mail

## Persistence plan

SQLite (WAL mode), one file, replacing the original's four Btrieve
files and one flat text file (schema sketch in
[meta spec](spec/meta.md) — the original's table layout maps over
almost directly). Live state stays in memory like the original; the DB
is the between-sessions truth. Not yet implemented.

## Sources of truth, in order

1. `salvage/data/*.toml` for numbers; `docs/spec/*.md` for mechanics.
2. When the spec is ambiguous or suspect: the original C in
   `mbmgemp/` decides — and the spec gets corrected in the same
   change.
3. Known original quirks and deliberate bug-compatibility decisions
   are listed at the end of [salvage.md](salvage.md).
