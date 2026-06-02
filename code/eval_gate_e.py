#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
try:
    from .artifact_reduce import gate_e_table, write_json
except ImportError:
    from artifact_reduce import gate_e_table, write_json

if __name__ == "__main__":
    out = Path("actual_outputs/gate_e_table.json")
    write_json(out, gate_e_table())
    print(f"wrote {out}")

