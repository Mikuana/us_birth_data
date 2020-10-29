import calendar
from datetime import date

import pytest
from rumydata import Layout, ParquetFile
from rumydata.field import Integer, Choice, Text, Field
from rumydata.rules.cell import make_static_cell_rule

from us_birth_data import Year, Month, DayOfWeek, State, Births
from us_birth_data import files
from us_birth_data.data import data_path, load_data

gt0 = make_static_cell_rule(lambda x: int(x) > 0, 'greater than 0')
after1968 = make_static_cell_rule(lambda x: int(x) >= 1968, '1968 is earliest available data')
no_future = make_static_cell_rule(lambda x: int(x) <= date.today().year, 'must be past or present year')
can_truncate_to_int = make_static_cell_rule(lambda x: int(float(x)) == float(x), 'must be a integer without decimal')


@pytest.fixture
def loaded_data():
    yield load_data()


@pytest.mark.slow
def test_parquet_data():
    lay = Layout({
        'year': Integer(4, 4, rules=[after1968, no_future]),
        'month': Choice([x for x in calendar.month_name if x]),
        'day_of_week': Choice(list(calendar.day_name), nullable=True),
        'state': Text(20, nullable=True),
        'delivery_method': Choice(['Vaginal', 'Cesarean'], nullable=True),
        'sex_of_child': Choice(['Male', 'Female']),
        'birth_facility': Choice(['In Hospital', 'Not in Hospital'], nullable=True),
        'age_of_mother': Field(nullable=True, rules=[can_truncate_to_int]),
        'births': Integer(6, rules=[gt0])
    })
    assert not ParquetFile(lay, max_errors=0).check(data_path)


@pytest.mark.parametrize('column', [
    Year, Month, DayOfWeek, State
])
def test_single_column_grouping(column):
    df = load_data(column)
    assert df.columns.to_list() == [column.name(), Births.name()]
    assert all(df.iloc[:, 0].value_counts() == 1)


@pytest.mark.parametrize('year', files.YearData.__subclasses__())
def test_year_counts(year, loaded_data):
    assert loaded_data[loaded_data['year'] == year.year]['births'].sum() == year.births


def test_total_count(loaded_data):
    year_sum = sum([x.births for x in files.YearData.__subclasses__()])
    data_sum = loaded_data['births'].sum()
    assert year_sum == data_sum
