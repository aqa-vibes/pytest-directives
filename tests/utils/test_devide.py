from typing import Sequence

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
    result = divide(count_parts, iterable)
    assert [list(part) for part in result] == expected


@pytest.mark.parametrize("count_parts, iterable", [
    pytest.param(0, [1, 2, 3], id="count_parts_zero"),
    pytest.param(-1, [1, 2, 3], id="count_parts_negative"),
])
def test_divide_invalid_count_parts(count_parts: int, iterable: Sequence):
    with pytest.raises(ValueError, match="'count_parts' must be at least 1"):
        divide(count_parts, iterable)


@pytest.mark.parametrize("count_parts, iterable", [
    pytest.param(2, 123, id="non_iterable_input"),
    pytest.param(2, None, id="none_input"),
])
def test_divide_non_iterable_input(count_parts: int, iterable: Sequence):
    with pytest.raises(TypeError):
        divide(count_parts, iterable)
