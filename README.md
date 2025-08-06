# pytest-directives
Control your tests flow.
 
Provides `directives`, that makes process of running tests clear and controllable.

## Install:
`pip install pytest-directives`

## Example:
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
* Combine directives and implement your tests flow as you need

# Development
1. Install [uv](https://docs.astral.sh/uv/getting-started/installation/#pypi)
2. Clone project
3. Install requirements 
```bash 
  uv sync
```
4. Activate virtual environment
    - Windows `.venv/Scripts/activate`
    - Linux `.venv/bin/activate`

# Run tests
```bash 
  inv tests
```