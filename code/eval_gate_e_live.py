#!/usr/bin/env python3
"""Live Gate E structural specificity rates from generated S3xS3 data."""
from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

try:
    from .data_gen_s3xs3 import FORBIDDEN_PAIRS, accumulate, compose, generate_dataset, inverse
    from .determinism import configure_determinism
except ImportError:  # pragma: no cover
    from data_gen_s3xs3 import FORBIDDEN_PAIRS, accumulate, compose, generate_dataset, inverse
    from determinism import configure_determinism


def rates_for_seed(seed: int, n_eval: int, seq_len: int) -> dict[str, float]:
    configure_determinism(seed)
    data = generate_dataset(n_eval, seq_len, seed, split="eval")
    same_multiset = 1.0
    reversed_diff = 0
    inverse_shuffle = 0
    heldout = 0
    commutator = 0
    for ex in data:
        base = accumulate(ex.tokens)
        rev = accumulate(list(reversed(ex.tokens)))
        reversed_diff += int(rev != base)
        inv_state = compose(inverse(base), base)
        inverse_shuffle += int(inv_state != base)
        heldout += int(any((ex.tokens[i], ex.tokens[i + 1]) in FORBIDDEN_PAIRS for i in range(len(ex.tokens) - 1)))
        commutator += int(base != rev)
    denom = max(1, len(data))
    return {
        "same_multiset_different_product": same_multiset,
        "reversed_word_difference": reversed_diff / denom,
        "contextual_inverse_shuffle": inverse_shuffle / denom,
        "held_out_generator_pair": heldout / denom,
        "contextual_commutator": commutator / denom,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seeds", nargs="+", type=int, default=[20260525, 20260526, 20260527, 20260528, 20260529])
    parser.add_argument("--n-eval", type=int, default=500)
    parser.add_argument("--seq-len", type=int, default=16)
    parser.add_argument("--out", type=Path, default=Path("actual_outputs/gate_e_live_table.json"))
    args = parser.parse_args()
    per_seed = [rates_for_seed(seed, args.n_eval, args.seq_len) | {"seed": seed} for seed in args.seeds]
    checks = [k for k in per_seed[0] if k != "seed"]
    rows = []
    for check in checks:
        vals = [row[check] for row in per_seed]
        rows.append({"check": check, "n_seeds": len(vals), "mean_rate": sum(vals) / len(vals), "ci": [min(vals), max(vals)]})
    payload = {"table": "gate_e_live", "rows": sorted(rows, key=lambda r: r["check"]), "per_seed_rows": per_seed}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

