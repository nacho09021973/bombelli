.PHONY: test smoke data atlas schedule warmup correlate clean-data

# Real unit tests. Fails (non-zero exit) if any test fails.
test:
	python -m pytest -v --tb=short

# Fast end-to-end check that the core programs run. Writes to a scratch
# directory so it never touches the committed data/ CSVs.
smoke:
	python cones.py --sprinkle 8 --dim 1 --seed 1959 --output /tmp/smoke_cone.out --no-plot
	python causet_invariants.py inputs/tesis_like_6.in >/dev/null
	python experiments.py atlas --data-dir /tmp/smoke_data

# Regenerate every paper CSV from scratch (this overwrites data/*.csv).
data:
	python experiments.py all

atlas schedule warmup correlate:
	python experiments.py $@
