# salvage/

Machine-extracted ground truth from the original GE 3.2 source:

- `data/` — ship classes, sysop config, and balance constants as TOML,
  loaded by the remake (`ge/data.py`) at runtime.
- `tools/` — the extractor scripts that generated `data/ships.toml`
  and `data/config.toml` from the original `.MSG` files.

The narrative documentation of the salvage pass — what was extracted,
from where, and the original's runtime model — lives in
[docs/salvage.md](../docs/salvage.md); the mechanics spec is in
[docs/spec/](../docs/spec/).
