# 3. Ships and Equipment

All hulls, shields and phasers are manufactured at **Zygor** and
bought there with the `new` command, in orbit. `help class` in-game
prints the class table; these are the shipped 3.2 values
(`salvage/data/ships.toml`).

## The ship classes

| # | Class | Shld≤ | Phsr≤ | Weapons | Attk | Cloak | Warp | Accel | Tons | Scan | Price |
|---|-------|------|------|---------|------|-------|------|-------|------|------|-------|
| 1 | Interceptor | 10 | 10 | torp, decoy, jam, zip, mine | – | – | 10 | 5000 | 1,000 | 10 | 65,000 |
| 2 | Stealth Fighter | 15 | 15 | torp, misl, decoy, jam, zip, mine | yes | yes | 20 | 5000 | 2,000 | 20 | 500,000 |
| 3 | Heavy Freighter | 5 | 5 | torp, decoy, jam, mine | yes | – | 8 | 3000 | 60,000 | 5 | 40,000 |
| 4 | Destroyer | 15 | 15 | torp, misl, decoy, jam, zip, mine | yes | – | 25 | 5000 | 5,000 | 10 | 600,000 |
| 5 | Star Cruiser | 15 | 15 | torp, misl, decoy, jam, zip, mine | yes | yes | 25 | 10000 | 3,000 | 20 | 700,000 |
| 6 | Battle Cruiser | 19 | 19 | torp, misl, decoy, jam, zip, mine | yes | yes | 30 | 3000 | 6,000 | 25 | 800,000 |
| 7 | Frigate | 12 | 12 | torp, misl, decoy, jam, zip, mine | yes | – | 30 | 10000 | 12,000 | 25 | 1,250,000 |
| 8 | Dreadnought | 19 | 19 | torp, misl, decoy, jam, zip, mine | yes | yes | 50 | 15000 | 40,000 | 50 | 2,000,000 |
| 9 | Freight Barge | 6 | 3 | decoy, jam | yes | – | 15 | 1000 | 200,000 | 20 | 3,000,000 |

*Scan* is scanner range in sectors. *Accel* is in speed units per
tick — it governs how fast you change speed *and* how fast you turn.
Freighters (3, 9) also take only half damage from most weapons
(damage factor 200 vs the fighters' 90–125); they are tougher than
they look, if slower than they'd like.

> **Salvage note:** the 1994 guide lists class 2 as "Light
> Freighter"; the shipped class table has the **Stealth Fighter**
> there instead — cloaked, missile-armed, warp 20, and the best value
> per credit in the yard. The guide's scoring table (Interceptor 10
> points, Dreadnought 500) is equally stale: shipped kill values run
> 500–10,000 (see [chapter 9](09-scoring.md)). There is also an
> unlisted class 41, the *Sysopian Death Star* — warp 255, 100
> million tons capacity — priced at 32 million credits and reserved,
> as the name suggests, for management.

**Buying**: `new ship <n>`, in orbit of Zygor. Your old ship is
*kept* — you own a fleet (up to 8 ships, stock config) and choose
which to board at login. A new hull arrives with shields and phasers
at Mark-1, so budget for the refit too.

## Shields and phasers, Mark 1–19

`new shield <mark>` / `new phaser <mark>` refit your current ship, up
to your class's maximum. Trade-in credit for your old unit is its
list price less one third (less a small brokerage fee on expensive
downgrades); the net charge is never below 1,000.

| Mark | Shield | Phaser | | Mark | Shield | Phaser |
|------|--------|--------|-|------|--------|--------|
| 1 | 5k | 5k | | 11 | 4.0m | 3.8m |
| 2 | 10k | 10k | | 12 | 6.0m | 5.0m |
| 3 | 40k | 40k | | 13 | 8.0m | 7.0m |
| 4 | 100k | 100k | | 14 | 10.0m | 9.0m |
| 5 | 250k | 220k | | 15 | 30.0m | 15.0m |
| 6 | 500k | 400k | | 16 | 50.0m | 30.0m |
| 7 | 750k | 650k | | 17 | 80.0m | 60.0m |
| 8 | 1.1m | 900k | | 18 | 120.0m | 100.0m |
| 9 | 1.5m | 1.2m | | 19 | 200.0m | 200.0m |
| 10 | 2.5m | 2.0m | | | | |

> **Salvage note:** the in-game `help newprice` screen says Mark-19
> shields cost 250.0m; the shipped price table says **200,000,000**
> (`salvage/data/config.toml [shield_prices]`). The game charged what
> the table said.

A higher shield mark charges faster, holds more, and bleeds less
charge per hit; a higher phaser mark reaches farther and hits harder,
and marks below a sysop-set threshold cannot touch a ship hiding in
hyperspace at all. Details in [chapter 5](05-combat.md).

## Energy and flux pods

Your ship runs on a neutron flux energy pool of **65,000** units.
Everything draws on it: acceleration past lightspeed, shields (100 ×
shield mark per tick while up), the cloak, phaser recharge, rotation,
hyper-phaser fire, missile warheads. It self-recharges only at a
trickle.

When the pool drops below 5,000 a **flux pod** is consumed
automatically and the pool refills to maximum (you're warned when the
last pod goes). `flux` swaps a pod in manually — immediately and
without argument, jettisoning whatever remained in the old one. A pod
weighs 20 tons and costs 200 credits base; running out of pods deep
in the void is the classic beginner's death. Carry spares.

## Cargo

Everything your ship carries is one of the game's 14 commodities:

| Item | Base price | Tons/100 | | Item | Base price | Tons/100 |
|------|-----------|----------|-|------|-----------|----------|
| men | 2 | 100 | | decoys | 18 | 300 |
| troops | 1 | 200 | | jammers | 21 | 400 |
| food | 2 | 200 | | zippers | 99 | 500 |
| fighters | 50 | 1,500 | | mines | 16 | 500 |
| missiles | 20 | 500 | | flux pods | 200 | 2,000 |
| torpedoes | 7 | 300 | | gold | 1,000 | 50 |
| ion cannons | 33 | 25,000 | | spies | 100 | 100 |

*Base price* is the Galactic Command's floor price — what your own
planets charge you, and what Zygor pays when you `sell`. Zygor and
Tahanian Station charge two to three times base. *Tons/100* is
shipping weight per hundred units against your class's tonnage;
ion cannons are the awkward freight (250 tons apiece), gold the
densest value.

`report inv` shows the hold; `jettison` dumps cargo; `transfer`,
`buy`, `sell` and `price` move and price it (see
[chapter 4](04-planets.md)).

## Damage and repairs

Hull damage runs 0–100%; at 100% the ship is destroyed. Serious hits
can also knock out individual systems — shields, phasers, fire
control, the cloak, the tactical display, even the helm — which
repair themselves slowly on their own.

`maintenance` in orbit hires a repair crew: **200 credits** at your
own planet (it needs a population of at least 25,000 men to support a
yard), **2,500** at Zygor or Tahanian Station. Repairs run about 3%
of the hull per combat tick, and finish by restoring every damaged
system and your engines' full rated warp. Leaving orbit — or getting
drawn into battle — cancels the work.
