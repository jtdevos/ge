#!/usr/bin/env python3
"""Extract sysop config options from MBMGEMSG.MSG into TOML.

Option line formats:
    NAME {prompt text: default} N min max
    NAME {prompt text? YES} B
    NAME {prompt text? CHOICE} E A B C
    NAME {value} S maxlen description
    NAME {prompt: X} C description
"""
import re
from collections import OrderedDict

SRC = "/Users/jim/develop/ge/mbmgemp/MBMGEMSG.MSG"
OUT = "/Users/jim/develop/ge/salvage/data/config.toml"

ITEMS = ["men", "missiles", "torpedoes", "ion_cannons", "flux_pods", "food",
         "fighters", "decoys", "troops", "zippers", "jammers", "mines",
         "gold", "spies"]

PAT = re.compile(
    r"^([A-Z][A-Z0-9]*) \{(.*)\} (?:\([^)]*\) )?"
    r"(N [0-9]+ [0-9]+|B|E .+?|C .*?|S [0-9]+.*?)\s*$")

RESERVED = re.compile(r"^(ITMPL|ITMWT|ITMVAL|ITMMH|ITMPR)(1[5-9]|2[0-5])$")

opts = OrderedDict()
for line in open(SRC, encoding="latin-1"):
    m = PAT.match(line.rstrip("\n"))
    if not m:
        continue
    name, body, spec = m.groups()
    kind = spec[0]
    split = re.match(r"^(.*)[:?]([^:?]*)$", body, re.S)
    prompt, val = (split.group(1).strip(), split.group(2).strip()) if split \
        else (body, body)
    if kind == "N":
        _, lo, hi = spec.split()
        opts[name] = (prompt, val, f"range {lo}-{hi}")
    elif kind == "B":
        val = {"YES": "true", "NO": "false"}[val]
        opts[name] = (prompt, val, "yes/no")
    elif kind == "E":
        opts[name] = (prompt, f'"{val}"', "one of: " + spec[2:].strip())
    elif kind == "C":
        opts[name] = (prompt, f'"{val}"', "char")
    elif kind == "S":
        opts[name] = (spec.split(None, 2)[-1] if len(spec.split()) > 2 else "",
                      f'"{body}"', "string")

def take(name):
    return opts.pop(name)

def emit_series(f, table, prefix, count, keyfn, start=1):
    f.write(f"\n[{table}]\n")
    for i in range(start, start + count):
        name = f"{prefix}{i:02d}"
        if name not in opts:
            print(f"warn: missing {name}")
            continue
        prompt, val, rng = take(name)
        f.write(f"{keyfn(i)} = {val}  # {prompt} ({rng})\n")

with open(OUT, "w") as f:
    f.write(
        "# Sysop-tunable configuration salvaged verbatim from\n"
        "# mbmgemp/MBMGEMSG.MSG (Galactic Empire 3.2 shipped defaults).\n"
        "# Comments preserve the original sysop prompt text and legal range.\n")

    itemkey = lambda i: ITEMS[i - 1]
    emit_series(f, "items.max_on_planet", "ITMPL", 14, itemkey)
    emit_series(f, "items.weight_per_100", "ITMWT", 14, itemkey)
    emit_series(f, "items.point_value", "ITMVAL", 14, itemkey)
    emit_series(f, "items.made_per_10k_manweeks", "ITMMH", 14, itemkey)
    emit_series(f, "items.base_price", "ITMPR", 14, itemkey)
    mark = lambda i: f"mark_{i:02d}"
    emit_series(f, "shield_prices", "SHLDPR", 19, mark)
    emit_series(f, "phaser_prices", "PHSRPR", 19, mark)

    # neutral sector (0,0) planet table: S00P<n><field>
    S00F = [("NM", "name"), ("OWN", "owner"), ("TYP", "type"),
            ("X", "x"), ("Y", "y"), ("ENV", "environment"),
            ("RES", "resource"), ("DEF", "defined")]
    f.write(
        "\n# Neutral sector (0,0) fixed planets. type: 1 = Zygor shipyard"
        "\n# stock, 2 = station (men/troops/food), 3 = wormhole, 0 = plain."
        "\n# x/y are position within the sector (0-9999).\n")
    for n in range(1, 10):
        f.write(f"\n[neutral_sector.planet_{n}]\n")
        for suffix, key in S00F:
            name = f"S00P{n}{suffix}"
            if name in opts:
                _, val, _ = take(name)
                f.write(f"{key} = {val}\n")

    f.write("\n[general]\n")
    for name, (prompt, val, rng) in opts.items():
        if RESERVED.match(name):
            continue
        f.write(f"{name} = {val}  # {prompt} ({rng})\n")

print(f"wrote {OUT}")
