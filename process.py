import gzip
from pathlib import Path
from typing import List

import pandas as pd
from tqdm import tqdm

import fields
import files

gzip_path = Path('gz')
pq_path = Path('pq')


def extract_fields(field_list: List[fields.Field] = None):
    field_list = field_list or fields.Field.__subclasses__()
    for file in files.YearData.__subclasses__():
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
        df = pd.DataFrame.from_dict(fd, dtype="category")

        df['dob_year'] = file.year

        df.to_parquet(Path(pq_path, f"{file.__name__}.parquet"))


if __name__ == '__main__':
    extract_fields()
