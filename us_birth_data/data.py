from pathlib import Path
from typing import List

import pandas as pd

from us_birth_data.fields import Column, Year, Month, DayOfWeek, State, Births


def get_data(columns: List[Column] = None):
    """ This has a doc string now """
    n = Births.name()
    p = Path(Path(__file__).parent, 'us_birth_data.parquet')
    if columns:  # add birth count if not already present
        columns = [c.name() for c in columns]
        if n not in columns:
            columns += [n]

        df = pd.read_parquet(p.as_posix(), columns=columns)
        df = df.groupby([x for x in df.columns.to_list() if x != n], as_index=False)[n].sum()
    else:
        df = pd.read_parquet(p.as_posix())

    return df
