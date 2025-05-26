import json
import logging

import pandas

from arena.ssn.ssn_utilities import dataframe_to_ssndict, convert_dict_to_row_dicts

logger = logging.getLogger(__name__)


class ParsedSheet:

    def __init__(self):
        self.rows = []
        self.sheet = None

    def resolve(self, cell_ref: str):
        """
        Resolve cell reference

        :param cell_ref:
        :return:
        """
        ref = resolve_cell_reference(cell_ref)
        return self.rows[ref[0]].cells[ref[1]]

class ParsedRow:

    def __init__(self, sheet: ParsedSheet, cells: list):
        self.sheet = sheet
        self.cells = cells

    def get_output(self):
        return self.cells[0]

    def get_operation(self):
        return self.cells[1]

    def get_inputs(self):
        return self.cells[2:]


class ParsedCell:

    def __init__(self, row: ParsedRow, key: str, value):
        self.row = row
        self.key = key
        self.value = value

    def is_cell_reference(self):
        return is_cell_reference(self.value)

    def is_test_parameter(self):
        if not type(self.value) == str:
            return False

        return self.value.startswith("?")


def parse_sheet(jsonl: str):
    """
    Parse sequence sheet from JSONL

    :param jsonl:
    :return:
    """

    sheet = ParsedSheet()
    for line in jsonl.splitlines():
        # Strip any leading or trailing whitespace
        stripped_line = line.strip()
        if not stripped_line:
            continue  # Skip empty lines
        # Parse the JSON line
        row_data = json.loads(stripped_line)
        # Extract cells data from the row
        if 'cells' in row_data:
            row = ParsedRow(sheet, [])

            cells = row_data['cells']
            for key, value in cells.items():
                cell = ParsedCell(row, key, value)
                row.cells.append(cell)
            sheet.rows.append(row)

    return sheet


def parse_sheet_sequence(sheet_sequence: list):
    """
    Parse sequence sheet from a list of dicts

    :param sheet_sequence:
    :return:
    """

    sheet = ParsedSheet()

    for cells in sheet_sequence:
        row = ParsedRow(sheet, [])
        for key, value in cells.items():
            cell = ParsedCell(row, key, value)
            row.cells.append(cell)
        sheet.rows.append(row)

    return sheet


def parse_sheet_dataframe(sheet_df: pandas.DataFrame):
    """
    Parse sequence sheet from Pandas DataFrame

    :param sheet_df:
    :return:
    """

    # Convert DataFrame back to dictionary
    ssn_dict = dataframe_to_ssndict(sheet_df)

    list_of_dicts = convert_dict_to_row_dicts(ssn_dict)
    sheet = parse_sheet_sequence(list_of_dicts)

    return sheet


import re

def is_cell_reference(cell_reference):
    if not type(cell_reference) == str:
        return False

    if not re.fullmatch("[A-Z]+[0-9]", cell_reference):
        return False

    return True


def resolve_cell_reference(cell_reference):
    if not re.fullmatch("[A-Z]+[0-9]", cell_reference):
        raise ValueError("Invalid cell reference: {}".format(cell_reference))

    # Extract column part (letters) and row part (digits)
    col_str = re.sub("[0-9]", "", cell_reference)
    row_str = re.sub("[A-Za-z]", "", cell_reference)

    # Convert column to 0-based index
    col = ord(col_str[0].upper()) - ord('A')

    # Convert row to integer and adjust for 0-based indexing
    row = int(row_str) - 1

    return (row, col)
