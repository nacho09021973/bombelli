# Thirty-Seven Years of Simulated Annealing on a Causal Set

*A revival of Bombelli (1987) with 2026 tools*

*Ignacio Arancibia · Claude Sonnet 4.6 (Anthropic) · 2026*

---

> *"An application of simulated annealing"*
> — Title of Appendix A.2, Luca Bombelli's PhD thesis, 1987

---

## What this is

In 1987, Luca Bombelli appended to his PhD thesis a Pascal program that tried to embed small causal sets into Minkowski spacetime by simulated annealing. The program ran on the workstations of the era, produced results for a handful of cases, and was never published as a standalone tool.

This repository documents what happens when that program is brought back to life and subjected to the computational tools of 2026: a GPU accelerator, ensemble statistics, and an AI collaborator. We make no claim of advancing causal set theory. We do claim to have learned something about the algorithm itself — and about how much was invisible to its author through no fault of his own.

The paper is in [`paper/bombelli_revival_2026.md`](paper/bombelli_revival_2026.md).

---

## What is in this folder

```
Bombelli/
├── cones.py                  # Faithful Python 3.12 port of Bombelli's Pascal annealer
├── causet_invariants.py      # Order-theoretic invariants (chains, links, height, MM dim)
├── cuda_backend.py           # CUDA/GPU acceleration layer
├── validation_suite.py       # End-to-end reproducibility tests
│
├── inputs/
│   ├── tesis_like_6.in       # 6-element causal set (fast benchmark)
│   └── tesis_like_12.in      # 12-element causal set (Bombelli's canonical case)
│
├── data/
│   ├── schedule_comparison.csv   # Bombelli defaults vs tuned schedule (Section III)
│   ├── warmup_comparison.csv     # Legacy / skip / guarded warmup (Section IV)
│   ├── dimension_atlas.csv       # Dimension estimators on manifoldlike and controls (Section V)
│   └── correlate_summary.csv     # Top order-theoretic correlates (Section VI)
│
├── paper/
│   └── bombelli_revival_2026.md  # The full comparison document
│
└── references/
    ├── Pascal.pdf                # Bombelli's original Pascal source (thesis appendix)
    └── Bombelli_1987_PhD.pdf     # Bombelli's PhD thesis, Syracuse University
```

---

## The one-minute version

**What Bombelli had in 1987:**
A Pascal program, a single workstation, and one run per case.

**What we have in 2026:**
The same program (ported to Python), a GPU, and the ability to run hundreds of seeds across a parameter grid.

**What changed:**
Two numbers. The Bombelli annealer with default parameters (T₀ = 100, α = 0.9) gives a mean final energy of 20.021 on his canonical 12-element test case. Change those two numbers to T₀ = 180, α = 0.8 — same algorithm, same energy function, same move set — and the mean drops to 0.166. A 99% reduction from changing two parameters. That reduction was invisible in 1987 because you need hundreds of runs across a grid to see it.

---

## The five findings

### I. The schedule matters more than anyone could have known

| Schedule | T₀ | α | Mean final energy (100 seeds) |
|:---|---:|---:|---:|
| Bombelli defaults | 100 | 0.9 | 20.021 |
| Tuned (grid scan) | 180 | 0.8 | 0.166 |

Source: [`data/schedule_comparison.csv`](data/schedule_comparison.csv)

### II. The warmup was destroying near-perfect initializations

The original warmup makes 10 unconditional accept steps before annealing. What those 10 steps do:

| Initialization | Legacy warmup | Skip warmup | Guarded warmup |
|:---|:---|:---|:---|
| Ground truth (E = 0) | Preserved 18/18 | Preserved 18/18 | Preserved 18/18 |
| Truth + small noise (ε = 10⁻³) | **Destroyed**: mean E = 18.92, 16/18 | Mean E = 12.12, 17/18 | **Recovered**: mean E = 0.001, 18/18 |
| Truth + medium noise (ε = 5×10⁻²) | Mean E = 395.8, 0/18 | Mean E = 286.0, 0/18 | Mean E = 255.3, 0/18 |
| Random initialization | Mean E = 405.2, 8/18 | Mean E = 307.9, 11/18 | Mean E = 271.4, 12/18 |

*Grid: d ∈ {2, 3, 4}, n ∈ {32, 64}, seeds 1959/1962/1987 — 18 cells per row.*

The guarded warmup accepts a proposed move only if it does not increase the energy. It is an external wrapper around the same internals — no change to the energy, the move set, or the cooling schedule.

Source: [`data/warmup_comparison.csv`](data/warmup_comparison.csv)

### III. The dimension estimators know the difference

Two independent dimension estimators — the Myrheim–Meyer formula and Meyer's midpoint scaling — computed on 256-element causal sets:

| Family | d | MM dim | Midpoint dim | Discrepancy |
|:---|:---:|---:|---:|---:|
| Minkowski | 2 | **2.02** | **2.06** | 0.07 |
| Minkowski | 3 | **3.06** | **3.00** | 0.28 |
| Minkowski | 4 | **4.07** | **3.80** | 0.42 |
| Kleitman–Rothschild | — | 2.37 | 4.71 | **2.34** |
| Corona poset | — | 1.98 | 7.00 | **5.02** |

For manifoldlike sprinklings the two estimators agree. For non-manifoldlike controls they diverge wildly. The divergence grows with n; the agreement shrinks with n. The sign of d|discrepancy|/dn is opposite for the two families — a diagnostic that requires running the program many times at many sizes.

Source: [`data/dimension_atlas.csv`](data/dimension_atlas.csv)

### IV. Denser causal sets are harder for the optimizer

At per-seed level (N = 90, n ∈ {32, 48, 64}):

| Invariant | Target | Raw Spearman ρ | Partial ρ (controlling for n) |
|:---|:---|---:|---:|
| `relation_count` | Floor saturation | +0.941 | +0.903 |
| `chain2_count` | Floor saturation | +0.941 | +0.903 |
| `height` | Floor saturation | +0.836 | +0.779 |
| `abs_discrepancy_mm_midpoint` | Floor saturation | −0.759 | −0.659 |
| `mm_dim` | Floor saturation | −0.698 | −0.530 |

The correlation survives controlling for finite-size scaling: even within a fixed n stratum, denser, taller causal sets are harder for the optimizer.

Source: [`data/correlate_summary.csv`](data/correlate_summary.csv)

### V. The computational frontier moved by orders of magnitude

| Causal set size n | 1987 frontier | 2026 ensemble (8 seeds, GPU) |
|---:|:---|:---|
| 6 | Single run, qualitative | Success rate 25–50 %, phase map available |
| 12 | Single run, qualitative | Success rate 0–12.5 %, schedule matters strongly |
| 16 | Not reported | Success rate 0–12.5 %, frontier of useful search |
| 24 | Not accessible | All runs time out at default budget |
| 32–64 | Not accessible | Ensemble statistics available; floor pathology characterised |

---

## How to run it

**Requirements:** Python 3.12, NumPy. CUDA is optional (CPU fallback is automatic).

```bash
# Run the annealer on the canonical 12-element input
python cones.py inputs/tesis_like_12.in --dim 2

# Run with the tuned schedule (T0=180, alpha=0.8) over 8 seeds
python cones.py inputs/tesis_like_12.in --dim 2 --temp0 180 --alpha 0.8 --seeds 8

# Compute order-theoretic invariants
python causet_invariants.py inputs/tesis_like_12.in

# Run the validation suite
python validation_suite.py
```

---

## What remains the same

The energy function is Bombelli's. The move set is Bombelli's. The cooling rule is Bombelli's. The input format is Bombelli's. The core loop is Bombelli's.

Everything else — the number of runs, the parameter scan, the controls, the invariants, the correlation analysis — is what 37 years of Moore's law, ensemble statistics, and AI assistance made visible.

The pioneers drew the map. We learned how large it is.

*The program works. It always did.*

---

## Citation

If you use this work, please cite:

```
Arancibia, I. and Claude Sonnet 4.6 (Anthropic). "Thirty-Seven Years of Simulated
Annealing on a Causal Set: A Revival of Bombelli (1987) with 2026 Tools." 2026.
```

And the original work this revives:

```
Bombelli, L. "Space-time as a Causal Net." PhD thesis, Syracuse University, 1987.

Bombelli, L., Lee, J., Meyer, D., Sorkin, R. D. "Space-time as a causal set."
Phys. Rev. Lett. 59, 521 (1987).
```

See [`CITATION.cff`](CITATION.cff) for machine-readable citation metadata.

---

## License

MIT — see [`LICENSE`](LICENSE).
