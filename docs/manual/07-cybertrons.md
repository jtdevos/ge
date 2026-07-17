# 7. Cyborgs and Cybertrons

Cyborgs are a race of automatons bent on the destruction of all human
life in the galaxy. Pilot and ship function as a single fighting
unit, and they are the reason the space lanes never feel safe.

## The Cybertron code

Every veteran knows the code; the source confirms it:

- **Small ships are beneath notice.** A Cybertron will not attack an
  Interceptor or a freighter-class hull unless provoked. Fire first —
  or fly too close — and the courtesy ends.
- **Success attracts attention.** The bigger your ship class, the
  more Cybertrons may be dispatched against you at once (a Stealth
  Fighter draws up to two; capital ships draw packs). And success in
  battle ends the courtesy by degrees: past about 30 kills every
  Cybertron that sees you is mean all the time; past 60, the warning
  shots become full torpedo volleys.
- **Mercy is real but rationed.** Against a modest ship flown by a
  modest record, a hunting Cybertron only presses the attack about
  one approach in three — and one hunt in five hundred it simply
  breaks off ("this is your lucky day").

## Fighting them

The Cybertron is armed with phasers and torpedoes but **no
missiles**, and it recycles its phasers slower than most human ships.
It is deadly in hyperspace with hyper-phasers. Its combat habits,
from the source ([cyborgs spec](../spec/cyborgs.md)):

- It pursues across the galaxy — jumping to hyperspace to close long
  distances, matching speeds for a knife fight when it arrives. If
  you stay put too long, it catches up. **Scouts top out at warp 8,
  cyberquads at warp 10**: a Destroyer outruns both.
- It fires torpedo volleys, keeps shields up, lays decoys in
  bunches, and its aim is exact — only its own occasional battle
  malfunctions (announced by strange transmissions) save you.
- Jam one and it goes blind — then **seeds the area with mines** and
  runs on a held course. Chase carefully.
- Wound one past 75% and it drops mines, sometimes pops a jammer,
  and flees. It may summon other Cyborg ships to cover the retreat.
  Beware: the parting minefield is tradition.
- They never run out of energy or torpedoes. You do the math on
  attrition; kill fast or disengage.
- A cloaked ship is invisible to them; a cloaked ship that mills
  around nearby usually bores them into leaving.

## The bestiary

Stock 3.2 fields five Cyborg classes and three ambient drones
(`salvage/data/ships.toml`):

| Class | Kill pts | Notes |
|-------|----------|-------|
| Cybertron Scout | 1,000 | warp 8; the everyday menace |
| Cybertron Battle Cruiser ("Cyberquad") | 2,000 | warp 10, thinks fast, always mean |
| Cybertron Base Star | 10,000 | immobile fortress; Mark-16 phasers, damage factor 20× a fighter's — a fleet action, not a duel |
| Sarten Attack Drone | 50 | a wasp |
| Sarten Obliterator | 500 | crawling siege monster, Mark-16 phasers, very hard to kill |
| Lydorian Garbage Scow | 5 | harmless wanderer; kill it for scrap |
| Murdonian Transport | 200 | cargo hauler *loaded* with loot; passive until fired on, then it calls for help and shoots back. Piracy target #1 |
| Vakory Survey Drone | 50 | scout; fights back, and mines the area when wounded |

Cybertrons carry cash and consumables (torpedoes, decoys, mines,
sometimes gold), and like any kill they drop a share of cargo to
their destroyer. Hunting them is honest work: they respawn endlessly
from the Cyborg yards, your score doesn't bleed when they kill you
(a tenth of the usual deduction), and nobody's colonists mourn.
