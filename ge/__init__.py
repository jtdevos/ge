"""Galactic Empire remake.

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
