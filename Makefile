PYTHON ?= python

.PHONY: setup data survey simulate analyse figures web test
setup:
	$(PYTHON) -m pip install -e ".[dev,dynamics,observations]"
	cd web && npm ci
data:
	$(PYTHON) -m exodynamics.cli data
survey:
	$(PYTHON) -m exodynamics.cli analyse
	$(PYTHON) scripts/update_readme.py
simulate:
	$(PYTHON) scripts/simulate_selected.py
analyse: survey simulate
figures:
	$(PYTHON) scripts/make_figures.py
web:
	cd web && npm run build
test:
	$(PYTHON) -m pytest
	cd web && npm run typecheck && npm run build
