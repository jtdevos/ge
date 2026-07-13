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
- `salvage/` — **ground truth for the remake**, extracted from the
  original. `salvage/spec/*.md` documents the mechanics with
  file-level provenance; `salvage/data/*.toml` holds the game's
  numbers (ship classes, 244 config options, balance constants).
  Start at `salvage/README.md`. When remake behavior is in question,
  the spec wins; when the spec is in question, the C source wins —
  and the spec should be corrected in the same change.
- Remake code (Python) lives at the top level as it grows (planned:
  `ge/` package for the sim + server).

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
cadences together (details in `salvage/spec/universe.md` and
`salvage/README.md`):

- **1 s**: rotation, acceleration, movement (each ship processed every
  3rd tick), self-destruct countdown; NPC spawn/AI dispatch.
- **6 s**: energy recharge, flux autoload, shields, cloak, repairs,
  incoming torpedo/missile/mine resolution, ion cannons, death check.
- **Planet sweep**: continuous walk of all planets, self-calibrated so
  a full pass ≈ `PLANTOCK` config minutes (production, spies, revolts).
- **Nightly**: planet scoring, report mail, mail purge, team scores,
  roster ranking.

## Commands

No build/test infrastructure exists yet for the remake. Currently
useful:

- Validate the extracted data files:
  `python3 -c "import tomllib,glob; [tomllib.load(open(f,'rb')) for f in glob.glob('salvage/data/*.toml')]"`
- `ships.toml`/`config.toml` were generated mechanically from
  `mbmgemp/MBMGESHP.MSG` / `MBMGEMSG.MSG`; if they need regeneration,
  the parsers are ~60-line scripts described in `salvage/README.md`
  (single-line `.MSG` option entries: `NAME {prompt: default} TYPE range`).

## Licensing caveat

The repo `README.md` says Apache 2.0, but every original source header
and `mbmgemp/README.TXT` says **GPL v2**. Unresolved. Flag this when
relevant (e.g. before publishing derived code); don't silently assert
either license in new files.
