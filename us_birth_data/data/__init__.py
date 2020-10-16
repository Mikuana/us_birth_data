import re
from pathlib import Path
from typing import List

import pandas as pd


class Column:
    @classmethod
    def name(cls):
        return re.sub(r'(?<!^)(?=[A-Z])', '_', cls.__name__).lower()


class Year(Column):
    """ Birth Year """

    type = 'uint16'


class Month(Column):
    """ Birth Month"""

    type = 'uint8'


class DayOfWeek(Column):
    """ Birth Day of Week """

    type = pd.api.types.CategoricalDtype(
        categories=['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'],
        ordered=True
    )


class State(Column):
    """ State of Occurrence """

    type = 'category'


class Births(Column):
    """ Record Weight """

    type = 'uint32'


def get_data(columns: List[Column] = None):
    n = Births.name()
    p = Path(Path(__file__).parent, 'usb.parquet')
    if columns:  # derive column names and add record weight if not already present
        columns = [c.name() for c in columns]
        if n not in columns:
            columns += [n]

    df = pd.read_parquet(p.as_posix(), columns=columns)
    df = df.groupby([x for x in df.columns.tolist() if x != n], as_index=False)[n].sum()
    return df


if __name__ == '__main__':
    print(get_data())
