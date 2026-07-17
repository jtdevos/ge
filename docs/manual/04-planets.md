# 4. Owning Planets

In order to build wealth you must colonize planets and maintain them.
Planets are the game's long engine: combat gets you headlines, but
the roster's top names are planet barons
(see [chapter 9](09-scoring.md)).

## Choosing a world

`scan pl <n>` rates a planet on two factors — **resources** and
**environment** — each POOR, MARGINAL, GOOD, or VERY GOOD. The two
ratings together set the production multiplier *and* how fast the
colony's treasury leaks away; a VERY GOOD / VERY GOOD world produces
about twice what a POOR/POOR one does and hemorrhages far less cash.
Be choosy: surviving on a poor planet demands frequent supply runs.

About a quarter of the planets you'll discover already carry an
independent population — men, a little food production, sometimes
more. These are the prizes: population is the one thing you can't
manufacture quickly.

## Claiming and provisioning

Orbit the planet and `admin`. If it's unowned you'll be asked whether
you wish to settle it, then to name it. A new colony sets its effort
to 50% men, 50% food; you may own at most 20 planets (stock config).

Whatever you `transfer down` belongs to the colonists — you cannot
transfer it back, only buy it back at base price. Leave them:

- **MEN** — the colony itself. Everything scales with population.
- **FOOD** — troops and men each eat 1 case per 100 heads per
  production pass, troops first. If food runs out, an eighth of the
  troops starve, then an eighth of the men, and you get the distress
  mail. The old rule of thumb — a case per 10 men — over-provisions;
  what matters is that food *production* outruns consumption.
- **TROOPS** — mercenaries. They produce nothing, eat well, mostly
  play cards, and are the only thing standing between your planet and
  a ground assault — or between you and your own colonists (below).
- **FIGHTERS** — the primary defense force, against both fighter
  raids and troop landings.
- **ION CANNONS** — automated cannon that fire on any hostile ship in
  orbit, every combat tick, hitting like a capital ship. An attacker
  won't stay long. Stock beats none; more stock survives pillage
  longer.

## Production

The colony works continuously; the planet ticker visits every world
in the galaxy in a rotating sweep (a full pass takes about 6 hours at
stock config — `PLANTOCK`). Each visit, production of each item runs
in proportion to:

- **population** — men are the workforce;
- **effort share** — the percentage you assign per item (`admin`
  option 3; all items together can't exceed 100%);
- **the item's labor cost** — from 8,000 food per 10,000 man-weeks
  down to 4 ion cannons for the same labor. Men "produce" men at a
  healthy 3,500 per 10k man-weeks: population growth is just another
  production line;
- **planet quality** — the env+res multiplier;
- **tax drag** — production scales by (1 − taxrate/120): tax at 100%
  and the colony works at a sixth of its potential;
- **treasury** — a colony with cash in its bank buys raw materials
  and produces **1.5×**.

Each item has a per-planet cap (roughly: unlimited men and food,
579,000 fighters, 250 ion cannons, 5 spies…); hitting a cap mails you
a "production halted" report — reassign that effort.

## Taxes and revolt

Set the rate 0–100% (`admin` option 5). Each production pass deposits
`men × rate% / 1200` credits into a **collected-tax pool** that only
you can withdraw (`admin` option 2, in orbit) — at stock cadence
(four passes a day) a 50% tax on 12,000 colonists pays about 2,000 a
day. Collect often: a conqueror gets whatever was waiting.

The harsher the tax, the less the colony produces, and the more
likely it **revolts**: whenever discontent (population × tax
pressure) outweighs the garrison, each production pass carries a
1-in-10 chance the colonists rise, gut the garrison, and declare the
planet *Free* — unowned, keeping everything you'd stationed there.
The garrison rule of thumb, straight from the source arithmetic:
**troops ≥ men × taxrate/343**. At 50% tax, one soldier per seven
colonists holds the peace ([economy spec](../spec/economy.md)).

## Trade

Planet cash (the colony's own bank, distinct from your tax pool)
comes from what anyone — including you — pays for its goods, and from
**gold**: transfer gold down and the colony converts it to cash at
1,000 credits apiece. A funded colony produces half again faster, so
seeding a young world with gold is real fiscal policy.

Per item (`admin` option 3) you set: the **markup** price others pay
(you always pay base), whether it's **for sale** at all, and a
**reserve** quantity never sold — keep fighters reserved, or a rival
will politely buy your garrison before an attack.

The planet's **trade password** (option 6) controls who may buy and
who may use your repair yard: `none` opens it to all, `team` admits
your teammates, any other word is a password for your alliance.
Setting `team` records your *current* team — reset it if you switch
teams.

Beacons (option 7) broadcast a 75-character message to ships passing
through the sector. Use them for warnings, advertisements, or poetry.

## Spies

Buy spies at your own planets (100 credits base, when you produce
them) and `spy` in orbit of a foreign planet to land one. A surviving
spy files occasional intelligence reports by GEmail — inventory
estimates with a stated confidence, notice of attacks, changes of
ownership. Counter-espionage is symmetric: the more spies a planet of
*yours* stocks, the better its odds of catching foreign agents (each
pass, roughly 1-in-(50/spycount + 1) — five in stock catches one
intruder per ~11 passes, and both sides receive an Official Protest).

## Losing planets

`abandon` in orbit releases a planet, colonists and stock intact.
Planets are otherwise lost only to revolt or conquest
([chapter 6](06-planetary-battles.md)). Nothing can take the place of
a well-rounded defense and frequent supply runs — leaving a colony
unchecked for more than a few days may spell disaster.
