import pytest

from pytest_directives.core.abc_directive import (
    ABCDirective,
    ABCRunnable,
    ABCRunStrategy,
    ABCTargetResolver,
    RunResult,
)


class DummyRunnable(ABCRunnable):
    def __init__(self, result: RunResult):
        self.result = result
        self.run_called_with = None

    async def run(self, *run_args: str) -> RunResult:
        self.run_called_with = run_args
        return self.result


class DummyTargetResolver(ABCTargetResolver[str]):
    def __init__(self, mapping: dict[str, ABCRunnable]):
        self.mapping = mapping
        self.resolve_calls = []

    def _resolve_target(self, target: str) -> ABCRunnable:
        self.resolve_calls.append(target)
        if target not in self.mapping:
            raise KeyError(f"Target {target!r} not found")
        return self.mapping[target]


class DummyRunStrategy(ABCRunStrategy):
    def __init__(self, is_ok: bool):
        self.is_ok = is_ok
        self.run_calls = []
        self.is_run_ok_calls = []

    async def run(self, items, run_item_callback):
        self.run_calls.append(list(items))
        for item in items:
            await run_item_callback(item)

    def is_run_ok(self, items_run_results):
        results_list = list(items_run_results)
        self.is_run_ok_calls.append(results_list)
        return self.is_ok


def test_runresult_repr_includes_all_fields():
    rr = RunResult(is_ok=True, stdout=["out"], stderr=["err"])
    repr_str = repr(rr)
    assert "is_ok=True" in repr_str
    assert "out" in repr_str
    assert "err" in repr_str


def test_runresult_repr_handles_empty_streams():
    rr = RunResult(is_ok=False)
    repr_str = repr(rr)
    assert "[]" in repr_str
    assert "is_ok=False" in repr_str


def test_target_resolver_returns_same_runnable_instance():
    runnable = DummyRunnable(RunResult(True))
    resolver = DummyTargetResolver({})
    result = resolver.to_runnable(runnable)
    assert result is runnable
    assert resolver.resolve_calls == []


def test_target_resolver_resolves_raw_target_to_runnable():
    runnable = DummyRunnable(RunResult(True))
    resolver = DummyTargetResolver({"key": runnable})
    result = resolver.to_runnable("key")
    assert result is runnable
    assert resolver.resolve_calls == ["key"]


def test_target_resolver_raises_if_target_not_found():
    resolver = DummyTargetResolver({})
    with pytest.raises(KeyError):
        resolver.to_runnable("missing")


@pytest.mark.asyncio
async def test_directive_runs_all_items_and_aggregates_success():
    runnable1 = DummyRunnable(RunResult(True))
    runnable2 = DummyRunnable(RunResult(True))
    resolver = DummyTargetResolver({"a": runnable1, "b": runnable2})
    strategy = DummyRunStrategy(is_ok=True)

    directive = ABCDirective(
        "a", "b",
        run_strategy=strategy,
        target_resolver=resolver,
        run_args=("base",)
    )

    result = await directive.run("extra")
    assert result.is_ok is True
    assert runnable1.run_called_with == ("base", "extra")
    assert runnable2.run_called_with == ("base", "extra")
    assert strategy.run_calls[0] == [runnable1, runnable2]
    assert len(strategy.is_run_ok_calls[0]) == 2


@pytest.mark.asyncio
async def test_directive_with_empty_items_returns_strategy_result():
    resolver = DummyTargetResolver({})
    strategy = DummyRunStrategy(is_ok=False)

    directive = ABCDirective(
        run_strategy=strategy,
        target_resolver=resolver
    )

    result = await directive.run()
    assert result.is_ok is False
    assert strategy.run_calls == [[]]
    assert strategy.is_run_ok_calls == [[]]


@pytest.mark.asyncio
async def test_directive_run_failure_reflected_in_result():
    runnable = DummyRunnable(RunResult(False))
    resolver = DummyTargetResolver({"x": runnable})
    strategy = DummyRunStrategy(is_ok=False)

    directive = ABCDirective(
        "x",
        run_strategy=strategy,
        target_resolver=resolver
    )

    result = await directive.run()
    assert result.is_ok is False


@pytest.mark.asyncio
async def test_run_item_appends_result_and_returns_it():
    runnable = DummyRunnable(RunResult(True))
    resolver = DummyTargetResolver({"a": runnable})
    strategy = DummyRunStrategy(is_ok=True)
    directive = ABCDirective(
        "a",
        run_strategy=strategy,
        target_resolver=resolver
    )

    res = await directive._run_item(runnable)
    assert res.is_ok is True
    assert directive._run_results == [res]


@pytest.mark.asyncio
async def test_run_item_propagates_exceptions_from_runnable():
    class FailingRunnable(ABCRunnable):
        async def run(self, *args: str) -> RunResult:
            raise RuntimeError("fail")

    runnable = FailingRunnable()
    resolver = DummyTargetResolver({"bad": runnable})
    strategy = DummyRunStrategy(is_ok=True)
    directive = ABCDirective(
        "bad",
        run_strategy=strategy,
        target_resolver=resolver
    )

    with pytest.raises(RuntimeError):
        await directive._run_item(runnable)
