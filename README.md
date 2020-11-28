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

Due to the large size of the data set, it cannot be included as part of the pip
installation. However, this package includes a function to easily obtain the
data and make it available for use.

Use the `download_full_data` command after installation to obtain the data from
the GitHub repo where the source code is hosted.

```python
from us_birth_data import download_full_data
download_full_data()
```

# Use

```python
import us_birth_data as usb
df = usb.load_full_data()
print(df)
```

```
        year      month day_of_week  ... age_of_mother parity births
0       1968      April         NaN  ...          13.0    NaN      2
1       1968      April         NaN  ...          14.0    NaN     10
2       1968      April         NaN  ...          15.0    NaN     22
3       1968      April         NaN  ...          16.0    NaN     56
4       1968      April         NaN  ...          17.0    NaN    102
      ...        ...         ...  ...           ...    ...    ...
100279  2019  September   Wednesday  ...          27.0    3.0      1
100280  2019  September   Wednesday  ...          28.0    NaN      1
100281  2019  September   Wednesday  ...          30.0    7.0      1
100282  2019  September   Wednesday  ...          35.0    NaN      1
100283  2019  September   Wednesday  ...          36.0    NaN      1
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
