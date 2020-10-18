from pathlib import Path
from typing import List

import pandas as pd

from us_birth_data.fields import Column, Month, DayOfWeek, Births


def get_data(columns: List[Column] = None):
    n = Births.name()
    p = Path(Path(__file__).parent, 'usb.parquet')
    if columns:  # add birth count if not already present
        columns = [c.name() for c in columns]
        if n not in columns:
            columns += [n]

        df = pd.read_parquet(p.as_posix(), columns=columns)
        df = df.groupby([x for x in df.columns.to_list() if x != n], as_index=False)[n].sum()
    else:
        df = pd.read_parquet(p.as_posix())

    return df


if __name__ == '__main__':
    print(get_data([DayOfWeek]))