from typing import List

import pytest
from ignore.utils import get_file, validate_gitignore_response


def pytest_addoption(parser):
    parser.addoption(
        "-n",
        action="store",
        default="python",
        help="Language name(s); pass as many names as necessary.",
    )


@pytest.mark.parametrize("names", [["python"], ["linux", "java"]])
def test_get_file(names: List[str]) -> None:
    """Test that get_file successfully fetches templates"""
    content = get_file(names)
    assert content is not None
    assert isinstance(content, str)
    assert len(content) > 0
    assert validate_gitignore_response(content)


def test_get_file_invalid_template() -> None:
    """Test that invalid templates return error content"""
    content = get_file(["invalidtemplate123456"])
    assert content is not None
    assert isinstance(content, str)
    assert not validate_gitignore_response(content)
