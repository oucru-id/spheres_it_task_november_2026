.PHONY: setup run test grade clean

VENV := .venv
PYTHON := $(VENV)/bin/python

setup:
	python3 -m venv $(VENV)
	$(VENV)/bin/pip install -r requirements.txt
	$(VENV)/bin/pip install -r harness/requirements.txt

run:
	$(PYTHON) -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload

test:
	BASE_URL=http://localhost:8000 $(PYTHON) -m pytest harness/ -v

# Grade a candidate's endpoint running at URL (default: localhost:8000)
# Usage: make grade URL=http://localhost:8000
URL ?= http://localhost:8000
grade:
	BASE_URL=$(URL) $(PYTHON) -m pytest harness/ -v --tb=short

clean:
	rm -rf $(VENV) __pycache__ .pytest_cache
