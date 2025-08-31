import pytest


def pytest_addoption(parser):
    """Adds a custom command-line option to pytest."""
    parser.addoption(
        "--part",
        action="store",
        default=None,
        help="Run as specific part",
        choices=("deel_4", "deel_7", "deel_9"),
    )
    parser.addoption(
        "--pl-filename", action="store", default=None, help="Specify the PL file to use"
    )
    parser.addoption(
        "--pl-sheet-name",
        action="store",
        default=None,
        help="Specify the PL tab to use",
    )


def pytest_collection_modifyitems(config, items):
    part = "UNKNOWN"
    part = config.getoption("--part")
    skip_not_selected = pytest.mark.skip(reason="not selected")
    for item in items:
        if part not in item.keywords:
            item.add_marker(skip_not_selected)


def pl_filename(request):
    return request.config.getoption("--pl-filename")


def pl_sheet_name(request):
    return request.config.getoption("--pl-sheet-name")


def parse_excel_from_row(filepath, sheet_name=0, start_row=3):
    """
    Reads an Excel file and parses data into a table starting from a specific row.

    Args:
        filepath (str): The path to the Excel file.
        sheet_name (str or int, optional): The name or index of the sheet to read.
                                           Defaults to 0 (the first sheet).
        start_row (int): The row number to start parsing from (1-indexed).
                         Defaults to 3.

    Returns:
        pandas.DataFrame: A DataFrame containing the parsed data, or None if an error occurs.
    """
    try:
        # We use `skiprows` to ignore the rows before our desired start_row.
        # Since rows are 0-indexed in pandas, we need to skip `start_row - 1` rows.
        # For example, to start at row 3, we skip rows 0 and 1 (2 rows).
        rows_to_skip = start_row - 1

        df = pd.read_excel(filepath, sheet_name=sheet_name, skiprows=rows_to_skip)

        print(
            f"Successfully parsed data from '{filepath}' starting at row {start_row}."
        )
        return df

    except FileNotFoundError:
        print(f"Error: The file '{filepath}' was not found")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


@pytest.fixture
def pl_lookup(request):
    # Parse the PL file, starting from row 3
    data_table = parse_excel_from_row(
        pl_filename(request), pl_sheet_name(request), start_row=3
    )

    if data_table is not None:
        print("\n--- Parsed Data Table ---")
        print(data_table)
        print("\n-------------------------")
