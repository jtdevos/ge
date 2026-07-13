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

The original author's own documentation (user guide, sysop guide,
installation) is preserved untouched in `mbmgemp/GE/DOCS/` and
`mbmgemp/*.DOC`.
