from invoke import Context, task


@task
def tests(context: Context):
    """Run all unit-tests. Ignore test_data."""
    context.run("uv run pytest tests/ --ignore=tests/pytest_directives/test_data/")

@task
def check(context: Context):
    """Run ruff checks."""
    context.run("uv run ruff check .")
