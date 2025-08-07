import pandas as pd


def get_data_types(df) -> dict:
    """
    返回每列的数据类型
    :param df: 待判断数据类型的DataFrame
    :return: Dictionary
    """
    data_types = {}
    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            data_types[col] = 'datetime'
        elif pd.api.types.is_numeric_dtype(df[col]):
            data_types[col] = 'numeric'
        else:
            data_types[col] = 'categorical'
    return data_types