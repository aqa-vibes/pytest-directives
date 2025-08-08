from pathlib import Path

from tests.pytest_directives import test_data


class PathTests:
    _test_data = Path(test_data.__path__[0])

    test_function = _test_data / 'test_function.py'
    test_failure = _test_data / 'test_failure.py'
    test_not_exist = _test_data / 'test_data/test.py'
    test_empty_folder = _test_data / 'test_empty_folder'
    test_several_functions = _test_data / 'test_several_functions.py'
    test_package = _test_data / 'test_package'
    test_class = _test_data / 'test_class.py'
