"""Real correctness tests for the Bombelli-revival code.

These tests check mathematical properties that must hold regardless of
implementation details: RNG determinism, energy reproducibility, the
exact Myrheim-Meyer values, Lorentz invariance of the interval residual,
causality of the sprinkler, and the zero-energy oracle. They are meant
to fail loudly if any of those break -- nothing here is a no-op.
"""

from __future__ import annotations

import io
import math
import contextlib
from pathlib import Path

import pytest

import causet_invariants as ci
import cones
import validation_suite as vs


# ---------------------------------------------------------------------
# RNG
# ---------------------------------------------------------------------

def test_pascal_rng_is_deterministic_per_seed():
    a = cones.PascalRNG(1959)
    b = cones.PascalRNG(1959)
    seq_a = [a.ran2() for _ in range(50)]
    seq_b = [b.ran2() for _ in range(50)]
    assert seq_a == seq_b


def test_pascal_rng_in_unit_interval():
    rng = cones.PascalRNG(12345)
    for _ in range(1000):
        v = rng.ran2()
        assert 0.0 <= v < 1.0


def test_pascal_rng_different_seeds_differ():
    a = [cones.PascalRNG(1).ran2() for _ in range(20)]
    b = [cones.PascalRNG(2).ran2() for _ in range(20)]
    assert a != b


# ---------------------------------------------------------------------
# Simulator reproducibility
# ---------------------------------------------------------------------

def _run(z, dim, seed, tmp):
    with contextlib.redirect_stdout(io.StringIO()):
        sim = cones.ConesSimulator(z=[list(r) for r in z], dim=dim, seed=seed,
                                   plot_path=None)
        sim.run(tmp)
    return sim


def test_simulator_is_reproducible(tmp_path):
    m, _ = vs.sprinkle_minkowski_diamond(n=16, seed=7, d_spacetime=2)
    s1 = _run(m, 1, 99, tmp_path / "a.out")
    s2 = _run(m, 1, 99, tmp_path / "b.out")
    assert s1.energies[0] == s2.energies[0]
    assert s1.xold == s2.xold and s1.rold == s2.rold


# ---------------------------------------------------------------------
# Myrheim-Meyer ordering fraction: exact known values
# ---------------------------------------------------------------------

@pytest.mark.parametrize("d,expected", [
    (1.0, 1.0),
    (2.0, 0.5),
    (3.0, 24.0 / 105.0),
    (4.0, 0.1),
])
def test_myrheim_meyer_f_known_values(d, expected):
    assert ci._myrheim_meyer_f(d) == pytest.approx(expected, rel=1e-9)


def test_myrheim_meyer_recovers_dimension():
    # A 1+1 sprinkling should invert to a dimension near 2.
    m, _ = vs.sprinkle_minkowski_diamond(n=200, seed=1959, d_spacetime=2)
    d = ci.myrheim_meyer_dimension(m)
    assert 1.8 <= d <= 2.2


def test_antichain_has_infinite_dimension():
    n = 10
    z = [[False] * n for _ in range(n)]
    assert ci.myrheim_meyer_dimension(z) == math.inf


# ---------------------------------------------------------------------
# Lorentz invariance of the interval residual
# ---------------------------------------------------------------------

def test_interval_rmse_zero_under_boost():
    m, pts = vs.sprinkle_minkowski_diamond(n=20, seed=3, d_spacetime=2)
    v = 0.4
    g = 1.0 / math.sqrt(1.0 - v * v)
    boosted = [(g * (t - v * x), g * (x - v * t)) for (t, x) in pts]
    assert vs.interval_rmse(pts, boosted) == pytest.approx(0.0, abs=1e-9)


def test_interval_rmse_zero_under_translation():
    m, pts = vs.sprinkle_minkowski_diamond(n=20, seed=4, d_spacetime=2)
    shifted = [(t + 5.0, x - 2.0) for (t, x) in pts]
    assert vs.interval_rmse(pts, shifted) == pytest.approx(0.0, abs=1e-9)


# ---------------------------------------------------------------------
# Sprinkler causality
# ---------------------------------------------------------------------

def test_sprinkler_matrix_is_transitive_and_upper_triangular():
    n = 30
    m, pts = vs.sprinkle_minkowski_diamond(n=n, seed=11, d_spacetime=3)
    # upper-triangular: no relation in the lower triangle or on diagonal
    for i in range(n):
        for j in range(0, i + 1):
            assert not m[i][j]
    # transitive: i<k<j related pairwise => i prec j
    for i in range(n):
        for k in range(i + 1, n):
            if not m[i][k]:
                continue
            for j in range(k + 1, n):
                if m[k][j]:
                    assert m[i][j]


def test_sprinkler_relations_match_minkowski_causality():
    n = 25
    m, pts = vs.sprinkle_minkowski_diamond(n=n, seed=2, d_spacetime=3)
    for i in range(n):
        for j in range(i + 1, n):
            dt = pts[j][0] - pts[i][0]
            dx2 = sum((b - a) ** 2 for a, b in zip(pts[i][1:], pts[j][1:]))
            timelike = dt * dt >= dx2 and dt >= 0
            assert m[i][j] == timelike


# ---------------------------------------------------------------------
# Energy oracle
# ---------------------------------------------------------------------

def test_energy_is_zero_at_ground_truth():
    for d_spacetime in (2, 3, 4):
        m, pts = vs.sprinkle_minkowski_diamond(n=24, seed=1959,
                                               d_spacetime=d_spacetime)
        e = vs.bombelli_energy_at(m, pts, d_spatial=d_spacetime - 1)
        assert e == pytest.approx(0.0, abs=1e-9)


def test_energy_positive_for_perturbed_truth():
    # A non-uniform, per-point perturbation breaks causal relations and so
    # must raise the energy above zero (a uniform shift would be a Poincare
    # isometry and leave it at zero).
    m, pts = vs.sprinkle_minkowski_diamond(n=24, seed=1959, d_spacetime=3)
    perturbed = [
        (t + 0.3 * math.sin(i), x + 0.3 * math.cos(i), y - 0.2 * (i % 3))
        for i, (t, x, y) in enumerate(pts)
    ]
    e = vs.bombelli_energy_at(m, perturbed, d_spatial=2)
    assert e > 0.0


# ---------------------------------------------------------------------
# Order-theoretic invariants on hand-checkable posets
# ---------------------------------------------------------------------

def test_invariants_on_a_chain():
    # Total order 0 < 1 < ... < n-1 (transitive closure of a path).
    n = 6
    z = [[j > i for j in range(n)] for i in range(n)]
    assert ci.relation_count(z) == n * (n - 1) // 2
    assert ci.ordering_fraction(z) == pytest.approx(1.0)
    assert ci.height(z) == n
    assert ci.antichain_profile(z) == [1] * n
    assert ci.link_count(z) == n - 1  # only consecutive covers


def test_parse_roundtrip(tmp_path):
    n = 4
    z = [[False] * n for _ in range(n)]
    z[0][1] = z[1][2] = z[0][2] = True
    entries = [("1" if z[i][j] else "0")
               for i in range(n) for j in range(i + 1, n)]
    p = tmp_path / "case.in"
    p.write_text(str(n) + "\n" + " ".join(entries) + "\n")
    parsed = cones.parse_cones_input(p)
    assert parsed == z
