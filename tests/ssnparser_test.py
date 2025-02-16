import logging
import sys

from arena.ssn.ssnparser import resolve_cell_reference, is_cell_reference, parse_sheet

# logging
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


def test_resolve_cell_reference():
    assert (0, 0) == resolve_cell_reference("A1")
    assert (2, 1) == resolve_cell_reference("B3")
    assert (4, 2) == resolve_cell_reference("C5")

def test_is_cell_reference():
    assert is_cell_reference("A1")
    assert is_cell_reference("B3")
    assert is_cell_reference("C5")

    assert not is_cell_reference("Hello")
    assert not is_cell_reference("1")
    assert not is_cell_reference(" ")


def test_parse():
    myStr = """{"cells": {"A1": {}, "B1": "create", "C1": "Stack"}}
                {"cells": {"A2": {}, "B2": "create", "C2": "java.lang.String", "D2": "'Hello World!'"}}
                {"cells": {"A3": {}, "B3": "push", "C3": "A1", "D3": "A2"}}
                {"cells": {"A4": 1, "B4": "size", "C4": "A1"}}"""

    sheet = parse_sheet(myStr)

    assert 4 == len(sheet.rows)
    assert 3 == len(sheet.rows[0].cells)
    assert 4 == len(sheet.rows[1].cells)
    assert 4 == len(sheet.rows[2].cells)
    assert 3 == len(sheet.rows[3].cells)

    assert 'C1' == sheet.rows[0].cells[2].key
    assert 'Stack' == sheet.rows[0].cells[2].value

    # resolve a cell
    cell = sheet.resolve("D2")
    assert "D2" == cell.key
    assert "'Hello World!'" == cell.value

    # test methods
    assert 'A2' == sheet.rows[1].get_output().key
    assert 'B2' == sheet.rows[1].get_operation().key
    assert ['C2', 'D2'] == [x.key for x in sheet.rows[1].get_inputs()]

    # is cell reference?
    assert not sheet.rows[1].get_operation().is_cell_reference()
    assert sheet.rows[2].get_inputs()[1].is_cell_reference()
