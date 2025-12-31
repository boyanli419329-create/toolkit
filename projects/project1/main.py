"""
Main module for Project 1

This module includes utilities to run and test the functions in the
`task_project1` module.

IMPORTANT:
Please refer to the project description for further details about this module.
"""

# ----------------------------------------------------------------------------
#  Import statements
#  PLEASE DO NOT CHANGE
# ----------------------------------------------------------------------------
from toolkit_paths import PROJECTS_DIR

from projects.project1.task_project1 import (
        lines_to_records,
        organize_by_ticker,
        calc_rets,
        mk_rets_dict,
        mk_mkt_val_dict,
        mk_vw_port,
        )


# ----------------------------------------------------------------------------
#  CONSTANTS
#  PLEASE DO NOT CHANGE
# ----------------------------------------------------------------------------
PRJ_DATA_DIR = PROJECTS_DIR.joinpath("project1", "data")
VALID_TICKERS = [
        'aal', 'aapl', 'abbv', 'baba', 'csco', 'dal', 'dis', 'ge', 
        'gme', 'intc', 'jnj', 'ko', 'meta', 'msft', 'nvda', 'orcl', 
        'pfe', 'pg', 't', 'tsla', 'tsm', 'v']


# ----------------------------------------------------------------------------
#  Auxiliary functions
#  PLEASE DO NOT CHANGE
# ----------------------------------------------------------------------------
def read_lines(ticker: str) -> list[str]:
    """
    Read the raw contents of a .dat file for the given ticker.

    Parameters
    ----------
    ticker : str
        Ticker symbol used to identify the file. The file name is expected
        to follow the pattern `<ticker>_prc.csv` (case-insensitive) and
        to be located under:

        toolkit/
        |__ projects/
        |   |__ project1/
        |   |   |__ data/
        |   |   |   |__ <ticker>.dat

    Returns
    -------
    list[str]
        A list of strings corresponding to the lines in the .dat file, read
        exactly as they appear in the source file.

    Examples
    --------
    If the contents of the .dat file `<ticker>.dat` are:

        date:2020-01-01,ticker:XXX,adj_close:1.1
        date:2020-01-02,ticker:XXX,adj_close:1.2

    then this function will return the following list:

    [
        'date:2020-01-01,ticker:XXX,adj_close:1.1',
        'date:2020-01-02,ticker:XXX,adj_close:1.2',
    ]

    Notes
    -----
    - This function is provided for you. Do not modify it.
    """
    # ----------------------------------
    # PLEASE DO NOT MODIFY THIS FUNCTION
    # ----------------------------------
    # Normalise the ticker symbol
    tic = ticker.strip().lower()
    # Ensure it is a valid parameter
    if tic not in VALID_TICKERS:
        raise ValueError(f"Invalid ticker '{ticker}'")
    # Build the path to the corresponding dat file
    pth = PRJ_DATA_DIR / f"{tic}.dat"
    # Read the contents of the file as text
    cnts = pth.read_text()
    # Split the text into individual lines and return them
    return cnts.splitlines()

def print_msg(*args, as_header = False):
    """
    Pretty-prints a list of arguments, one per line

    Parameters
    ----------
    *args
        Expressions to print

    as_header: bool, default False
        If True, add line separators to output

    Notes
    -----
    We created a similar function in class
    """
    if as_header:
        dashes = '-' * 40
        args = [dashes, *args, dashes]
    print(*args, sep='\n')

# ----------------------------------------------------------------------------
#  Main function
#  PLEASE DO NOT CHANGE
# ----------------------------------------------------------------------------
def main(
        tickers: list[str],
        prc_col: str = 'adj_close',
        ):
    """
    Orchestrate the workflow for Project 1 to compute value-weighted portfolio returns.

    This function demonstrates how the helper functions in `task_project1.py`
    are intended to be used together.  It reads `.dat` files for the selected
    tickers, extracts and organises the data, computes daily returns,
    calculates market values, and then produces value-weighted portfolio
    returns for all dates.

    Parameters
    ----------
    tickers : list[str]
        A list of ticker symbols identifying the files to be processed.
        Each file must exist in:
        ```
        toolkit/projects/project1/data/<ticker>.dat
        ```
        The function reads all lines from these files and combines them into
        a single list

    prc_col : str, default 'adj_close'
        The name of the price column to use when computing returns.

    Returns
    -------
    dict[str, float]
        A dictionary mapping each date (in `'YYYY-MM-DD'` format) to the
        value-weighted portfolio return on that date.

        Example:
        ```
        {
            '2024-12-02': 0.0015,
            '2024-12-03': -0.0023,
            ...
        }
        ```

    """
    # ----------------------------------
    # PLEASE DO NOT MODIFY THIS FUNCTION
    # ----------------------------------
    # Create a list with the combined lines for all tickers
    lines = []
    for tic in tickers:
        lines.extend(read_lines(tic))

    # Convert lines to records
    records = lines_to_records(lines)

    # prices and returns
    prices = organize_by_ticker(records, column=prc_col)
    rets = mk_rets_dict(prices)

    # Market value
    shares = organize_by_ticker(records, column='shares')
    mkt_val = mk_mkt_val_dict(prices=prices, shares=shares)

    # compute value-weighted returns
    vw_rets = mk_vw_port(rets=rets, mkt_val=mkt_val)

    return vw_rets


# ----------------------------------------------------------------------------
#  Test functions
#
#  IMPORTANT: If a function is named "test_..." instead of "_test_...",
#  PyCharm will try to debug the function by default. To prevent
#  this behaviour, add a single underscore to the start of test function names.
# ----------------------------------------------------------------------------
def _test_main(tickers, prc_col):
    """
    Copy of the main function that prints the average price.

    You may modify this function in any way you like.
    """
    print("Running _test_main...")
    lines = []
    for tic in tickers:
        lines.extend(read_lines(tic)) # <- Correct

    # Start testing from here...
    records = lines_to_records(lines)
    prices = organize_by_ticker(records, column=prc_col)
    rets = mk_rets_dict(prices)
    shares = organize_by_ticker(records, column='shares')
    mkt_val = mk_mkt_val_dict(prices=prices, shares=shares)
    vw_rets = mk_vw_port(rets=rets, mkt_val=mkt_val)

    print_msg(f"vw_rets: {vw_rets}", as_header=True)




# ----------------------------------------------------------------------------
#  Function to run all other tests
# ----------------------------------------------------------------------------
def run_tests():
    """
    Run all test functions.

    You may complete or extend this function in any way you like.
    """
    # Choose the parameters for the test functions
    tickers = ['aapl', 'csco']
    prc_col = 'adj_close'

    print(
        '-' * 40,
        "Parameters:",
        f"  tickers='{tickers}'",
        f"  prc_col='{prc_col}'",
        '-' * 40,
        sep='\n',
    )
    print("Running tests...\n")

    # Uncomment to run
    #_test_main(tickers=tickers,prc_col=prc_col)

    # Add other function calls here


# ----------------------------------------------------------------------------
#  Call the function to run the tests
# ----------------------------------------------------------------------------
run_tests()




    





