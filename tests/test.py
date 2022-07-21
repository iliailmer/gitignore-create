from typing import List

import pytest
from ignore.utils import get_all, get_file


def test_all() -> None:
    response = get_all()
    assert response.status_code == 200
    return


def pytest_addoption(parser):
    parser.addoption(
        "-n",
        action="store",
        default="python",
        help="Language name(s); pass as many names as necessary.",
    )


@pytest.fixture(params=[["python"], ["linux", "java"]])
def test_file(names: List[str]) -> None:
    response = get_file(names)
    assert response.status_code == 200
    return
