from invoke import task, Context

@task
def tests(context: Context):
    context.run("uv run pytest tests/ --ignore=tests/pytest_directives/test_data/")
