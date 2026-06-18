# Thirty-Nine Years of Simulated Annealing on a Causal Set
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
| Warmup protocol | Unconditional accepts | Three modes compared: legacy / skip / guarded |
| Non-manifoldlike controls | None | Kleitman–Rothschild orders, suspended corona posets |
| Dimension estimators | None (annealing only) | Myrheim–Meyer, Meyer midpoint scaling |
| Structural invariants | None | A battery of order-theoretic features (chain counts, link density, height, …) |
| Correlation analysis | None | Spearman ρ, partial Spearman controlling for *n* |
| Reproducibility | Thesis appendix | Frozen benchmark CSV + Python scripts in this repository |

---

## II. What Becomes Easier To Check

The original thesis demonstrated the method on very small causets where
a single run could be completed in minutes on the hardware of the day.
What changes in 2026 is not the method but the ability to run it many
times and look at the distribution of outcomes. All entries below use
the same energy function and move set as the original.

| Causal set size *n* | 1987-style run | 2026 CPU ensemble |
|---:|:---|:---|
| 6–16 | Single run, qualitative | Whole-ensemble statistics over many seeds; outcome depends strongly on the cooling schedule (quantified in section III) |
| 24–48 | Single or not reported | Still runnable on a CPU but slow; the optimizer's difficulty is characterised in section VI |
| 64+ | Not accessible | Ensembles become expensive because failed runs are slow; see the reduced ensembles in sections V–VI |

The concrete, reproducible witness is the `tesis_like_12.in` benchmark of
section III: under the tuned schedule the optimizer reaches a faithful
(zero-energy) embedding in 95 of 100 seeds, where the default schedule
reaches it in none. Rather than quote a single headline success rate, we
report full ensembles so the schedule dependence is visible.

---

## III. The Same Benchmark, Thirty-Nine Years Apart

The reproducible input `tesis_like_12.in` — twelve elements, a
tesis-like causal structure — serves as the common witness.

| Metric | Bombelli defaults (T₀ = 100, α = 0.9) | Tuned schedule (T₀ = 180, α = 0.8) | Change |
|:---|---:|---:|---:|
| Mean final energy (100 seeds) | 22.735 | 0.000 | −100 % |
| Zero-energy runs | 0 / 100 | 95 / 100 | +95 |
| Schedule selected by | Intuition / thesis norm | Empirical grid scan | — |

*Final energy is the total configuration energy at the end of the
schedule; "zero-energy" means below 10⁻⁶. Run at `dim = 3` over seeds
1959–2058. Regenerate with `python experiments.py schedule`.*

The tuned schedule uses the same annealer, the same energy function,
and the same move set as the original. The only difference is two
numbers — yet under the tuned schedule almost every run reaches a
faithful (zero-energy) embedding, while the defaults never do. This is
not a flaw in the 1987 work; it is just a reminder that annealing
schedules can matter a lot, and repeated runs make that easier to see.

---

## IV. What the Warmup Was Doing

One set of runs looked at the warmup phase. Before annealing begins the
program runs an unconditional-accept warmup loop (up to the simulator's
warmup limit) — a design choice intended to equilibrate the system at
high temperature. The table below shows what that warmup does to
controlled initializations.

| Initialization | Legacy warmup | Skip warmup | Guarded warmup |
|:---|:---|:---|:---|
| Ground truth (E = 0) | Preserved 18/18, E = 0.000 | Preserved 18/18, E = 0.000 | Preserved 18/18, E = 0.000 |
| Truth + small noise (ε = 10⁻³) | Mean E = 111.7, 16/18 | Mean E = 0.003, 18/18 | Mean E = 0.000, **18/18** |
| Truth + medium noise (ε = 5×10⁻²) | Mean E = 747.1, 0/18 | Mean E = 6.79, 1/18 | Mean E = 6.02, **5/18** |
| Random initialization | Mean E = 875.0, 0/18 | Mean E = 451.7, 0/18 | Mean E = 239.8, 0/18 |

*Grid: d ∈ {2, 3, 4}, n ∈ {32, 64}, seeds 1959/1962/1987 — 18 cells per
row. "Preserved" means final energy below 1.0. The warmup phase is
measured in isolation (no subsequent anneal), so this table isolates
what the warmup alone does. Random initialization uses the simulator's
own cold start. Regenerate with `python experiments.py warmup`.*

The guarded warmup accepts a proposed move only if it does not increase
the energy (greedy descent). It is an external wrapper around the same
`ConesSimulator` internals — no change to the energy, the move set, or
the cooling schedule. Across every perturbed and random row the guard
ends at the lowest energy, and on the near-truth initializations it
preserves the configuration where the legacy unconditional-accept
warmup destroys it.

**The oracle check** confirmed that the energy formula returns exactly
0.0 at ground-truth coordinates in 18/18 cases (the `truth` row above,
and verified directly in `tests/`). The Bombelli energy behaves as
expected on those controlled inputs; the large errors above come from
the search dynamics rather than from the energy formula itself. Because
the Bombelli move size at a node is proportional to that node's local
energy, a faithful configuration is a fixed point of every warmup mode,
which is why the `truth` row is preserved everywhere.

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
| Minkowski | 2 | 256 | **2.01** | **2.06** | 0.06 |
| Minkowski | 3 | 256 | **2.99** | **3.06** | 0.20 |
| Minkowski | 4 | 256 | **4.07** | **3.64** | 0.44 |
| Kleitman–Rothschild | — | 256 | 2.37 | 4.71 | **2.34** |
| Corona poset | — | 256 | 1.98 | 7.00 | **5.02** |

*Ensemble of 5 seeds (1959/1962/1987/1990/2003). Regenerate with
`python experiments.py atlas`.*

For manifoldlike sprinklings the two estimators stay close to the
expected dimension. For non-manifoldlike controls they separate. The
finite-size trend is a useful warning sign: the causal set may not be
well described by a low-dimensional sprinkling.

---

## VI. What the Correlate Audit Found

This audit asks whether any order-theoretic property of a causal set
predicts how hard the embedding optimizer finds it. The difficulty
proxy is the mean final energy a causet reaches across 8 optimizer
seeds under a near-greedy probe schedule (lower energy = easier); it is
correlated against embedding-free invariants over an ensemble of N = 30
Minkowski sprinklings, n ∈ {16, 20, 24}:

| Invariant | Difficulty proxy | Raw Spearman ρ | Partial ρ (controlling for *n*) |
|:---|:---|---:|---:|
| `relation_count` | Mean final energy | +0.844 | +0.687 |
| `height` | Mean final energy | +0.341 | +0.487 |
| `mm_dim` | Mean final energy | −0.283 | −0.645 |
| `abs_discrepancy_mm_midpoint` | Mean final energy | −0.043 | −0.322 |

*N = 30 (10 causets at each of n = 16, 20, 24), 8 optimizer seeds each.
`abs_discrepancy_mm_midpoint` uses 24 observations because the midpoint
estimator is undefined for some of the smallest causets. Regenerate with
`python experiments.py correlate`.*

The strongest predictor is the relation count: denser causal sets are
harder for the optimizer, and the effect survives controlling for size
(partial ρ = +0.69 within fixed *n*). The dimension estimators point the
other way once size is controlled — at fixed *n*, causets that look more
manifoldlike are reached more easily. This is a statement about this
optimizer's difficulty landscape on a small, fast ensemble, not about
physical embeddability.

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
