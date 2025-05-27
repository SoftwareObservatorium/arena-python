import logging
import sys
import time

import pandas as pd
import pytest

import main
from arena.arena import parse_stimulus_matrix, Sheet, run_sheets, collect_actuation_sheets, SheetInvocation, \
    lql_to_sheet_signature
from arena.engine.adaptation import PassThroughAdaptationStrategy, \
    SingleFunctionAdaptationStrategy
from arena.engine.artifacts import CodeCandidate, import_classes_under_test, write_modules_and_import_cuts
from arena.engine.classes import ClassUnderTest
from arena.engine.ssntestdriver import interpret_sheet, run_sheet, InvocationListener, Test, TestInvocation
from arena.lql.lqlparser import parse_lql
from arena.ssn.ssnparser import parse_sheet

# logging
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


def test_srm_base64_external_functions():
    """
    Demonstrates typical scenario: SM as input and SRM as output (here functions are assumed)

    :return:
    """

    # lql (interface specification)
    lql = """Base64 {
            encode(str)->str
        }
    """

    # stimulus sheet
    ssn_jsonl = """
                {"cells": {"A1": "", "B1": "create", "C1": "Base64"}}
                {"cells": {"A2": "", "B2": "encode", "C2": "A1", "D2": "'Hello World!'"}}
    """

    code_solutions = ["""
import base64

def encode(string):
    # Convert the string to bytes
    string_bytes = string.encode('utf-8')
    
    # Encode the bytes into Base64
    base64_encoded = base64.b64encode(string_bytes)
    
    # Decode the bytes back into a string
    base64_string = base64_encoded.decode('utf-8')
    
    return base64_string

"""]

    # classes under test
    target_folder = f"/tmp/arena-python-{round(time.time() * 1000)}"
    cuts = write_modules_and_import_cuts(target_folder, code_solutions)

    # create stimulus matrix
    sm = parse_stimulus_matrix([Sheet("test1()", ssn_jsonl, lql)], cuts, [SheetInvocation("test1", "")])
    logger.debug(sm.to_string())

    assert len(sm.columns) == 1
    assert len(sm.index) == 1

    # run stimulus matrix
    invocation_listener = InvocationListener()
    srm = run_sheets(sm, 1, invocation_listener, measure_code_coverage=True)
    # results based on internal ExecutedInvocation
    logger.debug(srm.to_string())

    assert len(srm.columns) == 1
    assert len(srm.index) == 1

    # create actuation sheets, now we have the real stimulus response matrix (SRM)
    srm_actuations = collect_actuation_sheets(srm)

    logger.debug(srm_actuations.to_string())

    assert len(srm_actuations.columns) == 1
    assert len(srm_actuations.index) == 1