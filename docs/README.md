# Documentation

Everything needed to pick this project up cold, in reading order:

1. [Repository README](../README.md) — what this project is, how to
   run the tests and demo.
2. [architecture.md](architecture.md) — remake design decisions, the
   sim/presentation seam, tick model, current status and next
   milestones.
3. [salvage.md](salvage.md) — how the original was mined for ground
   truth: the extracted data files, the original's runtime model, what
   was deliberately skipped, and known original quirks.
4. [spec/](spec/) — the mechanics reference, extracted from the
   original C with provenance:
   [universe](spec/universe.md) · [combat](spec/combat.md) ·
   [economy](spec/economy.md) · [cyborgs](spec/cyborgs.md) ·
   [meta](spec/meta.md) · [commands](spec/commands.md)
5. [original/](original/) — the recovered original player docs,
   transcribed verbatim: the 1994 Users Guide and the in-game help.
6. [manual/](manual/) — the reconstructed players manual: the
   original docs merged, corrected against source and shipped data,
   and completed — written from the original game's perspective. This
   is the remake's target player experience, and the eventual source
   for its in-game help text.

The original author's own files (user guide, sysop guide,
installation) remain untouched in `mbmgemp/GE/DOCS/` and
`mbmgemp/*.DOC`; `docs/original/` is the readable mirror of the
player-facing ones.
