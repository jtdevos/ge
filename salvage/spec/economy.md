# Planets and Economy

Salvaged from `GEPLANET.C` (production/spies/revolts), `GECMDS.C`
(orbit/admin/buy/sell/transfer/attack/spy/maint), `GEMAIN.C` (admin
menu state machine, nightly reports). Item economics (max per planet,
weight, point value, production manhours, base price) are per-item in
`salvage/data/config.toml [items]`.

## The 14 items

men, missiles, torpedoes, ion cannons, flux pods, food, fighters,
decoys, troops, zippers, jammers, mines, gold, spies. Everything in the
game — cargo, weapons stock, population, currency-by-proxy — is one of
these, held either in a ship's hold or a planet's inventory.

- **Weight**: ship capacity is class `max_tonnage`; adding items checks
  `Σ qty×weight/100 ≤ max_tons` (weights per 100 units in config).
- **Gold** is special: transferred *down* to a planet it converts to
  planet cash at base price on the next production pass. Zygor "sells"
  gold as a cash-conversion mechanism.
- **Spies** are consumed by the `spy` command (below).

## Planet attributes

- `environment` 0–3 and `resource` 0–3, rolled at generation. Their sum
  drives production and treasury decay (below) — a 3/3 world is ~2×
  the production multiplier of a 0/0 world and bleeds far less cash.
- Owner, name, trade password (`none` = open trade; `team` = teammates
  only; other = password-holders), tax rate 0–100%, cash, collected
  tax, beacon message (75 chars), per-item: qty, production rate %,
  markup price, reserve qty, sell-to-others flag, sold count.

## Colonization (`admin`)

Orbit an unowned planet → `adm` asks to claim (`y`), name it, then
drops into the admin menu. Claiming sets all production rates to 0
except **men 50%, food 50%**. Owner cap: `MAXPLNTS` config (default 20).

Admin menu (owner in orbit, `adm`):

1. **Status report** — full item table (rate/qty/markup/reserve/sell/
   sold), cash, collected tax, tax rate, password.
2. **Withdraw cash** — transfer from the planet's *tax* pool to the
   player (only collected tax is withdrawable, not planet cash).
3. **Item parameters** — per item: production rate % (0–100), sale
   markup (0–32000, this *is* the unit sale price to others), sell y/n,
   reserve stock (0–32000, never sold).
4. **Rename** planet.
5. **Tax rate** (0–100).
6. **Trade password** — `none` opens trade, `team` restricts to the
   owner's team (sets planet teamcode), anything else is a password.
7. **Beacon message** — empty input clears it.

`aba` (in orbit) abandons: owner cleared, planet keeps everything.

## Production (`multiply`, per planet-update pass)

Each populated, owned planet is visited round-robin by the planet
ticker (`plarti`, self-calibrating so a full sweep of the database ≈
`PLANTOCK` config minutes; each tick processes up to 20 records / 1
populated planet). Per pass:

1. **Food chain**: troops eat `troops/100` food; men eat `men/100`
   food (troops first). If food is short: 1/8 of troops die, then 1/8
   of men die (distress mail each).
2. **Gold conversion**: planet cash += `gold_qty × base_price(gold)`;
   gold zeroed.
3. **Per-item production**:
   `qty += men × (rate/100) × (manhours/10000/6) / 7 × fact`, where
   `fact = (env + res + 2) × 0.25 × (1 − taxrate/120)`, ×1.5 if planet
   cash > 0.
4. **Treasury decay**: each item pass multiplies planet cash by
   `0.95 − (6−(env+res))×10/100` — poor worlds hemorrhage money
   (note: applied once per item, 14× per pass — faithful behavior,
   arguably a bug worth keeping).
5. **Cap**: item qty capped at `max_on_planet × fact`; hitting the cap
   mails a "production halted" report.
6. **Tax collection**: `tax += men × taxrate/1200`.
7. **Revolt check**: if `men × (taxrate/120 × 0.35) > troops`, then 1
   in 10 chance per pass: troops cut to `troops/(rand%8+2)` and the
   planet goes **"**Free**"** (unowned, distress mail). Garrison or
   keep taxes low.

Zygor and T-Station are restocked every pass (see universe.md).

## Trade

Must be in orbit (`orb <n>`, requires distance ≤ 250).

- `pri <qty> <item>` quotes; `buy <qty> <item> [password]` buys.
  Own planet: pay base price, any stock. Foreign planet: pay the
  owner's markup as unit price, only `qty − reserve` and only if
  flagged sell=Y; password/team rules apply. Proceeds go to planet
  cash (which boosts its production ×1.5).
- Selling to the bank: `sel <qty> <item>` works only at **Zygor**
  (neutral planet 1): pays base price minus a 0.1% fee (min 1).
- `tra up|down <qty> <item>` moves cargo ship↔planet in orbit. Down:
  own planet, or any planet if sysop enabled `TRANSOPT`. Up: own or
  unowned planets only, cargo weight checked. (Wormholes: no.)
- `jet <qty|ALL> <item>` dumps cargo into space.

## Ship maintenance (`mai`)

In orbit of an owned planet with ≥ 25,000 men (or Zygor/T-Station):
costs 200 cash (2500 at Zygor/T-Station), repairs 3% damage per 6s
tick until clean, then restores all systems and rated warp. Cancelled
by battle lock.

## Planetary assault (`att <n> tro|fig`)

Requires class `can_attack_planets`; blocked vs own planet and in
neutral zone; sets `hostile` (ion cannons return fire every 6s tick
while you stay near — see combat.md) and battle lock.

### Troop assault (`att N tro`)

- Planet **fighters** strafe first: kill `(rand%35 + 9) × fighters`
  attackers.
- Ground battle: defenders kill `troops_def × (rndm(PLATTRT1)+0.25)`
  attackers; if attacker:defender ratio > 2%, attackers kill
  `troops_att × (rndm(PLATTRT2)+0.1)` defenders.
- Rout rules: if defenders left < ¼ of attackers → **won**. If
  attackers left < ¼ of defenders, survivors defect to the planet.
- If ratio > 2% and attackers > ½ defenders: random pillage of 0–14 of
  each item.
- Survivors re-board. **Capture**: survivors > 0 and planet has 0
  troops and 0 fighters.

### Fighter raid (`att N fig`)

- If planet has > 500 troops: flak kills `N × (rndm(PLATTRF1)+0.05)`.
- Defending fighters kill `def × (rndm(PLATTRF2)+0.2)` attackers;
  if ratio > 1% attackers kill `att × (rndm(PLATTRF3)+0.2)` defenders.
- Ratio > 5%: pillage roll (0–14 of each item except fighters).
- **Capture**: attackers survive, 0 defending fighters, < 5 troops.

Capture sets owner, clears hostility, +1 planet count. The former
owner gets distress mail (attack or loss) when the attack ratio was
significant; if they're online in the game they see it live and the
attacker is told they've "called for help".

## Spies (`spy`)

In orbit of a foreign planet, consumes 1 spy item, plants your spy
(one slot per planet — later spies replace; planet owner's own spy
suicides). Each production pass:

- Caught with odds `1/(50/spycount + 1)` (more spy stock on the planet
  = better counter-intel): both parties get "Official Protest" mail.
- Else 1 in 10 chance of an **Intelligence Report** mail: a random
  nonzero item's quantity, fuzzed by a stated confidence 50–98%.
- Spies also report planetary attacks on their host planet (1 in 6 per
  significant attack) and confirm changes of ownership.

## Scoring (planets)

Nightly (see meta.md) each owned planet adds to the owner's planet
score: `(cash + tax) / (1,000,000/PLTVCASH)` plus
`Σ point_value[i] × qty[i]/PLTVDIV` (config divisors). Population
count (men/10,000 per planet) is also tallied to the roster.
