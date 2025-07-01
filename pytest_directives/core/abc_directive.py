from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Awaitable, Iterable
from dataclasses import dataclass, field
from pprint import pformat
from typing import Callable, Generic, TypeVar

Target = TypeVar("Target")


class ABCTargetResolver(ABC, Generic[Target]):
    """
    Base class for TargetResolver's

    Implement creating ABCRunnable from Target.
    """
    def to_runnable(self, target: ABCRunnable | Target) -> ABCRunnable:
        if isinstance(target, ABCRunnable):
            return target
        return self._resolve_target(target=target)

    @abstractmethod
    def _resolve_target(self, target: Target) -> ABCRunnable: ...


@dataclass
class RunResult:
    """Information about run of one item"""
    is_ok: bool
    stdout: list[str] = field(default_factory=list)
    stderr: list[str] = field(default_factory=list)

    def __repr__(self) -> str:
        return (
            f'RunResult(is_ok={self.is_ok}'
            f'          stdout={pformat(self.stdout)},'
            f'          stderr={pformat(self.stderr)}'
            ')'
        )


class ABCRunnable:
    """
    Base class of Composite pattern.

    Implement how item should run.
    """
    @abstractmethod
    async def run(self,  *run_args: str) -> RunResult: ...


class ABCRunStrategy:
    """
    Base class of run strategy.

    Implement:
        1. How should multiple elements be run
        2. Is the result of running multiple elements satisfactory?
    """
    @abstractmethod
    async def run(
        self,
        items: list[ABCRunnable],
        run_item_callback: Callable[[ABCRunnable], Awaitable[RunResult]]
    ) -> None: ...

    @abstractmethod
    def is_run_ok(self, items_run_results: Iterable[RunResult]) -> bool: ...


class ABCDirective(ABCRunnable, Generic[Target]):
    """
    Base class for directives.

    :param raw_items: items, that should be run by that directive
    :param run_strategy: behavior of directive
    :param target_resolver: how need to create ABCRunnable from Target
    :param run_args: additional parameters, that will be added to `run` method of items
    """
    _items: list[ABCRunnable]
    _run_results: list[RunResult]

    def __init__(
        self,
        *raw_items: ABCRunnable | Target,
        run_strategy: ABCRunStrategy,
        target_resolver: ABCTargetResolver[Target],
        run_args: tuple[str, ...] = tuple(),
    ):
        self._run_args = run_args

        self._run_strategy = run_strategy
        self._target_resolver = target_resolver

        self._items = list(
            map(lambda item: self._target_resolver.to_runnable(item), raw_items)
        )
        self._run_results = list()

    async def run(self, *run_args: str) -> RunResult:
        self._run_args += run_args
        await self._run_strategy.run(items=self._items, run_item_callback=self._run_item)
        return RunResult(is_ok=self._run_strategy.is_run_ok(self._run_results))

    async def _run_item(self, item: ABCRunnable) -> RunResult:
        item_result = await item.run(*self._run_args)
        self._run_results.append(item_result)
        return item_result

