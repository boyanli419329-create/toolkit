"""
Module task_project2

IMPORTANT:

- This is the ONLY module you need to submit.
- Please refer to the project description for further details about this module.

"""

import pandas as pd

from projects.project2.helpers import (
        fmt_dt,
        wide_to_long_rets,
        )

def mk_ma_info(ma_deals: pd.DataFrame):
    """
    Construct a data frame with announcement information, including the
    announcement date, deal identifier, and the tickers of the acquirer and
    target firms.

    Parameters
    ----------
    ma_deals : frame
        A data frame with a RangeIndex and the following columns:

         #   Column         Dtype
        ---  ------         -----
         0   dealno         int64
         1   firmtype       object
         2   ticker         object
         3   announcement   object


    Returns
    -------
    frame
        A data frame with a RangeIndex and the following columns:

         #   Column         Dtype
        ---  ------         -----
         0   announcement   datetime64[ns]
         1   dealno         int64
         2   acq            object
         3   tgt            object

        In the output:

        - `acq` contains the ticker of the acquirer for each deal,
        - `tgt` contains the ticker of the target for each deal.

        Only deals for which both the acquirer and target tickers are
        available are included in the output.
    """
    idx_col = 'announcement'
    df = ma_deals.astype({idx_col: 'datetime64[ns]'})
    base_cols = [idx_col, 'dealno', 'ticker']

    dfs = {}
    for ft in ['acq', 'tgt']:
        cond = df.firmtype == ft
        ft_df = (
            df.loc[cond, base_cols]
              .set_index(idx_col, drop=False)
              .rename(columns={'ticker': ft})
        )
        dfs[ft] = ft_df

    out = (
        dfs['acq'].join(dfs['tgt'].loc[:, ['tgt']], how='inner')
            .reset_index(drop=True)
    )
    return out

def mk_stk_arets(
        stk_rets: pd.DataFrame = None,
        org_ff: pd.DataFrame = None,
        ):
    """
    Compute abnormal stock returns using the market return as a benchmark.

    Parameters
    ----------
    stk_rets : frame
        A data frame containing the daily stock returns from `ma_rets.csv`.
        This is the output of `helpers.read_stk_rets`.

    org_ff : frame
        A data frame containing the Fama–French daily factors downloaded
        from Ken French’s website. This is the output of `helpers.read_org_ff`.

    Returns
    -------
    frame
        A data frame with a RangeIndex and the following columns:

         #   Column  Dtype
        ---  ------  -----
         0   date    datetime64[ns]
         1   ticker  object
         2   aret    float64

        where:

        - `date` is the return date
        - `ticker` is the stock ticker
        - `aret` is the abnormal return for each ticker–date, 
           computed as the individual stock return minus the 
           market return.

    """
    cond = org_ff.index.isin(stk_rets.index)
    ff_df = org_ff.loc[cond]
    mkt = ff_df.loc[:, 'Mkt-RF'] + ff_df.loc[:, 'RF']
    arets = stk_rets.sub(mkt, axis=0)
    return wide_to_long_rets(arets, ret_col='aret')

def mean_by_dates(
        df: pd.DataFrame,
        date_col: str,
        value_col: str,
        ):
    """
    Compute the average value of `value_col` for each unique date in `date_col`.

    Parameters
    ----------
    df : frame
        A data frame containing at least the two columns `date_col` and 
        `value_col`.

    date_col : str
        The name of the column containing dates. This column must have
        dtype `datetime64[ns]`.

    value_col : str
        The name of the column containing the numeric values to be averaged.
        This column should contain floats.

    Returns
    -------
    series
        A Series indexed by the unique dates in `date_col` (as a
        DatetimeIndex), where each element is the average of `value_col`
        for that particular date, ignoring missing values.
    """
    dates = df.loc[:, date_col].unique()
    out = pd.Series(None, index=dates, dtype=float)
    values = df.set_index(date_col).loc[:, value_col]
    for date in dates:
        out.loc[date] = values.loc[[date]].mean()
    out.sort_index(inplace=True)
    return out

def expand_event_dates(
        events: pd.DataFrame,
        valid_dates: pd.DatetimeIndex,
        announce_col: str = 'announcement',
        date_col: str = 'date',
        ):
    """
    Expand an events data frame so that each event is repeated once for
    each valid date from 1 to 30 calendar days after its announcement.

    Parameters
    ----------
    events : frame
        A data frame that includes a column named `announce_col`. This
        column must have dtype 'datetime64[ns]'.

    valid_dates : DatetimeIndex
        A DatetimeIndex of valid dates (for example, trading days).

    announce_col : str, default 'announcement'
        Name of the column in `events` containing the announcement dates.

    date_col : str, default 'date'
        Name of the date column in the output data frame.

    Returns
    -------
    frame or None
        A data frame with a RangeIndex, the same columns as `events`,
        and an additional column named `date_col`. For each event, the
        function creates one row for each date in `valid_dates` that falls
        between 1 and 30 calendar days after the announcement date.

        If no event has any matching dates in `valid_dates`, returns `None`.

        The order of the columns in this data frame does not matter
    """
    td_start = pd.Timedelta(days=1)
    td_end = pd.Timedelta(days=30)

    dates = valid_dates.drop_duplicates().sort_values()
    dates = pd.Series(dates, index=dates)
    dates.index.name = date_col

    out = []
    for _, row in events.iterrows():
        announce = row[announce_col]
        data = row.to_dict()
        start = fmt_dt(announce + td_start)
        end = fmt_dt(announce + td_end)
        window_idx = dates.loc[start:end].index
        if len(window_idx) == 0:
            continue
        df = pd.DataFrame(data, index=window_idx).reset_index()
        out.append(df)

    if out:
        return pd.concat(out, ignore_index=True).reset_index(drop=True)

def mk_buy_tgt_sell_acq_rets(
        expanded_ma_info: pd.DataFrame,
        stk_rets: pd.DataFrame,
        ):
    """
    Returns from buying the target and selling the acquirer.

    Parameters
    ----------
    expanded_ma_info : frame
        A data frame with a RangeIndex and the following columns (in any order):

         Column         Dtype
         ------         -----
         date           datetime64[ns]
         announcement   datetime64[ns]
         dealno         int64
         acq            object
         tgt            object

        where:

        - `acq` contains the ticker of the acquirer for each deal,
        - `tgt` contains the ticker of the target for each deal.
        - `date` contains all dates in `stk_rets.index` that fall
          inside the period from one to 30 days after the event.

        All tickers are normalised using `helpers.fmt_tic`.

    stk_rets : frame
        A data frame containing the daily stock returns from `ma_rets.csv`.
        This is the output of `helpers.read_stk_rets`.

    Returns
    -------
    series
        A Series indexed by date, where each value is the return
        on an equal-weighted portfolio where we purchase the target and 
        sell the acquirer for up to 30 days


        See project for more information


    """
    idx_cols = ['date', 'ticker']

    rets = wide_to_long_rets(stk_rets)
    rets = rets.set_index(idx_cols[0], drop=False)
    events = expanded_ma_info.set_index(idx_cols[0], drop=False)
    dates = events.index.unique().intersection(rets.index)
    rets = rets.loc[dates]
    events = events.loc[dates]
    out = pd.Series(None, index=dates)
    for date in dates:
        rets_date = rets.loc[date].set_index(idx_cols)
        events_date = events.loc[date]

        buys = events_date.rename(columns={'tgt': idx_cols[1]}).set_index(idx_cols)
        buys = buys.join(rets_date, how='inner')

        sales = events_date.rename(columns={'acq': idx_cols[1]}).set_index(idx_cols)
        sales = sales.join(rets_date, how='inner')

        out.loc[date] = buys.loc[:, 'ret'].mean() - sales.loc[:, 'ret'].mean()

    return out.dropna().sort_index()

def mk_buy_tgt_sell_mkt_rets(
        expanded_ma_info: pd.DataFrame,
        stk_arets: pd.DataFrame,
        ):
    """
    Compute the daily returns of a trading strategy that buys the target
    and sells the market for each announced M&A deal.

    For every deal, the strategy takes a long position in the target's stock
    and a short position in the market starting one day after the
    announcement. Both positions are held for up to 30 calendar days
    after the announcement. Because `stk_arets` already contains abnormal
    returns (stock return minus market return), the return on this strategy
    for each deal–date is equal to the target's abnormal return on that date.
    On each trading date, the portfolio return is the equal-weighted average
    of these abnormal returns across all active deals.

    Parameters
    ----------
    expanded_ma_info : frame
        A data frame with a RangeIndex and the following columns (in any order):

         Column         Dtype
         ------         -----
         date           datetime64[ns]
         announcement   datetime64[ns]
         dealno         int64
         acq            object
         tgt            object

        where:

        - `acq` contains the ticker of the acquirer for each deal,
        - `tgt` contains the ticker of the target for each deal,
        - `date` contains all dates in the returns data that fall inside
          the period from one to 30 days after the announcement.

        All tickers are normalised using `helpers.fmt_tic`.

    stk_arets : frame
        A data frame with a RangeIndex and the following columns:

         #   Column  Dtype
        ---  ------  -----
         0   date    datetime64[ns]
         1   ticker  object
         2   aret    float64

        where:

        - `date` is the return date,
        - `ticker` is the stock ticker,
        - `aret` is the abnormal return for each ticker–date, computed
          as the individual stock return minus the market return.

    Returns
    -------
    series
        A Series indexed by date, where each value is the return on an
        equal-weighted portfolio that buys the target and sells the market
        for up to 30 calendar days following the announcement.
    """
    idx_cols = ['date', 'ticker']

    rets = stk_arets.set_index(idx_cols)

    events = expanded_ma_info.loc[:, [idx_cols[0], 'tgt']]
    events.rename(columns={'tgt': idx_cols[1]}, inplace=True)
    events.set_index(idx_cols, inplace=True)
    events = events.join(rets, how='inner').reset_index()
    out = mean_by_dates(events, date_col='date', value_col='aret')
    return out.dropna().sort_index()

def mk_tgt_rets_by_event_time(
        stk_rets: pd.DataFrame,
        expanded_ma_info: pd.DataFrame,
        ):
    """
    Create a data frame of target returns indexed by event time and organised
    by deal number.

    For each deal and each valid return date in `expanded_ma_info`, this
    function computes the event time as the number of calendar days between
    the announcement date and the return date. It then extracts the target's
    stock return for that deal–date pair and stores it in a two-dimensional
    table with:

        - rows indexed by event time (e.g., 1, 2, ..., 30), and
        - columns corresponding to deal numbers.

    Parameters
    ----------
    expanded_ma_info : frame
        A data frame containing, at minimum, the columns:

         Column         Dtype
         ------         -----
         date           datetime64[ns]
         announcement   datetime64[ns]
         dealno         int64
         acq            object
         tgt            object

        where:

        - `acq` is the acquirer ticker,
        - `tgt` is the target ticker,
        - `date` includes all valid return dates from 1 to 30 days
          after the announcement.

        All tickers are normalised using `helpers.fmt_tic`.

    stk_rets : frame
        A data frame containing daily stock returns from `ma_rets.csv`.
        This is the output of `helpers.read_stk_rets`. Columns are tickers and the
        index is the return date.

    Returns
    -------
    frame
        A data frame whose index is event time (integers) and whose columns
        are deal numbers. Entry `(t, d)` contains the target return for
        deal `d` at event time `t`. Missing returns are represented as NaN.
    """
    df = expanded_ma_info.copy()
    df.loc[:, 'event_time'] = (df.date - df.announcement).dt.days
    values = df.event_time.unique()
    deals = expanded_ma_info.dealno.unique()
    out = pd.DataFrame(None, index=values, columns=deals)
    for _, row in df.iterrows():
        date = row['date']
        tic = row['tgt']
        if date not in stk_rets.index or tic not in stk_rets.columns:
            continue
        out.loc[row['event_time'], row['dealno']] = stk_rets.loc[date, tic]
    return out.sort_index()

def mk_prop_positive_tgt_rets(
        tgt_rets_by_event_time: pd.DataFrame
        ):
    """
    Compute the proportion of deals with positive target returns at each
    event time.

    Parameters
    ----------
    tgt_rets_by_event_time : frame
        A data frame whose index is event time and whose columns are
        deal numbers. Each cell represents the target's return for that
        deal at that event time. This is the output of
        `mk_tgt_rets_by_event_time`.

    Returns
    -------
    series
        A Series indexed by event time. Each value represents the proportion
        of deals with a strictly positive target return at that event time.
        Missing returns are ignored when computing the proportion.
    """
    return (tgt_rets_by_event_time > 0).mean(axis=1)




