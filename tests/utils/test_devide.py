from collections.abc import Sequence

import pytest

from pytest_directives.core.utils.devide import divide


@pytest.mark.parametrize("count_parts, iterable, expected", [
    pytest.param(2, [1, 2, 3, 4], [[1, 2], [3, 4]], id="even_split"),
    pytest.param(3, [1, 2, 3, 4, 5], [[1, 2], [3, 4], [5]], id="with_remainder"),
    pytest.param(1, [1, 2, 3], [[1, 2, 3]], id="single_part"),
    pytest.param(3, [1, 2, 3], [[1], [2], [3]], id="each_element_as_part"),
    pytest.param(2, [], [[], []], id="empty_iterable"),
    pytest.param(3, (x for x in range(6)), [[0, 1], [2, 3], [4, 5]], id="generator_input"),
    pytest.param(5, [1, 2, 3], [[1], [2], [3], [], []], id="more_parts_than_elements"),
])
def test_divide_functionality(count_parts: int, iterable: Sequence, expected: Sequence):
    """Divide split iterables into expected parts."""
    result = divide(count_parts, iterable)
    assert [list(part) for part in result] == expected
