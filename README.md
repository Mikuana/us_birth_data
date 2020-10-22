# US Birth Data

[![PyPI](https://img.shields.io/pypi/v/us_birth_data)](https://pypi.org/project/us_birth_data/)
[![Documentation Status](https://readthedocs.org/projects/us_birth_data/badge/?version=latest)](https://us_birth_data.readthedocs.io/en/latest/?badge=latest)
[![codecov](https://codecov.io/gh/Mikuana/us_birth_data/branch/main/graph/badge.svg)](https://codecov.io/gh/Mikuana/us_birth_data)

This package simplifies the analysis of official birth records maintained by the
[National Vital Statistics System](https://www.cdc.gov/nchs/nvss/births.htm) (NVSS).
It does this by aggregating a limited set of common attributes across all years
that the data are available, then storing the resulting data set in the highly
compressed [parquet](https://parquet.apache.org/) format, which is small enough
that it can be included as part of this package.

# Install

The recommended method to install is via pip. This package requires python
version 3.8 or higher.

```
pip install us_birth_data
```

# Use

```python
import us_birth_data as usb
df = usb.load_data()
print(df)
```

```
    year      month day_of_week    state  births
0   1968      April         NaN  Alabama    4838
1   1968     August         NaN  Alabama    5754
2   1968   December         NaN  Alabama    5490
3   1968   February         NaN  Alabama    4916
4   1968    January         NaN  Alabama    5172
..   ...        ...         ...      ...     ...
79  2015  September    Saturday      NaN   36236
80  2015  September      Sunday      NaN   31619
81  2015  September    Thursday      NaN   53171
82  2015  September     Tuesday      NaN   65511
83  2015  September   Wednesday      NaN   64926
[442944 rows x 5 columns]
```

# Documentation

Please see the full documentation at [readthedocs](https://us_birth_data.readthedocs.io/).

# Why

The birth records are quite comprehensive, and go back to 1968. However, longitudinal
analysis of these records is challenging. The data sets have gone through numerous
schema changes over the decades. Some information that used to be available is no
longer included in the public data sets (e.g. state of occurrence), some new information
has been added (e.g delivery method), and many of the fields have undergone transformations
over time (e.g. place of delivery used to include "En route or born on arrival (BOA)",
but this value was dropped from the records in 1988). None of this is terribly
problematic when analysis is performed on only one or two years of records, but
spanning the entire length of these data sets requires complex processing.

The raw birth certificate data exceed 5 GB when _compressed_. Simultaneous
decompression of these data is problematic on the typical workstation, and even after
aggressive pruning of columns, loading hundreds of millions of records directly
into memory will overflow most workstations.

This issue is solved via a multi-step data processing pipeline that incrementally
decompresses the raw birth record data, prunes columns, and then reduces rows through
aggregation of grouped records. The years are then combined, with additional logic
to map similar attributes to consistent values over time. The result is a data set
which can easily be shared, but still rich enough to perform meaningful analysis.

Most attributes of the birth data are excluded. If you need additional detail, you
can use this package to generate your own data sets.
