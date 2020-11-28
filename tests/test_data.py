import calendar
from datetime import date

import pandas as pd
import pytest
from rumydata import Layout
from rumydata.field import Integer, Choice, Text, Field, Currency
from rumydata.rules.cell import make_static_cell_rule

from us_birth_data import Year, Births
from us_birth_data import files
from us_birth_data.fields import targets, Target
from us_birth_data.data import hashes

gt0 = make_static_cell_rule(
    lambda x: int(x) > 0, 'greater than 0'
)
after1968 = make_static_cell_rule(
    lambda x: int(x) >= 1968, '1968 is earliest available data'
)
no_future = make_static_cell_rule(
    lambda x: int(x) <= date.today().year,
    'must be past or present year'
)
can_truncate_to_int = make_static_cell_rule(
    lambda x: int(float(x)) == float(x),
    'must be a integer without decimal'
)

layout = Layout({
    'year': Integer(4, 4, rules=[after1968, no_future]),
    'month': Choice([x for x in calendar.month_name if x]),
    'day_of_week': Choice(list(calendar.day_name), nullable=True),
    'state': Text(20, nullable=True),
    'delivery_method': Choice(['Vaginal', 'Cesarean'], nullable=True),
    'sex_of_child': Choice(['Male', 'Female']),
    'birth_facility': Choice(['In Hospital', 'Not in Hospital'], nullable=True),
    'parity': Currency(3, nullable=True),
    'age_of_mother': Field(nullable=True, rules=[can_truncate_to_int]),
    'births': Integer(6, rules=[gt0])
})


@pytest.fixture(scope='session')
def annual_data():
    yield Year.load_data()


@pytest.mark.parametrize('target', targets)
def test_parquet_data(target: Target):
    values = target.load_data()[target.name()].unique().tolist()
    values = ['' if pd.isna(x) else str(x) for x in values]
    for value in values:
        assert not layout.layout[target.name()].check_cell(value)


@pytest.mark.parametrize('year', files.YearData.__subclasses__())
def test_year_counts(year, annual_data):
    data_count = annual_data[annual_data[Year.name()] == year.year][Births.name()].values[0]
    assert data_count == year.births


def test_total_count(annual_data):
    year_sum = sum([x.births for x in files.YearData.__subclasses__()])
    data_sum = annual_data[Births.name()].sum()
    assert year_sum == data_sum


def test_hashes():
    assert isinstance(hashes, dict)
