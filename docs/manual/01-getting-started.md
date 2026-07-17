# 1. Getting Started

It is 3250 in the standard year, 975 years since man developed
inter-planetary space navigation, and 412 years since neutron flux
warp technology was perfected by the ship builders of Zygor. These
are good times, where a commander with a good ship and some business
sense can make himself very, very rich — and times when the less
scrupulous can overrun a distant settlement and claim the planet for
their own.

The object of the game is to build and maintain as large an empire as
you can sustain, using any means you find appropriate — alone or with
a team of other players. Beware the dreaded Cybertrons at all cost.

## The universe

The galaxy is a two-dimensional grid of **sectors**, each 10000 ×
10000 parsecs, numbered from the center outward on a signed
coordinate system. Stock configuration spans sector −300 to +300 on
both axes — a 600 × 600 sector galaxy, well over a third of a million
sectors, essentially all of it unexplored.

> **Salvage note:** the 1994 Users Guide says "6000 by 6000 sectors"
> in prose while its own map is labelled ±300; the later 3.2c help
> relabels the map ±3000. The shipped default (`UNIVMAX` = 300) makes
> the guide's *map* the truth and both prose claims wishful. Sysops
> could resize the universe, and what happens at the edge is also
> sysop-chosen: either the galaxy wraps around, or your ship is
> stopped two sectors inside the boundary and takes a bruising 17%
> hull jolt ([universe spec](../spec/universe.md)).

Each sector holds 0 to 9 planetary bodies. About one sector in three
has any; a body has a 1-in-50 chance of being a **wormhole** rather
than a planet. Roughly a quarter of newly discovered planets already
carry an independent population — these are the colonizable finds.
The universe is generated lazily as commanders explore it: nobody,
not even the Galactic Command, knows what's in a sector until someone
has been there.

## Sector 0 0 — the neutral zone

Sector 0 0 is governed by the Galactic Command and is a declared
neutral zone. A single hostile action here is met with a swift and
preemptive strike from the Galactic Command's top secret weapons base
(10% hull damage per attempt, stock config — the *attacker* takes it;
nothing in the neutral zone can be locked onto or hit). Mines will
not detonate here, self-destructs are cancelled on entry, and their
blasts don't propagate here.

The neutral zone contains six fixed bodies
(`salvage/data/config.toml [neutral_sector]`):

- **Zygor** (planet 1) — the shipyard world. Sells ships, shield and
  phaser systems, and all weapons and equipment; buys back your
  excess goods; repairs any ship for a fee. Home of the Galactic
  Monetary Reserve Fund.
- **Tahanian Station** (planet 2) — an embarking station for
  colonists and mercenary soldiers. Sells men, troops, and food.
- **The Enforcer Planet** (planet 3) — the Galactic Command's weapons
  base. Nothing is for sale there, and nothing about it is your
  business.
- **Three portals** — the Kayriez, Lydorian, and Tryklon Portals,
  stable wormholes to distant parts of the galaxy. Use them to cross
  the galaxy fast, or to vanish from a pursuer.

Everything sold in Sector 0 0 costs two to three times the galactic
base price (the stations restock constantly and mark up roughly 2× on
each restock cycle). Your own planets will always be the cheaper
source — once you have some.

Once out of Sector 0 0 it is a free-for-all, and you must decide how
best to defend yourself and your planets.

## Your first ship

You start with an **Interceptor**: an extremely fast-response,
lightweight fighter designed for scouting, fitted with Mark-1 shields
and Mark-1 phasers, a torpedo fire-control system, decoys, and both
impulse and neutron-flux warp drives. You also start with **100,000
credits** and **3 flux pods** aboard.

> **Salvage note:** the guide's chapter 3 describes the Interceptor
> as warp 5 with a 500-ton hold; the shipped class table gives it
> **warp 10** and a **1000-ton** hold (`salvage/data/ships.toml`).
> One strategy screen in the 3.2c help even claims your first ship is
> a Light Freighter — stale text from an older configuration. The
> class table in [chapter 3](03-ships-and-equipment.md) is the truth.

The Interceptor cannot mount missiles, cannot attack planets, and
cannot cloak — but it enjoys one crucial privilege: **Cybertrons will
not attack it unless provoked**. Enjoy that immunity while you build;
you lose it the day you buy something bigger.

## Your first session

From the BBS menu, Galactic Empire opens on its main menu: **P**lay,
**G**eneral info, **R**oster, **M**ail, game statistics, and e**X**it.
`P` puts you aboard your ship at a random spot in Sector 0 0 and
drops you at the command prompt.

The prompt is a live feed, not a questionnaire. Radio traffic, combat
reports, arrivals and departures print the moment they happen,
between — and into — your keystrokes. Every command can be
abbreviated to its **first three letters** (`imp 50`, `sca se`,
`rep nav`), and most commands explain themselves when entered with no
arguments. `set filter on` mutes the routine chatter if the galaxy
gets too loud.

A sensible first hour:

1. `buy` supplies at Zygor and Tahanian Station: men, troops, food, a
   few fighters (see [chapter 4](04-planets.md) for amounts).
2. Pick a direction, `warp` out a handful of sectors, and `scan se`
   each sector looking for a planet with GOOD or VERY GOOD ratings
   (`scan pl <n>` shows a planet's quality).
3. `orbit` it, `admin` to claim and name it, `transfer down` your
   colonists and supplies.
4. Head home before anything with more guns notices you, collect
   taxes in a few days, and start saving for a real ship.

An alternative, albeit somewhat immoral, strategy is to purchase
weapons and lie waiting for other ships to leave Sector 0 0…

## Leaving the game

Type `x` at the command prompt to dock and exit. You **cannot exit
while in battle** — any hostile act, by you or against you, locks you
into the game for about a minute (10 combat ticks). Hanging up while
battle-locked destroys your ship. Remember: "Death before Dishonor"!

While you're away your empire lives on: planets produce, colonists
pay taxes (and sometimes revolt), spies file reports, and attacks on
your worlds generate distress mail. Check the **M**ail menu each
session — mail is purged after 3 days, stock config.
