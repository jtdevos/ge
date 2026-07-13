# Cyborgs and Droids (NPC ships)

Salvaged from `GECYBS.C`, `GEDROIDS.C`, and the spawner in `GEMAIN.C`
(`autortia`). NPC classes are data-driven: any ship class in
`salvage/data/ships.toml` with `type = "CYBORG"` or `"DROID"` gets AI
via per-class function hooks (`init_func` / `tick_func` / `kill_func` /
`won_func` in the class table).

## Spawning (`autorti`, every second)

- Every 30 seconds, one non-player channel slot is examined
  round-robin. If free, the spawner finds the first CYBORG/DROID class
  whose live population is below its `max_to_create`, and spawns one
  (1% of the time, or when all classes are full, it picks a random
  NPC class instead — population caps can be exceeded occasionally).
- Total NPC capacity = `NUMSHIPS` config (channel slots beyond the
  human terminals).
- Each NPC gets a synthetic user `@Cybrg-<n>` / `@Droid-<n>`.
  Cyborg users and ships persist in the database between spawns
  (they keep cash/kills); droids are ephemeral (memory only).
- Spawn position: uniform random anywhere in the universe (droids
  spawn within ±20 sectors of center on normal-size universes, to be
  seen). Cyborgs spawn with random consumables (0–4 flux pods, 0–24
  decoys/torps, 0–99 mines/jammers, 0–`CYBGOLD` gold) and full phaser
  charge, max class phaser/shield marks.
- The `@`-prefix hides them from rosters and mail purges their record.

## Cyborg brain (`cyb_lives`, per NPC tick)

The per-ship AI cadence is randomized: `tick` counts down each second;
idle cyborgs re-think every ~12–60 s, in-combat cybertrons every ~6–12
s, **cyberquads** (classes with `cyborg_toughness = 1`) every ~2–8 s.
At most `CYBMAXPERTICK` (2) cyborgs and `QUADMAXPERTICK` (5) quads act
per second. Cyborgs get a `CYB_ALLOW` (35) cash allowance per think and
their energy is simply reset to 50000 every think (they never run dry).

### Skill and mercy (the difficulty ramp)

- `cybskill` = 3–17 rolled at spawn: chance of *not* fumbling an
  action is `1 − 1/skill` (each attack rolls `rand % skill == 1` →
  whiff).
- `gebemean()`: quads are always mean; ordinary cybertrons are mean
  always once the *target player* has > `CYB_BE_NICE` (30) kills,
  otherwise only 1 think in `CYBSLO` (3). Below `CYB_BE_EASY` (60)
  player kills, cybertrons also fire fewer torpedoes (0–1 instead of
  0–5 per volley).
- Targeting respects class config: a cyborg only attacks player ships
  whose class ≥ its `lowest_user_class_attacked`; a player class with
  `cybs_can_attack = false` is only engaged if it shoots first or gets
  too close; at most `cybs_to_attack` (per *victim* class) cyborgs
  claim the same player at once (`noclaim`).
- 1 in `CYB_BREAKOFF` (500) thinks, a non-quad breaks off its attack
  for no reason ("this is your lucky day").

### Hunt state machine (`cyb_check_lockon`)

`cybmine` = channel of claimed prey (255 = none). While `holdcourse`
> 0 the cyborg flies straight and skips decisions.

- No prey: pick the closest eligible, unclaimed, uncloaked player.
  None available → idle (slow tick, random cruising via periodic
  course randomizer).
- Prey cloaked: mill around, 1 in 10 chance per think of giving up.
- Distance ≥ `HYPDST1` (config): **hyper-pursuit** — jumps to
  hyperspace at `distance × 2000` speed (instant, shields down).
- Distance ≥ `HYPDST2`: brake to ≤ warp 20, head straight in, occasional
  taunt.
- Distance > 3 sectors: close at top speed, shields up (normal space).
- Distance ≤ 3: match speeds — vs hyperspace prey chase at 1.25× prey
  speed (capped at own top speed); vs normal prey settle to ~warp 1
  knife-fight speed. Shields up. Taunts.

### Combat behavior (`cyb_attack`)

Each mean think vs prey in range (own scan range):

- In normal space: aims (`degrees` = exact bearing, focus 2) and fires
  phasers if charged (subject to fumble roll), fires a volley of 0–5
  torpedoes (0–1 vs low-kill players; torpedo stock magically refilled
  1–5 each volley), lays 5 decoys, keeps shields up.
- In hyperspace (both in hyper, within 30000): hyper-phasers.
- 1 in 20 thinks: random evasive course change for a few ticks.
- Missiles incoming while in hyper: drop to normal space speeds
  (shakes locks), zigzag.
- Mines detected nearby (`minesnear`): 1 in 10 → maybe zip (1 in 3),
  then flee the area and come back.
- **When jammed**: can't see, so seeds the area with mines (1 in 5 per
  think, timer 10) and runs at top speed on a held course.
- Badly damaged (> `CYB_MINDAM` 75%) while hunting: 1 in 10 per think
  → drop a mine (1 in 5), pop a jammer (1 in 100), and run in a random
  direction.

### Personality

`cyb_annoy` sends taunts on random rolls, drawn from a per-class block
of 16 messages in the MSG file (4 approach, 4 close-range, 4 combat, 4
misc — so each cyborg class has its own voice). Won/died hooks: winner
resets to cruise and banks its kill; cyborg deaths free the channel
(the persistent `@Cybrg` user keeps score for the roster).

## Droids (ambient ships)

Droids are flavor/loot traffic with per-type behavior, dispatched by
class *name*:

- **Lydorian Garbage Scow** (class 31): harmless wanderer, no warp;
  shields up when slow; one grumpy message. Kill it for scrap.
- **Murdonian Transport** (class 32): cargo hauler *loaded* with loot
  (up to 250 decoys/torps, missiles, ion cannons, gold...). Passive
  until fired on (`lastfired` set): then calls for help, returns phaser
  fire (and hyper-phaser in hyper), jinks randomly, drops out of hyper
  to shake missiles. Piracy target #1.
- **Vakory Survey Drone** (class 33): scout; if attacked fights back
  with phasers and up to 1 torpedo per think, speeds up to outrun
  missiles, and when damage > 75% lays mines, jams, and flees at top
  speed.

Droids are worth points (`kill_points`) and drop cargo loot like any
kill. They respawn via the normal spawner cycle.
