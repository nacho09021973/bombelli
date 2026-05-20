# Thirty-Seven Years of Simulated Annealing on a Causal Set
## A Revival of Bombelli (1987) with 2026 Tools

*Jose Ignacio Martin Gandul · 2026*

---

> *"An application of simulated annealing"*
> — Title of Appendix A.2, Luca Bombelli's PhD thesis, 1987

> *"¿Para qué llamar caminos*  
> *a los surcos del azar?"*  
> — Antonio Machado

---

Rafael Sorkin and Luca Bombelli introduced causal set theory in 1987:
the idea that spacetime, at the Planck scale, may be described by a
locally finite partially ordered set. The same year, Bombelli appended
to his thesis a Pascal program that tried to embed small causal sets
into Minkowski spacetime by simulated annealing. The program ran on
the workstations of the era, produced results for a handful of cases,
and was never published as a standalone tool.

This note documents a small experiment: port Bombelli's program to
Python, run it reproducibly on ordinary machines, and compare many runs
instead of one. It is meant as a readable revival for people who like
physics and computation, not as a formal claim of advancing causal set
theory.

---

## I. The Instruments

| Aspect | Bombelli (1987) | This work (2024–2026) |
|:---|:---|:---|
| Language | Pascal | Python 3.12 (faithful port) |
| Hardware | ~1 MIPS workstation | Ordinary CPU machine |
| Runs per case | Single run | Ensemble of K seeds (K ≥ 8) |
| Schedule selection | Fixed by hand | Empirical grid scan |
| Warmup protocol | 10 unconditional accepts | Three modes compared: legacy / skip / guarded |
| Non-manifoldlike controls | None | Kleitman–Rothschild orders, suspended corona posets |
| Dimension estimators | None (annealing only) | Myrheim–Meyer, Meyer midpoint scaling |
| Structural invariants | None | 15 order-theoretic features (chain counts, link density, height, …) |
| Correlation analysis | None | Spearman ρ, partial Spearman controlling for *n* |
| Reproducibility | Thesis appendix | Frozen benchmark CSV + Python scripts in this repository |

---

## II. What Becomes Easier To Check

The original thesis demonstrated the method on very small causets where
a single run could be completed in minutes on the hardware of the day.
The table below compares that single-run style with small CPU ensembles.
All 2026 entries use the same energy function and move set as the
original.

| Causal set size *n* | 1987-style run | 2026 CPU ensemble | Note |
|---:|:---|:---|:---|
| 6 | Single run, qualitative | Success rate 25–50 %, small grid available | Best cells: *dim* = 3–4 |
| 12 | Single run, qualitative | Success rate 0–12.5 %, schedule matters strongly | Benchmark `tesis_like_12.in` |
| 16 | Not reported | Success rate 0–12.5 %, budget-dependent | Small runs still possible |
| 24 | Not accessible | All runs time out at default budget | Too slow for this simple setup |
| 32–64 | Not accessible | Ensemble statistics available; floor pathology characterised | Phases 4A–4D |

*"Not accessible"* here means only that this simple historical method
does not scale comfortably under the default budget.

---

## III. The Same Benchmark, Thirty-Seven Years Apart

The reproducible input `tesis_like_12.in` — twelve elements, a
tesis-like causal structure — serves as the common witness.

| Metric | Bombelli defaults (T₀ = 100, α = 0.9) | Tuned schedule (T₀ = 180, α = 0.8) | Change |
|:---|---:|---:|---:|
| Mean final energy (100 seeds) | 20.021 | 0.166 | −99.2 % |
| Zero-energy runs | 0 / 100 | 0 / 100 | — |
| Schedule selected by | Intuition / thesis norm | Empirical grid scan | — |

The tuned schedule uses the same annealer, the same energy function,
and the same move set as the original. The only difference is two
numbers. This is not a flaw in the 1987 work; it is just a reminder
that annealing schedules can matter a lot, and repeated runs make that
easier to see.

---

## IV. What the Warmup Was Doing

One set of runs looked at the warmup phase. The original warmup phase
makes 10 unconditional accept steps before annealing begins — a design
choice intended to equilibrate the system at high temperature. The
table below shows what those 10 steps do to controlled initializations.

| Initialization | Legacy warmup | Skip warmup | Guarded warmup |
|:---|:---|:---|:---|
| Ground truth (E = 0) | Preserved 18/18, E = 0.000 | Preserved 18/18, E = 0.000 | Preserved 18/18, E = 0.000 |
| Truth + small noise (ε = 10⁻³) | Mean E = 18.92, 16/18 | Mean E = 12.12, 17/18 | Mean E = 0.001, **18/18** |
| Truth + medium noise (ε = 5×10⁻²) | Mean E = 395.8, 0/18 | Mean E = 286.0, 0/18 | Mean E = 255.3, 0/18 |
| Random initialization | Mean E = 405.2, 8/18 | Mean E = 307.9, 11/18 | Mean E = 271.4, **12/18** |

*Grid: d ∈ {2, 3, 4}, n ∈ {32, 64}, seeds 1959/1962/1987 — 18 cells per row.*

The guarded warmup accepts a proposed move only if it does not increase
the energy (greedy descent). It is an external wrapper around the same
`ConesSimulator` internals — no change to the energy, the move set, or
the cooling schedule. In the small-noise cases tested here, this simple
guard preserves near-truth configurations much better.

**The oracle check** (Phase 2C) confirmed that the energy formula
returns exactly 0.0 at ground-truth coordinates in 18/18 cases. The
Bombelli energy behaves as expected on those controlled inputs; the
large errors above come from the search dynamics rather than from the
energy formula itself.

---

## V. What the Order-Theoretic Invariants Reveal

The 1987 program had no way to ask "is this causal set manifoldlike
before we try to embed it?" Phase 1 of this study adds that question.

The table below compares two independent dimension estimators — the
Myrheim–Meyer formula and Meyer's midpoint scaling — on Minkowski
sprinklings (manifoldlike by construction) and two non-manifoldlike
controls (Kleitman–Rothschild three-layer orders and suspended corona
posets), at n = 256, ensemble of 5 seeds.

| Family | d_spacetime | n | MM dim | midpoint dim | \|discrepancy\| |
|:---|:---:|---:|---:|---:|---:|
| Minkowski | 2 | 256 | **2.02** | **2.06** | 0.07 |
| Minkowski | 3 | 256 | **3.06** | **3.00** | 0.28 |
| Minkowski | 4 | 256 | **4.07** | **3.80** | 0.42 |
| Kleitman–Rothschild | — | 256 | 2.37 | 4.71 | **2.34** |
| Corona poset | — | 256 | 1.98 | 7.00 | **5.02** |

For manifoldlike sprinklings the two estimators stay close to the
expected dimension. For non-manifoldlike controls they separate. The
finite-size trend is a useful warning sign: the causal set may not be
well described by a low-dimensional sprinkling.

---

## VI. What the Correlate Audit Found

Phase 4D (the robustness-vs-invariants audit) asked whether any
order-theoretic property of a causal set predicts how unstable the
embedding optimizer is across different random seeds. At per-seed level
(N = 90 observations, n ∈ {32, 48, 64}):

| Invariant | Target robustness metric | Raw Spearman ρ | Partial ρ (controlling for *n*) |
|:---|:---|---:|---:|
| `relation_count` | Floor saturation fraction | +0.941 | +0.903 |
| `chain2_count` | Floor saturation fraction | +0.941 | +0.903 |
| `height` | Floor saturation fraction | +0.836 | +0.779 |
| `abs_discrepancy_mm_midpoint` | Floor saturation fraction | −0.759 | −0.659 |
| `mm_dim` | Floor saturation fraction | −0.698 | −0.530 |

The correlation survives controlling for finite-size scaling: even
within a fixed *n* stratum, denser, taller causal sets are harder for
the optimizer in these runs. This is a statement about this optimizer's
difficulty landscape, not about physical embeddability.

---

## VII. A Timeline

| Year | Event |
|---:|:---|
| 1987 | Sorkin and Bombelli introduce causal set theory (*Phys. Rev. Lett.* 59, 521) |
| 1987 | Bombelli writes the Pascal annealing program (PhD thesis, Appendix A.2) |
| 1987–2024 | Program dormant. CST develops theoretically. Modern tools emerge. |
| 2024 | Faithful port to Python 3.12, validated against thesis inputs |
| 2024 | Faithful CPU implementation made portable and reproducible |
| 2024–2025 | Phases 1–3: structural atlas, embedding bridge, schedule probe, warmup audit |
| 2025–2026 | Phases 4–5: epsilon sweep, survival probe, seed robustness, morphology audit |
| 2026 | Phase 4D n-control extension: correlates survive finite-size correction |
| 2026 | This note |

---

## VIII. What Remains the Same

The energy function is Bombelli's. The move set is Bombelli's. The
cooling rule (`4 × exp(−ΔE / T)`) is Bombelli's. The input format is
Bombelli's. The core loop is Bombelli's.

Everything else — the number of runs, the parameter scan, the controls,
the invariants, the n-control audit — is a modern way to look more
carefully at the same small program.

---

## Acknowledgements

This work is a revival and empirical characterisation of the
computational program introduced in:

> L. Bombelli, *Space-time as a Causal Net*, PhD thesis, Syracuse
> University, 1987.

and motivated by the foundational paper:

> L. Bombelli, J. Lee, D. Meyer, R. D. Sorkin, *Space-time as a causal
> set*, Phys. Rev. Lett. **59**, 521 (1987).

The code in this repository is intentionally portable so it can run on
ordinary machines.

---

*Old code, rerun carefully, can still teach us something modest.*
