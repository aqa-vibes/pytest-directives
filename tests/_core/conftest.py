import asyncio
from typing import Callable, NamedTuple

import pytest

from pytest_directives.core.abc_directive import ABCRunnable, RunResult


class RunnableSpec(NamedTuple):
    is_ok: bool
    name: str
    delay: float


class MockRunnable(ABCRunnable):
    def __init__(self, is_ok: bool, name: str = "", delay: float = 0):
        self._is_ok = is_ok
        self.name = name
        self.delay = delay
        self.run_called = False

    async def run(self, *run_args: str) -> RunResult:
        self.run_called = True
        if self.delay:
            await asyncio.sleep(self.delay)
        return RunResult(is_ok=self._is_ok, stdout=[f"{self.name} ran"], stderr=[])

@pytest.fixture
def make_items() -> Callable[[list[RunnableSpec]], list[MockRunnable]]:
    def _make(items_data: list[RunnableSpec]) -> list[MockRunnable]:
        return [MockRunnable(is_ok, name, delay) for is_ok, name, delay in items_data]
    return _make

@pytest.fixture
def run_results() -> list[RunResult]:
    return list()


@pytest.fixture
def run_item_callback(run_results: list[RunResult]):
    async def run_item(item: ABCRunnable):
        res = await item.run()
        run_results.append(res)
        return res
    return run_item
