from pathlib import Path

import pytest


@pytest.fixture(scope="session")
def tests_dir_path() -> Path:
    return Path(__file__).parent.resolve()


@pytest.fixture(scope="session")
def resources_dir_path(tests_dir_path: Path) -> Path:
    return tests_dir_path / "resources"
