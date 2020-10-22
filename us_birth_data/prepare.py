import gzip
import shutil
import subprocess
from ftplib import FTP
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import List

import pandas as pd
from tqdm import tqdm

from us_birth_data import fields, files
from us_birth_data.files import YearData

gzip_path = Path('gz')
pq_path = Path('pq')


class FtpGet:
    """ Context manager class to handle the download of data set archives and documentation """
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

    def get_file(self, file_name, destination: Path):
        p = Path(destination, file_name)
        total = self.ftp.size(file_name)

        print(f"Starting download of {file_name}")
        with p.open('wb') as f:
            with tqdm(total=total) as progress_bar:
                def cb(chunk):
                    data_length = len(chunk)
                    progress_bar.update(data_length)
                    f.write(chunk)

                self.ftp.retrbinary(f'RETR {file_name}', cb)
        return p

    def list_data_sets(self):
        self.ftp.cwd(self.data_set_path)
        return self.ftp.nlst()

    def get_data_set(self, file_name, destination: Path):
        self.ftp.cwd(self.data_set_path)
        self.get_file(file_name, destination)


def zip_convert(zip_file):
    """
    Unzip file, recompress pub file as gz

    Requires 7zip to be installed so that it can be called as `7z` by a subprocess.

    Note: we can't use the built-in unzip package in python as some of the files
    we need to inflate are compressed using algorithms which python is not licensed
    to use.
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
    with TemporaryDirectory() as td:
        with FtpGet() as ftp:
            file_path = Path(td, file_name)
            ftp.get_data_set(file_name, file_path.parent)
        zip_convert(file_path)


def get_queue():
    queue = []
    with FtpGet() as ftp:
        available = ftp.list_data_sets()

    existing = [x.stem for x in gzip_path.iterdir() if x.is_file()]
    for data_set in available:
        if not any([x.startswith(Path(data_set).stem) for x in existing]):
            queue.append(data_set)
    return queue


def stage_pq(year_from=1968, year_to=2019, field_list: List[fields.OriginalColumn] = None):
    default_fields = (
        fields.Births, fields.State, fields.OccurrenceState, fields.Month,
        fields.Day, fields.DayOfWeek
    )
    field_list = field_list or default_fields
    for file in files.YearData.__subclasses__():
        if year_from <= file.year <= year_to:
            with gzip.open(Path(gzip_path, file.pub_file), 'rb') as r:
                print(f"Counting rows in {file.pub_file}")
                total = sum(1 for _ in r)
                print(f"{total} rows")

            fd = {x: [] for x in field_list if x.position(file)}
            with gzip.open(Path(gzip_path, file.pub_file), 'rb') as r:
                for line in tqdm(r, total=total):
                    if not line.isspace():
                        for k, v in fd.items():
                            fd[k].append(k.parse_from_row(file, line))

            new_keys = [x.name() for x in fd.keys()]
            fd = dict(zip(new_keys, fd.values()))
            df = pd.DataFrame.from_dict(fd)

            # field additions
            df[fields.Year.name()] = file.year

            n = fields.Births.name()
            if n in df:
                df[n] = df[n].fillna(1)
            elif file.year < 1972:
                df[n] = 2
            else:
                df[n] = 1

            df = df.groupby([x for x in df.columns.tolist() if x != n], as_index=False)[n].sum()
            df.to_parquet(Path(pq_path, f"{file.__name__}.parquet"))


def concatenate_years(year_from=1968, year_to=2015, columns: list = None) -> pd.DataFrame:
    df = pd.DataFrame()
    years = YearData.__subclasses__()
    for yd in years:
        if year_from <= yd.year <= year_to:
            rd = yd.read_parquet(columns=columns)

            if fields.DayOfWeek.name() not in rd and fields.Day.name() in rd:
                rd[fields.DayOfWeek.name()] = pd.to_datetime(
                    rd[['year', 'month', 'day']], errors='coerce'
                ).dt.strftime('%A')

            df = rd if df.empty else pd.concat([df, rd])

    tc = {
        x.name(): x.pd_type for x in
        (fields.Year, fields.Month, fields.DayOfWeek, fields.State, fields.Births)
    }
    df = df.astype(tc)
    df = df[list(tc.keys())]  # reorder columns

    cat_cols = df.columns[[isinstance(x, pd.CategoricalDtype) for x in df.dtypes]]
    for cc in cat_cols:
        df[cc] = df[cc].cat.remove_unused_categories()

    return df


def generate_data_set():
    gzip_path.mkdir(exist_ok=True)
    pq_path.mkdir(exist_ok=True)

    for q in get_queue():
        stage_gzip(q)

    stage_pq()
    df = concatenate_years()
    df.to_parquet(Path(Path(__file__).parent, 'us_birth_data.parquet'))
