# Held-out transition-pair falsifier — public artifacts

Public code, data, evaluation sets, and figures accompanying the preprint
on a **held-out transition-pair falsifier for projected finite-group state
tracking** (S₃×S₃ and a preliminary S₅ stress test).

These artifacts make the **benchmark protocol, held-out split, overlap audit,
specificity (Gate E) checks, and reported figures independently inspectable**.

> **Scope of this release.** This package contains the *benchmark, audit, and
> evaluation-artifact* layer only. The projected finite-group **carrier model
> implementation is intentionally not included** — some methods are patent
> pending. The released code is
> sufficient to regenerate the benchmark, verify the held-out split is clean,
> reproduce the Gate E specificity rates, and inspect every reported number.

## Layout

```
code/        carrier-free Python: benchmark generation, held-out split,
             overlap audit, Gate E specificity checks
  data_gen_s3xs3.py    generate_dataset / generate_sequence / overlap_audit / self_test
  eval_gate_e.py, eval_gate_e_live.py   Gate E structural specificity rates
  determinism.py        seeding helper
data/        result CSVs (sanitized) for every reported table/figure
eval_sets/   per-seed evaluation token/label arrays (short+medium horizons),
             split manifests, eval manifests, and SHA-256 hash manifests
configs/     run configurations for the projection-matched baselines and gates
figures/     author figure scripts + published vector PDFs
LICENSE
```

**Large evaluation arrays (524,288 and 1,048,576-token horizons)** exceed
GitHub's per-file limit and are archived separately on Zenodo (DOI: 10.5281/zenodo.20506128).
Their SHA-256 hashes are included in `eval_sets/` so the archived arrays can be
integrity-checked against this repository.

## Quick start

```bash
pip install -r requirements.txt          # numpy, scipy, matplotlib, pandas (+ torch for Gate E seeding)

# 1. Verify the held-out split is clean (forbidden pairs absent from train,
#    required pairs present in eval, zero train/eval overlap):
python code/data_gen_s3xs3.py --self-test        # or: python -c "import code.data_gen_s3xs3 as d; d.self_test()"

# 2. Reproduce the Gate E structural specificity rates:
python code/eval_gate_e_live.py --seeds 20260525 20260526 20260527 20260528 20260529

# 3. Inspect / regenerate figures (CSVs in data/):
python figures/regenerate_figures_color.py        # set RES to ./data if needed
```

## Reproducibility notes

- The arrays in `eval_sets/` are the **exact** token/label arrays evaluated in
  the paper; each carries a recorded SHA-256 for byte-for-byte verification.
- `code/data_gen_s3xs3.py` documents and reproduces the generation procedure
  (group definition, forbidden/required transition-pair split, overlap audit).
- Five fixed seeds are used throughout: 20260525–20260529.
- Chance levels: 1/36 ≈ 0.0278 (S₃×S₃), 1/120 ≈ 0.0083 (S₅), 1/6 (Gate A).

## License & citation

Released under the terms in `LICENSE`. If you use these artifacts, please cite
the accompanying preprint (see the paper's bibliography).
