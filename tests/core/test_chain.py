import asyncio
from collections.abc import Awaitable
from typing import Callable

from pytest_directives.core.abc_directive import ABCRunnable, RunResult
from pytest_directives.core.run_strategies import ChainRunStrategy
from tests.core.conftest import MockRunnable, RunnableSpec


def test_chain_stops_on_first_fail(
    make_items: Callable[[list[RunnableSpec]], list[MockRunnable]],
    run_item_callback: Callable[[ABCRunnable], Awaitable[RunResult]],
    run_results: list[RunResult]
):
    """
    Test that ChainRunStrategy stops execution at the first failed item.

    Only items up to and including the first failure should be run.
    The strategy should return failure if any item fails.
    """
    items = make_items([
        RunnableSpec(True, "a", 0),
        RunnableSpec(False, "b", 0),
        RunnableSpec(True, "c", 0)
    ])
    strategy = ChainRunStrategy()
    asyncio.run(strategy.run(list(items), run_item_callback))

    assert items[0].run_called
    assert items[1].run_called
    assert not items[2].run_called

    assert not strategy.is_run_ok(run_results)

def test_chain_all_success(
    make_items: Callable[[list[RunnableSpec]], list[MockRunnable]],
    run_item_callback: Callable[[ABCRunnable], Awaitable[RunResult]],
    run_results: list[RunResult]
):
    """
    Test that ChainRunStrategy returns success if all items succeed.

    All items should be run and the result should be successful.
    """
    items = make_items([
        RunnableSpec(True, "a", 0),
        RunnableSpec(True, "b", 0)
    ])

    strategy = ChainRunStrategy()
    asyncio.run(strategy.run(list(items), run_item_callback))

    assert all(item.run_called for item in items)

    assert strategy.is_run_ok(run_results)
