import subprocess

import pytest

from pytest_directives.pytest_directives import PytestResolver

from tests.pytest_directives.conftest import PathTests
from tests.pytest_directives.test_data import test_several_functions, test_package
from tests.pytest_directives.test_data.test_function import test_function
from tests.pytest_directives.test_data.test_class import TestClass


def get_pytest_collect_result(tests_path: str) -> str:
    proc = subprocess.Popen(f"pytest --collect-only {tests_path}", stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    stdout, _ = proc.communicate()
    return stdout.decode("utf-8")


@pytest.fixture
def pytest_resolver():
    return PytestResolver()


@pytest.mark.parametrize(
    "test_item,expected_path,expected_tests_count",
    (
        pytest.param(test_several_functions, PathTests.test_several_functions, 3, id='several tests'),
        pytest.param(test_package, PathTests.test_package, 1, id='package'),
        pytest.param(test_function, str(PathTests.test_function) + '::test_function', 1, id='one function'),
        pytest.param(TestClass, str(PathTests.test_class) + '::TestClass', 2, id='one class'),
        pytest.param(TestClass.test_method, str(PathTests.test_class) + '::TestClass::test_method', 1, id='one method'),
    ),
)
def test_collecting(pytest_resolver, test_item, expected_path, expected_tests_count):
    test_path = pytest_resolver._get_path(test_item)
    assert test_path == str(expected_path)
    assert f"collected {expected_tests_count} item" in get_pytest_collect_result(str(expected_path))