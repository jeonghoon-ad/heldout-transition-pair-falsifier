# Gate E frozen artifacts

This directory contains the canonical Gate E data-side specificity artifacts
used by the paper table.

## Contents

- `gate_e_table.json`: aggregate paper table with mean rates and bootstrap
  confidence intervals.
- `tc0_gate_e_clean_split_5seed_bootstrap_ci_20260525.json`: five-seed
  bootstrap-CI source.
- `tc0_gate_e_clean_split_5seed_rollup_20260525.json`: five-seed rollup source.
- `seed_20260900/` through `seed_20260904/`: per-seed rollup JSONs.

## Regeneration

Run from the repository root:

```bash
python code/eval_gate_e_live.py --seeds 20260900 20260901 20260902 20260903 20260904
```

The live script regenerates the five data-side checks from the deterministic
clean-split construction and writes `actual_outputs/gate_e_live_table.json`.
The expected aggregate means are:

| Check | Mean rate |
| --- | ---: |
| contextual_commutator | 1.0000 |
| contextual_inverse_shuffle | 0.7936 |
| held_out_generator_pair | 0.3402 |
| reversed_word_difference | 0.5554 |
| same_multiset_different_product | 1.0000 |

