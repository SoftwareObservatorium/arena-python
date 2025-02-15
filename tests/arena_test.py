import logging
import sys
from collections import deque

from arena.arena import parse_stimulus_matrix, Sheet, run_sheets, collect_actuation_sheets, SheetInvocation, \
    lql_to_sheet_signature
from arena.engine.adaptation import PassThroughAdaptationStrategy
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


def test_srm_list():
    """
    Demonstrates typical scenario: SM as input and SRM as output

    :return:
    """

    # lql (interface specification)
    lql = """List {
        append(object)->void
        pop()->object
        len()->int }
    """

    # stimulus sheet
    ssn_jsonl = """
                {"cells": {"A1": {}, "B1": "create", "C1": "List"}}
                {"cells": {"A2": {}, "B2": "append", "C2": "A1", "D2": "'Hello World!'"}}
                {"cells": {"A3": 1,  "B3": "len",  "C3": "A1"}}
                {"cells": {"A4": {}, "B4": "pop", "C4": "A1"}}
                {"cells": {"A5": 0,  "B5": "len", "C5": "A1"}}
    """

    # classes under test
    cuts = [ClassUnderTest("1", list), ClassUnderTest("2", deque)]

    # create stimulus matrix
    sm = parse_stimulus_matrix([Sheet("test1()", ssn_jsonl, lql)], cuts, [SheetInvocation("test1", "")])
    logger.debug(sm.to_string())

    # run stimulus matrix
    invocation_listener = InvocationListener()
    srm = run_sheets(sm, 1, invocation_listener)
    # results based on internal ExecutedInvocation
    logger.debug(srm.to_string())

    # create actuation sheets, now we have the real stimulus response matrix (SRM)
    srm_actuations = collect_actuation_sheets(srm)

    logger.debug(srm_actuations.to_string())


def test_list():
    # lql (interface specification)
    lql = """List {
        append(object)->void
        pop()->object
        len()->int }
    """
    parse_result = parse_lql(lql)

    # class under test
    cut = ClassUnderTest("1", list)

    adaptation_strategy = PassThroughAdaptationStrategy()
    adapted_implementations = adaptation_strategy.adapt(parse_result.interface, cut, 1)

    adapted_implementation = adapted_implementations[0]
    logger.debug(f" Class under test {adapted_implementation.cut.class_under_test}")

    # stimulus sheet
    ssn_jsonl = """
                {"cells": {"A1": {}, "B1": "create", "C1": "List"}}
                {"cells": {"A2": {}, "B2": "append", "C2": "A1", "D2": "'Hello World!'"}}
                {"cells": {"A3": 1,  "B3": "len",  "C3": "A1"}}
                {"cells": {"A4": {}, "B4": "pop", "C4": "A1"}}
                {"cells": {"A5": 0,  "B5": "len", "C5": "A1"}}
    """
    parsed_sheet = parse_sheet(ssn_jsonl)

    sheet_signature = lql_to_sheet_signature("test1()")

    # interpret (resolve bindings)
    invocations = interpret_sheet(TestInvocation(Test(sheet_signature.get_name(), parsed_sheet, parse_result.interface, sheet_signature), ""))
    logger.debug(invocations)

    assert 5 == len(invocations.sequence)

    # run on candidate implementation
    invocation_listener = InvocationListener()
    executed_invocations = run_sheet(invocations, adapted_implementation, invocation_listener)
    logger.debug(executed_invocations)

    assert 5 == len(executed_invocations.executed_sequence)
    assert 'Hello World!' == executed_invocations.get_executed_invocation(3).output.value


def test_queue():
    # lql (interface specification)
    lql = """Queue {
        append(object)->void
        pop()->object
        len()->int }
    """
    parse_result = parse_lql(lql)

    # class under test
    cut = ClassUnderTest("1", deque)

    adaptation_strategy = PassThroughAdaptationStrategy()
    adapted_implementations = adaptation_strategy.adapt(parse_result.interface, cut, 1)

    adapted_implementation = adapted_implementations[0]
    logger.debug(f" Class under test {adapted_implementation.cut.class_under_test}")

    # stimulus sheet
    ssn_jsonl = """
                {"cells": {"A1": {}, "B1": "create", "C1": "Queue"}}
                {"cells": {"A2": {}, "B2": "append", "C2": "A1", "D2": "'Hello World!'"}}
                {"cells": {"A3": 1,  "B3": "len",  "C3": "A1"}}
                {"cells": {"A4": {}, "B4": "pop", "C4": "A1"}}
                {"cells": {"A5": 0,  "B5": "len", "C5": "A1"}}
    """
    parsed_sheet = parse_sheet(ssn_jsonl)

    sheet_signature = lql_to_sheet_signature("test1()")

    # interpret (resolve bindings)
    invocations = interpret_sheet(TestInvocation(Test(sheet_signature.get_name(), parsed_sheet, parse_result.interface, sheet_signature), ""))
    logger.debug(invocations)

    assert 5 == len(invocations.sequence)

    # run on candidate implementation
    invocation_listener = InvocationListener()
    executed_invocations = run_sheet(invocations, adapted_implementation, invocation_listener)
    logger.debug(executed_invocations)

    assert 5 == len(executed_invocations.executed_sequence)
    assert 'Hello World!' == executed_invocations.get_executed_invocation(3).output.value