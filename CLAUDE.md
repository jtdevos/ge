# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repository is

A modern remake of **Galactic Empire** (GE), the 1988–94 real-time
multiplayer space-conquest door game for MajorBBS/Worldgroup by Michael
B. Murdock — plus the complete original C source it's being rebuilt
from. The remake's goal: faithful to the original's *feel and numbers*,
modern in implementation. It is a hobby project; simplicity of hosting
beats scalability.

## Repository layout

- `mbmgemp/` — original game source (K&R-ish C, MajorBBS module).
  **Reference material: do not modify.** It does not build on modern
  systems (requires the MajorBBS SDK and Btrieve); nobody should try.
  Other original-era directories: `mbmgemap/` (sysop map utility),
  `mbmgecvt/` (DB converter), `register/` (shareware registration —
  irrelevant).
- `docs/` — remake documentation: `docs/architecture.md` (design,
  status, roadmap), `docs/salvage.md` (extraction notes, original's
  runtime model, known quirks), `docs/spec/*.md` (mechanics reference
  with file-level provenance). Start at `docs/README.md`.
- `salvage/data/*.toml` — **ground truth numbers** (ship classes,
  config options, balance constants), loaded by the remake at runtime;
  `salvage/tools/` regenerates them from the `.MSG` files.
  When remake behavior is in question, the spec wins; when the spec is
  in question, the C source wins — and the spec should be corrected in
  the same change.
- `ge/` — the remake: deterministic Python sim core (tick loop,
  movement/energy/shields/incoming-ordnance so far). `tests/` covers
  it. Session/SSH layers do not exist yet.

## Remake architecture decisions (agreed with the owner)

- **Python + asyncio**, one process, one shared world — mirroring the
  original's runtime model. Persistence via **SQLite** (replaces
  Btrieve). Delivery is **SSH-first** via AsyncSSH; the server emits
  plain ANSI/VT100 so terminal-wrapper and web clients need no server
  changes.
- **POC interface is line-based**, replicating the original command
  prompt (3-letter prefix commands, push-based async output between
  prompts). A full-screen/hybrid mode may come later, therefore:
- **Hard seam between sim and presentation**: the sim core never
  formats output; session/rendering code never computes game rules.
  The sim emits events and answers queries. This is the one deliberate
  divergence from the original code (which mixes `prf()` calls into
  game logic).
- Game data (ship stats, prices, constants) is loaded from
  `salvage/data/*.toml`, not hardcoded — same values, sysop-tunable
  like the original.

## The original's tick model (must be preserved)

Balance constants are tuned to these cadences — port numbers and
cadences together (details in `docs/spec/universe.md` and
`docs/salvage.md`):

- **1 s**: rotation, acceleration, movement (each ship processed every
  3rd tick), self-destruct countdown; NPC spawn/AI dispatch.
- **6 s**: energy recharge, flux autoload, shields, cloak, repairs,
  incoming torpedo/missile/mine resolution, ion cannons, death check.
- **Planet sweep**: continuous walk of all planets, self-calibrated so
  a full pass ≈ `PLANTOCK` config minutes (production, spies, revolts).
- **Nightly**: planet scoring, report mail, mail purge, team scores,
  roster ranking.

## Commands

- Tests: `.venv/bin/python -m pytest -q` (create the venv with
  `python3 -m venv .venv && .venv/bin/pip install pytest`). Single
  test: `.venv/bin/python -m pytest tests/test_movement.py -k warp -q`.
- Watch the sim run: `.venv/bin/python -m ge.demo [seed]`.
- Regenerate extracted data after fixing an extractor:
  `python3 salvage/tools/extract_ships.py` /
  `python3 salvage/tools/extract_config.py`.

The sim core (`ge/sim.py`) is synchronous and deterministic — no
asyncio, no I/O; `Sim.tick()` is one game second, all randomness goes
through the injected `Random`. Tests hand-seed empty sectors around
the test area so lazy universe generation can't drop a planet under a
moving ship.

## Licensing

The project is **GPL v2 or later**, matching the original author's
grant (source headers and `mbmgemp/README.TXT`). The remake code is a
derivative work and stays GPL v2+; don't introduce dependencies or
copied code with incompatible licenses. (An earlier Apache 2.0 label
from the SourceForge→GitHub mirror was corrected in July 2026.)
