# 5. Ship-to-Ship Combat

The easiest target in the galaxy is a ship with shields down, sitting
still. Everything in this chapter is about not being that ship.

## The rules of engagement

- **Battle lock.** Any hostile act — firing, being fired on, laying a
  mine, jamming, zipping — locks both parties into the game for about
  a minute (renewed by each act). While locked you cannot exit;
  hanging up destroys your ship. Repairs in progress are cancelled.
- **The neutral zone.** Ships in Sector 0 0 cannot be targeted or
  hit; attempting hostilities there costs *you* 10% hull per attempt.
- **Kill credit.** Your victim's destroyer is whoever fired on them
  last. The victor collects points, a share of the loser's cargo, 2%
  of their cash (stock config), and — one time in six — their **star
  charts**: the locations of up to 20 of their planets.
- Hull damage runs to 100% = destroyed. Above 20% damage, any further
  hit may knock out a system: shields, phasers, fire control, cloak,
  tactical display, or helm. Damaged systems limp back on their own;
  a maintenance crew fixes everything at once.

## Finding the enemy

`scan se` maps your sector; `scan ra <1–9>` shows contacts by range
with bearing, heading, and speed, lettered A (closest) outward;
`scan sh <letter>` inspects one; `scan lo` reads neutron distortions
at long range — the way to find a player across the galaxy. `lock
<letter>` keeps your fire control on one contact as letters reshuffle;
`@` then means "the locked ship" in any fire command.

## Phasers

`phaser <bearing> [focus]` — a line-of-sight beam, focus 0 (needle)
to 5 (flood). Narrow focus hits harder but must be aimed dead-on; use
1–2 against a located target, 5 to sweep for a cloaked ship you can
smell but not see. Damage falls off with distance; reach improves
with phaser mark (about 2 + mark×0.4 sectors of meaningful beam).

The phaser bank charges to 100% (drawing energy as it goes), fires
only at 60% or better, and dumps its *entire* charge each shot —
there is no half-squeeze. After firing, wait out the recharge or
switch weapons.

**Firing any weapon drops your shields, and they are not re-raised
for you.** Train the reflex: fire, then `shi up`. (A charged shield
comes back up instantly.)

## Hyper-phasers

In hyperspace your phaser bank automatically becomes the
hyper-phaser: a very narrow (5°), very powerful beam drawing 5,000
energy per shot straight off the neutron flux, effective only against
ships **also in hyperspace**. A few well-placed shots destroy
anything. Cheap phaser marks can't touch hyperspace targets at all —
another reason the refit matters.

## Torpedoes

`torpedo <letter|@>` — fast, fire-and-forget, a fixed powerful
charge. The fire control must achieve lock: harder with distance,
impossible against a target above lightspeed, a fully cloaked ship,
or through jamming. At most 3 torpedoes can chase one ship. The
victim is warned, sees "incoming" every tick, and has three outs:

- **outrun the lock** — any jump past warp 1 sheds all torpedoes;
- **decoys** — each decoy out gives a chance per tick of eating an
  inbound weapon once it's close;
- **shields** — a torpedo through shields does half damage at most.

Close before firing: less flight time is less time to react.

## Missiles

`missile <letter|@> <energy>` — you build the warhead, 1 to 50,000
energy. Missiles are slower than torpedoes but **follow their target
into hyperspace**; only sustained speed above roughly warp 4–7 shakes
them. Decoys and shields work as with torpedoes; a 20,000+ warhead
through bare hull is catastrophic, 40,000+ prints "devastating" on
whatever's left.

> **Salvage note:** the Users Guide says a missile drains your flux
> pile "by 10% of that amount"; the in-game help says by the full
> amount. The source divides by the `MISENGFC` config — stock 100, so
> firing a maximum warhead costs all of **500 energy** (GECMDS.C:1278).
> Missiles are cheap to throw; the ammunition is the cost.

## Mines

`mine <timer>` — a neutron mine at your current position, timer 1–50
combat ticks (about 6 seconds each). Anyone within a sector of a live
mine gets proximity warnings with bearing and distance — *unless
they're jammed*, which is the classic setup: jam, mine, run. The
blast is cubic-falloff and shield-permeable enough to gut a fighter
at close range; it can gut *you* too, so clear out. Layers get kill
credit. Stock config: 3 mines out per player, 12 ticking galaxy-wide.

## The support rack

- **Decoys** (`decoy`) — drone that mimics your sensor signature,
  drifts away from you, eats inbound torpedoes and missiles that
  wander near, and shows up as a ship contact on enemy scans. Up to
  10 out; each lives about 90 seconds. More decoys than inbound
  weapons is the rule of thumb.
- **Jammers** (`jammer`) — blinds *every* ship within your scan
  range for a few combat ticks (closer = longer): no weapon locks, no
  mine warnings. It announces itself; use it to cover a retreat, blind
  a gunner, or hide the minefield.
- **Zippers** (`zipper`) — trips every mine within scan range into
  detonating on the next tick. Sweep a suspected field from a safe
  distance — or trip an enemy's mines while he's still standing next
  to them.

## Cloak

`cloak on|off`, on capable hulls. A few seconds to charge the
ST-coils, then you are unscannable and untargetable. The drain is
brutal; when energy runs out the cloak collapses — audibly, to the
whole sector. Moving hard while cloaked can give nearby ships a
bearing fix. You cannot fire anything while cloaked, hyperspace
forces the cloak off, and a damaged cloak generator takes time to
heal. Use it sparingly — it is most useful covering a retreat.

## Shields

`shield up|down`. Shields charge over time (higher marks charge
faster and deeper), drain 100 × mark energy per combat tick while up,
and drop on their own if your pool runs dangerously low. Each hit
knocks charge off — high marks bleed far less per hit — and a shield
battered to nothing is *damaged*: it must mend before it will rise
again. Against you, shields halve torpedo damage, blunt missiles and
phasers, and are the difference between "hit" and "crippled".

## The veterans' page

Everything the original strategy guide taught still holds; the
mechanics above tell you why.

- Shields up, keep moving. Fire, then `shi up` — every time.
- Get close before torpedoes. If he jumps to light speed, jump with
  him and go to hyper-phasers past warp 1.
- Hit by a hyper-phaser? Series of 180° high-speed turns — your
  attacker has to re-aim a 5° beam. Drop out of hyper in another
  sector and cloak as the last ditch.
- Torpedoes incoming: jump to lightspeed. Missiles incoming: run
  flat out and pray, or feed them decoys.
- Cybertron scouts top out at warp 8, cyberquads at warp 10 — a
  Destroyer outruns both ([chapter 7](07-cybertrons.md)).
- Damaged? Sector 0 0 or any owned planet with a yard, `maintenance`,
  and don't get shot at while they work.
- Two ships are twice as powerful as one. Form alliances.
- Loot the kill. You will be looted in turn with grace.
