import calendar
from datetime import date

import pytest
from rumydata import Layout, ParquetFile
from rumydata.field import Integer, Choice, Text
from rumydata.rules.cell import make_static_cell_rule

from us_birth_data.data import data_path

gt0 = make_static_cell_rule(lambda x: int(x) > 0, 'greater than 0')
after1968 = make_static_cell_rule(lambda x: int(x) >= 1968, '1968 is earliest available data')
no_future = make_static_cell_rule(lambda x: int(x) <= date.today().year, 'must be past or present year')


@pytest.mark.slow
def test_parquet_data():
    lay = Layout({
        'year': Integer(4, 4, rules=[after1968, no_future]),
        'month': Choice([x for x in calendar.month_name if x]),
        'day_of_week': Choice(list(calendar.day_name), nullable=True),
        'state': Text(20, nullable=True),
        'births': Integer(6, rules=[gt0])
    })
    assert not ParquetFile(lay, max_errors=0).check(data_path)
