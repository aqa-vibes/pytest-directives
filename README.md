[![codecov](https://codecov.io/github/aqa-vibes/pytest-directives/graph/badge.svg?token=U1JEXELDHA)](https://codecov.io/github/aqa-vibes/pytest-directives)
# pytest-directives
Control your tests flow.
 
Provides `directives`, that makes process of running tests clear and controllable.

## Install:
`pip install pytest-directives`

## Example:
#### Run your test
1. Create test with pytest
```python
# test_something.py

def test_something():
    assert False, 'Some product error'
```
2. Describe your flow
```python
# simple_flow.py

import asyncio
import logging

from pytest_directives import sequence

import test_something


simple_flow = sequence(test_something, )

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format='%(message)s',)
    asyncio.run(
        simple_flow.run()
    )
```
3. Run as usual python code `python simple_flow.py`
```
Using proactor: IocpProactor
Run test from directive PytestRunnable: C:\Users\i.kuzmenko\PycharmProjects\LOCAL\pytest-directives\test_something.py
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-8.4.1, pluggy-1.6.0 -- C:\Users\i.kuzmenko\PycharmProjects\LOCAL\pytest-directives\.venv\Scripts\python.exe
rootdir: C:\Users\i.kuzmenko\PycharmProjects\LOCAL\pytest-directives
configfile: pyproject.toml
plugins: asyncio-1.1.0, cov-6.2.1
asyncio: mode=Mode.AUTO, asyncio_default_fixture_loop_scope=function, asyncio_default_test_loop_scope=function
collecting ... collected 1 item

test_something.py::test_something FAILED                                 [100%]

================================== FAILURES ===================================
_______________________________ test_something ________________________________

    def test_something():
>       assert False, 'Some product error'
E       AssertionError: Some product error
E       assert False


test_something.py:3: AssertionError
=========================== short test summary info ===========================
FAILED test_something.py::test_something - AssertionError: Some product error
============================== 1 failed in 0.07s ==============================
Errors in tests results
```


#### Three main directives
```python
from pytest_directives import sequence, chain, parallel

sequence()  # run items one by one; ignore errors

chain()     # run items one by one; stop when first fail found

parallel()  # run items in parallel; ignore errors
```

#### How to run directives
```python
from pytest_directives import sequence

# just import your tests
from tests import test_file_1, test_file_2, test_file_3


# define order in `flow`
sequence_flow = sequence(
    test_file_1,
    test_file_2,
    test_file_3
)

# add some options to pytest
pytest_run_args = (
    "-v",
    "--alluredir=./allure-results",
)

import asyncio
# start your flow
asyncio.run(
    sequence_flow.run(*pytest_run_args)
)
```

#### Combine directives in flows
```python
from pytest_directives import sequence, chain, parallel


abstract_flow = sequence(
    chain(
        chain(
            # prepare infrastructure or tests environment
        ),
        # if infrastructure failed, exit from here
        parallel(
            # run tests in parallel to increase speed of testing
        )
    ),
    sequence(
        # do some important stuff at the end of tests,
        #   like collect logs, metrics or just cleanup environment
    )
)

smoke_flow = sequence(
    chain(
        chain(
            prepare_environment(),
            check_infrastructure_health()
        ),
        parallel(
            run_test_group_a(),
            run_test_group_B(),
            run_api_tests()
        ),
    ),
    sequence(
        collect_logs(),
        generate_report(),
        cleanup_environment()
    )
)
```

## Features
* Can run tests by `import` package, module, function, class or method
* Run pytest in separate process (say no to sharing fixture) by `asyncio.create_subprocess_exec`
* Can use `pytest.marks` / `pytest-xdist` or other as usual by using `.run(*args)` parameter
* Combine directives and implement your tests flow as you need

# Development
1. Install [uv](https://docs.astral.sh/uv/getting-started/installation/#pypi)
2. Clone project
3. Install requirements 
```bash 
  uv sync
```

# Run tests
```bash 
  inv tests
```