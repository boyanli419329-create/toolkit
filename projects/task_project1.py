"""
Module task_project1

IMPORTANT:

- This is the ONLY module you need to submit.
- Please refer to the project description for further details about this module.

"""


def lines_to_records(lines):
    """
    Convert non-empty lines from a `.dat` file into dictionaries.

    Parameters
    ----------
    lines : list[str]
        A list of strings representing lines from a `.dat` file, exactly
        as they appear in the file.
        Each non-empty line in the input list contains comma-separated
        key–value pairs, where each pair is separated by a colon.

    Returns
    -------
    list[dict[str, str]]
        A list of dictionaries, each corresponding to one line in the file.
        Each dictionary maps field names to their string values.

    Examples
    --------
    >> lines = [
            'date:2016-02-10,ticker:CSCO,open:23.13,close:22.51,adj_close:16.8671,shares:5076080000',
            'date:2016-02-09,ticker:CSCO,open:22.6,close:22.65,adj_close:16.972,shares:5076080000',
        ]
    >> lines_to_records(lines)
    [
        {
            'date': '2016-02-10',
            'ticker': 'CSCO',
            'open': '23.13',
            'close': '22.51',
            'adj_close': '16.8671',
            'shares': '5076080000'
        },
        {
            'date': '2016-02-09',
            'ticker': 'CSCO',
            'open': '22.6',
            'close': '22.65',
            'adj_close': '16.972',
            'shares': '5076080000'
        }
    ]
    """
    out = []
    for line in lines:
        dic = {}
        for ele in line.split(','):
            key, value = ele.split(':')
            dic[key] = value
        out.append(dic)
    return out

def organize_by_ticker(records: list[dict], column: str):
    """
    Group records by ticker and convert values in a selected column

    Given a list of dictionaries as returned by `lines_to_records`, this
    function builds a nested dictionary organised by ticker symbol and date.

    Parameters
    ----------
    records : list[dict]
        A list of dictionaries, each containing at least the keys `'date'`,
        `'ticker'`, and the column specified in `column`.

    column : str
        The name of the column whose values should populate the inner
        dictionaries.

    Returns
    -------
    dict[str, dict[str, float | None]]
        A nested dictionary of the form:
            {
                '<ticker>': {
                    '<date>': <value>,
                       
                },
                   
            }
        where `<value>` is a float or `None` if missing.

    Examples
    --------
    >> records = [
           {'date': '2016-02-10', 'ticker': 'CSCO', 'adj_close': '16.8671'},
           {'date': '2016-02-09', 'ticker': 'CSCO', 'adj_close': '16.972'},
        ]

    >> organize_by_ticker(records, column='adj_close')
    {'CSCO': {'2016-02-10': 16.8671, '2016-02-09': 16.972}}


    """
    data = {}
    for dic in records:
        ticker = dic['ticker']
        date = dic['date']
        value = dic[column]
        if ticker not in data:
            data[ticker] = {}

        if not value:
            value = None
        else:
            value = float(value)
        data[ticker][date] = value
    return data

def calc_rets(prices: dict):
    """
    Compute simple returns from a dictionary of prices.

    Each return is calculated relative to the previous date in the series,
    regardless of whether the dates are consecutive in calendar time.
    The first date in the series is assigned a return value of `None`.

    Parameters
    ----------
    prices : dict[str, float]
        A dictionary mapping date strings in `'YYYY-MM-DD'` format to
        prices (floats).

    Returns
    -------
    dict[str, float | None]
        A dictionary of the same form as `prices`, where each value represents
        the simple return relative to the previous date.

    Notes
    -----
    - Returns are computed based on sorted dates.
    - If the previous price is missing or non-positive, the corresponding
      return is `None`.

    Examples
    --------
    >> prices = {'2025-01-01': 100.0, '2025-01-02': 110.0, '2025-01-05': 121.0}

    >> calc_rets(prices)

    {'2025-01-01': None, '2025-01-02': 0.1, '2025-01-05': 0.1}
    """
    out = {}
    dates = sorted(prices.keys())
    for i, date in enumerate(dates):
        ret = None
        if i > 0:
            prior_prc = prices[dates[i - 1]]
            prc = prices[date]
            if prc is not None:
                if prior_prc is not None and prior_prc > 0:
                    ret = (prc / prior_prc) - 1
        out[date] = ret
    return out

def mk_rets_dict(prices: dict):
    """
    Compute simple returns for each ticker in a nested price dictionary.


    Parameters
    ----------
    prices : dict[str, dict[str, float]]
        A nested dictionary with structure:
            {<ticker>: {<date>: <price>,    }}

    Returns
    -------
    dict[str, dict[str, float | None]]
        A nested dictionary of the same structure:
            {<ticker>: {<date>: <return>,    }}
        The first date for each ticker will have a value of `None`.

    Examples
    --------
    >> prices = {
            'AAPL': {'2025-01-01': 100.0, '2025-01-02': 110.0},
            'MSFT': {'2025-01-01': 200.0, '2025-01-03': 210.0}
        }
    >> mk_rets_dict(prices)
    {
        'AAPL': {'2025-01-01': None, '2025-01-02': 0.1},
        'MSFT': {'2025-01-01': None, '2025-01-03': 0.05}
    }
    """
    for tic in prices:
        for date, ret in calc_rets(prices[tic]).items():
            prices[tic][date] = ret
    return prices

def mk_mkt_val_dict(prices: dict, shares: dict):
    """
    Compute market values by multiplying prices and shares for matching 
    dates.

    Parameters
    ----------
    prices : dict[str, dict[str, float]]
        A nested dictionary mapping tickers to date–price pairs.

    shares : dict[str, dict[str, float]]
        A nested dictionary mapping tickers to date–shares pairs.

    Returns
    -------
    dict[str, dict[str, float]]
        A nested dictionary mapping tickers to date–market value pairs.
        Only entries with matching tickers and dates present in both input
        dictionaries are included.

    Examples
    --------
    >> prices = {
        'AAPL': {
            '2025-01-01': 100.0,
            '2025-01-02': 110.0,
            '2025-01-05': 121.0,  
        },
        'MSFT': {
            '2025-01-01': 200.0,
            '2025-01-03': 210.0,  
        },
    }
    >> shares = {
        'AAPL': {
            '2025-01-01': 1000,
            '2025-01-02': 2000,
            '2025-01-05': None,  
        },
        'MSFT': {
            '1999-01-01': 2000,
            '1999-01-03': 2000,  
        },
    }
    >> mk_mkt_val_dict(prices=prices, shares=shares)

    {'AAPL': {'2025-01-01': 100000.0, '2025-01-02': 220000.0}, 'MSFT': {}}
    """
    mkt_value = {}
    for tic, prices_dict in prices.items():
        if tic not in shares:
            continue
        mkt_value[tic] = {}
        shares_dict = shares[tic]
        for date, price in prices_dict.items():
            if date not in shares_dict:
                continue
            shr = shares_dict[date]
            if price is not None and shr is not None:
                mkt_value[tic][date] = price * shr
    return mkt_value

def mk_vw_port(rets: dict, mkt_val: dict):
    """
    Compute value-weighted portfolio returns across all tickers.

    For each date, this function calculates the portfolio return as the
    weighted average of individual ticker returns, using market values as
    weights. Dates and tickers with missing or invalid data are skipped.

    Parameters
    ----------
    rets : dict[str, dict[str, float | None]]
        A nested dictionary of returns with structure:
            {<ticker>: {<date>: <ret>,    }}
        (typically produced by `mk_rets_dict`).
    mkt_val : dict[str, dict[str, float]]
        A nested dictionary of market values with structure:
            {<ticker>: {<date>: <mkt_val>,    }}
        (typically produced by `mk_mkt_val_dict`).

    Returns
    -------
    dict[str, float]
        A dictionary mapping each date to the portfolio’s
        value-weighted return. Only dates with at least one valid return and
        corresponding market value are included.

    Examples
    --------
    >> rets = {
            'AAPL': {'2025-01-01': 0.1, '2025-01-02': 0.1},
            'MSFT': {'2025-01-01': None, '2025-01-02': 0.2}
        }
    >> mkt_val = {
            'AAPL': {'2025-01-01': 100, '2025-01-02': 100},
            'MSFT': {'2025-01-02': 200}
        }
    >> mk_vw_port(rets, mkt_val)
    {'2025-01-01': 0.1, '2025-01-02': 0.16666666666666666}
    """
    numer = {}
    denom = {}
    for tic, ret_by_date in rets.items():
        mv_by_date = mkt_val.get(tic, {})
        for date, r in ret_by_date.items():
            if date not in mv_by_date:
                continue
            mv = mv_by_date[date]
            if r is None or mv is None:
                continue
            numer[date] = numer.get(date, 0.0) + (mv * r)
            denom[date] = denom.get(date, 0.0) + mv
    out = {}
    for date, d in denom.items():
        if d > 0:
            out[date] = numer[date] / d

    return out



