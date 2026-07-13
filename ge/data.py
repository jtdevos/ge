"""Load the salvaged game data (salvage/data/*.toml) into typed objects.

These files are the shipped defaults of the original GE 3.2; treat them
as sysop-tunable configuration, not code.
"""

from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace

ITEM_NAMES = [
    "men", "missiles", "torpedoes", "ion_cannons", "flux_pods", "food",
    "fighters", "decoys", "troops", "zippers", "jammers", "mines",
    "gold", "spies",
]
NUMITEMS = len(ITEM_NAMES)

# item indexes (I_* in GEMAIN.H)
(I_MEN, I_MISSILE, I_TORPEDO, I_IONCANNON, I_FLUXPOD, I_FOOD, I_FIGHTER,
 I_DECOYS, I_TROOPS, I_ZIPPERS, I_JAMMERS, I_MINE, I_GOLD, I_SPY) = range(14)


@dataclass(frozen=True)
class ShipClass:
    slot: int
    type: str            # USER | CYBORG | DROID | <NONE>
    name: str
    title_name: str
    max_shield_type: int
    max_phaser_type: int
    has_torpedoes: bool
    has_missiles: bool
    has_decoys: bool
    has_jammer: bool
    has_zipper: bool
    has_mines: bool
    can_attack_planets: bool
    has_cloak: bool
    acceleration: int
    max_warp: int
    max_tonnage: int
    kill_points: int
    scan_range: int
    damage_factor: int
    price: int = 0
    cybs_can_attack: bool = False
    cybs_to_attack: int = 0
    lowest_user_class_attacked: int = 0
    max_to_create: int = 0
    cyborg_toughness: int = 0


@dataclass(frozen=True)
class NeutralPlanet:
    plnum: int
    name: str
    owner: str
    type: int            # 1 Zygor shipyard, 2 station, 3 wormhole, 0 plain
    x: int               # position within sector 0,0 (0-9999)
    y: int
    environment: int
    resource: int


class GameData:
    """All salvaged data: ship classes, config, constants, item tables."""

    def __init__(self, root: Path | None = None):
        root = root or Path(__file__).resolve().parent.parent / "salvage" / "data"

        ships = tomllib.load(open(root / "ships.toml", "rb"))
        self.classes: dict[int, ShipClass] = {}
        for slot, fields in ships["class"].items():
            self.classes[int(slot)] = ShipClass(slot=int(slot), **fields)

        config = tomllib.load(open(root / "config.toml", "rb"))
        self.cfg = SimpleNamespace(**config["general"])
        self.items = config["items"]  # max_on_planet/weight_per_100/... by name
        self.shield_prices = [config["shield_prices"][f"mark_{i:02d}"]
                              for i in range(1, 20)]
        self.phaser_prices = [config["phaser_prices"][f"mark_{i:02d}"]
                              for i in range(1, 20)]
        self.neutral_planets = [
            NeutralPlanet(plnum=n, **{k: v for k, v in p.items() if k != "defined"})
            for n, p in ((int(k.split("_")[1]), v)
                         for k, v in config["neutral_sector"].items())
            if p.get("defined", False)
        ][: self.cfg.S00PLNUM]

        constants = tomllib.load(open(root / "constants.toml", "rb"))
        flat: dict[str, object] = {}
        for section, values in constants.items():
            if section == "item_indexes":
                continue
            flat.update(values)
        self.const = SimpleNamespace(**flat)

        # per-item arrays in item-index order (like the original globals)
        self.baseprice = [self.items["base_price"][n] for n in ITEM_NAMES]
        self.weight = [self.items["weight_per_100"][n] for n in ITEM_NAMES]
        self.value = [self.items["point_value"][n] for n in ITEM_NAMES]
        self.manhours = [self.items["made_per_10k_manweeks"][n] for n in ITEM_NAMES]
        self.maxpl = [self.items["max_on_planet"][n] for n in ITEM_NAMES]

    def user_classes(self) -> list[ShipClass]:
        return [c for c in self.classes.values() if c.type == "USER"]
