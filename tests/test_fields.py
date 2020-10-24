import pytest

from tests.utils import recurse_subclasses
from us_birth_data import fields
from us_birth_data.files import YearData

original_columns = recurse_subclasses(fields.OriginalColumn)


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
    class Xyz(fields.OriginalColumn):
        positions = {YearData: (0, 1)}

    assert Xyz.position(YearData) == (0, 1)


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
