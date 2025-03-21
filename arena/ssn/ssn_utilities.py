import pandas as pd


def ssndict_to_dataframe(data):
    """
    Convert the dictionary to a pandas DataFrame
    :param data:
    :return:
    """

    max_row = 0
    max_col = 'A'

    # Determine the size of the DataFrame
    for cell_id in data.keys():
        row = int(cell_id[1:])
        col = cell_id[0]
        max_row = max(max_row, row)
        max_col = max(max_col, col)

    # Create a DataFrame of the appropriate size
    columns = [chr(i) for i in range(ord('A'), ord(max_col) + 1)]
    df = pd.DataFrame(index=range(1, max_row + 1), columns=columns)

    # Fill the DataFrame with the data
    for cell_id, value in data.items():
        row = int(cell_id[1:])
        col = cell_id[0]
        df.at[row, col] = value

    return df


def dataframe_to_ssndict(df) -> dict:
    """
    Convert the DataFrame to dictionary format

    :param df:
    :return:
    """
    data = {}
    add = 0
    for r_idx, row in df.iterrows():
        if r_idx == 0:
            # depending on whether we start with 0 or 1 (i.e., index set)
           add += 1

        for c_idx, value in row.items():
            if not pd.isna(value):  # Avoid adding NaN values
                cell_id = f"{c_idx}{r_idx + add}"
                data[cell_id] = value
    return data


def convert_dict_to_row_dicts(spreadsheet_data: dict) -> list[dict]:
    """
    Function to generate rows from spreadsheet data

    :param spreadsheet_data:
    :return:
    """

    from collections import defaultdict

    # Create a defaultdict to hold rows
    rows = defaultdict(dict)

    # Iterate over each cell in the spreadsheet data
    for cell, value in spreadsheet_data.items():
        # Extract the row number from the cell reference (e.g., "A1" -> "1")
        row = ''.join(filter(str.isdigit, cell))

        # Store the value in the appropriate row dictionary with full cell reference as the key
        if row:
            rows[row][cell] = value

    # Convert the defaultdict to a list of row dictionaries, sorted by row number
    row_list = [rows[row_number] for row_number in sorted(rows.keys(), key=int)]

    return row_list