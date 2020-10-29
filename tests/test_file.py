import re
from datetime import date
from pathlib import Path

import pandas as pd
import pytest

from us_birth_data import files

years = files.YearData.__subclasses__()


@pytest.fixture
def pub_file_pat():
    yield re.compile(r'Nat\d{4}(us|US)?\..*gz')


@pytest.mark.parametrize('year', years)
def test_valid_year(year):
    assert 1968 <= year.year <= date.today().year


@pytest.mark.parametrize('year', years)
def test_valid_pub_file(year, pub_file_pat):
    assert pub_file_pat.fullmatch(year.pub_file)


@pytest.mark.parametrize('year', years)
def test_births_total(year):
    assert year.births > 0


@pytest.mark.parametrize('year', years)
def test_unique_year(year):
    fys = [x.year for x in years]
    assert fys.count(year.year) == 1, "year is not unique"


@pytest.mark.parametrize('year', years)
def test_file_year_match(year):
    assert year.pub_file[:7].endswith(str(year.year)), 'file name year does not match'


def test_year_read(tmpdir):
    import os
    os.chdir(tmpdir)
    os.mkdir('pq')
    pd.DataFrame({'c1': []}).to_parquet(Path(tmpdir, 'pq', 'YearData.parquet'))
    assert isinstance(files.YearData.read_parquet(), pd.DataFrame)
