# Galactic Empire

> It is 3250 in the standard year, 975 years since man has developed
> inter-planetary space navigation…

**Galactic Empire** (GE) is a real-time multiplayer space exploration
and conquest game written by Michael B. Murdock for MajorBBS/Worldgroup
systems, 1988–1994. Players fly warships through a procedurally
generated galaxy, colonize planets, run economies, form teams, and
fight each other and the dreaded Cybertrons — all through a terse
command prompt over a modem.

This repository contains two things:

1. **The complete original source** (`mbmgemp/` and friends, C,
   GPL v2+) — preserved as reference material. It requires the
   MajorBBS SDK and Btrieve and does not build on modern systems.
2. **A remake, in progress** — an exploratory project to bring GE back
   as an SSH-hosted game: faithful to the original's mechanics,
   balance, and feel, but built in modern Python.

## The remake (exploratory — expect the ground to shift)

This is a hobby archaeology-and-rebuilding project, being figured out
as it goes. The approach so far:

- **Salvage pass** — the original C was systematically mined for
  ground truth: every game mechanic documented with provenance
  ([docs/spec/](docs/spec/)), and every number (34 ship classes, 300+
  config options, the hand-tuned balance constants) extracted into
  TOML ([salvage/data/](salvage/data/)). The story of that dig, and
  the original's runtime model, is in [docs/salvage.md](docs/salvage.md).
- **Sim core** — a deterministic, I/O-free simulation (`ge/`) ported
  from the spec: tick loop, movement/warp/hyperspace physics, energy,
  shields, incoming ordnance, self-destruct, death. No combat
  *firing*, economy, NPCs, or network layer yet.
- **Planned** — the rest of combat, then a line-mode session layer
  replicating the original prompt, served over SSH (AsyncSSH), with
  SQLite persistence. Design decisions, rationale, and the current
  roadmap live in [docs/architecture.md](docs/architecture.md).

**Full documentation, including a reconstructed player's manual,
starts at [docs/](docs/README.md).** The docs are written so that the
repository itself is all the context anyone (human or AI) needs to
continue the work.

## Next steps

Candidate topics for upcoming sessions, roughly in dependency order —
though this is an exploration, so any of these could be picked up (or
abandoned) next:

- **Firing side of combat** — lock-on rolls, phasers/hyper-phasers,
  torpedo/missile launch, mines, zippers. The *receiving* side is
  already in the sim; this makes ships dangerous
  ([spec](docs/spec/combat.md)).
- **Kill rewards** — the original `killem()` flow: loot transfer,
  score award/deduction, cash transfer, planet-map capture
  ([spec](docs/spec/combat.md)).
- **Scanning and reports** — `sca`/`rep`/`nav`, the first real
  consumers of sim queries and the contact-letter table that firing
  commands target by.
- **Session layer** — command parser + line-mode renderer, first over
  stdin (playable single-player smoke test), then over SSH via
  AsyncSSH with public-key identity.
- **Message text extraction** — pull the original's voice (prompts,
  combat messages, taunts) out of `MBMGEMSG.MSG` so events render as
  the real thing; later, the ANSI screens in `MBMGEGRF.C`.
- **Persistence** — SQLite schema mapped from the original's Btrieve
  files ([spec](docs/spec/meta.md)); save/load the world between runs.
- **Planet economy tick** — production, food/starvation, revolts,
  spies; the offline-empire half of the game
  ([spec](docs/spec/economy.md)).
- **Cyborg AI** — the spawner and cybertron hunt/attack state machine;
  makes the universe hostile without other players
  ([spec](docs/spec/cyborgs.md)).
- **Retro client experiments** — point cool-retro-term at the SSH
  server for the green-phosphor feel; longer-term, a custom
  terminal-wrapper client (CRT shader, Alien-cockpit chrome).

## Running what exists

Requires Python ≥ 3.11. No runtime dependencies; pytest for tests.

```sh
python3 -m venv .venv
.venv/bin/pip install pytest

# run the test suite
.venv/bin/python -m pytest -q

# watch the sim tick: spawns a ship, orders warp 5, prints the
# event stream for two minutes of game time
.venv/bin/python -m ge.demo [seed]
```

There is nothing playable yet — `ge.demo` is a smoke test of the
simulation, not a game client.

Regenerating the extracted data (only needed if the extractors
change): `python3 salvage/tools/extract_ships.py` and
`python3 salvage/tools/extract_config.py`.

## Repository map

| Path | What |
|---|---|
| [`docs/`](docs/README.md) | Remake documentation: architecture, salvage notes, mechanics spec |
| [`salvage/data/`](salvage/data/) | The original's numbers as TOML (loaded by the remake at runtime) |
| `salvage/tools/` | Extractors that generated the data files from the original `.MSG` files |
| [`ge/`](ge/) | The remake: Python sim core |
| `tests/` | pytest suite for the sim core |
| `mbmgemp/` | **Original source** (do not modify) — game module, plus the author's docs in `mbmgemp/GE/DOCS/` |
| `mbmgemap/`, `mbmgecvt/`, `register/` | Original-era utilities (map tool, DB converter, shareware registration) |

## License

GE is free software licensed under the
[GNU General Public License, version 2](LICENSE) or (at your option)
any later version, as released by its original author — see the
notices in the source headers and `mbmgemp/README.TXT`. The remake
code in this repository is licensed under the same terms.

(Earlier revisions of this repository labeled the project Apache 2.0;
that labeling was an error introduced when the code was mirrored from
SourceForge — the author's GPL v2+ grant is the operative license.)
