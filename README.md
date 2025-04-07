# LASSO Arena Test-Driver for Python

work in progress

For more information about the `arena` and the LASSO platform, visit our website: https://softwareobservatorium.github.io/

## Install

Assumes Python3 >= 3.12 (tested with Ubuntu 24.04 LTS)

### Using `pip`

Example using Python's virtual environment (you need to have `virtualenv` installed; e.g. using `pip`)

```shell
pip3 install virtualenv # depending on your OS/Python distribution
```

Clone and install all required dependencies

```shell
git clone https://github.com/SoftwareObservatorium/arena-python.git
python3 -m venv arena
source arena/bin/activate
cd arena-python/
```

Install packages

```shell
pip3 install -r requirements.txt
```

### Using `hatch`

project is managed with `hatch` (https://hatch.pypa.io/latest/)

```shell
git clone https://github.com/SoftwareObservatorium/arena-python.git
python3 -m venv arena
source arena/bin/activate
cd arena-python/
```

Install hatch

```shell
pip3 install hatch
```

Build project

```shell
python3 -m hatch build
```

Test project

```shell
python3 -m hatch test
```

### Optional Dependencies (Jupyter+Pandas)

To run the example notebooks, the following dependencies need to be installed as well

```shell
pip3 install jupyter
pip3 install pandas

# start jupyter locally
jupyter lab
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

* [Load units under tests from local machine](notebooks/base64_example.ipynb)
* [Use builtin types (collections example)](notebooks/list_example.ipynb)
* [Use LLMs (via Ollama/OpenAI) to generate units under test (i.e., code candidates)](notebooks/llm_ollama_example.ipynb)

Tests that demonstrate the arena test driver can be found in [tests/](tests/).

* [arena_test.py](tests/arena_test.py) contains integration tests (system tests)

