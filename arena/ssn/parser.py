class ParsedSheet:

    def __init__(self, name: str):
        self.name = name
        self.rows = []


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

class ParsedCell:

    def __init__(self, row: ParsedRow, key: str, value):
        self.row = row
        self.key = key
        self.value = value


import json

def parse(sheet_name : str, jsonl: str):
    sheet = ParsedSheet(sheet_name)
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

import re

def is_cell_reference(cell_reference):
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

# FIXME remove
if __name__ == "__main__":
    myStr = """{"cells": {"A1": {}, "B1": "create", "C1": "Stack"}}
                {"cells": {"A2": {}, "B2": "create", "C2": "java.lang.String", "D2": "'Hello World!'"}}
                {"cells": {"A3": {}, "B3": "push", "C3": "A1", "D3": "A2"}}
                {"cells": {"A4": 1, "B4": "size", "C4": "A1"}}"""

    sheet = parse("test1", myStr)
    print(sheet.rows)
