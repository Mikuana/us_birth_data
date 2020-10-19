from pathlib import Path
from typing import List, Tuple

import pandas as pd

from us_birth_data.fields import Column, Births


def load_data(columns: Tuple[Column, List[Column]] = None) -> pd.DataFrame:
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
    p = Path(Path(__file__).parent, 'us_birth_data.parquet')
    if columns:  # add birth count if not already present
        if isinstance(columns, Column):
            columns = [columns]
        columns = [c.name() for c in columns]
        if n not in columns:
            columns += [n]

        df = pd.read_parquet(p.as_posix(), columns=columns)
        df = df.groupby([x for x in df.columns.to_list() if x != n], as_index=False)[n].sum()
    else:
        df = pd.read_parquet(p.as_posix())

    return df
