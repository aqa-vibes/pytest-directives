import asyncio
from collections.abc import Awaitable, Iterable
import os
from typing import Callable

from .abc_directive import ABCRunnable, ABCRunStrategy, RunResult
from .utils.devide import divide


class SequenceRunStrategy(ABCRunStrategy):
    """
    Sequence strategy.

    * Runs sequentially
    * Ignores errors
    * Result is_ok if at least one item passes
    """

    async def run(
        self,
        items: list[ABCRunnable],
        run_item_callback: Callable[[ABCRunnable], Awaitable[RunResult]]
    ) -> None:
        """Execute all items one by one."""
        for item in items:
            await run_item_callback(item)

    def is_run_ok(self, items_run_results: Iterable[RunResult]) -> bool:
        """Return True if at least one item passed."""
        return any(map(lambda item_result: item_result.is_ok, items_run_results))


class ChainRunStrategy(ABCRunStrategy):
    """
    Chain strategy.

    * Runs sequentially
    * Stop on first error
    * Result is_ok if all items passed
    """

    async def run(
        self,
        items: list[ABCRunnable],
        run_item_callback: Callable[[ABCRunnable], Awaitable[RunResult]]
    ) -> None:
        """Execute all items one by one, stop on first error."""
        for item in items:
            item_result = await run_item_callback(item)
            if not item_result.is_ok:
                break

    def is_run_ok(self, items_run_results: Iterable[RunResult]) -> bool:
        """Return True if all items passed."""
        return all(map(lambda item_result: item_result.is_ok, items_run_results))


# todo add note
DIRECTIVE_PARALLEL_PROCESSES = int(os.environ.get('DIRECTIVE_PARALLEL_PROCESSES', 4))   # noqa: PLW1508


class ParallelRunStrategy(ABCRunStrategy):
    """
    Parallel strategy.

    * Runs parallel
    * Ignores errors
    * Result is_ok if all items passes
    """

    async def run(
        self,
        items: list[ABCRunnable],
        run_item_callback: Callable[[ABCRunnable], Awaitable[RunResult]]
    ) -> None:
        """Split items to chunks and execute them parallel."""
        count_chunks = DIRECTIVE_PARALLEL_PROCESSES
        chunked_items = [list(c) for c in divide(count_chunks, items)]
        chunks = [self._run_chunk(chunk, run_item_callback=run_item_callback) for chunk in chunked_items]

        await asyncio.gather(*chunks)

    @staticmethod
    async def _run_chunk(
        chunk_items: Iterable[ABCRunnable],
        run_item_callback: Callable[[ABCRunnable], Awaitable[RunResult]]
    ) -> None:
        """Execute all items parallel."""
        if not chunk_items:
            return
        chunk_coroutines = [run_item_callback(item) for item in chunk_items]

        for chunk_item in chunk_coroutines:
            await chunk_item

    def is_run_ok(self, items_run_results: Iterable[RunResult]) -> bool:
        """Return True if all items passed."""
        return all(map(lambda item_result: item_result.is_ok, items_run_results))
