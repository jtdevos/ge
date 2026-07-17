# 6. Planetary Battles

Ships raid; armies conquer. Taking a defended world is the most
expensive purchase in the game, and the most profitable: the planet,
its goods, its bank, and its civilization become yours.

## The defense

A planet defends itself with three arms
(see [chapter 4](04-planets.md) for stocking them):

- **Fighters** — Nova Class Battle Fighters under a fully automated
  tactical computer. Deadly against troops (each pass shreds dozens),
  evenly matched against other fighters. They engage first; your
  troops are not called up until the fighters are gone.
- **Troops** — mercenaries who will fight to the death. The last
  line, and the thing that holds a planet.
- **Ion cannons** — automated ion-plasma transmitters that fire on
  any hostile ship in orbit every combat tick, hitting for up to half
  a hull per blast against bare armor. They stop firing only when
  you leave (or the stock runs out). Strictly defensive, no kill
  credit sought or given.

An attacker is always at a disadvantage: the local forces are better
supported and fresh. Come with superior numbers.

## The assault

`attack <n> tro` or `attack <n> fig`, in orbit, from a hull rated for
planetary assault (see the class table — an Interceptor cannot).
Attacking sets you **hostile**: the ion cannons open up immediately
and stay on you while you remain close. Each wave resolves in a blow-
by-blow report; survivors return to your ship for another wave.

**Match arms.** Fighters against fighters first; when the defending
fighters are gone, land troops against troops. Troops thrown against
fighters get strafed — between 10 and 50 lost per fighter pass —
and fighter raids against a heavily garrisoned world (over 500
troops) fly into flak.

Rules of the ground war, from the source
([economy spec](../spec/economy.md)):

- Overwhelming force routs: when defenders drop below a quarter of
  your surviving attackers, the field is yours.
- Under-strength landings defect: attackers left below a quarter of
  the defenders *join the planet's garrison*.
- A serious wave that doesn't capture still **pillages** — a little
  of everything walks off with your returning forces.

**Capture** requires, after a wave: for a troop assault, no defending
troops and no fighters left; for a fighter raid, no defending
fighters and fewer than 5 troops. Until then the planet holds — the
old rule "one fighter or one squad of troops (5) keeps the flag" is
exact.

Capture transfers the planet, everything on it, and everything in its
bank. The former owner gets the distress mail — and if they're online
when you strike, they see it live, and you are told they've been
called for help. Expect company.

## Costing an invasion

Troops are 1 credit each at base and weigh next to nothing; fighters
are 50 and heavy. The arithmetic favors mass: against a garrison of
1,000 troops and 100 fighters, bring at least a few hundred fighters
to clear the sky (expect roughly even trades), then thousands of
troops for the ground — and remember every wave under ion fire costs
hull. Veterans soften a rich target first by buying out its unsold
fighter stock (if the owner forgot a reserve), landing a spy for the
inventory report, and timing the blow for when the tax pool is fat.
