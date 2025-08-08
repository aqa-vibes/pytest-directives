from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Awaitable, Iterable
from dataclasses import dataclass, field
from pprint import pformat
from typing import Callable, Generic, TypeVar


Target = TypeVar("Target")


class ABCTargetResolver(ABC, Generic[Target]):
    """
    Abstract base class responsible for converting targets into runnable items.

    A target resolver provides the logic to transform domain-specific objects (`Target`)
    into instances of `ABCRunnable`, allowing directives to uniformly work with mixed input types.

    Subclasses must implement `_resolve_target`, which defines how to convert a `Target` into an `ABCRunnable`.
    """

    def to_runnable(self, target: ABCRunnable | Target) -> ABCRunnable:
        """
        Convert the input target to an `ABCRunnable` instance.

        If the input is already an `ABCRunnable`, it is returned as-is.
        Otherwise, it is resolved using `_resolve_target`.

        :param target: An object that is either already runnable or needs to be resolved.
        :return: The corresponding `ABCRunnable` instance.
        """
        if isinstance(target, ABCRunnable):
            return target
        return self._resolve_target(target=target)

    @abstractmethod
    def _resolve_target(self, target: Target) -> ABCRunnable:
        """
        Resolve a raw target into an `ABCRunnable`.

        Subclasses must implement the logic for transforming a target into a runnable item.

        :param target: The input domain-specific object to convert.
        :return: An `ABCRunnable` instance representing the target.
        """
        ...


@dataclass
class RunResult:
    """Information about run of one item."""

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
    """Base class of Composite pattern."""

    @abstractmethod
    async def run(self,  *run_args: str) -> RunResult:
        """Implement how item should run."""
        ...


class ABCRunStrategy:
    """
    Abstract base class defining a run strategy for executing multiple runnable items.

    Responsibilities of subclasses:
        1. Define the logic for executing multiple child items.
        2. Determine whether the aggregated run results are considered successful.
    """

    @abstractmethod
    async def run(
        self,
        items: list[ABCRunnable],
        run_item_callback: Callable[[ABCRunnable], Awaitable[RunResult]]
    ) -> None:
        """
        Execute a collection of child items using the provided callback.

        :param items: A list of runnable items to execute.
        :param run_item_callback: An async callback used to run a single item.
        """
        ...

    @abstractmethod
    def is_run_ok(self, items_run_results: Iterable[RunResult]) -> bool:
        """
        Evaluate whether the run results meet the criteria for a successful execution.

        :param items_run_results: An iterable of RunResult objects, one for each executed item.
        :return: True if the run is considered successful; otherwise, False.
        """
        ...


class ABCDirective(ABCRunnable, Generic[Target]):
    """
    Abstract base class representing a directive.

    Encapsulates the execution of multiple runnable items with a specific run strategy and item resolution logic.

    A directive is responsible for:
        1. Converting input items to runnable instances using a target resolver.
        2. Executing all items using a provided run strategy.
        3. Aggregating and evaluating run results.

    :param raw_items: A variable number of items (either ABCRunnable or Target) to be executed.
    :param run_strategy: Strategy object that defines how the directive should execute items.
    :param target_resolver: Resolver that converts a Target into an ABCRunnable.
    :param run_args: Additional arguments passed to each item's `run` method.
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
        """
        Execute all resolved items using the specified run strategy.

        :param run_args: Additional arguments to be passed to each item's `run` method.
        :return: Aggregated RunResult representing the overall success of the directive.
        """
        self._run_args += run_args
        await self._run_strategy.run(items=self._items, run_item_callback=self._run_item)
        return RunResult(is_ok=self._run_strategy.is_run_ok(self._run_results))

    async def _run_item(self, item: ABCRunnable) -> RunResult:
        """
        Execute a single runnable item and stores its result.

        :param item: A runnable item to be executed.
        :return: The result of the item execution.
        """
        item_result = await item.run(*self._run_args)
        self._run_results.append(item_result)
        return item_result
