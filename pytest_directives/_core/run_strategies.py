import asyncio
import os
from typing import Iterable, Callable, Coroutine, Any

from .abc_directive import ABCRunStrategy, RunResult, ABCRunnable
from .utils.devide import divide


class SequenceRunStrategy(ABCRunStrategy):
    """
    * Runs sequentially
    * Ignores errors
    * Result is_ok if at least one item passes
    """

    async def run(
        self,
        items: list[ABCRunnable],
        run_item_callback: Callable[[ABCRunnable], Coroutine[Any, Any, RunResult]]
    ) -> None:
        for item in items:
            await run_item_callback(item)

    def is_run_ok(self, items_run_results: Iterable[RunResult]) -> bool:
        return any(map(lambda item_result: item_result.is_run_ok, items_run_results))


class ChainRunStrategy(ABCRunStrategy):
    """
    * Runs sequentially
    * Stop on first error
    * Result is_ok if all items passed
    """

    async def run(
        self,
        items: list[ABCRunnable],
        run_item_callback: Callable[[ABCRunnable], Coroutine[Any, Any, RunResult]]
    ) -> None:
        for item in items:
            item_result = await run_item_callback(item)
            if not item_result.is_ok:
                break

    def is_run_ok(self, items_run_results: Iterable[RunResult]) -> bool:
        return all(map(lambda item_result: item_result.is_run_ok, items_run_results))


# todo add note
DIRECTIVE_PARALLEL_PROCESSES = os.environ.get('DIRECTIVE_PARALLEL_PROCESSES', 4)


class ParallelRunStrategy(ABCRunStrategy):
    """
    * Runs parallel
    * Ignores errors
    * Result is_ok if at least one item passes
    """

    async def run(
        self,
        items: list[ABCRunnable],
        run_item_callback: Callable[[ABCRunnable], Coroutine[Any, Any, RunResult]]
    ) -> None:
        count_chunks = DIRECTIVE_PARALLEL_PROCESSES
        chunked_items = [list(c) for c in divide(count_chunks, items)]
        chunks = [self._run_chunk(chunk, run_item_callback=run_item_callback) for chunk in chunked_items]

        for chunk in chunks:
            await chunk

    @staticmethod
    async def _run_chunk(
        chunk_items: Iterable[ABCRunnable],
        run_item_callback: Callable[[ABCRunnable], Coroutine[Any, Any, RunResult]]
    ) -> None:
        if not chunk_items:
            return
        chunk_coroutines = [run_item_callback(item) for item in chunk_items]
        await asyncio.gather(*chunk_coroutines)

    def is_run_ok(self, results: Iterable[RunResult]) -> bool:
        return all(map(lambda x: x.is_run_ok, results))