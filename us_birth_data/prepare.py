from datetime import date
import gzip
import shutil
import subprocess
from ftplib import FTP
from tempfile import TemporaryDirectory
from typing import List

import pandas as pd
from tqdm import tqdm

from us_birth_data import fields, files
from us_birth_data.files import YearData
from us_birth_data.misc import *
from us_birth_data.misc import gzip_path, pq_path


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
                def cb(data):
                    data_length = len(data)
                    progress_bar.update(data_length)
                    f.write(data)

                self.ftp.retrbinary(f'RETR {file_name}', cb)
        return p

    def list_data_sets(self):
        self.ftp.cwd(self.data_set_path)
        return self.ftp.nlst()

    def get_data_set(self, file_name, destination: Path):
        self.ftp.cwd(self.data_set_path)
        self.get_file(file_name, destination)


def get_data_set(file_name):
    target = Path(zip_path, file_name)
    if target.exists():
        print(f"Already exists skipping download for: {target}")
    else:
        with TemporaryDirectory() as td:
            with FtpGet() as ftp:
                file_path = Path(td, file_name)
                ftp.get_data_set(file_name, file_path.parent)
                file_path.rename(Path(zip_path, file_path.name))
    return target


def zip_convert(zip_file):
    """ Unzip file, recompress pub file as gz, then remove zip """
    print(f"Convert to gzip: {zip_file}")
    with TemporaryDirectory() as td:
        subprocess.check_output(['7z', 'x', zip_file, '-o' + Path(td).as_posix()])

        sizes = [(fp.stat().st_size, fp) for fp in Path(td).rglob('*') if fp.is_file()]
        sizes.sort(reverse=True)

        with sizes[0][1].open('rb') as f_in:  # assume largest file is actual data
            with gzip.open(Path(gzip_path, zip_file.stem + sizes[0][1].suffix + '.gz'), 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)

    zip_file.unlink()


def get_queue():
    queue = []
    with FtpGet() as ftp:
        available = ftp.list_data_sets()

    existing = [x.stem for x in gzip_path.iterdir() if x.is_file()]
    for data_set in available:
        if not any([x.startswith(Path(data_set).stem) for x in existing]):
            queue.append(data_set)
    return queue


def stage_pq(year_from=1968, year_to=2019, field_list: List[fields.BaseField] = None):
    default_fields = (
        fields.RecordWeight,
        fields.State,
        fields.OccurrenceState,
        fields.DobMonth,
        fields.DobDayOfMonth,
        fields.DobDayOfWeek
    )
    field_list = field_list or default_fields
    for file in files.YearData.__subclasses__():
        if year_from <= file.year <= year_to:
            with gzip.GzipFile(Path(gzip_path, file.pub_file)) as r:
                print(f"Counting rows in {file.pub_file}")
                total = sum(1 for _ in r)
                print(f"{total} rows")

            fd = {x: [] for x in field_list if x.position(file)}
            with gzip.GzipFile(Path(gzip_path, file.pub_file)) as r:
                for line in tqdm(r, total=total):
                    if not line.isspace():
                        for k, v in fd.items():
                            fd[k].append(k.parse_from_row(file, line))

            new_keys = [x.field_name for x in fd.keys()]
            fd = dict(zip(new_keys, fd.values()))
            df = pd.DataFrame.from_dict(fd)

            # field additions
            df['dob_year'] = file.year

            if 'record_weight' in df:
                df['record_weight'] = df['record_weight'].fillna(1)
            elif file.year < 1972:
                df['record_weight'] = 2
            else:
                df['record_weight'] = 1

            cl = df.columns.tolist()
            cl.remove('record_weight')
            df = df.groupby(cl, as_index=False)['record_weight'].sum()

            df.to_parquet(Path(pq_path, f"{file.__name__}.parquet"))


def get_years(year_from=1968, year_to=2019, columns: list = None):
    df = pd.DataFrame()
    years = YearData.__subclasses__()
    for yd in years:
        if year_from <= yd.year <= year_to:
            rd = yd.read_parquet(columns=columns)

            if 'dob_day_of_week' not in rd and 'dob_day_of_month' in rd:
                rdt = rd[['dob_year', 'dob_month', 'dob_day_of_month']]
                rdt.columns = ['year', 'month', 'day']
                rd['dob_day_of_week'] = pd.to_datetime(rdt, errors='coerce').dt.strftime('%A')

            df = rd if df.empty else pd.concat([df, rd])

    # weekday ordering
    weekday_type = pd.api.types.CategoricalDtype(
        categories=['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'],
        ordered=True
    )

    # type casting
    tc = {
        'dob_year': 'uint16',
        'dob_month': 'uint8',
        'dob_day_of_week': weekday_type,
        'state': 'category',
        'record_weight': 'uint32'
    }
    df = df.astype(tc)
    df = df[list(tc.keys())]
    return df


if __name__ == '__main__':
    # zip_path.mkdir(exist_ok=True)
    # gzip_path.mkdir(exist_ok=True)
    #
    # for q in get_queue():
    #     zf = get_data_set(q)
    #     zip_convert(zf)

    stage_pq(2003, 2004)

    dfx = get_years()
    print(dfx)
    dfx.to_parquet('us_birth_data/data/usb.parquet')
