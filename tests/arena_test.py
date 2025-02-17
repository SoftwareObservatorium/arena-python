import logging
import sys

import pytest

import main
from arena.arena import parse_stimulus_matrix, Sheet, run_sheets, collect_actuation_sheets, SheetInvocation, \
    lql_to_sheet_signature
from arena.engine.adaptation import PassThroughAdaptationStrategy
from arena.engine.artifacts import CodeCandidate, import_classes_under_test
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


def test_srm_list_builtin_nojsonl():
    """
    Demonstrates typical scenario: SM as input and SRM as output (use dict instead of jsonl)

    :return:
    """

    # lql (interface specification)
    lql = """List {
        append(object)->void
        pop()->object
        len()->int }
    """

    # stimulus sheet
    ssn_sequence = [
        {"A1": {}, "B1": "create", "C1": "List"},
        {"A2": {}, "B2": "append", "C2": "A1", "D2": "'Hello World!'"},
        {"A3": 1, "B3": "len", "C3": "A1"},
        {"A4": {}, "B4": "pop", "C4": "A1"},
        {"A5": 0, "B5": "len", "C5": "A1"}]

    # classes under test
    #    cuts = [ClassUnderTest("1", list), ClassUnderTest("2", collections.deque)] works as well
    cuts = [ClassUnderTest("1", "list"), ClassUnderTest("2", "collections.deque")]

    # create stimulus matrix
    sm = parse_stimulus_matrix([Sheet("test1()", ssn_sequence, lql)], cuts, [SheetInvocation("test1", "")])
    logger.debug(sm.to_string())

    assert len(sm.columns) == 2
    assert len(sm.index) == 1

    # run stimulus matrix
    invocation_listener = InvocationListener()
    srm = run_sheets(sm, 1, invocation_listener)
    # results based on internal ExecutedInvocation
    logger.debug(srm.to_string())

    assert len(srm.columns) == 2
    assert len(srm.index) == 1

    # create actuation sheets, now we have the real stimulus response matrix (SRM)
    srm_actuations = collect_actuation_sheets(srm)

    logger.debug(srm_actuations.to_string())

    assert len(srm_actuations.columns) == 2
    assert len(srm_actuations.index) == 1


def test_srm_list_builtin():
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
    #    cuts = [ClassUnderTest("1", list), ClassUnderTest("2", collections.deque)] works as well
    cuts = [ClassUnderTest("1", "list"), ClassUnderTest("2", "collections.deque")]

    # create stimulus matrix
    sm = parse_stimulus_matrix([Sheet("test1()", ssn_jsonl, lql)], cuts, [SheetInvocation("test1", "")])
    logger.debug(sm.to_string())

    assert len(sm.columns) == 2
    assert len(sm.index) == 1

    # run stimulus matrix
    invocation_listener = InvocationListener()
    srm = run_sheets(sm, 1, invocation_listener)
    # results based on internal ExecutedInvocation
    logger.debug(srm.to_string())

    assert len(srm.columns) == 2
    assert len(srm.index) == 1

    # create actuation sheets, now we have the real stimulus response matrix (SRM)
    srm_actuations = collect_actuation_sheets(srm)

    logger.debug(srm_actuations.to_string())

    assert len(srm_actuations.columns) == 2
    assert len(srm_actuations.index) == 1


def test_srm_base64_external_classes():
    """
    Demonstrates typical scenario: SM as input and SRM as output (here Classes are assumed)

    :return:
    """

    # lql (interface specification)
    lql = """Base64 {
            base64_encode(str)->str
        }
    """

    # stimulus sheet
    ssn_jsonl = """
                {"cells": {"A1": {}, "B1": "create", "C1": "Base64"}}
                {"cells": {"A2": {}, "B2": "base64_encode", "C2": "A1", "D2": "'Hello World!'"}}
    """

    # classes under test
    base_folder = f"{main.PROJECT_ROOT}/code-samples/base64"
    c1 = CodeCandidate("917239ca-5093-44a6-a284-64e1acb8ccac", "Base64",
                       f"{base_folder}/917239ca-5093-44a6-a284-64e1acb8ccac/candidate.py")
    c2 = CodeCandidate("c108afda-e52c-454b-a7ed-c05f48257a9b", "Base64",
                       f"{base_folder}/c108afda-e52c-454b-a7ed-c05f48257a9b/candidate.py")
    c3 = CodeCandidate("c9571f41-161b-46ed-a528-941d96a0dd2b", "Base64",
                       f"{base_folder}/c9571f41-161b-46ed-a528-941d96a0dd2b/candidate.py")
    cuts = import_classes_under_test([c1, c2, c3])

    # create stimulus matrix
    sm = parse_stimulus_matrix([Sheet("test1()", ssn_jsonl, lql)], cuts, [SheetInvocation("test1", "")])
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


def test_srm_base64_external_functions():
    """
    Demonstrates typical scenario: SM as input and SRM as output (here functions are assumed)

    :return:
    """

    # lql (interface specification)
    lql = """Base64 {
            base64_encode(str)->str
        }
    """

    # stimulus sheet
    ssn_jsonl = """
                {"cells": {"A1": {}, "B1": "create", "C1": "Base64"}}
                {"cells": {"A2": {}, "B2": "base64_encode", "C2": "A1", "D2": "'Hello World!'"}}
    """

    # classes under test
    base_folder = f"{main.PROJECT_ROOT}/code-samples/base64_functions"
    c1 = CodeCandidate("917239ca-5093-44a6-a284-64e1acb8ccac", "",
                       f"{base_folder}/917239ca-5093-44a6-a284-64e1acb8ccac/candidate.py")
    c2 = CodeCandidate("c108afda-e52c-454b-a7ed-c05f48257a9b", "",
                       f"{base_folder}/c108afda-e52c-454b-a7ed-c05f48257a9b/candidate.py")
    c3 = CodeCandidate("c9571f41-161b-46ed-a528-941d96a0dd2b", "",
                       f"{base_folder}/c9571f41-161b-46ed-a528-941d96a0dd2b/candidate.py")
    cuts = import_classes_under_test([c1, c2, c3])

    # create stimulus matrix
    sm = parse_stimulus_matrix([Sheet("test1()", ssn_jsonl, lql)], cuts, [SheetInvocation("test1", "")])
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


#@pytest.mark.skip(reason="no reports for some reason? flaky ..")
def test_srm_base64_external_classes_code_coverage():
    """
    Demonstrates typical scenario: SM as input and SRM as output

    :return:
    """

    # lql (interface specification)
    lql = """Base64 {
            base64_encode(str)->str
        }
    """

    # stimulus sheet
    ssn_jsonl = """
                {"cells": {"A1": {}, "B1": "create", "C1": "Base64"}}
                {"cells": {"A2": {}, "B2": "base64_encode", "C2": "A1", "D2": "'Hello World!'"}}
    """

    # classes under test
    base_folder = f"{main.PROJECT_ROOT}/code-samples/base64"
    c1 = CodeCandidate("917239ca-5093-44a6-a284-64e1acb8ccac", "Base64",
                       f"{base_folder}/917239ca-5093-44a6-a284-64e1acb8ccac/candidate.py")
    c2 = CodeCandidate("c108afda-e52c-454b-a7ed-c05f48257a9b", "Base64",
                       f"{base_folder}/c108afda-e52c-454b-a7ed-c05f48257a9b/candidate.py")
    c3 = CodeCandidate("c9571f41-161b-46ed-a528-941d96a0dd2b", "Base64",
                       f"{base_folder}/c9571f41-161b-46ed-a528-941d96a0dd2b/candidate.py")
    cuts = import_classes_under_test([c1, c2, c3])

    # create stimulus matrix
    sm = parse_stimulus_matrix([Sheet("test1()", ssn_jsonl, lql)], cuts, [SheetInvocation("test1", "")])
    logger.debug(sm.to_string())

    assert len(sm.columns) == 3
    assert len(sm.index) == 1

    # run stimulus matrix
    invocation_listener = InvocationListener()
    srm = run_sheets(sm, 1, invocation_listener, measure_code_coverage=True)  # enable code coverage
    # results based on internal ExecutedInvocation
    logger.debug(srm.to_string())

    assert len(srm.columns) == 3
    assert len(srm.index) == 1

    # create actuation sheets, now we have the real stimulus response matrix (SRM)
    srm_actuations = collect_actuation_sheets(srm)

    logger.debug(srm_actuations.to_string())

    assert len(srm_actuations.columns) == 3
    assert len(srm_actuations.index) == 1


def test_list():
    # lql (interface specification)
    lql = """List {
        append(object)->void
        pop()->object
        len()->int }
    """
    parse_result = parse_lql(lql)

    # class under test
    cut = ClassUnderTest("1", "list")

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
    invocations = interpret_sheet(
        TestInvocation(Test(sheet_signature.get_name(), parsed_sheet, parse_result.interface, sheet_signature), ""))
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
    cut = ClassUnderTest("1", "collections.deque")

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
    invocations = interpret_sheet(
        TestInvocation(Test(sheet_signature.get_name(), parsed_sheet, parse_result.interface, sheet_signature), ""))
    logger.debug(invocations)

    assert 5 == len(invocations.sequence)

    # run on candidate implementation
    invocation_listener = InvocationListener()
    executed_invocations = run_sheet(invocations, adapted_implementation, invocation_listener)
    logger.debug(executed_invocations)

    assert 5 == len(executed_invocations.executed_sequence)
    assert 'Hello World!' == executed_invocations.get_executed_invocation(3).output.value


def test_queue_parameterized_sheet():
    """
    Parameterized sheets

    :return:
    """

    # lql (interface specification)
    lql = """Queue {
        append(object)->void
        pop()->object
        len()->int }
    """
    parse_result = parse_lql(lql)

    # class under test
    cut = ClassUnderTest("1", "collections.deque")

    adaptation_strategy = PassThroughAdaptationStrategy()
    adapted_implementations = adaptation_strategy.adapt(parse_result.interface, cut, 1)

    adapted_implementation = adapted_implementations[0]
    logger.debug(f" Class under test {adapted_implementation.cut.class_under_test}")

    # stimulus sheet
    ssn_jsonl = """
                {"cells": {"A1": {}, "B1": "create", "C1": "Queue"}}
                {"cells": {"A2": {}, "B2": "append", "C2": "A1", "D2": "?p1"}}
                {"cells": {"A3": 1,  "B3": "len",  "C3": "A1"}}
                {"cells": {"A4": {}, "B4": "pop", "C4": "A1"}}
                {"cells": {"A5": 0,  "B5": "len", "C5": "A1"}}
    """
    parsed_sheet = parse_sheet(ssn_jsonl)

    sheet_signature = lql_to_sheet_signature("test1(p1=str)")  # python types ...

    # interpret (resolve bindings)
    invocations = interpret_sheet(
        TestInvocation(Test(sheet_signature.get_name(), parsed_sheet, parse_result.interface, sheet_signature),
                       "'Hello World!'"))
    logger.debug(invocations)

    assert 5 == len(invocations.sequence)

    # run on candidate implementation
    invocation_listener = InvocationListener()
    executed_invocations = run_sheet(invocations, adapted_implementation, invocation_listener)
    logger.debug(executed_invocations)

    assert 5 == len(executed_invocations.executed_sequence)
    assert 'Hello World!' == executed_invocations.get_executed_invocation(3).output.value


def test_queue_code_expression():
    """
    Code expressions

    :return:
    """

    # lql (interface specification)
    lql = """Queue {
        append(object)->void
        pop()->object
        len()->int }
    """
    parse_result = parse_lql(lql)

    # class under test
    cut = ClassUnderTest("1", "collections.deque")

    adaptation_strategy = PassThroughAdaptationStrategy()
    adapted_implementations = adaptation_strategy.adapt(parse_result.interface, cut, 1)

    adapted_implementation = adapted_implementations[0]
    logger.debug(f" Class under test {adapted_implementation.cut.class_under_test}")

    # stimulus sheet
    ssn_jsonl = """
                {"cells": {"A1": {}, "B1": "create", "C1": "Queue"}}
                {"cells": {"A2": {}, "B2": "$eval", "C2": "['hello', 'world']"}}
                {"cells": {"A3": {},  "B3": "append",  "C3": "A1", "C4": "A2"}}
                {"cells": {"A4": {}, "B4": "pop", "C4": "A1"}}
    """
    parsed_sheet = parse_sheet(ssn_jsonl)

    sheet_signature = lql_to_sheet_signature("test1()")  # python types ...

    # interpret (resolve bindings)
    invocations = interpret_sheet(
        TestInvocation(Test(sheet_signature.get_name(), parsed_sheet, parse_result.interface, sheet_signature), ""))
    logger.debug(invocations)

    assert 4 == len(invocations.sequence)

    # run on candidate implementation
    invocation_listener = InvocationListener()
    executed_invocations = run_sheet(invocations, adapted_implementation, invocation_listener)
    logger.debug(executed_invocations)

    assert 4 == len(executed_invocations.executed_sequence)
    assert ['hello', 'world'] == executed_invocations.get_executed_invocation(3).output.value
