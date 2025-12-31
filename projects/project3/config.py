""" config.py

Configuration options for the project3 package

"""
# IMPORTANT: Please do NOT modify this file except for defining the TICMAP dictionary

import os
import toolkit_config as tcfg

ROOTDIR = os.path.join(tcfg.PRJDIR, 'project3')
DATADIR = os.path.join(ROOTDIR, 'data')


# ------------------------------------------------------------------------------
# Part 4.2.1: Define the TICMAP Dictionary in config.py
# ------------------------------------------------------------------------------

# Your first task is to choose a stock exchange market where your team will implement
# a volatility trading strategy.

#    One country may have multiple stock exchanges.
#    For example, the U.S. has NYSE, NASDAQ, and AMEX as its main exchanges.

#    You must select at least 50 stocks listed on a single stock exchange
#    within your chosen country.

#    The selected country can be part of either a developed or emerging market.
#    Refer to the MSCI market classification for guidance:
#       https://www.msci.com/our-solutions/indexes/market-classification

# ------------------------------------------------------------------------------
# Define the TICMAP dictionary below
# ------------------------------------------------------------------------------

# This dictionary should contain ticker-to-company name mappings in the format:
#     'TICKER': 'Company Name'

#    If you use yfinance to download price data, make sure the tickers match
#    those used on Yahoo Finance (e.g., 'AAPL' for Apple Inc.).

#    If you're using another data source, be aware that ticker symbols may differ
#    and should be adjusted accordingly.

# Example:
# TICMAP = {
#     'AAPL': 'Apple Inc.',
#     'GOOGL': 'Alphabet Inc.',
#     ...
# }

# This dictionary will be used throughout the project to download and organize
# price data for your selected investment universe.

# Hint:
# Consider why you chose this country and market—you'll be asked to reflect on
# your selection in a later part of Project 3.


TICMAP = {
     'AAPL': 'Apple Inc.',
     'GOOGL': 'Alphabet Inc.',

 }
TICKERS = sorted(TICMAP.keys())


# -------------------------------------------------------- 
#   Aux function to process col names
# --------------------------------------------------------
def standardise_colnames(df):
    """ Renames the columns in `df` so that 
    - Names are lower case
    - Spaces are replaced with '_'

    Parameters
    ----------
    df : dataframe


    Notes
    -----
    - If column with the standardised name already exists, the new column will
      include a '_' prefix

    Examples
    -------

    >> df = pd.DataFrame([(1, 2), (3, 4)], columns=['A', 'B C'])
    >> print(df)

       A  B C
    0  1    2
    1  3    4

    >> df2 = standardise_colnames(df)
    >> print(df2)

       a  b_c
    0  1    2
    1  3    4

    """
    cols = set(df.columns)
    # You can define `local` functions
    def _parse_name(colname):
        # Processes the column name
        new_name = colname.lower().replace(' ', '_')
        # Decide what to do. The options are:
        # 1) column name is already properly formatted:
        #   => do nothing
        # 2) column name is not properly formatted but exists in the dataframe
        #   => Include '_' prefix
        # 3) Else: return formatted name
        if new_name == colname: 
            # Returns original column
            return colname
        elif new_name in cols:
            return '_' + new_name
        else:
            return new_name
    return df.rename(columns=_parse_name)




