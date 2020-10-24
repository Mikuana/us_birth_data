import pytest

from us_birth_data import fields


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
