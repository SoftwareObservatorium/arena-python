import logging
import sys
import time

import pandas as pd
import pytest
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import OllamaLLM

from arena.arena import parse_stimulus_matrix, SheetInvocation, Sheet, run_sheets, collect_actuation_sheets
from arena.engine.artifacts import write_modules_and_import_cuts
from arena.engine.ssntestdriver import InvocationListener
from arena.provider.gai import prompt_code_units

# logging
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


@pytest.mark.skip(reason="depends on external Ollama service")
def test_prompt_code():
    """
    Obtain code solutions from LLM model via Ollama and then run tests

    :return:
    """

    # use this for OpenAI instead of Ollama
    # os.environ["OPENAI_API_KEY"] = "demo" # FIXME your API KEY
    # llm = OpenAI(
    #     model="gpt-4o-mini"
    # )

    llm = OllamaLLM(model="llama3.1") # localhost
    template = 'def greatest_common_divisor(a: int, b: int) -> int: """ Return a greatest common divisor of two integers a and b >>> greatest_common_divisor(3, 5) 1 >>> greatest_common_divisor(25, 15) 5 """'
    prompt = ChatPromptTemplate.from_template(template)

    code_solutions = prompt_code_units(llm, prompt, samples = 3) # let's obtain 3

    logger.debug(f"solutions {code_solutions}")

    target_folder = f"/tmp/arena-python-{round(time.time() * 1000)}"
    # classes under test
    cuts = write_modules_and_import_cuts(target_folder, code_solutions)

    logger.debug(f"cuts {cuts}")

    # lql (interface specification)
    lql = """GCD {
            greatest_common_divisor(int,int)->int
        }
    """

    # stimulus sheet
    # ssn_jsonl = """
    #             {"cells": {"A1": {}, "B1": "create", "C1": "GCD"}}
    #             {"cells": {"A2": "5", "B2": "greatest_common_divisor", "C2": "A1", "D2": "25", "E2": "15"}}
    # """

    # stimulus sheet (as a data frame)
    ss = pd.DataFrame([
        {"A": {}, "B": "create", "C": "GCD", "D": None, "E": None},
        {"A": "5", "B": "greatest_common_divisor", "C": "A1", "D": "25", "E": "15"}
    ])

    # create stimulus matrix
    sm = parse_stimulus_matrix([Sheet("test1()", ss, lql)], cuts, [SheetInvocation("test1", "")])
    logger.debug(sm.to_string())

    assert len(sm.columns) == 3
    assert len(sm.index) == 1

    # run stimulus matrix
    invocation_listener = InvocationListener()
    srm = run_sheets(sm, 1, invocation_listener)
    # results based on internal ExecutedInvocation
    logger.debug(srm.to_string())

    assert len(srm.columns) == 3
    assert len(srm.index) == 1

    # create actuation sheets, now we have the real stimulus response matrix (SRM)
    srm_actuations = collect_actuation_sheets(srm)

    logger.debug(srm_actuations.to_string())

    assert len(srm_actuations.columns) == 3
    assert len(srm_actuations.index) == 1

