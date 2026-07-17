# 8. Teams and Communications

## The radio

Every ship carries a communications console with three channels —
**A**, **B**, and **C** — each tunable with `freq`:

- `freq A hail` — the hailing setting; receives every general hail.
- `freq B 12345` — a numbered frequency. **Below 20000** the channel
  is ordinary sub-space radio, heard in your current star system
  only. **At 20000 and above** transmissions are converted to
  hyperspace modulation packets and heard by anyone on the same
  frequency **anywhere in the galaxy**.

`send <channel> <message>` transmits. An obscure high frequency
shared by your alliance is a private galaxy-wide intercom; just
remember that privacy here is security through obscurity — anyone who
tunes your number hears everything.

> **Salvage note:** one 3.2c help screen puts the hyperspace
> threshold at 32000; the other says 20000. The source compares
> against 20000 (`freq` handling, GECMDS.C) — the 32000 text is
> stale.

## Teams

Teams are formal alliances: a shared roster line, shared distress
calls, and planet trading via the `team` password
([chapter 4](04-planets.md)). A team is identified by a 5-digit code,
chosen at founding, that never changes; names can.

```text
team start <code> <founder-pw> <member-pw> <name…>   found a team
team join <code> <member-pw>                          join one
team unjoin                                           leave
team members / team score                             who and how well
team kick <founder-pw> <user>                         expel (change the
                                                      password too, or
                                                      they'll rejoin)
team newpass <founder-pw> <new-member-pw>             rotate the key
team newname <founder-pw> <name…>                     rebrand
```

Anyone holding the founder password is a founder — guard it better
than your trade passwords. Stock limits: 50 teams, and a sysop-set
cap on members.

Team score is the average of member scores plus a flat bonus per
member (see [chapter 9](09-scoring.md)): a weak member dilutes the
average, but the per-head bonus means big teams of solid players
score best. Distress calls from teammates reach you at ranges
ordinary radio won't, and when a teammate's planet is attacked, the
whole team hears about it.

## GEmail

The galaxy writes to you while you sleep:

- **Distress mail** — your planet attacked, revolting, or starving;
  your spies' reports and Official Protests when they're caught.
- **Production reports** — nightly snapshot of every planet you own:
  stock, cash, tax pool, rates.
- **Production halted** — a colony hit an item's storage cap and
  that effort is going to waste.

Read it from the **M**ail option on the main menu, every session —
stock config purges mail after **3 days**, and the nightly production
report is the only census your empire gets. `planet` lists your
holdings, but it too is refreshed only by the nightly sweep: planets
claimed today appear tomorrow.

## Watching the galaxy

`who` lists the commanders currently in the game. `roster` ranks
everyone (see [chapter 9](09-scoring.md)); `data` shows the game's
configuration and version. Entering and leaving the game is announced
to everyone — a cloaked ship slips in and out silently.
