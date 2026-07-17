# 10. Command Reference

Every command, in the order the shipyard teaches them: alphabetical.
All commands abbreviate to their **first three letters**; item names
likewise (`tor` is torpedoes, `flu` flux pods). Most commands explain
themselves when entered bare or malformed. Angle brackets are
arguments; square brackets optional.

Item keywords, used by `buy`/`sell`/`price`/`transfer`/`jettison`:
`men tro mis tor ion flu foo fig dec min jam zip gol` (spies are
bought like any item but leave the ship only via `spy`).

---

**`abandon`** — release ownership of the planet you orbit. The colony
keeps everything. Simple enough.

**`abort`** — cancel a running self-destruct. Public knowledge if
under 10 seconds remained.

**`admin`** — in orbit: claim an unowned planet (you'll be asked,
then prompted for a name), or open the Planet Administration Menu of
one you own: accounting report, collect taxes, work assignments and
trade policy, rename, tax rate, trade password, beacon message.
See [chapter 4](04-planets.md).

**`attack <n> tro|fig`** — planetary assault with n troops or
fighters, in orbit, assault-capable hulls only. Triggers ion cannons.
See [chapter 6](06-planetary-battles.md).

**`buy <qty> <item> [password]`** — buy from the planet you orbit.
Base price at your own planets; the owner's markup elsewhere, subject
to their reserve, sale flag, and trade password.

**`cloak on|off`** — engage the cloaking system (capable hulls).
Seconds to charge, heavy energy drain, no firing while cloaked.

**`cls`** — clear the screen (ANSI).

**`data`** — show the game's configuration and version. *(Absent
from the original guide.)*

**`decoy`** — deploy one decoy (max 10 out, ~90 s life).

**`destruct`** — start the 20-second self-destruct. The countdown is
announced to ships in range at T−10, −5, −2; the blast wrecks
everything nearby, scaled up frighteningly by your hull class. No
kill credit to anyone. Not in the neutral zone — entering it cancels
the countdown.

**`flux`** — swap a fresh flux pod into the energy pool, now, no
confirmation, old pod jettisoned with whatever it still held.

**`freq <A|B|C> <n|hail>`** — tune a radio channel. `hail` receives
all general hails; frequencies below 20000 carry in the local star
system, 20000 and above carry galaxy-wide.
See [chapter 8](08-teams-and-comms.md).

**`help [topic]`** — the online help: every command above plus topics
(`battle`, `class`, `planets`, `strategy`, `wormholes`, …).
`help class` prints the live ship table.

**`impulse <0–99> [deg]`** — sub-light speed as a percentage of
lightspeed, optional relative turn (positive starboard, negative
port — `impulse 10 355` also turns 5° port).

**`jammer`** — launch a jammer: every ship within scan range loses
weapon locks and mine warnings for a few combat ticks.

**`jettison <qty|ALL> <item>`** — dump cargo into space.

**`lock <letter>` / `lock`** — hold fire control on a contact as scan
letters reshuffle; bare `lock` releases. `@` in `torpedo`/`missile`
fires on the locked ship. The lock releases when the target dies or
leaves scanner range.

**`maintenance [password]`** — hire repairs, in orbit: 200 credits at
your own planet (population 25,000+ required), 2,500 at Zygor or
Tahanian Station, password-holders' planets too. ~3% hull per combat
tick; restores all systems and rated warp when done. Cancelled by
leaving orbit or battle.

**`mine <1–50>`** — lay a neutron mine with that many combat ticks on
the timer (~6 s each; the old docs call them "centocks"). Not in the
neutral zone, not while cloaked. Stock: 3 out per player.

**`missile <letter|@> <1–50000>`** — fire a missile with that much
warhead energy (flux cost: warhead ÷ 100 at stock). Tracks into
hyperspace; shaken only above ~warp 4–7.

**`navigate <x> <y>`** — bearing and distance to a sector (its
upper-left corner).

**`new ship|shield|phaser <n>`** — purchase at Zygor, in orbit. Ships
1–9 (see [the class table](03-ships-and-equipment.md)); shields and
phasers Mark 1–19 up to your class limit, with trade-in credit for
the old unit.

> **Salvage note:** both original docs illustrate this command with
> "`new ship 2` — purchase a new Heavy Freighter". Class 2 is not and
> never was the Heavy Freighter; that's class 3. The example bug
> outlived two editions.

**`orbit <planet #>`** — enter orbit, legal within range 250. Stops
the ship. The only safe way to be near a planet.

**`phaser <bearing> [focus 0–5]`** — fire phasers along a relative
bearing. Focus 0 is a needle, 5 a flood; in hyperspace the command
fires the hyper-phaser instead (no focus, 5° beam, 5,000 energy).
Drops your shields — raise them after.

**`planet`** — list the planets registered to you, current as of the
nightly sweep (today's conquests appear tomorrow).

**`price <qty> <item>`** — quote before you buy; same rules as `buy`
without the spending.

**`rename <name>`** — rename your ship. Leave off the "The"; it's
added for you.

**`report nav|sys|inv|acc`** — the ship's books: navigation
(position, heading, speed), systems (damage, charge, energy),
inventory (hold), account (cash).

**`roster [all]`** — the top players (stock shows 10; the guide's
"top 20" was another era), with team standings; `all` lists everyone.

**`rotate <deg>` / `rotate @<deg>`** — turn relative / to absolute
galactic heading, always through the shorter arc, at your class's
turn rate. Works at any speed, 30 energy per order.

**`scan se|ra|pl|sh|lo`** — the tactical scanners:
`se` sector map (planets, wormholes, ships); `ra <1–9>` range
contacts, lettered nearest-first; `pl <n>` planet detail (ratings,
owner, stock for sale); `sh <letter>` ship detail; `lo` long-range
neutron-distortion sweep — finds ships across the galaxy. Decoys scan
as ships; cloaked ships don't scan at all.

**`sell <qty> <item>`** — sell excess goods back to the Empire, in
orbit of Zygor, at base price less a small transfer tax (0.1%).

**`send <A|B|C> <message>`** — transmit on a channel. The only means
of communication between ships.

**`set <option> on|off` / `set ?`** — user preferences: `scanfull`
(full-screen ANSI range scans), `scannames` (player names on scans),
`scanhome` (home the cursor before scan redraws), `filter` (mute
routine chatter — combat warnings always come through).

**`shield up|down`** — raise or lower shields. Charged shields rise
instantly; firing any weapon drops them and does **not** re-raise
them.

**`spy`** — land a spy (from cargo) on the foreign planet you orbit.
Reports arrive by GEmail until he's caught.

**`team …`** — `start`, `join`, `unjoin`, `members`, `score`, and the
founder tools `kick`, `newpass`, `newname`.
See [chapter 8](08-teams-and-comms.md).

**`torpedo <letter|@>`** — fire a torpedo; fire control must achieve
lock (impossible above warp 1 targets, full cloak, jamming). Max 3
chasing one ship.

**`transfer up|down <qty> <item>`** — move cargo between ship and the
planet you orbit. Down: your own planets (anything transferred down
belongs to the colony). Up: your own or unowned planets, weight
permitting.

**`warp <0–50> [deg]`** — warp speed, optional turn, limited by your
hull's rating — exceed it at your engines' peril
([chapter 2](02-navigation.md)).

**`who`** — list the commanders in the game right now. *(Absent from
the original guide.)*

**`x`** — exit to the main menu. Blocked while battle-locked.

**`zipper`** — detonate every mine within scan range, next tick.
Easy enough!

---

*Sysops additionally have `sysop …` tools — conjuring cargo, spawning
Cybertrons, the Mark-20 shield and phaser, the Sysopian Death Star —
none of which you will ever see used fairly.*
