from pathlib import Path
from typing import List, Union

import pandas as pd

from us_birth_data.fields import Column, Births, targets

data_folder = Path(__file__).parent
full_data_path = Path(data_folder, 'us_birth_data.parquet')


def load_data(columns: Union[Column, List[Column]] = None) -> pd.DataFrame:
    """
    Load Birth Data

    Will read the parquet file that is included with this package and return it
    as a DataFrame, using the pandas package. Always includes the "births" column.

    :param columns: (optional) one or more Column objects. Will subset the
        return to just the specified columns, along with the Births column. This
        improves the load time and reduces memory requirement as unused columns
        can be skipped during read.
    :return: a pandas.DataFrame containing birth data
    """
    n = Births.name()
    if columns:  # add birth count if not already present
        if not isinstance(columns, list):
            columns = [columns]
        columns = [c.name() for c in columns]
        if n not in columns:
            columns += [n]

        df = pd.read_parquet(data_path.as_posix(), columns=columns)
        cl = [x for x in df.columns.to_list() if x != n]

        cat_cols = df.columns[[isinstance(x, pd.CategoricalDtype) for x in df.dtypes]]
        for cc in cat_cols:
            df[cc] = df[cc].astype(str)

        df = df.groupby(by=cl, dropna=False, as_index=False).sum()
        df = df.astype({x.name(): x.pd_type for x in targets if x in cl})
    else:
        df = pd.read_parquet(data_path.as_posix())

    return df
