import asyncio
from typing import Callable, Awaitable
import time

from pytest_directives.core.abc_directive import ABCRunnable, RunResult
from pytest_directives.core.run_strategies import ParallelRunStrategy

from tests._core.conftest import RunnableSpec, MockRunnable


def test_parallel_success(
    make_items: Callable[[list[RunnableSpec]], list[MockRunnable]],
    run_item_callback: Callable[[ABCRunnable], Awaitable[RunResult]],
    run_results: list[RunResult]
):
    """
    Test that ParallelRunStrategy returns success if all items passes.
    All items should be run in parallel.
    """
    items = make_items([
        RunnableSpec(True, "a", 0.1),
        RunnableSpec(True, "b", 0.1),
        RunnableSpec(True, "c", 0.1)
    ])
    strategy = ParallelRunStrategy()
    asyncio.run(strategy.run(list(items), run_item_callback))

    assert all(item.run_called for item in items)

    assert strategy.is_run_ok(run_results)

def test_parallel_all_fail(
    make_items: Callable[[list[RunnableSpec]], list[MockRunnable]],
    run_item_callback: Callable[[ABCRunnable], Awaitable[RunResult]],
    run_results: list[RunResult]
):
    """
    Test that ParallelRunStrategy returns failure if at least one failed.
    All items should be run in parallel.
    """
    items = make_items([
        RunnableSpec(True, "a", 0),
        RunnableSpec(False, "b", 0)
    ])

    strategy = ParallelRunStrategy()
    asyncio.run(strategy.run(list(items), run_item_callback))

    assert all(item.run_called for item in items)

    assert not strategy.is_run_ok(run_results)


def test_parallel_run(
    make_items: Callable[[list[RunnableSpec]], list[MockRunnable]],
    run_item_callback: Callable[[ABCRunnable], Awaitable[RunResult]],
    run_results: list[RunResult]
):
    """
    Test that ParallelRunStrategy really run items parallel
    """
    items = make_items([
        RunnableSpec(True, "a", 2),
        RunnableSpec(True, "b", 2),
        RunnableSpec(True, "b", 2),
        RunnableSpec(True, "b", 2)
    ])

    strategy = ParallelRunStrategy()
    start = time.monotonic()
    asyncio.run(strategy.run(list(items), run_item_callback))
    elapsed = time.monotonic() - start

    assert all(item.run_called for item in items)

    assert elapsed < 3, f"Tasks did not run in parallel, elapsed: {elapsed:.2f}s"