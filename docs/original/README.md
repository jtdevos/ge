# Original Player Documentation (recovered)

Faithful transcriptions of Galactic Empire's original player-facing
documentation, from the files shipped in `mbmgemp/`. These are
**archival artifacts**: original wording, spelling, numbering and
errors are preserved exactly (down to "rouge ships" and section
"11.145"). Corrections and completions live in the
[reconstructed manual](../manual/), never here.

| Transcription | Source | What it is |
|---|---|---|
| [users-guide.md](users-guide.md) | `mbmgemp/MBMGEMP.DOC` | The USERS GUIDE v3.2, revised 02/01/94 — the manual sysops gave players |
| [online-help.md](online-help.md) | `mbmgemp/MBMGEHLP.MSG` | The in-game `help` database, v3.2c — 61 screens |

## Provenance notes

- **Which copies:** the repo holds three copies of each. For the
  guide, `mbmgemp/MBMGEMP.DOC` is transcribed — it differs from
  `GE/DOCS/` and `GE/REL/` only in the author's contact block (the
  later St. Cloud address and email). For the help file,
  `mbmgemp/MBMGEHLP.MSG` is transcribed — one revision newer than
  `GE/MSG/` (it adds the `set filter` option); `GE/REL/` is
  identical. `GE/REL2/MBMG2HLP.MSG` is a different product: the
  "Galactic Empire Trainer" variant (Cybertrons renamed Simultrons),
  not transcribed.
- **Verification:** the guide transcription is checked word-for-word
  against the DOC by `salvage/tools/check_transcription.py`; the help
  transcription is generated from the MSG by
  `salvage/tools/extract_help.py`. Rerun both after touching either.
- **The two documents disagree** with each other and with the shipped
  data in places (galaxy size, starting ship, missile energy cost,
  radio threshold, Mark-19 shield price, ship class 2, scoring
  values). Each dispute is resolved against the C source in the
  reconstructed manual's *Salvage notes*.

## Not transcribed (sysop-facing, read them in place)

- `mbmgemp/GEREADME.DOC` — sysop README and release history
- `mbmgemp/GEINST.DOC` — installation
- `mbmgemp/GE/DOCS/GESYSOP.DOC` — sysop command notes
- `mbmgemp/GE/DOCS/GETERM.DOC` — terminal/ANSI notes
- `mbmgemap/MBMGEMAP.DOC` — the sysop map utility
