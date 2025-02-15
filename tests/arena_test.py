import logging
import sys
from collections import deque

from arena.engine.adaptation import AdaptedImplementation, PassThroughAdaptationStrategy
from arena.engine.ssntestdriver import interpret_sheet, run_sheet, InvocationListener
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


def test_list():
    # lql (interface specification)
    lql = """List {
        append(object)->void
        pop()->object
        len()->int }
    """
    parse_result = parse_lql(lql)

    # class under test
    cut = list

    adaptation_strategy = PassThroughAdaptationStrategy()
    adapted_implementations = adaptation_strategy.adapt(parse_result.interface, cut, 1)

    adapted_implementation = adapted_implementations[0]
    logger.debug(f" Class under test {adapted_implementation.class_under_test}")

    # stimulus sheet
    ssn_jsonl = """
                {"cells": {"A1": {}, "B1": "create", "C1": "List"}}
                {"cells": {"A2": {}, "B2": "append", "C2": "A1", "D2": "'Hello World!'"}}
                {"cells": {"A3": 1,  "B3": "len",  "C3": "A1"}}
                {"cells": {"A4": {}, "B4": "pop", "C4": "A1"}}
                {"cells": {"A5": 0,  "B5": "len", "C5": "A1"}}
    """
    parsed_sheet = parse_sheet("test1", ssn_jsonl)

    # interpret (resolve bindings)
    invocations = interpret_sheet(parsed_sheet, parse_result.interface)
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
    cut = deque

    adaptation_strategy = PassThroughAdaptationStrategy()
    adapted_implementations = adaptation_strategy.adapt(parse_result.interface, cut, 1)

    adapted_implementation = adapted_implementations[0]
    logger.debug(f" Class under test {adapted_implementation.class_under_test}")

    # stimulus sheet
    ssn_jsonl = """
                {"cells": {"A1": {}, "B1": "create", "C1": "Queue"}}
                {"cells": {"A2": {}, "B2": "append", "C2": "A1", "D2": "'Hello World!'"}}
                {"cells": {"A3": 1,  "B3": "len",  "C3": "A1"}}
                {"cells": {"A4": {}, "B4": "pop", "C4": "A1"}}
                {"cells": {"A5": 0,  "B5": "len", "C5": "A1"}}
    """
    parsed_sheet = parse_sheet("test1", ssn_jsonl)

    # interpret (resolve bindings)
    invocations = interpret_sheet(parsed_sheet, parse_result.interface)
    logger.debug(invocations)

    assert 5 == len(invocations.sequence)

    # run on candidate implementation
    invocation_listener = InvocationListener()
    executed_invocations = run_sheet(invocations, adapted_implementation, invocation_listener)
    logger.debug(executed_invocations)

    assert 5 == len(executed_invocations.executed_sequence)
    assert 'Hello World!' == executed_invocations.get_executed_invocation(3).output.value