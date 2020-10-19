US Birth Data
===========================

This package simplifies the analysis of official birth records maintained by the
[National Vital Statistics System](https://www.cdc.gov/nchs/nvss/births.htm) (NVSS).
It does this by aggregating a limited set of common attributes across all years
that the data are available, then storing the resulting data set in the highly
compressed [parquet](https://parquet.apache.org/) format, which is small enough
that it can be included as part of this package.


Installation
############


The recommended method to install is via pip. This package requires python
version 3.8 or higher.::

    pip install us_birth_data


Use
###

The most straightforward way to use these data is to load them from the package
with the `load_data` method. This returns a `pandas.DataFrame` object. ::

    >>> import us_birth_data as usb
    >>> usb.load_data()

        year      month day_of_week    state  births
    0   1968      April         NaN  Alabama    4838
    1   1968     August         NaN  Alabama    5754
    2   1968   December         NaN  Alabama    5490
    3   1968   February         NaN  Alabama    4916
    4   1968    January         NaN  Alabama    5172
    ..   ...        ...         ...      ...     ...
    79  2015  September     Saturday      NaN   36236
    80  2015  September      Sunday      NaN   31619
    81  2015  September    Thursday      NaN   53171
    82  2015  September     Tuesday      NaN   65511
    83  2015  September   Wednesday      NaN   64926
    [442944 rows x 5 columns]


More targeted use of the data would be to load only the columns that are needed.
This can be accomplished by providing one or more `Column` objects during the
call to load data. This takes advantage of the fact that the parquet file format
is a columnar store, and by choosing a subset of columns, we can improve performance
of the load by skipping the unwanted columns during reading. ::

    >>> usb.load_data(usb.Year)

        year   births
    0   1968  3501564
    1   1969  3599036
    2   1970  3734914
    3   1971  3563126
    ..   ...      ...
    44  2012  3960796
    45  2013  3940764
    46  2014  3998175
    47  2015  3988733

    >>> usb.load_data([usb.Year, usb.Month])

         year      month  births
    0    1968    January  277404
    1    1968   February  266082
    2    1968      March  282152
    3    1968      April  273564
    4    1968        May  288468
    ..    ...        ...     ...
    571  2015     August  352782
    572  2015  September  348479
    573  2015    October  339904
    574  2015   November  319605
    575  2015   December  336576
    [576 rows x 3 columns]

Objects
#######

.. automodule:: us_birth_data
    :members:
    :show-inheritance:


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
