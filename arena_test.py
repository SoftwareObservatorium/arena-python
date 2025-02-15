import logging
import sys

from arena.engine.adaptation import AdaptedImplementation
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
    # class under test
    adapted_implementation = AdaptedImplementation(list)
    logger.debug(f" Class under test {adapted_implementation.class_under_test}")

    # lql (interface specification)
    lql = """list {
        append(object)->void
        pop()->object
        len()->int }
    """
    parse_result = parse_lql(lql)

    # stimulus sheet
    ssn_jsonl = """
                {"cells": {"A1": {}, "B1": "create", "C1": "list"}}
                {"cells": {"A2": {}, "B2": "append", "C2": "A1", "D2": "'Hello World!'"}}
                {"cells": {"A3": 1,  "B3": "len",  "C3": "A1"}}
                {"cells": {"A4": {}, "B4": "pop", "C4": "A1"}}
                {"cells": {"A5": 0,  "B5": "len", "C5": "A1"}}
    """
    parsed_sheet = parse_sheet("test1", ssn_jsonl)

    # interpret (resolve bindings)
    invocations = interpret_sheet(parsed_sheet, parse_result.interface)
    logger.debug(invocations)

    # run on candidate implementation
    invocation_listener = InvocationListener()
    executed_invocations = run_sheet(invocations, adapted_implementation, invocation_listener)
    logger.debug(executed_invocations)
