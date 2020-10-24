import pytest

from tests.utils import recurse_subclasses
from us_birth_data import fields
from us_birth_data.files import YearData

original_columns = recurse_subclasses(fields.OriginalColumn)


class Xyz(fields.OriginalColumn):
    handler = fields.Handlers.integer
    positions = {YearData: (1, 2)}
    na_value = 9
    labels = {1: 'x', 99: 'Unknown'}


@pytest.mark.parametrize('raw,processed', [
    ('01', 1),
    ('1', 1)
])
def test_handler_integer(raw, processed):
    assert fields.Handlers.integer(raw) == processed


@pytest.mark.parametrize('raw,processed', [
    ('01', '01'),
    ('1', '1'),
    (' ', ' ')
])
def test_handler_character(raw, processed):
    assert fields.Handlers.character(raw) == processed


def test_snake_name():
    assert fields.Column.name() == 'column'
    assert fields.OriginalColumn.name() == 'original_column'


def test_position_map():
    assert Xyz.position(YearData) == (1, 2)


def test_decode():
    assert Xyz.decode(1) == 'x'
    assert Xyz.decode(9) == 'Unknown'


def test_parse_from_row():
    assert Xyz.parse_from_row(YearData, '0123456789') == 'x'


@pytest.mark.parametrize('column', original_columns)
def test_labels(column):
    """ All encoded original columns need a way to represent unknown values """
    if column.labels:
        assert 'Unknown' in column.labels.values(), "does not have an Unknown value label"


@pytest.mark.parametrize('column', original_columns)
def test_positions_map(column):
    """ All original columns need to map positions to years """
    if column != fields.UmeColumn:
        assert all([issubclass(k, YearData) for k in column.positions.keys()])


@pytest.mark.parametrize('column', original_columns)
def test_positions_range(column):
    """ All original columns need to map positions to years """
    if column != fields.UmeColumn:
        for v in column.positions.values():
            assert isinstance(v, tuple)
            assert len(v) == 2
            assert v[0] <= v[1]
