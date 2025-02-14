from arena.engine.ssntestdriver import interpret
from arena.lql.lqlparser import parse_lql
from arena.ssn.ssnparser import parse_sheet

if __name__ == '__main__':
    # class under test
    cut = list
    print(cut)

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
                {"cells": {"A5": 0,  "B5": "size", "C5": "A1"}}
    """
    parsed_sheet = parse_sheet("test1", ssn_jsonl)

    # execute
    interpret(parsed_sheet, parse_result.interface)
