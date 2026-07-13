# Sessions, Scoring, Teams, Mail, Housekeeping

Salvaged from `GEMAIN.C` (menus, midnight cleanup, DB layer),
`GEFUNCS.C` (login/init/mail), `GECMDS.C` (new/team/set/sysop/roster).

## Session flow

The BBS main menu launches GE. Inside, the player is in a state machine
(`substt`): main menu → fleet select → **FIGHTSUB** (in-game command
prompt) → admin sub-menus (see economy.md).

- **Main menu**: `P`lay, `G`eneral info, `R`oster, `M`ail menu, `5`
  game stats, `I` company info, `?` redisplay, `X` exit, plus an
  optional sysop-defined menu item (`OPTMENU`/`OPTCHR`/`OPTTXT`).
- **Play**: looks up the user record (creates it with `STRTCASH`
  config × 1000 cash if new), lists their ships: 0 ships → a free
  class-0 ship (Light Freighter/Interceptor, slot 1 in ships.toml) is
  created ("first time" welcome); 1 ship → board it; multiple → pick
  from numbered list.
- Game capacity: `MAXPLRS` simultaneous players; non-paying BBS users
  blocked unless `FREEBIES`.
- **Ship spawn**: random position in the neutral sector (0,0), rerolled
  until ≥ 1000 units from every planet; random heading; stopped;
  energy 50000; phaser charge 100%; shield/phaser mark 1; 3 flux pods,
  no other cargo; damage 0.
- **Exit** (`x` at the prompt): blocked while battle-locked
  (`cantexit`). Ship is persisted and leaves the shared world
  (announced to the sector). **Hangup while battle-locked = ship
  destroyed** (combat log-off penalty); a clean hangup just saves.
- Entering/leaving is announced game-wide/sector-wide (unless cloaked).

## The command prompt

Input at FIGHTSUB is matched by **first three letters** against the
command table (binary search; see commands.md). Anything else → "Huh?".
Commands marked payers-only in the table are gated on BBS account
class. Sysop commands require the module's sysop key and `SYSCMDS`
config; `SYSONLY` restricts further.

## Persistence (original: 4 Btrieve files + 1 text file)

| File | Contents | Key(s) |
|---|---|---|
| MBMGEUSR.DAT | WARUSR player records (score, cash, kills, teams) | userid |
| MBMGESHP.DAT | WARSHP ships (one record per owned ship) | userid+shipno, userid |
| MBMGEPLT.DAT | GALSECT sectors + GALPLNT planets + GALWORM wormholes (one 512-byte record each; plnum 0 = the sector itself) | (xsect,ysect,plnum), type-prefixed second key |
| MBMGEMAL.DAT | in-game mail | userid+class+msgno |
| MBMGETEA.DAT | teams, pipe-delimited text | — |

Live ships/users are held in per-channel memory arrays; the DB is
authoritative between sessions. NPC (cyborg) users persist with `@`
prefixed userids.

## Scoring

Score = `plscore` (planet value) + `klscore` (combat).

- **Combat** (on kill, see combat.md): victim class `kill_points`
  + roster bonus `SCRBONUS/rospos` (leaders are worth more); victim
  loses `SCRFACT`% of the same (÷10 if killed by NPC); optional cash
  transfer `CHGLOSER`% of victim's cash.
- **Planets** (nightly): for each owned planet,
  `(cash+tax)/(1000000/PLTVCASH) + Σ value[i]×qty[i]/PLTVDIV`
  (per-item point values in config.toml).
- **Roster** (`ros`, or R at menu): top `MAXLIST` players by score,
  plus team standings; nightly ranking stamps `rospos` per player.

## Nightly midnight cleanup (`gemidnight`)

1. Zero every player's planet count/score/population tallies.
2. Sweep the whole planet DB: for each owned planet, recompute owner's
   planet score, +1 planet, population += men/10000, and queue a
   **production report** mail (full item/cash/tax snapshot) to the
   owner.
3. Purge mail older than `MAILDAYS` (default 7) and all mail to
   `@`/`*` synthetic users.
4. Recount team membership (bad teamcodes reset to 0), recompute team
   scores: `TEAMBONU×100 + Σ member_score/teamcount` per member;
   remove empty teams; rewrite MBMGETEA.DAT.
5. Re-rank the roster (`rospos`).

## Teams (`tea`)

- `tea start <code> <secret> <password> <name...>` — code is exactly 5
  digits; secret is the founder's admin password; password is what
  members use to join. Max 50 teams; max `TEAMMAX` members.
- `tea join <code> <password>` / `tea unjoin` / `tea members` /
  `tea score` (standings) / founder: `tea kick <secret> <userid>`,
  `tea newpass <secret> <pass>`, `tea newname <secret> <name>`.
- Team effects: shared planet trading (password `team`), distress
  mail/broadcasts, team score on the roster, `TEAMBONU` nightly bonus.

## In-game mail

Mail classes: 1 distress (attacks, revolts, starvation, spy reports),
2 max-out (production halted), 3 production reports (nightly), 4 game
stats, 5 player stats. Read from the main-menu Mail submenu (new-mail
notice at login, 1-in-10 nag otherwise). Messages carry structured
fields (planet, sector, quantities) formatted through MSG templates.
Producers throughout the sim send mail whether or not the player is
online — this is the async layer that makes the empire feel alive
between sessions.

## User options (`set <opt> on|off`, `set ?`)

- `scannames` — show player userids on scans vs ship names only.
- `scanhome` — ANSI: park cursor at home after scan redraw.
- `scanfull` — full-screen ANSI scan display vs scrolling text.
- `filter` — suppress routine broadcast chatter (the FILTER output
  class; ALWAYS-class messages come through regardless).

## Sysop commands (`sys ...`, gated)

`sys get <n> <item>` (conjure cargo), `sys kill <userid>`,
`sys cash <n>`, `sys cyborg <n>` (spawn), `sys cyborgoff`,
`sys cybmine <n>` (sic a cyborg on a channel), `sys class <n>`
(change own ship class), `sys shieldtype/phasertype <n>` (mark 20 =
instant-kill/immune sysop gear), `sys cybhalt`/`sys cybstart`
(pause NPC AI).

## Buying ships and refits (`new`, only in orbit of Zygor)

- `new ship <n>` — buy hull class n (1-based; must be a USER class,
  price from ships.toml `price`), keeping your old ship (fleet up to
  `MAXSHIPS`, pick at login). New hull spawns as a fresh ship at Zygor.
- `new shield <mark>` / `new phaser <mark>` — refit up to class max
  (`max_shield_type`/`max_phaser_type`), prices in config.toml.
  Trade-in credit: you get back your current mark's price minus ⅓
  (i.e. 67%... precisely `price − price/3`), minus a 2% brokerage fee
  if the trade-in exceeds the new price; minimum net charge 1000 when
  upgrading.

## Radio (`sen`, `fre`)

Three tunable radio bands per ship (sub-space, hyper-space, planetary);
`sen <msg>` broadcasts to everyone on the same frequency (respecting
their `filter` option); distress semantics for teams. `who` lists
players in the game; `dat` shows game config/version data.
