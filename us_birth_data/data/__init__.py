import re
from pathlib import Path
from typing import List

import pandas as pd


class Column:
    @classmethod
    def name(cls):
        return re.sub(r'(?<!^)(?=[A-Z])', '_', cls.__name__).lower()


class DobYear(Column):
    """ Birth Year """

    type = 'uint16'


class DobMonth(Column):
    """ Birth Month"""

    type = 'uint8'


class DobDayOfWeek(Column):
    """ Birth Day of Week """

    type = pd.api.types.CategoricalDtype(
        categories=['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'],
        ordered=True
    )


class State(Column):
    """ State of Occurrence """

    type = 'category'


class RecordWeight(Column):
    """ Record Weight """

    type = 'uint32'


def get_data(columns: List[Column] = None):
    rw = RecordWeight.name()
    p = Path(Path(__file__).parent, 'usb.parquet')
    if columns:  # derive column names and add record weight if not already present
        columns = [c.name() for c in columns]
        if rw not in columns:
            columns += [rw]

    df = pd.read_parquet(p.as_posix(), columns=columns)

    cl = df.columns.tolist()
    cl.remove(rw)
    df = df.groupby(cl, as_index=False)[rw].sum()
    return df


if __name__ == '__main__':
    print(get_data([State]))
