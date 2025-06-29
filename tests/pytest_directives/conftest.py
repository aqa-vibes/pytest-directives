from dataclasses import dataclass
from pathlib import Path

import pytest


class PathTests:
    test_function: Path = Path('./test_data/test_function.py')
    test_failure: Path = Path('./test_data/test_failure.py')
    test_not_exist: Path = Path('./test_data/test_data/test.py')
    test_empty_folder: Path = Path('./test_data/test_empty_folder')
