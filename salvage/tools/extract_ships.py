#!/usr/bin/env python3
"""Parse ship-class option lines from MBMGESHP.MSG into TOML.

MSG option line format (single-line options only; HELP blocks span lines
and are deliberately not matched):

    S01SHLD {  Maximum Shield Type: 10} (S01TYPE#<NONE>) N 0 19
    S01TORP {  Has Torpedo Capability? YES} (S01TYPE#<NONE>) B
    S01TYPE {Class 01 type of Ship? USER} E USER CYBORG DROID <NONE>
    S01NAME {Interceptor} (S01TYPE#<NONE>) S 29 Class-01 Ship Name
"""
import re
import sys
from collections import defaultdict

SRC = "/Users/jim/develop/ge/mbmgemp/MBMGESHP.MSG"
OUT = "/Users/jim/develop/ge/salvage/data/ships.toml"

# fieldname -> (toml key, kind) ; kind drives default extraction
FIELDS = {
    "TYPE":  ("type", "enum"),
    "NAME":  ("name", "str"),
    "SNAME": ("title_name", "str"),
    "SHLD":  ("max_shield_type", "num"),
    "PHSR":  ("max_phaser_type", "num"),
    "TORP":  ("has_torpedoes", "bool"),
    "MISL":  ("has_missiles", "bool"),
    "DECY":  ("has_decoys", "bool"),
    "JAMMR": ("has_jammer", "bool"),
    "ZIPPR": ("has_zipper", "bool"),
    "MINE":  ("has_mines", "bool"),
    "ATTK":  ("can_attack_planets", "bool"),
    "CLOK":  ("has_cloak", "bool"),
    "ACCL":  ("acceleration", "num"),
    "WARP":  ("max_warp", "num"),
    "TONS":  ("max_tonnage", "num"),
    "PRIC":  ("price", "num"),
    "PNTS":  ("kill_points", "num"),
    "SRNG":  ("scan_range", "num"),
    "CATK":  ("cybs_can_attack", "bool"),
    "NATK":  ("cybs_to_attack", "num"),
    "LATK":  ("lowest_user_class_attacked", "num"),
    "MAKE":  ("max_to_create", "num"),
    "TOUGH": ("cyborg_toughness", "num"),
    "DAMF":  ("damage_factor", "num"),
}

LINE = re.compile(r"^S(\d\d)([A-Z0-9]+) \{(.*)\}")

classes = defaultdict(dict)
for line in open(SRC, encoding="latin-1"):
    m = LINE.match(line.rstrip())
    if not m:
        continue
    clsno, field, body = int(m.group(1)), m.group(2), m.group(3)
    if field not in FIELDS:
        if field not in ("HELP", "RES2", "RES3"):
            print(f"warn: unknown field S{clsno:02d}{field}", file=sys.stderr)
        continue
    key, kind = FIELDS[field]
    if kind == "str":
        val = repr(body)[1:-1]
        classes[clsno][key] = f'"{val}"'
    elif kind == "num":
        val = body.rsplit(":", 1)[1].strip()
        classes[clsno][key] = val
    elif kind == "bool":
        val = re.split(r"[?:]", body)[-1].strip()
        classes[clsno][key] = {"YES": "true", "NO": "false"}[val]
    elif kind == "enum":
        val = body.rsplit("?", 1)[1].strip()
        classes[clsno][key] = f'"{val}"'

order = [k for k, _ in FIELDS.values()]
with open(OUT, "w") as f:
    f.write(
        "# Ship class table salvaged verbatim from mbmgemp/MBMGESHP.MSG\n"
        "# (Galactic Empire 3.2 shipped defaults). Class slots with type\n"
        '# "<NONE>" were unused but kept so slot numbering matches the\n'
        "# original. Field ranges per the original sysop config:\n"
        "#   max_shield_type/max_phaser_type 0-19, acceleration 0-32767,\n"
        "#   max_warp 0-255, max_tonnage/price 1-2000000000,\n"
        "#   kill_points 1-32767, scan_range 1-10000000,\n"
        "#   cybs_to_attack/max_to_create 0-255, cyborg_toughness 0-1,\n"
        "#   damage_factor 1-32767 (higher = takes less damage)\n"
    )
    for clsno in sorted(classes):
        f.write(f"\n[class.{clsno:02d}]\n")
        for key in order:
            if key in classes[clsno]:
                f.write(f"{key} = {classes[clsno][key]}\n")
print(f"wrote {OUT}: {len(classes)} classes")
