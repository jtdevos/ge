# Galactic Empire — The Reconstructed Players Manual

This is the players manual Galactic Empire 3.2 *should* have shipped
with: the original 1994 Users Guide and the in-game help, merged,
corrected against the game's own source code, and completed with the
things every veteran knew but no document ever wrote down. It is
written from the perspective of the original game — the remake aims
to be faithful to it, so this doubles as the remake's target player
experience.

## Sources and how disputes were settled

1. **The C source** (`mbmgemp/*.C`) — final authority on behavior.
2. **The shipped data** (`salvage/data/*.toml`, extracted from the
   `.MSG` files) — authority on every number. All values quoted here
   are the stock 3.2 defaults; nearly all of them were sysop-tunable,
   so any particular BBS may have differed.
3. **The original docs** (transcribed in [`docs/original/`](../original/))
   — authority on voice, lore, and intent.

Where this manual contradicts the original Users Guide or help text,
a **Salvage note** says so and cites the winner. The mechanics
citations point into [`docs/spec/`](../spec/), which carries the
file-level provenance back to the C source.

## Contents

1. [Getting Started](01-getting-started.md) — the universe, Sector
   0 0, your first ship, your first session
2. [Navigation](02-navigation.md) — bearings, impulse, warp,
   hyperspace, wormholes, and the things that kill travelers
3. [Ships and Equipment](03-ships-and-equipment.md) — the class
   table, shields and phasers, energy, cargo
4. [Owning Planets](04-planets.md) — colonizing, production, taxes,
   trade, spies, and keeping the colonists from revolting
5. [Ship-to-Ship Combat](05-combat.md) — every weapon and defense,
   and the battle wisdom to use them
6. [Planetary Battles](06-planetary-battles.md) — invading and
   defending worlds
7. [Cyborgs and Cybertrons](07-cybertrons.md) — the enemy, their
   code of conduct, and the ambient drones
8. [Teams and Communications](08-teams-and-comms.md) — radio,
   alliances, teams, and GEmail
9. [Scoring](09-scoring.md) — how the roster ranks you
10. [Command Reference](10-command-reference.md) — every command,
    corrected and complete
