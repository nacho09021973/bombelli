#!/usr/bin/env python3
"""Reproducible experiment driver for the Bombelli-revival paper.

Every table of numbers in ``paper/bombelli_revival_2026.md`` is produced
by one subcommand of this script. Nothing is hard-coded: each CSV under
``data/`` is the literal output of running the corresponding experiment
here. Run ``python experiments.py all`` to regenerate every file, or run
a single experiment by name.

All experiments are deterministic given their seeds, so anyone can rerun
them and obtain byte-identical CSVs. The parameters (sizes, seed lists,
dimensions, annealing budget) are defined as named constants at the top
of each experiment function and explained in its docstring; they are the
experimental design, not magic numbers.

Subcommands
-----------
atlas       -> data/dimension_atlas.csv      (paper section V)
schedule    -> data/schedule_comparison.csv  (paper section III)
warmup      -> data/warmup_comparison.csv    (paper section IV)
correlate   -> data/correlate_summary.csv    (paper section VI)
all         -> all of the above
"""

from __future__ import annotations

import argparse
import contextlib
import io
import math
import random
import statistics
import tempfile
from pathlib import Path
from typing import Callable, Dict, List, Sequence, Tuple

import causet_invariants
import cones
import validation_suite as vs


DATA_DIR = Path(__file__).resolve().parent / "data"

Coord = Tuple[float, ...]
CausalMatrix = List[List[bool]]


def _write_csv(path: Path, header: Sequence[str], rows: Sequence[Sequence[object]]) -> None:
    """Write a CSV with a fixed header. Floats are pre-formatted by callers."""

    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [",".join(header)]
    for row in rows:
        lines.append(",".join(str(cell) for cell in row))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _mean(values: Sequence[float]) -> float:
    finite = [v for v in values if math.isfinite(v)]
    return statistics.fmean(finite) if finite else float("nan")


# ---------------------------------------------------------------------
# Experiment 1: dimension atlas (paper section V)
# ---------------------------------------------------------------------

ATLAS_N = 256
ATLAS_SEEDS = (1959, 1962, 1987, 1990, 2003)


def experiment_atlas(out: Path) -> List[Dict[str, object]]:
    """Two independent dimension estimators across causet families.

    For each family we build ``len(ATLAS_SEEDS)`` causets of size
    ``ATLAS_N`` and compute, per causet:

    - the Myrheim-Meyer dimension (ordering-fraction inversion), and
    - Meyer's midpoint-scaling dimension (nested-interval cardinalities).

    Both estimators live in :mod:`causet_invariants` and depend only on
    the causal matrix, never on an embedding. Manifoldlike Minkowski
    sprinklings should give two estimators that agree near the true
    dimension; the non-manifoldlike controls (Kleitman-Rothschild and
    suspended corona) should make them diverge. The reported
    ``mean_abs_discrepancy`` is the mean over seeds of
    ``|mm_dim - midpoint_dim|``.
    """

    families: List[Tuple[str, str, Callable[[int], CausalMatrix]]] = []
    for d in (2, 3, 4):
        families.append(
            (
                "minkowski",
                str(d),
                lambda seed, d=d: vs.sprinkle_minkowski_diamond(
                    n=ATLAS_N, seed=seed, d_spacetime=d
                )[0],
            )
        )
    families.append(
        ("kleitman_rothschild", "NA",
         lambda seed: vs.generate_kleitman_rothschild(ATLAS_N, seed=seed))
    )
    families.append(
        ("corona", "NA",
         lambda seed: vs.generate_corona_poset(ATLAS_N, seed=seed))
    )

    rows: List[Dict[str, object]] = []
    for family, d_label, builder in families:
        mm_vals: List[float] = []
        mid_vals: List[float] = []
        disc_vals: List[float] = []
        for seed in ATLAS_SEEDS:
            z = builder(seed)
            mm = causet_invariants.myrheim_meyer_dimension(z)
            mid = causet_invariants.midpoint_scaling_dimension(z)
            mm_vals.append(mm)
            mid_vals.append(mid)
            if math.isfinite(mm) and math.isfinite(mid):
                disc_vals.append(abs(mm - mid))
        rows.append({
            "family": family,
            "d_spacetime": d_label,
            "n": ATLAS_N,
            "n_seeds": len(ATLAS_SEEDS),
            "mean_mm_dim": _mean(mm_vals),
            "mean_midpoint_dim": _mean(mid_vals),
            "mean_abs_discrepancy": _mean(disc_vals),
        })

    _write_csv(
        out,
        ["family", "d_spacetime", "n", "n_seeds",
         "mean_mm_dim", "mean_midpoint_dim", "mean_abs_discrepancy"],
        [[r["family"], r["d_spacetime"], r["n"], r["n_seeds"],
          f"{r['mean_mm_dim']:.2f}", f"{r['mean_midpoint_dim']:.2f}",
          f"{r['mean_abs_discrepancy']:.2f}"] for r in rows],
    )
    return rows


# ---------------------------------------------------------------------
# Experiment 2: schedule comparison (paper section III)
# ---------------------------------------------------------------------

SCHEDULE_INPUT = Path(__file__).resolve().parent / "inputs" / "tesis_like_12.in"
SCHEDULE_DIM = 3
SCHEDULE_N_SEEDS = 100
SCHEDULE_BASE_SEED = 1959
SCHEDULE_ZERO_EPS = 1e-6
# (label, initial_temp, cooling_factor, selection_method)
SCHEDULES = (
    ("bombelli_defaults", 100.0, 0.9, "intuition"),
    ("tuned", 180.0, 0.8, "empirical_grid_scan"),
)


def _run_to_final_energy(
    z: CausalMatrix,
    *,
    dim: int,
    seed: int,
    initial_temp: float,
    cooling_factor: float,
) -> float:
    """Run a full anneal and return the final total configuration energy.

    "Final energy" is the energy of the configuration at the end of the
    annealing schedule, i.e. ``ConesSimulator.energies[0]`` after the
    run. This is the quantity that measures how good an embedding the
    optimizer found (0 means a faithful embedding). Output is discarded.
    """

    with tempfile.TemporaryDirectory() as tmp, contextlib.redirect_stdout(io.StringIO()):
        sim = cones.ConesSimulator(
            z=[list(row) for row in z],
            dim=dim,
            seed=seed,
            interactive=False,
            plot_path=None,
            initial_temp=initial_temp,
            cooling_factor=cooling_factor,
        )
        sim.run(Path(tmp) / "out.txt")
    return sim.energies[0]


def experiment_schedule(out: Path) -> List[Dict[str, object]]:
    """Bombelli's default schedule vs an empirically tuned one.

    The same annealer, energy function and move set are run on the
    ``tesis_like_12`` benchmark for ``SCHEDULE_N_SEEDS`` seeds under two
    cooling schedules. Only the initial temperature and cooling factor
    differ. We report the mean final energy and how many runs reached
    (near) zero energy.

    The two schedules are the Bombelli defaults and the best cell found
    by a separate grid scan over ``initial_temp`` and ``cooling_factor``
    (see ``scripts``-free note in the paper); the tuned values are fixed
    here so the comparison is reproducible.
    """

    z = cones.parse_cones_input(SCHEDULE_INPUT)
    n = len(z)
    seeds = [SCHEDULE_BASE_SEED + i for i in range(SCHEDULE_N_SEEDS)]

    rows: List[Dict[str, object]] = []
    for label, t0, alpha, selection in SCHEDULES:
        energies = [
            _run_to_final_energy(z, dim=SCHEDULE_DIM, seed=s,
                                 initial_temp=t0, cooling_factor=alpha)
            for s in seeds
        ]
        zero_runs = sum(1 for e in energies if e < SCHEDULE_ZERO_EPS)
        rows.append({
            "input": SCHEDULE_INPUT.name,
            "n_elements": n,
            "n_seeds": SCHEDULE_N_SEEDS,
            "schedule_label": label,
            "initial_temp": t0,
            "cooling_factor": alpha,
            "mean_final_energy": _mean(energies),
            "zero_energy_runs": f"{zero_runs}/{SCHEDULE_N_SEEDS}",
            "selection_method": selection,
        })

    _write_csv(
        out,
        ["input", "n_elements", "n_seeds", "schedule_label", "initial_temp",
         "cooling_factor", "mean_final_energy", "zero_energy_runs",
         "selection_method"],
        [[r["input"], r["n_elements"], r["n_seeds"], r["schedule_label"],
          r["initial_temp"], r["cooling_factor"],
          f"{r['mean_final_energy']:.3f}", r["zero_energy_runs"],
          r["selection_method"]] for r in rows],
    )
    return rows


# ---------------------------------------------------------------------
# Experiment 3: warmup comparison (paper section IV)
# ---------------------------------------------------------------------

WARMUP_DIMS = (2, 3, 4)            # simulator spatial dimensions
WARMUP_SIZES = (32, 64)
WARMUP_SEEDS = (1959, 1962, 1987)
WARMUP_LIMIT = 100                 # reconfigure steps in the warmup phase
WARMUP_SMALL_EPS = 1e-3
WARMUP_MEDIUM_EPS = 5e-2
WARMUP_PRESERVE_EPS = 1.0          # final energy below this counts as "near truth"


def _truth_coords(points: Sequence[Coord], dim: int) -> List[Coord]:
    """Truth coordinates as ``(t, x_1, ..., x_dim)`` for the simulator.

    The sprinkler returns ``d_spacetime - 1`` spatial coordinates. When
    the optimizer runs at ``dim`` spatial dimensions we keep the first
    ``dim`` spatial coordinates (here ``dim == d_spacetime - 1`` always,
    so none are dropped) and the time coordinate as the timelike radius.
    """

    out: List[Coord] = []
    for p in points:
        spatial = list(p[1:1 + dim])
        spatial += [0.0] * (dim - len(spatial))
        out.append((p[0], *spatial))
    return out


def _perturb(coords: Sequence[Coord], eps: float, rng: random.Random) -> List[Coord]:
    """Add independent Gaussian noise of scale ``eps`` to every coordinate.

    The time coordinate is kept strictly positive (the simulator requires
    a positive timelike radius) by reflecting any non-positive value.
    """

    out: List[Coord] = []
    for p in coords:
        t = p[0] + rng.gauss(0.0, eps)
        if t <= 0.0:
            t = abs(t) + 1e-9
        spatial = tuple(x + rng.gauss(0.0, eps) for x in p[1:])
        out.append((t, *spatial))
    return out


def _inject(sim: cones.ConesSimulator, coords: Sequence[Coord]) -> None:
    """Seed the simulator with explicit coordinates and initialize state."""

    for i, p in enumerate(coords):
        sim.rnew[i] = p[0]
        sim.xnew[i] = list(p[1:1 + sim.dim])
        sim.change[i] = True
    sim.rave = sum(p[0] for p in coords) / len(coords)
    with contextlib.redirect_stdout(io.StringIO()):
        sim.energy()
        sim.update()


def _warmup_phase(sim: cones.ConesSimulator, mode: str) -> None:
    """Run one of three external warmup wrappers around the same internals.

    legacy   : the original unconditional-accept warmup loop.
    skip     : no warmup at all.
    guarded  : greedy descent -- accept a proposed move only when it does
               not raise the energy. Pure external wrapper; the energy,
               move set and cooling rule are untouched.
    """

    if mode == "skip":
        return
    if mode == "legacy":
        count = 0
        while count < WARMUP_LIMIT and sim.energies[0] > 0.0:
            sim.reconfigure()
            sim.energy()
            sim.update()
            count += 1
        return
    if mode == "guarded":
        count = 0
        while count < WARMUP_LIMIT and sim.energies[0] > 0.0:
            sim.reconfigure()
            sim.energy()
            if sim.deltae <= 0.0:      # accept only non-increasing moves
                sim.update()
            count += 1
        return
    raise ValueError(f"unknown warmup mode {mode!r}")


# (label, kind, eps) -- kind selects how the initial coordinates are built
WARMUP_INITS = (
    ("truth", "truth", 0.0),
    ("truth_plus_small_noise", "noise", WARMUP_SMALL_EPS),
    ("truth_plus_medium_noise", "noise", WARMUP_MEDIUM_EPS),
    ("random", "random", 0.0),
)
WARMUP_MODES = ("legacy_warmup", "skip_warmup", "guarded_warmup")
_MODE_KEY = {"legacy_warmup": "legacy", "skip_warmup": "skip", "guarded_warmup": "guarded"}


def experiment_warmup(out: Path) -> List[Dict[str, object]]:
    """Effect of the warmup phase on controlled initializations.

    For each grid cell (``WARMUP_DIMS`` x ``WARMUP_SIZES`` x
    ``WARMUP_SEEDS`` = 18 cells) we sprinkle a Minkowski causet, build a
    controlled initial embedding, run one warmup mode, and read the
    resulting total energy. Because the Bombelli move size at a node is
    proportional to that node's local energy, a faithful (zero-energy)
    configuration is a fixed point of every mode -- the interesting rows
    are the perturbed and random initializations.

    We report, per (init, mode), the mean final energy over the 18 cells
    and how many cells stayed near the truth (final energy below
    ``WARMUP_PRESERVE_EPS``).
    """

    # Pre-build the 18 grid cells (causet + truth coords) once.
    cells: List[Tuple[int, CausalMatrix, List[Coord]]] = []
    for dim in WARMUP_DIMS:
        d_spacetime = dim + 1
        for n in WARMUP_SIZES:
            for seed in WARMUP_SEEDS:
                m, pts = vs.sprinkle_minkowski_diamond(
                    n=n, seed=seed, d_spacetime=d_spacetime)
                cells.append((dim, [list(r) for r in m], _truth_coords(pts, dim)))

    rows: List[Dict[str, object]] = []
    for init_idx, (init_label, kind, eps) in enumerate(WARMUP_INITS):
        for mode_label in WARMUP_MODES:
            mode = _MODE_KEY[mode_label]
            finals: List[float] = []
            preserved = 0
            for cell_idx, (dim, m, truth) in enumerate(cells):
                # Deterministic per-cell noise stream (stable across runs).
                noise_rng = random.Random(1000 * (init_idx + 1) + cell_idx)
                sim = cones.ConesSimulator(
                    z=m, dim=dim, seed=WARMUP_SEEDS[cell_idx % len(WARMUP_SEEDS)],
                    plot_path=None)
                if kind == "truth":
                    _inject(sim, truth)
                elif kind == "noise":
                    _inject(sim, _perturb(truth, eps, noise_rng))
                elif kind == "random":
                    with contextlib.redirect_stdout(io.StringIO()):
                        sim.startup(io.StringIO())  # simulator's own cold start
                _warmup_phase(sim, mode)
                e = sim.energies[0]
                finals.append(e)
                if e < WARMUP_PRESERVE_EPS:
                    preserved += 1
            rows.append({
                "init_label": init_label,
                "warmup_mode": mode_label,
                "n_runs": len(cells),
                "mean_final_energy": _mean(finals),
                "preserved_near_truth": f"{preserved}/{len(cells)}",
            })

    _write_csv(
        out,
        ["init_label", "warmup_mode", "n_runs",
         "mean_final_energy", "preserved_near_truth"],
        [[r["init_label"], r["warmup_mode"], r["n_runs"],
          f"{r['mean_final_energy']:.3f}", r["preserved_near_truth"]]
         for r in rows],
    )
    return rows


# ---------------------------------------------------------------------
# Experiment 4: correlate audit (paper section VI)
# ---------------------------------------------------------------------
#
# This is a reduced but fully honest reconstruction of the robustness-vs-
# invariants audit. The original paper quoted a 90-observation ensemble;
# regenerating that faithfully needs hours of full-budget anneals, so this
# driver uses a smaller ensemble and a reduced annealing budget. Every
# parameter is named and documented; rerun to reproduce the committed CSV.

CORRELATE_SIZES = (16, 20, 24)
CORRELATE_CAUSETS_PER_N = 10        # -> N = 30 observations
CORRELATE_D_SPACETIME = 3           # sprinklings; optimizer embeds at dim = 2
CORRELATE_OPT_SEEDS = tuple(range(1959, 1967))   # 8 optimizer seeds per causet
# A near-greedy "probe" schedule (low initial temperature) keeps the
# optimizer's energy bounded so the runs are fast and the achieved energy
# is a stable difficulty signal rather than a runaway random walk.
CORRELATE_ANNEAL_LIMIT = 60
CORRELATE_MAX_DATA = 10
CORRELATE_T0 = 15.0
CORRELATE_COOLING = 0.9


def _ranks(xs: Sequence[float]) -> List[float]:
    """Fractional ranks with averaged ties (for Spearman correlation)."""

    order = sorted(range(len(xs)), key=lambda i: xs[i])
    ranks = [0.0] * len(xs)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and xs[order[j + 1]] == xs[order[i]]:
            j += 1
        avg = (i + j) / 2.0 + 1.0
        for k in range(i, j + 1):
            ranks[order[k]] = avg
        i = j + 1
    return ranks


def _pearson(a: Sequence[float], b: Sequence[float]) -> float:
    n = len(a)
    ma = sum(a) / n
    mb = sum(b) / n
    cov = sum((x - ma) * (y - mb) for x, y in zip(a, b))
    va = sum((x - ma) ** 2 for x in a)
    vb = sum((y - mb) ** 2 for y in b)
    if va <= 0.0 or vb <= 0.0:
        return 0.0
    return cov / math.sqrt(va * vb)


def _spearman(a: Sequence[float], b: Sequence[float]) -> float:
    return _pearson(_ranks(a), _ranks(b))


def _partial_spearman(x: Sequence[float], y: Sequence[float],
                      z: Sequence[float]) -> float:
    """Spearman partial correlation of x and y controlling for z.

    Rank-transform all three, then apply the first-order partial
    correlation formula to the rank variables.
    """

    rx, ry, rz = _ranks(x), _ranks(y), _ranks(z)
    rxy, rxz, ryz = _pearson(rx, ry), _pearson(rx, rz), _pearson(ry, rz)
    denom = math.sqrt(max((1 - rxz ** 2) * (1 - ryz ** 2), 0.0))
    if denom == 0.0:
        return 0.0
    return (rxy - rxz * ryz) / denom


def _mean_final_energy(z: CausalMatrix, dim: int) -> float:
    """Optimizer-difficulty proxy: mean achieved energy across seeds.

    For a fixed causet we run ``CORRELATE_OPT_SEEDS`` independent anneals
    with the probe schedule and return the mean of the final total
    energies. A lower value means the optimizer reliably found a good
    embedding (the causet is easy); a higher value means it could not.
    This is a direct, baseline-free measure of how hard the causet is for
    the optimizer, and it is what section VI correlates against the
    causet's order-theoretic invariants.
    """

    finals: List[float] = []
    for seed in CORRELATE_OPT_SEEDS:
        with tempfile.TemporaryDirectory() as tmp, contextlib.redirect_stdout(io.StringIO()):
            sim = cones.ConesSimulator(
                z=[list(r) for r in z], dim=dim, seed=seed, plot_path=None,
                anneal_limit=CORRELATE_ANNEAL_LIMIT, max_data=CORRELATE_MAX_DATA,
                initial_temp=CORRELATE_T0, cooling_factor=CORRELATE_COOLING)
            sim.run(Path(tmp) / "o.txt")
        finals.append(sim.energies[0])
    return _mean(finals)


def experiment_correlate(out: Path) -> List[Dict[str, object]]:
    """Do order-theoretic invariants predict optimizer difficulty?

    Builds ``CORRELATE_CAUSETS_PER_N`` Minkowski sprinklings at each size,
    measures each causet's mean achieved energy across optimizer seeds,
    and correlates that difficulty proxy against a set of embedding-free
    invariants using Spearman rank correlation and its partial version
    controlling for the causet size ``n``.
    """

    dim = CORRELATE_D_SPACETIME - 1
    ns: List[float] = []
    target: List[float] = []
    invariants: Dict[str, List[float]] = {
        "relation_count": [],
        "height": [],
        "mm_dim": [],
        "abs_discrepancy_mm_midpoint": [],
    }
    notes = {
        "relation_count": "size-like invariant",
        "height": "size-like invariant",
        "mm_dim": "dimensionless",
        "abs_discrepancy_mm_midpoint": "dimensionless",
    }

    for n in CORRELATE_SIZES:
        for c in range(CORRELATE_CAUSETS_PER_N):
            seed = 100 * n + c            # distinct, reproducible per cell
            z = vs.sprinkle_minkowski_diamond(
                n=n, seed=seed, d_spacetime=CORRELATE_D_SPACETIME)[0]
            ns.append(float(n))
            target.append(_mean_final_energy(z, dim))
            invariants["relation_count"].append(float(causet_invariants.relation_count(z)))
            invariants["height"].append(float(causet_invariants.height(z)))
            mm = causet_invariants.myrheim_meyer_dimension(z)
            mid = causet_invariants.midpoint_scaling_dimension(z)
            invariants["mm_dim"].append(mm)
            invariants["abs_discrepancy_mm_midpoint"].append(
                abs(mm - mid) if math.isfinite(mm) and math.isfinite(mid) else float("nan"))

    n_obs = len(target)
    rows: List[Dict[str, object]] = []
    for name, xs in invariants.items():
        # drop any non-finite observation pairwise
        idx = [i for i in range(n_obs) if math.isfinite(xs[i])]
        xv = [xs[i] for i in idx]
        yv = [target[i] for i in idx]
        zv = [ns[i] for i in idx]
        rows.append({
            "invariant": name,
            "target": "mean_final_energy",
            "raw_spearman_rho": _spearman(xv, yv),
            "partial_spearman_rho_ctrl_n": _partial_spearman(xv, yv, zv),
            "n_observations": len(idx),
            "note": notes[name],
        })

    rows.sort(key=lambda r: abs(r["raw_spearman_rho"]), reverse=True)

    def _fmt(v: float) -> str:
        return f"{v:+.3f}"

    _write_csv(
        out,
        ["invariant", "target", "raw_spearman_rho",
         "partial_spearman_rho_ctrl_n", "n_observations", "note"],
        [[r["invariant"], r["target"], _fmt(r["raw_spearman_rho"]),
          _fmt(r["partial_spearman_rho_ctrl_n"]), r["n_observations"], r["note"]]
         for r in rows],
    )
    return rows


# ---------------------------------------------------------------------
# Dispatch
# ---------------------------------------------------------------------

EXPERIMENTS: Dict[str, Tuple[Callable[[Path], object], str]] = {
    "atlas": (experiment_atlas, "dimension_atlas.csv"),
    "schedule": (experiment_schedule, "schedule_comparison.csv"),
    "warmup": (experiment_warmup, "warmup_comparison.csv"),
    "correlate": (experiment_correlate, "correlate_summary.csv"),
}


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "experiment",
        choices=list(EXPERIMENTS) + ["all"],
        help="which experiment to run",
    )
    parser.add_argument("--data-dir", type=Path, default=DATA_DIR,
                        help="directory for the output CSVs")
    args = parser.parse_args(argv)

    names = list(EXPERIMENTS) if args.experiment == "all" else [args.experiment]
    for name in names:
        func, filename = EXPERIMENTS[name]
        out = args.data_dir / filename
        print(f"[{name}] -> {out}")
        func(out)
        print(out.read_text().rstrip())
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
