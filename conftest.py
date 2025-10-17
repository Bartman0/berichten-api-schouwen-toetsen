import logging
import pytest
import pandas as pd
from numpy import isnan

logger = logging.getLogger()


def pytest_addoption(parser):
    """Adds a custom command-line option to pytest."""
    parser.addoption(
        "--part",
        action="store",
        default=None,
        help="Run as specific part",
        choices=(
            "deel_2",
            "deel_4",
            "deel_7",
            "deel_9",
            "deel_2_reset",
            "deel_4_reset",
            "deel_7_reset",
            "deel_9_reset",
            "deel_3_verwacht",
            "deel_5_verwacht",
            "deel_6_verwacht",
        ),
        required=True,
    )
    parser.addoption(
        "--pl-filename",
        action="store",
        default=None,
        help="Specify the PL file to use",
        required=True,
    )
    parser.addoption(
        "--pl-sheet-name",
        action="store",
        default=None,
        help="Specify the PL tab to use",
        required=True,
    )


def pytest_collection_modifyitems(config, items):
    part = config.getoption("--part")
    skip_not_selected = pytest.mark.skip(reason="not selected")
    for item in items:
        if part not in item.keywords:
            item.add_marker(skip_not_selected)


def pl_filename(request):
    return request.config.getoption("--pl-filename")


def pl_sheet_name(request):
    return request.config.getoption("--pl-sheet-name")


def parse_excel_from_row(filepath, sheet_name=0, start_row=2):
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
        df = pd.read_excel(
            filepath,
            sheet_name=sheet_name,
            skiprows=rows_to_skip,
            converters={
                "PLnummer": str,
                "BSN": str,
                "opmerking": str,
                "opmerking.1": str,
                "opmerking.2": str,
            },
        )
        logger.debug(
            f"Successfully parsed data from '{filepath}' starting at row {start_row}."
        )
    except FileNotFoundError:
        print(f"Error: The file '{filepath}' was not found")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    return df


@pytest.fixture
def pl_lookup(request):
    data_table = parse_excel_from_row(
        pl_filename(request), pl_sheet_name(request), start_row=2
    )
    logger.debug(data_table)
    lookup = {}
    for _, row in data_table.iterrows():
        lookup[row["PLnummer"]] = row["BSN"]
    return lookup


@pytest.fixture
def bsns_deel_2(request):
    data_table = parse_excel_from_row(
        pl_filename(request), pl_sheet_name(request), start_row=2
    )
    logger.debug(data_table)
    bsns = [
        row["BSN"] for _, row in data_table.iterrows() if not (isnan(row["A-nummer"]))
    ]
    logger.debug(f"deel_2 BSN's [{len(bsns)}]: {bsns}")
    return bsns


@pytest.fixture
def bsns_deel_3_verwacht(request):
    data_table = parse_excel_from_row(
        pl_filename(request), pl_sheet_name(request), start_row=2
    )
    logger.debug(data_table)
    bsns = [
        row["BSN"]
        for _, row in data_table.iterrows()
        if str(row["opmerking.1"]) != "nan"
    ]
    logger.debug(f"deel_3 basisset BSN's verwacht [{len(bsns)}]: {bsns}")
    return bsns


@pytest.fixture
def bsns_deel_5_verwacht(request):
    data_table = parse_excel_from_row(
        pl_filename(request), pl_sheet_name(request), start_row=2
    )
    logger.debug(data_table)
    bsns = [
        row["BSN"]
        for _, row in data_table.iterrows()
        if str(row["opmerking.2"]) != "nan"
    ]
    logger.debug(f"deel_5 basisset BSN's verwacht [{len(bsns)}]: {bsns}")
    return bsns


@pytest.fixture
def bsns_deel_6_verwacht(request):
    data_table = parse_excel_from_row(
        pl_filename(request), pl_sheet_name(request), start_row=2
    )
    logger.debug(data_table)
    bsns = [
        row["BSN"]
        for _, row in data_table.iterrows()
        if str(row["opmerking.3"]) != "nan"
    ]
    logger.debug(f"deel_6 basisset BSN's verwacht [{len(bsns)}]: {bsns}")
    return bsns
