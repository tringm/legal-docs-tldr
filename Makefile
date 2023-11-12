WORKDIR?=.
VENVDIR?=$(WORKDIR)/.venv

# Virtual environment
.PHONY: venv
venv: $(VENVDIR)/bin/activate

.PHONY: clean-venv
clean-venv:
	rm -rf $(VENVDIR)

poetry.lock: pyproject.toml
	poetry lock

$(VENVDIR)/bin/activate: poetry.lock
	poetry install

.PHONY: tests
tests: venv
	pre-commit run --all-files
	poetry run pytest
	pipenv run coverage report
