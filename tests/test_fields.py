import pytest

from us_birth_data import fields
from us_birth_data._utils import _recurse_subclasses
from us_birth_data.files import YearData

original_columns = _recurse_subclasses(fields.Source)
original_columns = [x for x in original_columns if x != fields._UmeColumn]


class Xyz(fields.Source):
    handler = fields.Handlers.integer
    positions = {YearData: (1, 2)}
    na_value = 9
    labels = {1: 'x', 99: 'Unknown'}


@pytest.mark.parametrize('raw,processed', [
    (b'01', 1),
    (b'1', 1)
])
def test_handler_integer(raw, processed):
    assert fields.Handlers.integer(raw) == processed


@pytest.mark.parametrize('raw,processed', [
    (b'01', '01'),
    (b'1', '1'),
    (b' ', ' ')
])
def test_handler_character(raw, processed):
    assert fields.Handlers.character(raw) == processed


def test_snake_name():
    assert fields.Column.name() == 'column'
    assert fields.Source.name() == 'source'


def test_position_map():
    assert Xyz.position(YearData) == (1, 2)


def test_decode():
    assert Xyz.decode(1) == 'x'
    assert Xyz.decode(9) is None
    assert Xyz.decode(99) == 'Unknown'


def test_parse_from_row():
    assert Xyz.parse_from_row(YearData, '0123456789') == 'x'


@pytest.mark.parametrize('column', original_columns)
def test_positions_map(column):
    """ All original columns need to map positions to years """
    assert all([issubclass(k, YearData) for k in column.positions.keys()])


@pytest.mark.parametrize('column', original_columns)
def test_positions_range(column):
    """ All original columns need to map positions to years """
    for v in column.positions.values():
        assert isinstance(v, tuple)
        assert len(v) == 2
        assert v[0] <= v[1]


@pytest.mark.parametrize('column', original_columns)
def test_contiguous_spans(column):
    actual = sorted([y.year for y in column.positions])
    expected = list(range(min(actual), max(actual) + 1))
    assert actual == expected
