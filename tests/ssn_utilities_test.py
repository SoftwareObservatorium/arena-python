import logging
import sys

from arena.ssn.ssn_utilities import ssndict_to_dataframe, dataframe_to_ssndict, convert_dict_to_row_dicts

# logging
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


def test_to_from():
    spreadsheet_data = {
        "A1": {}, "B1": "create", "C1": "GCD",
        "A2": "5", "B2": "greatest_common_divisor", "C2": "A1", "D2": "25", "E2": "15"
    }

    # Convert dictionary to DataFrame
    df = ssndict_to_dataframe(spreadsheet_data)
    print("DataFrame:")
    print(df)

    # Convert DataFrame back to dictionary
    reconstructed_dict = dataframe_to_ssndict(df)
    print("\nReconstructed Dictionary:")
    print(reconstructed_dict)

    assert spreadsheet_data == reconstructed_dict


def test_generate_rows_from_dict():
    spreadsheet_data = {
        "A1": {}, "B1": "create", "C1": "GCD",
        "A2": "5", "B2": "greatest_common_divisor", "C2": "A1", "D2": "25", "E2": "15"
    }

    # Convert the spreadsheet data into a list of row dictionaries
    row_data = convert_dict_to_row_dicts(spreadsheet_data)

    # Output the row data
    for row in row_data:
        print(row)

    assert [{'A1': {}, 'B1': 'create', 'C1': 'GCD'}, {'A2': '5', 'B2': 'greatest_common_divisor', 'C2': 'A1', 'D2': '25', 'E2': '15'}] == row_data

