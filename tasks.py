from invoke import Context, task


@task
def tests(context: Context, xml_cov: bool = False):
    """Run all unit-tests. Ignore test_data."""
    run_tests_command = "uv run pytest tests/ --ignore=tests/pytest_directives/test_data/ --cov=pytest_directives"
    if xml_cov:
        run_tests_command += " --cov-branch --cov-report=xml"
    context.run(run_tests_command)


@task
def linter(context: Context):
    """Run ruff checks."""
    context.run("uv run ruff check .")

@task
def types(context: Context):
    """Run mypy checks."""
    context.run("uv run mypy .")
