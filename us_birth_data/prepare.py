"""
Data Set Preparation

This module contains functions which are used in the preparation of data sets
for this package.
"""

import gzip
import json
import shutil
import subprocess
from ftplib import FTP
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import List

import numpy as np
import pandas as pd
from tqdm import tqdm

from us_birth_data import fields
from us_birth_data.data import folder, full_data, gzip_data
from us_birth_data.files import YearData

gzip_path = Path('gz')


class FtpGet:
    """
    FTP File Retriever

    Context manager class to handle the connection to Vital Statistics FTP servers,
    list available data sets, and download.
    """

    host = 'ftp.cdc.gov'
    data_set_path = '/pub/Health_Statistics/NCHS/Datasets/DVS/natality'

    def __init__(self):
        self.ftp = FTP(self.host)
        self.ftp.login()

    def __enter__(self):
        self.ftp.login()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.ftp.close()

    def list_data_sets(self):
        """
        List Data Sets

        A convenience wrapper to display the list of available data sets for
        download.
        """
        self.ftp.cwd(self.data_set_path)
        return self.ftp.nlst()

    def get_data_set(self, file_name, destination: Path):
        """
        Get Data Set

        Download a file from FTP server, providing progress bar
        :param file_name: the name of the file to download
        :param destination: the destination of the file, as a pathlib.Path
        """
        p = Path(destination, file_name)
        self.ftp.cwd(self.data_set_path)
        total = self.ftp.size(file_name)

        print(f"Starting download of {file_name}")
        with p.open('wb') as f:
            with tqdm(total=total) as progress_bar:
                def cb(chunk):
                    data_length = len(chunk)
                    progress_bar.update(data_length)
                    f.write(chunk)

                self.ftp.retrbinary(f'RETR {file_name}', cb)


def zip_convert(zip_file: Path):
    """
    Unzip file, recompress pub file as gz

    Requires 7zip to be installed so that it can be called as `7z` by a subprocess.
    This process discards all but the largest file in the zip archive (if there
    are more than one).

    Note: we can't use the built-in unzip package in python as some of the files
    we need to inflate are compressed using algorithms which python is not licensed
    to use.

    :param zip_file: file to be converted into a Gzip.
    """
    print(f"Convert to gzip: {zip_file}")
    with TemporaryDirectory() as td:
        subprocess.check_output(['7z', 'x', zip_file, '-o' + Path(td).as_posix()])

        sizes = [(fp.stat().st_size, fp) for fp in Path(td).rglob('*') if fp.is_file()]
        sizes.sort(reverse=True)

        with sizes[0][1].open('rb') as f_in:  # assume largest file is actual data
            with gzip.open(Path(gzip_path, zip_file.stem + sizes[0][1].suffix + '.gz'), 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)

    zip_file.unlink()


def stage_gzip(file_name):
    """
    Stage FTP Data Set as Gzip

    A convenience wrapper to obtain a single year file archive from the FTP server,
    decompress the data, then recompress as Gzip and place in a local cache.

    :param file_name: the name of the data set archive on the FTP server
    """
    with TemporaryDirectory() as td:
        with FtpGet() as ftp:
            file_path = Path(td, file_name)
            ftp.get_data_set(file_name, file_path.parent)
        zip_convert(file_path)


def generate_ftp_queue() -> List[str]:
    """
    Generate FTP Queue

    Compare the cache of Gzip data sets to those available on the FTP server,
    and create a list of files that are missing from the local.

    :return: a list of data set files that need to be downloaded from the FTP
        server.
    """
    queue = []
    with FtpGet() as ftp:
        available = ftp.list_data_sets()

    existing = [x.stem for x in gzip_path.iterdir() if x.is_file()]
    for data_set in available:
        if not any([x.startswith(Path(data_set).stem) for x in existing]):
            queue.append(data_set)
    return queue


def reduce(year_from=1968, year_to=9999, sample_size=0) -> pd.DataFrame:
    """
    Data Set Reduction

    Iterate through files and fields defined in the package to extract specified
    data from the fixed width files store in the local Gzip cache, and aggregate
    the results to reduce the size of the final DataFrame.

    While this process is CPU intensive, it has a reasonable impact on memory
    due to the fact that Gzip files can be inflated in blocks. This eliminates
    the need to inflate the entire file either in memory or on disk.

    :param year_from: the earliest year that you want to include in the reduction.
        By default, starts at the earliest available year.
    :param year_to: the latest year that you want to include in the reduction.
        By default, this value will include all future years of data.
    :param sample_size: the number of records that you want to sample from each
        annual file before moving on to the next. This is extremely useful when
        developing and testing new field mappings. By default, will include all
        records from all years.

    :return: a pandas.DataFrame containing the minimum possible number of records,
        aggregated by birth counts.
    """
    tc = {x.name(): x.pd_type for x in fields.targets}
    mdf = pd.DataFrame()

    for file in YearData.__subclasses__():
        if year_from <= file.year <= year_to:

            print(f"Counting rows in {file.pub_file}")
            if sample_size:
                total = sample_size
            else:
                with gzip.open(Path(gzip_path, file.pub_file), 'rb') as r:
                    total = sum(1 for _ in r)
            print(f"{total} rows")

            fd = {x: [] for x in fields.sources}
            print(f"Extracting raw data from {file.pub_file}")
            with gzip.open(Path(gzip_path, file.pub_file), 'rb') as r:
                for ix, line in enumerate(tqdm(r, total=total)):
                    if sample_size and ix > sample_size:
                        break
                    if not line.isspace():
                        for k, v in fd.items():
                            fd[k].append(k.parse_from_row(file, line))

            new_keys = [x.name() for x in fd.keys()]
            fd = dict(zip(new_keys, fd.values()))
            df = pd.DataFrame.from_dict(fd)

            kw = dict(year=file.year)
            print(f"Reshaping {str(file.year)} data")
            for t in fields.targets:
                df[t.name()] = t.remap(df, **kw)

            df = df[list(tc.keys())]
            print(f"Grouping {str(file.year)} data")

            for col in df.dtypes:
                if isinstance(col, pd.CategoricalDtype):
                    df[col] = col.cat.add_categories('NaN').fillna('NaN')

            df = df.groupby(
                [x for x in df.columns.tolist() if x != fields.Births.name()],
                as_index=False, dropna=False
            )[fields.Births.name()].sum()

            df = df.replace('NaN', np.nan)
            mdf = df if df.empty else pd.concat([mdf, df])

    mdf = mdf.astype(tc)
    return mdf


def store_hashes(files: List[Path]):
    """
    Store File Hashes

    Since this package includes data which are not necessarily provided as part
    of the package (i.e. they require downloading from an internet source), a sha256
    hash sum is included with each file to ensure the integrity of all data. This
    function calculates these hashes, then stores them in a JSON file that is
    distributed with the package.
    :param files: the files to have their hash sums calculated
    """
    hp = Path(folder, "hashes.json")
    hash_output = {}
    for file in files:
        h = sha256()
        h.update(file.read_bytes())
        hash_output[file.name] = f"sha256::{h.hexdigest()}"

    hp.write_text(json.dumps(hash_output, indent=2))


def split_data_by_column() -> List[Path]:
    """
    Split full data into smaller sets

    Reduce the size of the overall data by limiting to just three fields and
    aggregating. This makes it possible to package a longitudinal data for every
    field in the package.

    :return: the list of files generated by the split
    """
    n = fields.Births.name()
    y = fields.Year.name()
    outputs = []
    for field in fields.targets:
        f = field.name()
        columns = [y, f, n] if y != f else [y, n]
        df = pd.read_parquet(full_data, columns=columns)
        if isinstance(df[f].dtypes, pd.CategoricalDtype):
            df[f] = df[f].cat.add_categories('NaN').fillna('NaN')

        df = df.groupby(by=[y, f] if y != f else y, dropna=False, as_index=False, observed=True).sum()
        df = df.replace('NaN', np.nan)
        p = Path(folder, f"{f}.parquet")
        df.to_parquet(p)
        outputs.append(p)
    return outputs


def prepare_data(**kwargs):
    """
    Prepare Package Data

    Performs the complete set of actions necessary to process data for use in
    this package. Will download all available data sets from FTP server, will
    recompress the data as gzip, will remap and reduce the resulting data sets,
    break into a collection of smaller cardinality tables, then store a set of
    hashes.
    """
    gzip_path.mkdir(exist_ok=True)
    for q in generate_ftp_queue():
        stage_gzip(q)

    reduce_kwargs = {x: kwargs.pop(x, None) for x in ['sample_size']}
    reduce(**reduce_kwargs).to_parquet(full_data)

    with gzip.open(gzip_data, 'wb') as f:
        f.write(full_data.read_bytes())

    files = split_data_by_column() + [full_data, gzip_data]
    store_hashes(files)
