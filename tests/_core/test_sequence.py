import asyncio
from typing import Callable, Awaitable

from pytest_directives.core.abc_directive import ABCRunnable, RunResult
from pytest_directives.core.run_strategies import SequenceRunStrategy

from tests._core.conftest import RunnableSpec, MockRunnable


def test_sequence_run_strategy_success(
    make_items: Callable[[list[RunnableSpec]], list[MockRunnable]],
    run_item_callback: Callable[[ABCRunnable], Awaitable[RunResult]],
    run_results: list[RunResult]
):
    """
    Test that SequenceRunStrategy returns success if at least one item succeeds.
    All items should be run, and the result should be successful if any item passes.
    """
    items = make_items([RunnableSpec(True, "a", 0), RunnableSpec(False, "b", 0), RunnableSpec(True, "c", 0)])
    strategy = SequenceRunStrategy()
    asyncio.run(strategy.run(items, run_item_callback))

    assert all(item.run_called for item in items)

    assert strategy.is_run_ok(run_results)


def test_sequence_run_strategy_all_fail(
    make_items: Callable[[list[RunnableSpec]], list[MockRunnable]],
    run_item_callback: Callable[[ABCRunnable], Awaitable[RunResult]],
    run_results: list[RunResult]
):
    """
    Test that SequenceRunStrategy returns failure if all items fail.
    All items should be run, and the result should be failure if none succeed.
    """
    items = make_items([RunnableSpec(False, "a", 0), RunnableSpec(False, "b", 0)])
    strategy = SequenceRunStrategy()
    asyncio.run(strategy.run(items, run_item_callback))

    assert not strategy.is_run_ok(run_results)