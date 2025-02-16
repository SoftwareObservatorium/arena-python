# LASSO Arena Test-Driver for Python

work in progress

## Install

project is managed with `hatch` (https://hatch.pypa.io/latest/)

```commandline
pip install hatch
```

Build project

```commandline
python -m hatch build
```

Test project

```commandline
python -m hatch test
```

## LQL Parser

LQL parser in python using antlr4 grammar

* _antlr4-python3-runtime_
* [lqlparser.py](arena/lql/lqlparser.py)

## Sequence sheet notation (SSN)

Sequence sheet notation and engine realized in python.

* [ssntestdriver.py](arena/engine/ssntestdriver.py)

## Adaptation

Adaptation strategies are realized in

* [adaptation.py](arena/engine/adaptation.py)

## Introspection and class loading

* [introspection.py](arena/introspection.py)
* [execution.py](arena/execution.py)

## Stimulus Matrix (SM) / Stimulus Response Matrix (SRM)

SMs and SRMs are based on pandas DataFrame

* [arena.py](arena/arena.py)

## Demonstration

### Jupyter Notebooks

see examples in [notebooks](notebooks/)

* [base64_example.ipynb](notebooks/base64_example.ipynb)
* [list_example.ipynb](notebooks/list_example.ipynb)

Tests that demonstrate the arena test driver can be found in [tests/](tests/).

* [arena_test.py](tests/arena_test.py) contains integration tests (system tests)

