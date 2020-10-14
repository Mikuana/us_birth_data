from pathlib import Path

import pandas as pd


def small(columns=None, years=None):
    p = Path(Path(__file__).parent, 'small.parquet')
    return pd.read_parquet(p.as_posix(), columns=columns)
