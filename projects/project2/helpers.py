""" 
Configuration options and helper functions for Project 2

This module defines configuration options and helper functions
used by both `main.py` and `task_project2.py`

All the functions in this module should be assumed correct: 
Please do not modify
         
"""

import pandas as pd

from toolkit_paths import PROJECTS_DIR

PRJ_DATA_DIR = PROJECTS_DIR.joinpath("project2", "data")
FF_CSV_NAME = 'FF_Research_Data_Factors_daily.csv'
MA_RETS_CSV = 'ma_rets.csv'
MA_DEALS_CSV = 'ma_deals.csv'

# ----------------------------------------------------------------------------
#   Dictionary with the location of source files 
# ----------------------------------------------------------------------------
locs = {
        'ff_csv': PRJ_DATA_DIR / FF_CSV_NAME,
        'ma_rets_csv': PRJ_DATA_DIR / MA_RETS_CSV,
        'ma_deals_csv': PRJ_DATA_DIR / MA_DEALS_CSV,
        }


# ----------------------------------------------------------------------------
#   Helper functions 
#   PLEASE DO NOT CHANGE
# ----------------------------------------------------------------------------
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


def fmt_dt(date) -> str:
    """
    Return a string with the date
    """
    return date.strftime('%Y-%m-%d')


def fmt_tic(tic) -> str:
    """
    Returns the formatted ticker
    """
    return str(tic).upper().strip()


def read_org_ff():
    """
    Read the CSV file containing the Fama–French daily factors from this
    project's data folder and return a data frame with its contents.

    File location:

        toolkit/
        |__ projects/
        |   |__ project2/
        |   |   |__ data/
        |   |   |   |__ FF_Research_Data_Factors_daily.csv

    Returns
    -------
    frame
        A data frame with a DatetimeIndex and the following columns:

         #   Column   Dtype
        ---  ------   -----
         0   Mkt-RF   float64
         1   SMB      float64
         2   HML      float64
         3   RF       float64

    See the project description for more information.
    """
    return pd.read_csv(locs['ff_csv'], parse_dates=[0], index_col=0)

def summarise_series(ser: pd.Series):
    """
    Return a small table with summary statistics for a return series.

    The table includes:

        - Mean: the sample mean
        - Nobs: the number of non-missing observations
        - StdDev: the sample standard deviation (ddof = 1)
        - tstat: the t-statistic for testing mean = 0,
                 computed as mean / (StdDev / sqrt(Nobs))

    Parameters
    ----------
    ser : Series
        A pandas Series containing numeric values. Missing values are ignored.

    Returns
    -------
    frame
        A single-row data frame with index:
            ['mean', 'nobs', 'stddev', 'tstat']
        and corresponding values.
    """
    # Drop missing values
    x = ser.dropna()

    n = len(x)
    mean = x.mean()
    std = x.std(ddof=1) if n > 1 else float('nan')
    se = std / (n**0.5) if n > 0 else float('nan')
    tstat = mean / se if se not in (0, float('nan')) else float('nan')

    out = pd.DataFrame({
        'mean': [mean],
        'nobs': [n],
        'stddev': [std],
        'tstat': [tstat],
    })

    return out

def read_stk_rets():
    """
    Read the CSV file containing daily stock returns from this project's
    data folder and return a data frame with its contents.

    File location:

        toolkit/
        |__ projects/
        |   |__ project2/
        |   |   |__ data/
        |   |   |   |__ ma_rets.csv

    Returns
    -------
    frame
        A data frame with a DatetimeIndex and individual stock returns
        as columns. Column labels represent tickers.

    Notes
    -----
    Tickers are normalised using `fmt_tic`.
    """
    df = pd.read_csv(locs['ma_rets_csv'], parse_dates=['date'], index_col='date')
    df.columns = [fmt_tic(x) for x in df.columns]
    return df

def read_ma_deals():
    """
    Read the CSV file containing M&A deal information from this project's
    data folder and return a data frame with its contents.

    File location:

        toolkit/
        |__ projects/
        |   |__ project2/
        |   |   |__ data/
        |   |   |   |__ ma_deals.csv

    Returns
    -------
    frame
        A data frame with a RangeIndex and the following columns:

         #   Column         Dtype
        ---  ------         -----
         0   dealno         int64
         1   firmtype       object
         2   ticker         object
         3   announcement   object

    Notes
    -----
    Tickers are normalised using `fmt_tic`.
    """
    df = pd.read_csv(locs['ma_deals_csv'])
    df.loc[:, 'ticker'] = [fmt_tic(x) for x in df.ticker]
    return df

def wide_to_long_rets(
        wide: pd.DataFrame,
        date_col: str = 'date',
        ret_col: str = 'ret',
        tic_col: str = 'ticker',
        ):
    """
    Reshape a data frame with individual ticker returns in separate columns
    (wide format) into a long-format data frame with columns `date_col`,
    `tic_col`, and `ret_col`.

    Parameters
    ----------
    wide : frame
        A data frame with a DatetimeIndex and individual returns stored
        in separate columns. Column labels are tickers.

    date_col : str
        The label of the date column in the output data frame.
        Defaults to 'date'.

    ret_col : str
        The label of the column containing returns in the output
        data frame. Defaults to 'ret'.

    tic_col : str
        The label of the column containing tickers in the output
        data frame. Defaults to 'ticker'.

    Returns
    -------
    frame
        A data frame with a RangeIndex and columns:

         #   Column      Dtype
        ---  ------      -----
         0   `date_col`  datetime64[ns]
         1   `tic_col`   object
         2   `ret_col`   float64

    Example
    -------
    If `wide` is:

                      ACBI    ACTG
        date
        2021-01-04 -0.0151 -0.0355
        2021-01-05  0.0121  0.0500
        2021-01-06  0.0807 -0.0226

    Then `wide_to_long_rets(wide)` returns:

                date ticker     ret
        0 2021-01-04   ACBI -0.0151
        1 2021-01-04   ACTG -0.0355
        2 2021-01-05   ACBI  0.0121
        3 2021-01-05   ACTG  0.0500
        4 2021-01-06   ACBI  0.0807
        5 2021-01-06   ACTG -0.0226
    """
    df = wide.stack().reset_index()
    df.columns = [date_col, tic_col, ret_col]
    return df



