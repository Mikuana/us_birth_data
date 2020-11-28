"""
US Birth Data

This package simplifies the analysis of official birth records maintained by the
`National Vital Statistics System <https://www.cdc.gov/nchs/nvss/births.htm>`_ (NVSS).
It does this by aggregating a limited set of common attributes across all years
that the data are available, then storing the resulting data set in the highly
compressed [parquet](https://parquet.apache.org/) format, which is small enough
that it can be included as part of this package.

"""

from us_birth_data.fields import (
    Year, Month, DayOfWeek, State, DeliveryMethod, SexOfChild, BirthFacility,
    AgeOfMother, Parity, Births, Target
)
from us_birth_data.final import load_full_data, download_full_data

__version__ = '0.1.3'

__all__ = [
    'Year', 'Month', 'DayOfWeek', 'State', 'DeliveryMethod',
    'SexOfChild', 'BirthFacility', 'AgeOfMother', 'Parity', 'Births',
    'load_full_data', 'download_full_data'
]
