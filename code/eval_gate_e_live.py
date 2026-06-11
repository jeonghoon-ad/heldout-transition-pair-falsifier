#!/usr/bin/env python3
"""Live Gate E data-side specificity checks for the public release.

The five Gate E quantities are finite-group product checks. They do not
evaluate a neural model. This script ports the frozen clean-split generator
used for the paper artifacts and regenerates the same per-seed test rates
from deterministic seeds.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import random
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from statistics import mean
from typing import Any

import numpy as np


PAPER_SEEDS = [20260900, 20260901, 20260902, 20260903, 20260904]
CHECK_ORDER = [
    "contextual_commutator",
    "contextual_inverse_shuffle",
    "held_out_generator_pair",
    "reversed_word_difference",
    "same_multiset_different_product",
]
PRIMARY_CHECKS = {"same_multiset_different_product", "contextual_commutator"}
LABEL_CHANGE_CHECKS = {
    "contextual_inverse_shuffle",
    "held_out_generator_pair",
    "reversed_word_difference",
}
S3_TABLE = np.asarray(
    [
        [0, 1, 2, 3, 4, 5],
        [1, 2, 0, 5, 3, 4],
        [2, 0, 1, 4, 5, 3],
        [3, 4, 5, 0, 1, 2],
        [4, 5, 3, 2, 0, 1],
        [5, 3, 4, 1, 2, 0],
    ],
    dtype=np.int64,
)


@dataclass
class Candidate:
    check: str
    variants: list[tuple[str, list[int]]]
    metric_value: bool

    @property
    def structural_keys(self) -> set[tuple[str, str]]:
        return {(multiset_signature(tokens), str(len(tokens))) for _, tokens in self.variants}

    def reduced_keys_for(self, inv: np.ndarray) -> set[str]:
        return {reduced_signature(reduce_word(inv, tokens)) for _, tokens in self.variants}

    @property
    def split_key(self) -> str:
        parts = []
        for variant, tokens in self.variants:
            parts.append(
                f"{variant}:{multiset_signature(tokens)}:{len(tokens)}:{reduced_signature(tokens)}"
            )
        return f"{self.check}::" + "||".join(sorted(parts))


def kst_now() -> str:
    return datetime.now(timezone(timedelta(hours=9))).strftime("%Y-%m-%d %H:%M KST")


def stable_bucket(text: str, buckets: int) -> int:
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    return int(digest[:12], 16) % buckets


def product(table: np.ndarray, tokens: list[int]) -> int:
    out = 0
    for token in tokens:
        out = int(table[out, int(token)])
    return out


def inverse_table(table: np.ndarray) -> np.ndarray:
    n = int(table.shape[0])
    inv = np.zeros(n, dtype=np.int64)
    for i in range(n):
        for j in range(n):
            if table[i, j] == 0 and table[j, i] == 0:
                inv[i] = j
                break
    return inv


def product_table(base: np.ndarray) -> np.ndarray:
    n = int(base.shape[0])
    table = np.zeros((n * n, n * n), dtype=np.int64)
    for a1 in range(n):
        for a2 in range(n):
            left = a1 * n + a2
            for b1 in range(n):
                for b2 in range(n):
                    right = b1 * n + b2
                    table[left, right] = int(base[a1, b1]) * n + int(base[a2, b2])
    return table


def build_s3xs3_full() -> tuple[np.ndarray, list[int], str]:
    table = product_table(S3_TABLE)
    n = int(S3_TABLE.shape[0])
    r = 1
    s = 3
    identity = 0
    generators = [
        r * n + identity,
        s * n + identity,
        identity * n + r,
        identity * n + s,
    ]
    description = "S3 x S3 full product generators (r,e), (s,e), (e,r), (e,s)"
    return table, generators, description


def inverse_word(inv: np.ndarray, tokens: list[int]) -> list[int]:
    return [int(inv[int(x)]) for x in reversed(tokens)]


def reduce_word(inv: np.ndarray, tokens: list[int]) -> list[int]:
    stack: list[int] = []
    for token in tokens:
        item = int(token)
        if stack and int(inv[item]) == stack[-1]:
            stack.pop()
        else:
            stack.append(item)
    return stack


def reduced_signature(tokens: list[int]) -> str:
    return " ".join(str(int(x)) for x in tokens)


def multiset_signature(tokens: list[int]) -> str:
    return " ".join(str(int(x)) for x in sorted(tokens))


def word_record(
    inv: np.ndarray,
    role: str,
    check: str,
    sample_idx: int,
    variant: str,
    tokens: list[int],
) -> dict[str, Any]:
    reduced = reduce_word(inv, tokens)
    return {
        "role": role,
        "check": check,
        "sample_idx": int(sample_idx),
        "variant": variant,
        "seq_len": len(tokens),
        "length_bucket": len(tokens),
        "word": " ".join(str(int(x)) for x in tokens),
        "reduced_word": " ".join(str(int(x)) for x in reduced),
        "reduced_len": len(reduced),
        "multiset_signature": multiset_signature(tokens),
    }


def random_word(rng: np.random.Generator, generators: list[int], length: int) -> list[int]:
    return [int(x) for x in rng.choice(np.asarray(generators, dtype=np.int64), size=length, replace=True)]


def make_same_multiset(
    table: np.ndarray,
    rng: np.random.Generator,
    generators: list[int],
    seq_len: int,
    tries: int,
) -> Candidate | None:
    base = random_word(rng, generators, seq_len)
    base_product = product(table, base)
    for _ in range(tries):
        permuted = list(base)
        rng.shuffle(permuted)
        if product(table, permuted) != base_product:
            return Candidate("same_multiset_different_product", [("base", base), ("permuted", permuted)], True)
    return None


def make_contextual_commutator(
    table: np.ndarray,
    inv: np.ndarray,
    rng: np.random.Generator,
    generators: list[int],
    context_len: int,
) -> Candidate | None:
    left = random_word(rng, generators, context_len)
    right = random_word(rng, generators, context_len)
    a = int(rng.choice(generators))
    b = int(rng.choice(generators))
    core = [a, b, int(inv[a]), int(inv[b])]
    if product(table, core) == 0:
        return None
    full = left + core + right
    context_only = left + right
    return Candidate(
        "contextual_commutator",
        [("full", full), ("context_only", context_only)],
        product(table, full) != product(table, context_only),
    )


def make_contextual_inverse_shuffle(
    table: np.ndarray,
    inv: np.ndarray,
    rng: np.random.Generator,
    generators: list[int],
    half_len: int,
    context_len: int,
) -> Candidate:
    left = random_word(rng, generators, context_len)
    right = random_word(rng, generators, context_len)
    half = random_word(rng, generators, half_len)
    canceling_core = half + inverse_word(inv, half)
    shuffled_core = list(canceling_core)
    rng.shuffle(shuffled_core)
    canceling = left + canceling_core + right
    shuffled = left + shuffled_core + right
    return Candidate(
        "contextual_inverse_shuffle",
        [("canceling", canceling), ("shuffled", shuffled)],
        product(table, canceling) != product(table, shuffled),
    )


def make_reversed(
    table: np.ndarray,
    rng: np.random.Generator,
    generators: list[int],
    seq_len: int,
) -> Candidate:
    word = random_word(rng, generators, seq_len)
    rev = list(reversed(word))
    return Candidate(
        "reversed_word_difference",
        [("forward", word), ("reversed", rev)],
        product(table, word) != product(table, rev),
    )


def make_held_out_generator_pair(
    table: np.ndarray,
    rng: np.random.Generator,
    generators: list[int],
    context_len: int,
) -> Candidate | None:
    left = random_word(rng, generators, context_len)
    right = random_word(rng, generators, context_len)
    a = int(rng.choice(generators))
    b = int(rng.choice(generators))
    ab = left + [a, b] + right
    ba = left + [b, a] + right
    if ab == ba:
        return None
    return Candidate(
        "held_out_generator_pair",
        [("ab", ab), ("ba", ba)],
        product(table, ab) != product(table, ba),
    )


def assign_role(candidate: Candidate, buckets: int, test_bucket: int) -> str:
    return "test" if stable_bucket(candidate.split_key, buckets) == test_bucket else "train"


def collect_seed(args: argparse.Namespace, seed: int) -> dict[str, Any]:
    table, generators, description = build_s3xs3_full()
    inv = inverse_table(table)
    rng = np.random.default_rng(seed)
    rows: list[dict[str, Any]] = []
    metrics: list[dict[str, Any]] = []
    counts = {(role, check): 0 for role in ("train", "test") for check in CHECK_ORDER}
    seen_reduced: dict[str, set[str]] = {"train": set(), "test": set()}
    seen_structural: dict[str, set[tuple[str, str]]] = {"train": set(), "test": set()}
    factories = [
        lambda: make_same_multiset(table, rng, generators, args.seq_len, args.max_shuffle_tries),
        lambda: make_contextual_commutator(table, inv, rng, generators, args.context_len),
        lambda: make_contextual_inverse_shuffle(table, inv, rng, generators, args.inverse_half_len, args.context_len),
        lambda: make_reversed(table, rng, generators, args.seq_len),
        lambda: make_held_out_generator_pair(table, rng, generators, args.context_len),
    ]

    attempts = 0
    while attempts < args.max_attempts and not all(count >= args.n_per_role for count in counts.values()):
        attempts += 1
        for make in factories:
            candidate = make()
            if candidate is None:
                continue
            role = assign_role(candidate, args.split_buckets, args.test_bucket)
            key = (role, candidate.check)
            if counts[key] >= args.n_per_role:
                continue
            opposite = "test" if role == "train" else "train"
            reduced_keys = candidate.reduced_keys_for(inv)
            if reduced_keys & seen_reduced[opposite]:
                continue
            if candidate.structural_keys & seen_structural[opposite]:
                continue
            sample_idx = counts[key]
            counts[key] += 1
            for variant, tokens in candidate.variants:
                rows.append(word_record(inv, role, candidate.check, sample_idx, variant, tokens))
            seen_reduced[role].update(reduced_keys)
            seen_structural[role].update(candidate.structural_keys)
            metrics.append(
                {
                    "role": role,
                    "check": candidate.check,
                    "sample_idx": sample_idx,
                    "metric_value": candidate.metric_value,
                    "split_key": candidate.split_key,
                }
            )
    meta = {
        "group": "s3xs3_full",
        "group_description": description,
        "generators": generators,
        "attempts": attempts,
        "complete": all(count >= args.n_per_role for count in counts.values()),
        "counts": {f"{role}:{check}": count for (role, check), count in counts.items()},
    }
    return {
        "seed": seed,
        "word_rows": rows,
        "metric_records": metrics,
        "meta": meta,
    }


def summarize_metric_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for role in ("train", "test"):
        for check in CHECK_ORDER:
            vals = [row["metric_value"] for row in records if row["role"] == role and row["check"] == check]
            out.append({"role": role, "check": check, "n": len(vals), "rate": sum(vals) / len(vals) if vals else None})
    return out


def overlap_audit(word_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for check in CHECK_ORDER:
        train = [row for row in word_rows if row["role"] == "train" and row["check"] == check]
        test = [row for row in word_rows if row["role"] == "test" and row["check"] == check]
        train_reduced = {row["reduced_word"] for row in train}
        test_reduced = {row["reduced_word"] for row in test}
        train_struct = {(row["multiset_signature"], row["length_bucket"]) for row in train}
        test_struct = {(row["multiset_signature"], row["length_bucket"]) for row in test}
        verbatim = len(train_reduced & test_reduced) / max(1, len(test_reduced))
        structural = len(train_struct & test_struct) / max(1, len(test_struct))
        out.append(
            {
                "check": check,
                "train_rows": len(train),
                "test_rows": len(test),
                "verbatim_reduced_word_overlap": verbatim,
                "structural_overlap_same_multiset_same_length_bucket": structural,
                "status": "PASS" if verbatim == 0.0 and structural == 0.0 else "REVIEW",
            }
        )
    return out


def rollup_seed(seed_payload: dict[str, Any]) -> dict[str, Any]:
    metrics = summarize_metric_records(seed_payload["metric_records"])
    overlap = overlap_audit(seed_payload["word_rows"])
    mandatory_same = next(
        row for row in metrics if row["role"] == "test" and row["check"] == "same_multiset_different_product"
    )["rate"] >= 0.70
    mandatory_choice = any(
        row["role"] == "test"
        and row["check"] in {"contextual_commutator", "contextual_inverse_shuffle"}
        and row["rate"] >= 0.25
        for row in metrics
    )
    overlap_pass = all(row["status"] == "PASS" for row in overlap)
    included_checks = sum(
        1 for row in metrics if row["role"] == "test" and row["rate"] is not None and row["rate"] >= 0.50
    )
    return {
        "updated": kst_now(),
        "snapshot_id": "gate_e_clean_split_20260525__s3xs3_full__n1000_per_role",
        "meta": seed_payload["meta"],
        "metrics": metrics,
        "overlap": overlap,
        "gate_e_clean_pass": bool(
            mandatory_same
            and mandatory_choice
            and included_checks >= 3
            and overlap_pass
            and seed_payload["meta"]["complete"]
        ),
        "read": "Data-level Gate E specificity package; not neural model accuracy.",
    }


def percentile(xs: list[float], pct: float) -> float:
    ordered = sorted(xs)
    idx = (len(ordered) - 1) * pct
    lo = int(idx)
    hi = min(lo + 1, len(ordered) - 1)
    frac = idx - lo
    return ordered[lo] * (1 - frac) + ordered[hi] * frac


def bootstrap_ci(values: list[float], *, n_boot: int, seed: int) -> tuple[float, float]:
    rng = random.Random(seed)
    boots = []
    for _ in range(n_boot):
        sample = [values[rng.randrange(len(values))] for _ in values]
        boots.append(mean(sample))
    return percentile(boots, 0.025), percentile(boots, 0.975)


def table_from_seed_rollups(seed_rollups: dict[int, dict[str, Any]], *, n_boot: int, bootstrap_seed: int) -> dict[str, Any]:
    by_check: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for seed, payload in sorted(seed_rollups.items()):
        for row in payload["metrics"]:
            if row["role"] != "test":
                continue
            by_check[row["check"]].append(
                {
                    "seed": seed,
                    "rate": float(row["rate"]),
                    "complete": bool(payload["meta"]["complete"]),
                    "gate_e_clean_pass": bool(payload["gate_e_clean_pass"]),
                }
            )
    rows = []
    seed_rates = []
    for check in CHECK_ORDER:
        records = sorted(by_check[check], key=lambda x: x["seed"])
        values = [float(r["rate"]) for r in records]
        ci_low, ci_high = bootstrap_ci(values, n_boot=n_boot, seed=bootstrap_seed + sum(ord(c) for c in check))
        ci_width = ci_high - ci_low
        if check in PRIMARY_CHECKS:
            target = 0.05
            ci_class = "primary accuracy"
        elif check in LABEL_CHANGE_CHECKS:
            target = 0.08
            ci_class = "label-change style"
        else:
            target = 0.08
            ci_class = "label-change style"
        rows.append(
            {
                "check": check,
                "ci": [ci_low, ci_high],
                "ci_width": ci_width,
                "mean_rate": mean(values),
                "metric_type": "structural rate"
                if check == "same_multiset_different_product"
                else "group-product specificity rate",
                "n_seeds": len(values),
                "width_pass": ci_width <= target,
                "width_target": target,
            }
        )
        for record in records:
            seed_rates.append({"check": check, **record})
    return {
        "table": "gate_e_live",
        "source": "live clean-split regeneration from public Gate E script",
        "updated": kst_now(),
        "config": {
            "seeds": sorted(seed_rollups),
            "n_per_role": next(iter(seed_rollups.values()))["meta"]["counts"]["test:contextual_commutator"],
            "n_boot": n_boot,
            "bootstrap_seed": bootstrap_seed,
            "group": "s3xs3_full",
        },
        "rows": rows,
        "seed_rates": seed_rates,
    }


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_seed_artifacts(
    seed_dir: Path,
    seed_payload: dict[str, Any],
    rollup: dict[str, Any],
    args: argparse.Namespace,
) -> None:
    seed_dir.mkdir(parents=True, exist_ok=True)
    write_csv(
        seed_dir / "tc0_gate_e_clean_split_word_manifest_20260525.csv",
        seed_payload["word_rows"],
        ["role", "check", "sample_idx", "variant", "seq_len", "length_bucket", "word", "reduced_word", "reduced_len", "multiset_signature"],
    )
    write_csv(
        seed_dir / "tc0_gate_e_clean_split_metrics_20260525.csv",
        seed_payload["metric_records"],
        ["role", "check", "sample_idx", "metric_value", "split_key"],
    )
    preflight = {
        "updated": kst_now(),
        "config": {
            "context_len": args.context_len,
            "inverse_half_len": args.inverse_half_len,
            "max_attempts": args.max_attempts,
            "max_shuffle_tries": args.max_shuffle_tries,
            "n_per_role": args.n_per_role,
            "output_dir": str(seed_dir),
            "seed": seed_payload["seed"],
            "seq_len": args.seq_len,
            "split_buckets": args.split_buckets,
            "test_bucket": args.test_bucket,
        },
        "meta": seed_payload["meta"],
        "metric_rows": str(seed_dir / "tc0_gate_e_clean_split_metrics_20260525.csv"),
        "word_manifest": str(seed_dir / "tc0_gate_e_clean_split_word_manifest_20260525.csv"),
    }
    (seed_dir / "tc0_gate_e_clean_split_preflight_20260525.json").write_text(
        json.dumps(preflight, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (seed_dir / "tc0_gate_e_clean_split_rollup_20260525.json").write_text(
        json.dumps(rollup, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seeds", nargs="+", type=int, default=PAPER_SEEDS)
    parser.add_argument("--seq-len", type=int, default=32)
    parser.add_argument("--inverse-half-len", type=int, default=12)
    parser.add_argument("--context-len", type=int, default=8)
    parser.add_argument("--n-per-role", type=int, default=1000)
    parser.add_argument("--split-buckets", type=int, default=5)
    parser.add_argument("--test-bucket", type=int, default=0)
    parser.add_argument("--max-shuffle-tries", type=int, default=16)
    parser.add_argument("--max-attempts", type=int, default=500000)
    parser.add_argument("--n-boot", type=int, default=2000)
    parser.add_argument("--bootstrap-seed", type=int, default=20260525)
    parser.add_argument("--out", type=Path, default=Path("actual_outputs/gate_e_live_table.json"))
    parser.add_argument("--seed-artifact-dir", type=Path, default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    seed_rollups: dict[int, dict[str, Any]] = {}
    for seed in args.seeds:
        seed_payload = collect_seed(args, seed)
        rollup = rollup_seed(seed_payload)
        seed_rollups[seed] = rollup
        if args.seed_artifact_dir is not None:
            write_seed_artifacts(args.seed_artifact_dir / f"seed_{seed}", seed_payload, rollup, args)
    payload = table_from_seed_rollups(seed_rollups, n_boot=args.n_boot, bootstrap_seed=args.bootstrap_seed)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
