# Combat Systems

Salvaged from `GECMDS.C` (firing commands), `GEFUNCS.C` (incoming
weapon resolution, shields, death), `GEMAIN.C` (tick cadence).
Config names refer to `salvage/data/config.toml`; constants to
`salvage/data/constants.toml`. All "per tick" below = the 6-second
systems tick unless noted.

## General combat rules

- **Battle lock**: any hostile act (firing, being locked onto, laying a
  mine, jamming, zipping, attacking a planet) sets `cantexit =
  FIRETICKS` (10 ticks ≈ 60 s) on both parties. While battle-locked a
  player cannot exit the game (hanging up while locked destroys the
  ship), and repairs cancel.
- **Neutral zone**: any fire attempt in sector 0,0 instead zaps the
  *firer* for `SE100DAM` (config, default 10) hull damage. Ships in the
  neutral zone can't be locked onto or hit.
- **Last-fired credit**: each ship remembers the last channel that
  fired on it (`lastfired`); whoever holds that when it dies gets the
  kill (mine hits credit the mine layer; self-destruct and ion cannons
  credit no one).
- Hull damage is 0–100%. ≥100% = destroyed. Most damage is scaled by
  the victim class's `damage_factor` (`damfact`, default 90:
  `dam / (damfact/100)` — bigger factor = tougher ship).

## Phasers (normal space)

`pha <deg> [focus]`, relative bearing −180..180, focus 0–5 (default 1
via percent=1... focus width 0–5 degrees).

- Charge: `phasr` 0–100%, reloads `PRELOAD` (10) per tick, consuming
  `PENGUSE` (57) energy per reload tick. Must be ≥ `PMINFIRE` (60) to
  fire. Firing dumps the whole charge (`phasr → 0`).
- Firing is a **beam sweep**: every ship in the game whose bearing from
  the shooter is within `focus + PHABIAS` (2°) of the fire direction is
  a potential hit (no explicit range gate — the distance falloff does
  that).
- Base damage `pdamage`: `dam = PDAMMAX × (1 − dist/reach)^PFIRDST ×
  (1 − focus/11)² × charge%`, where `reach = 20000 + phasertype×4000`
  units and `PFIRDST` (config "Phaser distance factor", default per
  MSG) is the falloff exponent. Then scaled by
  `(1 + phasertype)/2.5`, divided by target-size factor
  `1 + max_tons/15000`, and by the victim's `damage_factor`.
- Ships in hyperspace can only be hit if the shooter's phaser mark ≥
  `PHATOWRP` (config), and take half damage.
- Firing drops your shields for the shot (auto down/up), is impossible
  while cloaked, and cannot target ships in the neutral zone.
- Phaser mark 20 is the sysop weapon: flat 101 damage (instant kill).
- Victim's shields, if up, absorb per **shieldhit** below; otherwise
  full hull damage plus a random-system-damage roll.

## Hyper-phasers (in hyperspace)

`pha <deg>` while `where == 1`:

- Needs `HPMINFIR` (6000) energy; consumes `HPFIRAMT` (5000); one-tick
  cooldown (`hypha`).
- Beam width fixed `HPBEAMW` (5°); only hits ships **also in
  hyperspace**, within the shooter's class scan range.
- Damage: `HPDAMMAX × (1 − dist/40000)^HPFIRDST`, scaled by
  `phasertype`, divided by target size factor; no shield interaction
  (shields can't be up in hyper).

## Torpedoes

`tor <ship-letter|@>` — letter from last scan, `@` = current lock.

- Requires torpedo capability, normal space, not cloaked; consumes one
  torpedo item; target anywhere in scan range (not just same sector).
- **Lock-on roll** (`lockon`): fails outright if target is in the
  neutral zone, cloak fully up (`cloak == 10`), or out of scan range,
  if your fire control is damaged, or you're jammed. Otherwise
  `fact = (1.2 − (v_you+v_tgt)/5000) × (5 − dist)/TORFACT'` where
  `TORFACT' = TORFACT/10` (default 4.0); lock succeeds if
  `fact > 0.7`. A target moving above warp 1 (speed > 999) cannot be
  torpedo-locked. Both parties get battle-locked either way, and the
  target is warned.
- Max `MAXTORPS` (3) torpedoes chasing any one ship.
- Flight: starts at current distance (+20); closes at `TORPSPED`
  (config, default units/tick). Victim sees "incoming" each tick.
- **Decoys eat torpedoes**: while in flight at distance < 5000, each
  deployed decoy rolls `rand % DECODDS == 0` to destroy it.
- Impact: shields up → `dam = TDAMMAX × rndm(0.5)` (0–½ max) through
  size/damfact scaling, plus `shieldhit` of 10–29; shields down →
  `dam = TDAMMAX × (0.5 + rndm(0.5))` (½–full). Random system damage
  roll either way. Entering hyperspace sheds all chasing torps.

## Missiles

`mis <ship-letter|@> <energy>` — energy 1–50000 packed into warhead.

- Consumes one missile item plus `energy/MISENGFC` (config) flux from
  your pool (must leave `MOVENGMIN` margin).
- Lock roll: `fact = (5 − dist)/MISFACT'` (`MISFACT' = MISFACT/10`,
  default 2.0) — speed doesn't matter, but the *victim* can outrun
  them: missiles die when the target exceeds warp 4–7.
- Max `MAXMISSL` (3) per target; closes at `MISLSPED`/tick; decoys work
  under distance 3000, odds `1/DECODDS`.
- Impact damage scales with warhead energy: energy is first reduced by
  the victim's `damage_factor`, then
  shields up → `MDAMMAX × (E/50000) × rndm(0.1)` + `shieldhit` of
  `(E/999) × (0.5..1.0)`; shields down → `MDAMMAX × (E/50000) ×
  (0.5..1.0)`. Victim sees a size epithet ("very small" <1000 …
  "devastating" ≥40000).

## Mines

`min <timer>` — timer 1–50 (roughly ×6 s... checked every tick,
decremented each 6s tick).

- Global pool `NUMMINES` (config, default), per-player cap `USRMINES`
  (config). Dropped at your current position; illegal in the neutral
  zone; can't drop while cloaked.
- Every mine is checked each 6s tick (checks fire when `timer%5==0`):
  ships within `MINERANGE` (10000 = 1 sector) get a proximity warning
  with bearing+distance — **unless they carry an active jammer effect**
  (jammed ships also don't hear the final beep... they get no warning).
- At timer 0 it detonates: cubic falloff
  `dam = MNDAMMAX × (1 − d/10000)³`, ton-factor scaled; shields up
  divides damage by `rand%5 + shieldtype` and shield takes
  `shieldhit(dam+20)`. Mine layer's channel gets kill credit.
- Detonation is suppressed in the neutral zone.

## Decoys

`dec` — deploys one (max `MAXDECOY` = 10 out). Lives `DECOYTIME` (15)
ticks. While alive, each decoy independently rolls to eat incoming
torps/missiles (above). Also appears as a ship contact on scans.

## Jammers

`jam` — jams **every ship within your scan range** (including
yourself... no: all ships in game within range, closer = longer):
`jamtime × (1 − dist/scanrange)` ticks of jammer effect (config
`JAMTIME` 1–10). A jammed ship cannot achieve weapons lock and receives
no mine warnings. Consumes one jammer item.

## Zippers

`zip` — every mine within scan range is set to detonate on the next
tick. Consumes one zipper. (Sector-wide announcement.)

## Ion cannons (planetary defense)

Automatic, on the 6s tick: a ship that is `hostile` toward a planet
(set by `att`) and still near it gets hit every tick as long as the
planet has ion cannons in stock: shields up → `dam = IDAMMAX ×
rndm(0.15)` + heavy shield knock (40–89); shields down → `dam =
IDAMMAX × (0.5 + rndm(0.5))`. No kill credit. Hostility clears when
you leave the sector or fly > 1000 units from the planet.

## Cloak

`clo on|off`. Requires class capability and `CLENGUSE` energy per tick
upkeep (cloak drops when energy runs out, announced to the sector).

- Engaging takes ~2 ticks (state 1 → 2 → 10); only at `cloak == 10`
  are you actually hidden (unscannable, untargetable).
- While cloaked you cannot fire anything, and moving fast may still
  reveal a bearing: impulse burns > random(10–210) while cloaked give
  nearby ships (within half their scan range, unjammed) a bearing
  fix ±10°.
- Cloak device can be damaged (negative `cloak` counts up 1/tick to
  repair). Hyperspace forces cloak off.

## Shields

`shi up|dn`. Marks 1–19 (20 = sysop). Requires `SHMINPWR` (200) energy
to keep up; consumes `shieldtype × SHENGUSE` (×100) per tick while
charging/up.

- Charge: 0..`40 + type×10`, regains `type×3` per tick.
- `shieldhit(dam)`: charge drops `(80 − type×SHIELD_FACTOR) × dam%`
  (SHIELD_FACTOR = 4; type 19 → only 4×dam%, type 20 → 0). If charge
  falls ≤ 2 the shields are *damaged* (status SHIELDDM, extra 3×knock)
  and must repair (type units/tick back toward 0, then down).
- Shields auto-drop in hyperspace, when energy < `SHMINPWR`, and
  momentarily whenever you fire torpedoes/missiles/phasers.
- With shields up, weapon hull damage uses the reduced "shields up"
  formulas above; the flat `SHHITENG` (1000) energy drain constant
  exists but the shield energy cost is the per-tick charge cost.

## Random system damage

After any phaser/torpedo/missile hit (and ion), if hull damage > 20%:
roll `rndm((101 − damage)/1.5) == 0` (likelier as damage climbs), then
a d6 picks the wounded system:

0. shields damaged (charge → −rand(damage+10), status DM)
1. phasers damaged (`phasr` → negative; must recharge past 0)
2. fire control broken for `rand%20` (blocks weapons lock)
3. cloak damaged (negative timer)
4. tactical display broken (scan/report garbled) — timer −rand(damage+10)
5. helm broken (no impulse/warp/rotate) — same timer

Ships with sysop shield (type 20) are immune. Damaged systems tick back
toward 0 on the 6s tick; `mai repair` (−3%/tick) clears everything when
damage reaches 0.

## Self destruct

`des` (blocked in neutral zone) starts a `COUNTDOWN` (20) second
countdown, announced to ships in range at T−10/5/2; `abo` aborts
(publicly if under 10 s). At zero: ship dies (damage 101) and everything
within `DESTRUCTRANGE` (10000, non-neutral) takes mine-style cubic
falloff damage ×`(shipclass/2 + 1)` — a capital ship makes a big bang.
No kill credit awarded. Entering the neutral zone cancels the countdown.

## Death and kills (`killem`)

When a ship reaches 100% damage:

- If `lastfired` is a valid other ship, that player:
  - gets the kill (+1), and **loot**: for each cargo item except men
    and troops, `qty / (rand%5 + 1)`, capped by cargo capacity.
  - gains score: class `kill_points` + roster bonus
    (`SCRBONUS / victor's roster position`); the victim *loses*
    `SCRFACT`% of that amount (only 1/10th of the deduction if killed
    by a cyborg/NPC), floored at 0.
  - if `CHGLOSER` config > 0 and both are human: victim also loses that
    percent of cash on hand to the victor.
  - 1 in `RNDDOC` (6) chance the victor captures the victim's **planet
    map** (list of up to 20 of their planets with coordinates).
- Otherwise the death is announced unattributed.
- The dead ship's record is deleted (player ship count −1); the victim
  respawns at the shipyard flow (`new` ship purchase); all torps and
  missiles the dead channel owned go inert.
- NPC classes run their `kill_func`/`won_func` hooks (cyborg taunts,
  respawn logic).

## Ship-to-ship comms and intel (adjacent systems)

- `sen <msg>` broadcasts on your radio frequency (sub-space range
  limited); `fre` changes channels; distress calls reach same-team
  players farther away.
- `loc <letter>` sets a persistent target lock (`@` in fire commands);
  lock drops if target leaves scan range or game.
- `sca` builds the sector map + contact table (letters A.. for up to 15
  contacts) — decoys appear as contacts; cloaked ships don't.
  `nav x y` gives bearing/distance to any sector center.
- `rep` is the full status board (position, heading, speed, energy,
  charge, damage %, systems, cargo).
