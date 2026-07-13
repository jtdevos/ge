# Galactic Empire — Salvage Pass

Ground truth extracted from the original Worldgroup/MajorBBS source
(`mbmgemp/`, GE 3.2, © 1988–1994 Michael B. Murdock, GPL v2) to serve
as the reference for a modern remake. The goal: **faithful to the
feel and the numbers, modern in the making.**

Nothing here is remake code — it's a specification of what the
original actually does, with file/line-level provenance, so remake
behavior can be checked against it.

## Contents

### `salvage/data/` — the game's numbers, transliterated

| File | Source | Contents |
|---|---|---|
| [`ships.toml`](../salvage/data/ships.toml) | `MBMGESHP.MSG` | All 34 ship class slots (9 player hulls, 5 cybertrons, 3 droids, class 41, empty slots) with shipped default stats |
| [`config.toml`](../salvage/data/config.toml) | `MBMGEMSG.MSG` | All 300+ sysop-tunable options: per-item economics (max/weight/value/manhours/price ×14 items), shield & phaser mark prices (×19), the neutral-sector planet table, and ~72 general settings |
| [`constants.toml`](../salvage/data/constants.toml) | `GEMAIN.H` | The compiled-in balance constants ("carefully chosen and refined… modify with caution") |

`ships.toml` and `config.toml` are generated mechanically from the
`.MSG` files by the scripts in `salvage/tools/`
(`python3 salvage/tools/extract_ships.py`,
`python3 salvage/tools/extract_config.py`; values validated with
`tomllib`). `constants.toml` was transcribed by hand with the original
comments.

### `docs/spec/` — mechanics documentation

| File | Covers | Main sources |
|---|---|---|
| [`universe.md`](spec/universe.md) | Coordinates, sector generation, planets, wormholes, neutral zone, movement/warp/hyperspace physics, energy | `GEPLANET.C`, `GEFUNCS.C`, `GELIB.C` |
| [`combat.md`](spec/combat.md) | Phasers, hyper-phasers, torpedoes, missiles, mines, decoys, jammers, zippers, cloak, shields, ion cannons, self-destruct, system damage, death & kill rewards | `GECMDS.C`, `GEFUNCS.C` |
| [`economy.md`](spec/economy.md) | Items, colonization, planet admin, production/food/revolts, trade, planetary assault, spies, maintenance | `GEPLANET.C`, `GECMDS.C`, `GEMAIN.C` |
| [`cyborgs.md`](spec/cyborgs.md) | NPC spawning, cybertron AI (skill, mercy rules, hunt state machine, tactics), the three droid types | `GECYBS.C`, `GEDROIDS.C` |
| [`meta.md`](spec/meta.md) | Session flow, persistence, scoring, nightly cleanup, teams, mail, user options, sysop tools, ship purchase | `GEMAIN.C`, `GEFUNCS.C`, `GECMDS.C` |
| [`commands.md`](spec/commands.md) | All 44 prompt commands with syntax, plus interaction conventions | `GECMDS.C`, `MBMGEHLP.MSG` |

## The original's runtime model (what a remake must reproduce)

One shared world in one process. All state in per-channel memory
arrays, flushed to Btrieve databases; the BBS scheduler drives
everything through timers:

- **1 s tick** — rotation/acceleration/movement (each ship every 3rd
  tick) and self-destruct countdowns; NPC spawner + AI dispatch.
- **6 s tick** — ship systems: energy recharge, flux autoload, shield
  charge, cloak upkeep, repairs, incoming torpedo/missile/decoy/mine
  resolution, ion cannon fire, death check.
- **Planet sweep** — walks the planet DB continuously, self-calibrated
  so one full pass ≈ `PLANTOCK` minutes; runs production, spies,
  revolts.
- **120 s** — neutral-zone warning broadcast.
- **Midnight** — planet scores, production report mail, mail purge,
  team scores, roster ranking.

Balance constants are tuned to these cadences; port the cadences with
the numbers.

## Not salvaged (deliberately)

- `SECURE.C`, `register/` — shareware copy-protection. Irrelevant.
- `MBMGEGRF.C` ANSI screens — the tactical/helm art should be
  extracted as templates when the remake's presentation layer exists
  (source of truth is still there to read).
- Full message text (`MBMGEMSG.MSG`, 6k lines) — the remake should
  read message strings from the original file (or a converted copy) so
  the game's voice survives; converting them all now would be noise.
- Btrieve details, MajorBBS API glue, Pharlap/DOS ifdefs.

## Known original quirks (bug-compatibility decisions to make)

- Treasury decay is applied once **per item** inside the production
  loop (14× per pass) — planets bleed cash much faster than the
  formula suggests at first read (`GEPLANET.C:286`).
- `cybupdate == 0` DB-flush branch in `GECYBS.C:481` appears
  unreachable (the author's own comment agrees).
- The docs say a 6000×6000-sector galaxy; the shipped default
  `UNIVMAX=300` gives 600×600.
- `sell` works only at Zygor but prints a generic usage error if tried
  elsewhere; `price`/`buy` share one code path distinguished by
  `margv[0]`.
- Mines give no warning to jammed ships *and* no detonation warning —
  jamming yourself is a mixed blessing.
- Fighter-raid ratio uses float math with an acknowledged bug comment
  (`GECMDS.C:3820`); behavior documented as-is in economy.md.
