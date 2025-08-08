from pathlib import Path

import pytest

from pytest_directives.pytest_directives import PytestRunnable
from tests.pytest_directives.test_data_paths import PathTests


async def test_success_run():
    pytest_runnable = PytestRunnable(
        test_path=str(PathTests.test_function)
    )

    run_result = await pytest_runnable.run()
    assert run_result.is_ok


@pytest.mark.parametrize(
    'test_path',
    (
        pytest.param(PathTests.test_failure, id='test failed'),
        pytest.param(PathTests.test_empty_folder, id='no tests'),
        pytest.param(PathTests.test_not_exist, id='wrong path'),
    )
)
async def test_not_success_run(test_path: Path):
    pytest_runnable = PytestRunnable(
        test_path=str(test_path)
    )

    run_result = await pytest_runnable.run()
    assert not run_result.is_ok
