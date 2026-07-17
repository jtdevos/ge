# 9. Scoring

Your score is the sum of two ledgers: the **combat score**, which
moves the moment you kill, and the **planet score**, recomputed every
night during the system cleanup. Quick blood buys headlines; over the
long haul the roster belongs to those who build planetary empires and
manage them well.

## Combat scoring

Destroying a ship pays its class's kill value (stock 3.2 table,
`salvage/data/ships.toml`):

| Class | Points | | Class | Points |
|-------|-------:|-|-------|-------:|
| Interceptor | 750 | | Freight Barge | 5,000 |
| Stealth Fighter | 1,500 | | Cybertron Scout | 1,000 |
| Heavy Freighter | 500 | | Cyberquad | 2,000 |
| Destroyer | 2,000 | | Cybertron Base Star | 10,000 |
| Star Cruiser | 5,000 | | Sarten Attack Drone | 50 |
| Battle Cruiser | 5,000 | | Sarten Obliterator | 500 |
| Frigate | 5,000 | | Murdonian Transport | 200 |
| Dreadnought | 10,000 | | Vakory Survey Drone / Scow | 50 / 5 |

> **Salvage note:** the 1994 guide's table (Interceptor 10 …
> Dreadnought 500) describes an older tuning; the shipped values
> above are 20–75× larger. The *shape* survived — capital kills pay
> most — with one twist: an Interceptor kill now pays more than a
> Heavy Freighter, pricing the annoyance of catching one.

On top of the class points:

- **Roster bonus** — killing a ranked player pays up to 1,000 extra,
  scaled by their rank: the #1 player is worth the full bonus, #10 a
  tenth of it. Regicide pays.
- **The loser bleeds** — the victim *loses* 35% of what the victor
  gained (stock `SCRFACT`), so a kill genuinely reorders the roster.
  Death to a Cybertron costs only a tenth of that — the galaxy
  doesn't mock the war dead.
- **Cash spoils** — 2% of the victim's cash on hand transfers to a
  human victor (stock `CHGLOSER`), on top of cargo loot.

## Planet scoring

Nightly, each planet you own contributes:

- its wealth: 1 point per 100,000 credits of planet cash plus
  uncollected tax, and
- its population: 1 point per 1,000 men — men being the only item
  with a point value in stock config (`[items.point_value]`), which
  is why population is empire score, and why populated planets are
  worth stealing.

The nightly sweep also recounts your planets and total population
for the roster, then re-ranks everyone.

## Team scoring

Recomputed nightly: **team score = Σ member scores ÷ member count +
500 per member** (stock `TEAMBONU`). The averaging means a passenger
drags the team down; the per-member bonus means a big team of good
players beats a small one. The guide's cryptic formula "(A/B)+(C*B)"
says the same thing.

## Reading the roster

`roster` shows the top of the table (`roster all` for everyone, `R`
from the main menu), with team standings alongside. Rankings are
stamped nightly — so your roster *position* (and the bounty on your
head) updates at midnight, even though the scores themselves move in
real time.
