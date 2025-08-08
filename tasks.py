from invoke import Context, task


@task
def tests(context: Context, cov: bool = False):
    """Run all unit-tests. Ignore test_data."""
    run_tests_command = "uv run pytest tests/ --ignore=tests/pytest_directives/test_data/"
    if cov:
        run_tests_command += " --cov=pytest_directives"
    context.run(run_tests_command)

@task
def linter(context: Context):
    """Run ruff checks."""
    context.run("uv run ruff check .")

@task
def types(context: Context):
    """Run mypy checks. """
    context.run("uv run mypy")
