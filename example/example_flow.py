import asyncio

from pytest_directives.pytest_directives import sequence, chain, parallel


def example_flow():
    return sequence(

    )


if __name__ == '__main__':
    args = [
        r"--alluredir=\allure_results",
    ]
    asyncio.run(example_flow().run(*args))