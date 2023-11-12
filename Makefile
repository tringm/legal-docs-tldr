WORKDIR?=.
VENVDIR?=$(WORKDIR)/.venv

setup: venv pre-commit

# Virtual environment
.PHONY: venv
venv: $(VENVDIR)/bin/activate

#.PHONY: clean-venv
clean-venv:
	rm -rf $(VENVDIR)

poetry.lock: pyproject.toml
	poetry lock

$(VENVDIR)/bin/activate: poetry.lock
	poetry install


# Pre-commit
.PHONY: pre-commit
pre-commit: .pre-commit-config.yaml
	pre-commit install

.PHONY: tests
tests: venv
	pre-commit run --all-files
	poetry run pytest
	pipenv run coverage report
