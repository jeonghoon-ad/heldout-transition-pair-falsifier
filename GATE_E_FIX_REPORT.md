# Gate E public repo fix report

Updated: 2026-06-11 10:23 KST

## Summary

`code/eval_gate_e_live.py` has been replaced with a carrier-free port of the
original Gate E clean-split generator. The live script now regenerates the
five data-side group-product specificity checks with seeds `20260900` through
`20260904`, `n_per_role=1000`, group `s3xs3_full`, and generators
`[6, 18, 1, 3]`.

The regenerated per-seed test rates and aggregate means/bootstrap confidence
intervals match the frozen paper artifacts exactly.

## Defect fixed

The previous public live script was a simplified demo and did not implement the
Gate E checks used by the paper:

- `contextual_commutator` and `reversed_word_difference` used the same expression.
- `held_out_generator_pair` checked pair presence rather than whether swapping
  generator order changes the group product.
- `same_multiset_different_product` was a constant instead of a generated
  same-multiset product-change check.

## Original script hunt

Found (in the authors' internal archive; not part of this release):

- `tc0_gate_e_clean_split_preflight_20260525.py`
- `tc0_gate_e_clean_split_rollup_20260525.py`
- `tc0_gate_e_clean_split_5seed_rollup_20260525.py`
- `tc0_gate_e_clean_split_5seed_bootstrap_ci_20260525.py`

Evidence checked:

- Five seed logs under `artifacts/gate_e_clean_split_5seed_20260525/logs/`.
- Per-seed preflight JSONs under `artifacts/gate_e_clean_split_5seed_20260525/seed_*/`.
- Per-seed rollups under `artifacts/gate_e_clean_split_5seed_20260525/seed_*/`.

## Port

The public live script now ports the original construction:

- finite group table for `s3xs3_full`;
- deterministic candidate generation for the five checks;
- train/test role assignment by stable SHA-256 bucket;
- rejection of train/test reduced-word and structural overlap;
- per-seed rollup;
- aggregate mean and bootstrap confidence interval generation.

No model code is used.

## Acceptance validation

Command run from repository root:

```bash
python3 code/eval_gate_e_live.py --out actual_outputs/gate_e_live_table.json
```

Validation result:

```text
PER-SEED VALIDATION
20260900: contextual_commutator=1.0000, contextual_inverse_shuffle=0.8090, held_out_generator_pair=0.3150, reversed_word_difference=0.5530, same_multiset_different_product=1.0000
20260901: contextual_commutator=1.0000, contextual_inverse_shuffle=0.7970, held_out_generator_pair=0.3420, reversed_word_difference=0.5740, same_multiset_different_product=1.0000
20260902: contextual_commutator=1.0000, contextual_inverse_shuffle=0.8040, held_out_generator_pair=0.3260, reversed_word_difference=0.5370, same_multiset_different_product=1.0000
20260903: contextual_commutator=1.0000, contextual_inverse_shuffle=0.7800, held_out_generator_pair=0.3640, reversed_word_difference=0.5630, same_multiset_different_product=1.0000
20260904: contextual_commutator=1.0000, contextual_inverse_shuffle=0.7780, held_out_generator_pair=0.3540, reversed_word_difference=0.5500, same_multiset_different_product=1.0000
AGGREGATE VALIDATION
contextual_commutator: mean=1.0000, ci=[1.0000, 1.0000]
contextual_inverse_shuffle: mean=0.7936, ci=[0.7826, 0.8046]
held_out_generator_pair: mean=0.3402, ci=[0.3248, 0.3556]
reversed_word_difference: mean=0.5554, ci=[0.5454, 0.5656]
same_multiset_different_product: mean=1.0000, ci=[1.0000, 1.0000]
ALL_GATE_E_VALUES_MATCH
```

## Frozen artifacts added

- `data/gate_e/gate_e_table.json`
- `data/gate_e/tc0_gate_e_clean_split_5seed_bootstrap_ci_20260525.json`
- `data/gate_e/tc0_gate_e_clean_split_5seed_rollup_20260525.json`
- `data/gate_e/seed_20260900/tc0_gate_e_clean_split_rollup_20260525.json`
- `data/gate_e/seed_20260901/tc0_gate_e_clean_split_rollup_20260525.json`
- `data/gate_e/seed_20260902/tc0_gate_e_clean_split_rollup_20260525.json`
- `data/gate_e/seed_20260903/tc0_gate_e_clean_split_rollup_20260525.json`
- `data/gate_e/seed_20260904/tc0_gate_e_clean_split_rollup_20260525.json`
- `data/gate_e/README.md`

## Hygiene and verification

- `python3 -m py_compile code/eval_gate_e_live.py`: pass.
- Forbidden vocabulary grep on modified/added public files: 0 matches.
- Wrapper attempt:
  - `business/Patent/scripts/run_with_review_check.sh code/eval_gate_e_live.py --help`
  - result: blocked before execution because this public repo is not inside an
    IP-family review folder and the wrapper cannot locate a review root.
  - direct Python execution was used for validation after `py_compile`.
- No git commit or push was performed.

## SHA-256

```text
648d940b4d8973e427e9189ed001ad337d81dc14865c939bf9d3b423cc009ccb  code/eval_gate_e_live.py
7e332c564d2195700e332172d1705ba187307b3a2559846a9dc45bb8654be0c3  README.md
69b8a949f592e3e4618eb6d3322733a0678367d5f0be01155d8a697a55ae548c  data/gate_e/README.md
f02bf43c669385ad904c79c942523442de5b4f4a954260978bf4b9eea615ab36  data/gate_e/gate_e_table.json
0092111ce0e6372992716b532e5f36951ab03bc64bee361c4a322379b564fb0c  data/gate_e/tc0_gate_e_clean_split_5seed_bootstrap_ci_20260525.json
408b8f42f881dea5960d0c6aa9b317a1c0234af1d23c189b6c7a3a180b6cfc40  data/gate_e/tc0_gate_e_clean_split_5seed_rollup_20260525.json
d124990bdebbf9684595749d9f8a01b1ecd6fa3345d722a380d79c0207c05b9b  data/gate_e/seed_20260900/tc0_gate_e_clean_split_rollup_20260525.json
5548c89203d9a02f3394d0be22ece2342aebf2dc78f6ce7a0313fdb5eb72fde5  data/gate_e/seed_20260901/tc0_gate_e_clean_split_rollup_20260525.json
63d10e0d83ba58c473114cd88de1683516a486803b575bf287fd0ad92e0b0895  data/gate_e/seed_20260902/tc0_gate_e_clean_split_rollup_20260525.json
0ee3aaf675a734197e80bbd554e37d8fba042fb6661f54d6ab36fdf02a52c15a  data/gate_e/seed_20260903/tc0_gate_e_clean_split_rollup_20260525.json
ba771cf26ac9e9ce410801e08a0c7749b28d2a5953fae9d4a662f7490cb9c015  data/gate_e/seed_20260904/tc0_gate_e_clean_split_rollup_20260525.json
67dd253d739e68225388df7831554457ab29a2037a580ec24e2cbfbe4d1cfa16  actual_outputs/gate_e_live_table.json
```
