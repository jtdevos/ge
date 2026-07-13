# Command Reference

The in-game prompt matches input by the **first three letters** against
this table (`gecmds[]` in `GECMDS.C`, binary search, so effectively
case-insensitive 3-letter prefixes). "Pay" = available to non-paying
BBS accounts in the original's table (`cando` flag); a remake can
ignore that column. `x` exits to the main menu (blocked while
battle-locked). Full behavioral detail lives in the other spec files.

Angle args: `<deg>` is a relative bearing −180..+180 unless prefixed
with `@` where noted. `<ship>` is a contact letter from the last scan,
or `@` for the locked target.

| Cmd | Syntax | What it does |
|-----|--------|--------------|
| ? / hel | `help [topic]` | Help index / topic (45+ topics in MBMGEHLP.MSG) |
| aba | `abandon` | Give up ownership of the orbited planet |
| abo | `abort` | Cancel self-destruct (public if < 10 s left) |
| adm | `admin` | Claim planet / open planet admin menu (in orbit) |
| att | `attack <n> tro\|fig` | Planetary assault with troops or fighters |
| buy | `buy <qty> <item> [password]` | Buy from orbited planet |
| clo | `cloak on\|off` | Cloaking device (class-dependent) |
| cls | `cls` | Clear screen |
| dat | `data` | Show game configuration/version info |
| dec | `decoy` | Deploy a decoy (max 10 out, ~15 tick life) |
| des | `destruct` | Start 20 s self-destruct countdown |
| flu | `flux` | Manually consume a flux pod → full energy |
| fre | `freq <A\|B\|C> <n\|hail>` | Tune radio channel (0/hail = open hail; <20000 sector band; ≥20000 game-wide band) |
| imp | `impulse <pct> [deg]` | Sub-warp speed, 0–99% of warp 1, optional turn |
| jam | `jammer` | Jam all ships in scan range (no locks, no mine warnings) |
| jet | `jettison <qty\|ALL> <item>` | Dump cargo |
| loc | `lock <ship>` / `lock` | Set / clear persistent target lock |
| mai | `maintenance [password]` | Buy repairs in orbit (owned planet ≥ 25k men, or Zygor/T-Station) |
| min | `mine <timer>` | Lay a mine, timer 1–50 ticks |
| mis | `missile <ship> <energy>` | Fire energy-warhead missile (1–50000) |
| nav | `navigate <x> <y>` | Bearing + distance to a sector |
| new | `new ship\|shield\|phaser <n>` | Buy hull / refit (Zygor orbit only) |
| orb | `orbit <n>` | Orbit planet n (within 250 range); stops ship |
| pha | `phaser <deg> [focus 0–5]` | Fire phasers (hyper-phasers in hyperspace) |
| pla | `planet` | List planets you own |
| pri | `price <qty> <item>` | Price quote (same rules as buy, no purchase) |
| ren | `rename <name>` | Rename your ship |
| rep | `report nav\|sys\|inv\|acc` | Status: navigation / systems / inventory / account |
| ros | `roster` | Score roster + team standings |
| rot | `rotate <deg>` / `rotate @<deg>` | Turn relative / to absolute heading (30 energy) |
| sca | `scan se\|ra\|pl\|sh <ship>\|lo` | Sector map / range contacts / planets / detail ship scan / long-range |
| sel | `sell <qty> <item>` | Sell to the bank (Zygor orbit only, 0.1% fee) |
| sen | `send <A\|B\|C> <message>` | Radio broadcast on channel |
| set | `set <option> on\|off` / `set ?` | User options: scannames, scanhome, scanfull, filter |
| shi | `shields up\|down` | Shields (marks 1–19) |
| spy | `spy` | Plant a spy on the orbited foreign planet |
| sys | `sysop <subcmd> ...` | Sysop tools (get/kill/cash/cyborg/class/...) |
| tea | `team join\|unjoin\|score\|start\|members\|kick\|newpass\|newname` | Team management (5-digit codes, founder secret) |
| tor | `torpedo <ship>` | Fire torpedo (speed-based lock, max 3 chasing a target) |
| tra | `transfer up\|down <qty> <item>` | Move cargo ship↔planet in orbit |
| war | `warp <n> [deg]` | Warp speed (≤ 1.5× rated asks the engines for trouble) |
| who | `who` | List players in the game |
| zip | `zipper` | Detonate all mines in scan range |

## Original help topics

Besides per-command help, `MBMGEHLP.MSG` ships prose topics worth
carrying over verbatim for flavor: `battle` (1–3), `class`,
`communicate`, `cybertron`, `galaxy`, `moving`, `planets` (1–3),
`scoring`, `sector`, `starting`, `strategy`, `wormholes`, `hyper`.

## Interaction niceties worth preserving

- Commands are terse and forgiving: 3-letter prefixes, item names also
  3-letter matched (`tor` = torpedoes as cargo, by position).
- Output is *push-based*: combat, radio, sector arrivals and cyborg
  taunts print asynchronously between your commands — the prompt is a
  live feed, not a request/response loop. The `filter` option tames it.
- Two output classes: ALWAYS (combat, warnings) and FILTER
  (ambient chatter, suppressible per-user).
- ANSI users get full-screen scan displays and the tactical/helm
  screens (`MBMGEGRF.C`); non-ANSI falls back to plain text of the
  same data.
