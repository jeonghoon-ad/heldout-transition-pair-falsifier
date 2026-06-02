#!/usr/bin/env python3
"""S3 x S3 data generation with explicit held-out ordered-pair splits."""
from __future__ import annotations

import argparse
import itertools
import json
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

Perm = tuple[int, int, int]
GroupElt = tuple[Perm, Perm]


def compose_perm(a: Perm, b: Perm) -> Perm:
    return tuple(a[i] for i in b)  # apply b, then a


def inv_perm(a: Perm) -> Perm:
    out = [0, 0, 0]
    for i, j in enumerate(a):
        out[j] = i
    return tuple(out)  # type: ignore[return-value]


S3: list[Perm] = list(itertools.permutations(range(3)))
S3_INDEX = {p: i for i, p in enumerate(S3)}
IDENTITY: GroupElt = ((0, 1, 2), (0, 1, 2))
GENERATORS: list[GroupElt] = [
    ((1, 0, 2), (0, 1, 2)),
    ((1, 2, 0), (0, 1, 2)),
    ((0, 1, 2), (1, 0, 2)),
    ((0, 1, 2), (1, 2, 0)),
]
FORBIDDEN_PAIRS = [(0, 2), (2, 0)]


def compose(a: GroupElt, b: GroupElt) -> GroupElt:
    return compose_perm(a[0], b[0]), compose_perm(a[1], b[1])


def inverse(g: GroupElt) -> GroupElt:
    return inv_perm(g[0]), inv_perm(g[1])


def all_group_elements() -> list[GroupElt]:
    return [(a, b) for a in S3 for b in S3]


GROUP_ELEMENTS = all_group_elements()
GROUP_INDEX = {g: i for i, g in enumerate(GROUP_ELEMENTS)}


def state_index(g: GroupElt) -> int:
    return GROUP_INDEX[g]


def accumulate(tokens: Iterable[int]) -> GroupElt:
    state = IDENTITY
    for token in tokens:
        state = compose(GENERATORS[token], state)
    return state


def has_pair(tokens: list[int], pair: tuple[int, int]) -> bool:
    return any((tokens[i], tokens[i + 1]) == pair for i in range(len(tokens) - 1))


def violates_forbidden(tokens: list[int], pairs: list[tuple[int, int]] = FORBIDDEN_PAIRS) -> bool:
    return any(has_pair(tokens, p) for p in pairs)


def reduced_word(tokens: list[int]) -> tuple[int, ...]:
    """Cheap canonicalization by deleting adjacent inverse generator pairs."""
    inverse_token = {0: 0, 1: 1, 2: 2, 3: 3}
    stack: list[int] = []
    for token in tokens:
        if stack and inverse_token[token] == stack[-1]:
            stack.pop()
        else:
            stack.append(token)
    return tuple(stack)


def structural_signature(tokens: list[int]) -> tuple[int, tuple[int, ...]]:
    return len(tokens), tuple(sorted(tokens))


@dataclass(frozen=True)
class Example:
    tokens: list[int]
    label: int


def generate_sequence(seq_len: int, rng: random.Random, *, require_pairs: bool, forbid_pairs: bool) -> list[int]:
    if require_pairs and seq_len < 4:
        raise ValueError("seq_len must be >=4 when requiring both held-out pairs")
    for _ in range(100000):
        tokens = [rng.randrange(len(GENERATORS)) for _ in range(seq_len)]
        if require_pairs:
            tokens[0:2] = [0, 2]
            tokens[2:4] = [2, 0]
            rng.shuffle(tokens)
        if forbid_pairs and violates_forbidden(tokens):
            continue
        if require_pairs and not all(has_pair(tokens, p) for p in FORBIDDEN_PAIRS):
            continue
        return tokens
    raise RuntimeError("failed to generate sequence under split constraints")


def generate_dataset(n: int, seq_len: int, seed: int, *, split: str) -> list[Example]:
    rng = random.Random(seed)
    require = split == "eval"
    forbid = split == "train"
    data = []
    for _ in range(n):
        tokens = generate_sequence(seq_len, rng, require_pairs=require, forbid_pairs=forbid)
        data.append(Example(tokens=tokens, label=state_index(accumulate(tokens))))
    return data


def overlap_audit(train: list[Example], eval_: list[Example]) -> dict[str, float | int | str]:
    train_words = {reduced_word(x.tokens) for x in train}
    eval_words = [reduced_word(x.tokens) for x in eval_]
    train_struct = {structural_signature(x.tokens) for x in train}
    eval_struct = [structural_signature(x.tokens) for x in eval_]
    exact = sum(w in train_words for w in eval_words)
    structural = sum(s in train_struct for s in eval_struct)
    return {
        "n_train": len(train),
        "n_eval": len(eval_),
        "verbatim_overlap": exact,
        "verbatim_overlap_rate": exact / max(1, len(eval_)),
        "structural_overlap": structural,
        "structural_overlap_rate": structural / max(1, len(eval_)),
        "status": "PASS" if exact == 0 else "REVIEW",
    }


def to_jsonable(data: list[Example]) -> list[dict[str, object]]:
    return [{"tokens": x.tokens, "label": x.label} for x in data]


def write_dataset(path: Path, train: list[Example], eval_: list[Example]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"train": to_jsonable(train), "eval": to_jsonable(eval_), "audit": overlap_audit(train, eval_)}
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def self_test() -> int:
    train = generate_dataset(64, 8, 20260525, split="train")
    eval_ = generate_dataset(16, 8, 20260526, split="eval")
    for offset in range(1, 200):
        if overlap_audit(train, eval_)["status"] == "PASS":
            break
        eval_ = generate_dataset(16, 8, 20260526 + offset, split="eval")
    forbidden_count = sum(violates_forbidden(x.tokens) for x in train)
    required_ok = sum(all(has_pair(x.tokens, p) for p in FORBIDDEN_PAIRS) for x in eval_)
    audit = overlap_audit(train, eval_)
    print(f"FORBIDDEN PAIR COUNT IN TRAIN: {forbidden_count}")
    print(f"REQUIRED PAIR COUNT IN EVAL: >= 1 per sequence ({required_ok}/{len(eval_)})")
    print(f"OVERLAP AUDIT: {audit['status']}")
    return 0 if forbidden_count == 0 and required_ok == len(eval_) and audit["status"] == "PASS" else 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--out", type=Path)
    parser.add_argument("--seed", type=int, default=20260525)
    parser.add_argument("--n-train", type=int, default=200)
    parser.add_argument("--n-eval", type=int, default=8)
    parser.add_argument("--seq-len", type=int, default=8)
    args = parser.parse_args()
    if args.self_test:
        return self_test()
    if not args.out:
        raise SystemExit("--out is required unless --self-test is used")
    train = generate_dataset(args.n_train, args.seq_len, args.seed, split="train")
    eval_ = generate_dataset(args.n_eval, args.seq_len, args.seed + 1, split="eval")
    write_dataset(args.out, train, eval_)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
