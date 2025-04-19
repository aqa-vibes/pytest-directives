import asyncio
import inspect
import logging
from pathlib import Path
from types import ModuleType, FunctionType, MethodType
from typing import Union, Callable, TypeAlias

from ._core.abc_directive import ABCRunnable, ABCTargetResolver, ABCDirective, RunResult, ABCRunStrategy
from ._core.run_strategies import SequenceRunStrategy, ChainRunStrategy, ParallelRunStrategy
from ._pytest_hardcode import ExitCode

TestTargetType: TypeAlias = Union[ModuleType, FunctionType, MethodType, Callable]


class PytestRunnable(ABCRunnable):
    def __init__(self, test_path: str):
        self._test_path = test_path
        super().__init__()

    async def run(self, *run_args: str) -> RunResult:
        """Run test item in another process, wait until done and collect results"""
        logging.debug(f"Run test from directive {self.__class__.__name__}: {self._test_path}")
        process = await asyncio.create_subprocess_exec(
            "pytest", *run_args, self._test_path, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )

        # todo another way to detect that process stop
        while True:
            stdout_line = await process.stdout.readline()  # type: ignore[union-attr]
            stderr_line = await process.stderr.readline()  # type: ignore[union-attr]
            if stdout_line:
                logging.info(stdout_line.decode().rstrip())
            elif stderr_line:
                logging.error(stderr_line.decode().rstrip())
            else:
                break

        await process.wait()

        if process.returncode != ExitCode.OK:
            is_ok = False
            logging.error("Errors in tests results")
        else:
            is_ok = True
            logging.debug("Tests ends without errors")
        return RunResult(is_ok=is_ok)


class PytestResolver(ABCTargetResolver):

    def _resolve_target(self, target: TestTargetType) -> PytestRunnable:
        return PytestRunnable(test_path=self._get_path(target))

    @staticmethod
    def _get_path(target: TestTargetType):
        """Get full path to run tests in pytest"""
        path = inspect.getfile(target)
        if path.endswith("__init__.py"):
            path = target.__path__[0]  # type: ignore[union-attr]

        path = str(Path(path))

        if not isinstance(target, ModuleType):
            path += f"::{target.__name__}"

        return path


class ABCPytestDirective(ABCDirective):
    def __init__(
        self,
        *raw_items: ABCRunnable | TestTargetType,
        run_strategy: ABCRunStrategy,
        run_args: tuple[str, ...] = tuple(),
    ):
        super().__init__(
            *raw_items,
            run_strategy=run_strategy,
            run_args=run_args,
            target_resolver=PytestResolver()
        )


class PytestSequenceDirective(ABCPytestDirective):
    def __init__(
        self,
        *raw_items: ABCRunnable | TestTargetType,
        run_args: tuple[str, ...] = tuple(),
    ):
        super().__init__(
            *raw_items,
            run_args=run_args,
            run_strategy=SequenceRunStrategy(),
        )


class PytestChainDirective(ABCPytestDirective):
    def __init__(
        self,
        *raw_items: ABCRunnable | TestTargetType,
        run_args: tuple[str, ...] = tuple(),
    ):
        super().__init__(
            *raw_items,
            run_args=run_args,
            run_strategy=ChainRunStrategy(),
        )


class PytestParallelDirective(ABCPytestDirective):
    def __init__(
        self,
        *raw_items: ABCRunnable | TestTargetType,
        run_args: tuple[str, ...] = tuple(),
    ):
        super().__init__(
            *raw_items,
            run_args=run_args,
            run_strategy=ParallelRunStrategy(),
        )


# shortcuts
sequence = PytestSequenceDirective
chain = PytestChainDirective
parallel = PytestParallelDirective