from typing import List, Union

import pandas as pd

from us_birth_data.data import full_data
from us_birth_data.fields import Target


def load_full_data(columns: List[Union[str, Target]] = None, **kwargs) -> pd.DataFrame:
    """
    A convenience wrapper over the pandas.read_parquet method, to load the full
    us_birth_data set into a DataFrame. This data set is not installed with this
    package, so the first time you run this package it will prompt you to download
    it.

    :param columns: If not None, only these columns will be read from the file.
    :param kwargs: passes kwargs directly to the underlying pandas function
    :return: a pandas DataFrame
    """
    if columns:
        columns = [c.name() if issubclass(c, Target) else c for c in columns]

    assert full_data.exists(), f"File {full_data.as_posix()} does not exist. Download it."
    return pd.read_parquet(path=full_data, columns=columns, **kwargs)
