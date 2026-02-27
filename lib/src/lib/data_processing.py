import pandas as pd


def map_values(data: pd.Series | pd.DataFrame, mapping: dict, column=None) -> pd.Series | pd.DataFrame:
    data_mapped = data.copy()
    if column is not None:
        data_mapped[column] = data_mapped[column].replace(mapping)
    else:
        data_mapped = data_mapped.replace(mapping)
    return data_mapped


def map_index(data: pd.Series | pd.DataFrame, mapping: dict, axis=1) -> pd.Series | pd.DataFrame:
    data_mapped = data.copy()
    if axis == 1:
        data_mapped = data_mapped.rename(columns=mapping)
    elif axis == 0:
        data_mapped = data_mapped.rename(index=mapping)
    return data_mapped


def df_equals(df, column, equals):
    print("Deprecated. Use filter_df instead")
    return df.loc[df[column] == equals]


def df_isin(df, column, isin):
    print("Deprecated. Use filter_df instead")
    return df.loc[df[column].isin(isin)]


def filter_df(
    df: pd.DataFrame, filter: dict[str, str | list[str]], invert: bool = False
) -> pd.DataFrame:
    result = df.copy()
    for column, value in filter.items():
        result = filter_df_column(result, column, value, invert=invert)
    return result


def filter_df_column(
    df: pd.DataFrame, column: str, value: str | list[str], invert: bool = False
) -> pd.DataFrame:
    if isinstance(value, str):
        value = [value]
    where = df[column].isin(value)
    if invert:
        where = ~where
    return df.loc[where]


def filter_by_group(df, df_groups):
    merge_on = df_groups.columns.to_list()
    df_filtered = pd.merge(df, df_groups, on=merge_on)
    return df_filtered


def aggregate_by_groups(df, var_name, groups, rename=False):
    """Aggregate the dataframe `df` by the groups in `groups`.

    Parameters
    ----------
    df : pd.DataFrame
        Tidy DataFrame to aggregate.
    var_name : str
        Name of the variable to aggregate. All other columns are used as groupby.
    groups : pd.DataFrame
        Tidy DataFrame with two columns, providing the aggregation groups.
    rename : bool, optional
        Whether to rename the first column of `groups` to the second, by default False.

    Returns
    -------
    pd.DataFrame
        Aggregated DataFrame, with the first column of `groups` replaced by the second.
    """
    fine = groups.columns[0]
    coarse = groups.columns[1]
    merged = pd.merge(df, groups, on=fine, sort=False)

    groupby = df.columns.tolist()
    groupby = [item if item != fine else coarse for item in groupby]
    groupby.remove(var_name)

    aggregated = merged.drop(columns=fine).groupby(groupby, sort=False).sum().reset_index()

    if rename:
        aggregated = aggregated.rename(columns={coarse: fine})

    return aggregated


def aggregate_by_column(
    df: pd.DataFrame, col_agg: str | list[str], var_name: str | list[str]
) -> pd.DataFrame:
    """Aggregate the dataframe `df` by summing over `col_agg`. The columns
    indicated by `col_values` will be summed. All other columns will be grouped by.

    Parameters
    ----------
    df : pd.DataFrame
        Tidy DataFrame to aggregate.
    col_agg : str|list[str]
        Name of the variable to aggregate. All other columns are used as groupby.
    var_name : str|list[str]
        Name(s) of the variable to aggregate. All other columns are used as groupby.

    Returns
    -------
    pd.DataFrame
        Aggregated DataFrame, with the first column of `groups` replaced by the second.
    """
    groupby = list(df.columns)
    _drop_from_list(groupby, col_agg)
    _drop_from_list(groupby, var_name)

    result = df.drop(columns=col_agg).groupby(groupby, sort=False).sum().reset_index()

    return result


def rename_aggregate_by_label(
    df: pd.DataFrame,
    column,
    labels: str | list[str],
    new_label: str,
    var_name: str | list[str],
) -> pd.DataFrame:
    groupby = list(df.columns)
    _drop_from_list(groupby, var_name)

    return (
        df.replace({t: new_label for t in labels}).groupby(groupby, sort=False).sum().reset_index()
    )


def drop_duplicates(df, ignore, var_name):
    check_duplicates = list(df.columns)
    _drop_from_list(check_duplicates, ignore)
    _drop_from_list(check_duplicates, var_name)

    return df.loc[~df[check_duplicates].duplicated(keep="first")]


def _drop_from_list(some_list: list, drop: object | list[object]):
    if not isinstance(drop, list):
        drop = [drop]
    for item in drop:
        some_list.remove(item)


def get_sort_key_callable(order: list):
    dict_order = dict(enumerate(order))
    dict_order = {value: key for key, value in dict_order.items()}
    return lambda x: x.map(dict_order)
