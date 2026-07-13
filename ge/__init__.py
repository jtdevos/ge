"""Galactic Empire remake.

Derived from Galactic Empire 3.2, Copyright (C) 1988-1994 Michael B.
Murdock, released under the GNU General Public License v2 or later.
This remake is distributed under the same terms; see LICENSE.

Package layout:
    data      -- loads salvage/data/*.toml (ground truth from the original)
    geometry  -- port of GELIB.C (bearings, vectors, distance)
    models    -- world-state dataclasses (WARSHP/GALPLNT equivalents)
    universe  -- lazy sector generation (port of GEPLANET.C)
    events    -- events the sim emits; presentation renders them
    sim       -- the simulation core and tick loop

The sim core never formats output and never does I/O; session and
transport layers live outside this package (see CLAUDE.md).
"""
