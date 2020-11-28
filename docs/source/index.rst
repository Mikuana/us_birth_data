US Birth Data
===========================

This package simplifies the analysis of official birth records maintained by the
`National Vital Statistics System <https://www.cdc.gov/nchs/nvss/births.htm>`_ (NVSS).
It does this by aggregating a limited set of common attributes across all years
that the data are available, then storing the resulting data set in the highly
compressed `parquet <https://parquet.apache.org/>`_ format, which is small enough
that it can be included as part of this package.


Installation
############


The recommended method to install is via pip. This package requires python
version 3.8 or higher.::

    pip install us_birth_data



Use the `download_full_data` command after installation to obtain the data from
the GitHub repo where the source code is hosted.::

    from us_birth_data import download_full_data
    download_full_data()


Use
###

The most straightforward way to use these data is to load them from the package
with the `load_data` method. This returns a `pandas.DataFrame` object. ::

    >>> import us_birth_data as usb
    >>> usb.load_data()

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

Definitions
###########

.. automodule:: us_birth_data
    :members:
    :show-inheritance:


Why
###

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


Resources
#########

The links below provide reference to useful resources when working with NVSS birth
data.

 - `National Center for Health Statistics Vital Statistics Online <https://www.cdc.gov/nchs/data_access/vitalstatsonline.htm>`_
 - `National Bureau of Economic Research <http://data.nber.org/data/vital-statistics-natality-data.html>`_
 - `Vital Statistics <https://github.com/Mikuana/vitalstatistics>`_ an R project precursor to this python package

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
