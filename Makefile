PYTHON ?= python

.PHONY: check lint test smoke data verify-data verify-data-fast atlas schedule warmup correlate

check: lint test smoke verify-data-fast

lint:
	$(PYTHON) -m py_compile cones.py causet_invariants.py validation_suite.py experiments.py visualize_causets.py visualize_local_minima.py

# Real unit tests. Fails (non-zero exit) if any test fails.
test:
	$(PYTHON) -m pytest -v --tb=short

# Fast end-to-end check that the core programs run. Writes to a scratch
# directory so it never touches the committed data/ CSVs.
smoke:
	$(PYTHON) cones.py --sprinkle 8 --dim 1 --seed 1959 --output /tmp/smoke_cone.out --no-plot
	$(PYTHON) causet_invariants.py inputs/tesis_like_6.in >/dev/null
	$(PYTHON) experiments.py atlas --data-dir /tmp/smoke_data

# Regenerate every paper CSV from scratch (this overwrites data/*.csv).
data:
	$(PYTHON) experiments.py all

# Regenerate committed CSVs in a scratch directory and fail on any drift.
verify-data:
	@tmpdir=$$(mktemp -d); trap 'rm -rf "$$tmpdir"' EXIT; \
	$(PYTHON) experiments.py all --data-dir "$$tmpdir" >/dev/null; \
	for source in data/*.csv; do \
		diff -u "$$source" "$$tmpdir/$$(basename "$$source")"; \
	done

# Fast CI-sized reproducibility check; the complete verification is above.
verify-data-fast:
	@tmpdir=$$(mktemp -d); trap 'rm -rf "$$tmpdir"' EXIT; \
	$(PYTHON) experiments.py atlas --data-dir "$$tmpdir" >/dev/null; \
	diff -u data/dimension_atlas.csv "$$tmpdir/dimension_atlas.csv"

atlas schedule warmup correlate:
	$(PYTHON) experiments.py $@
