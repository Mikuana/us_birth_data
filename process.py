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
    for file in files.PubFile.__subclasses__():
        field_dict = {x: [] for x in field_list}
        with gzip.GzipFile(Path(gzip_path, file.file_name)) as r:
            print(f"Counting rows in {file.file_name}")
            total = sum(1 for _ in r)
            print(f"{total} rows")

        with gzip.GzipFile(Path(gzip_path, file.file_name)) as r:
            for line in tqdm(r, total=total):
                if not line.isspace():
                    for k, v in field_dict.items():
                        field_dict[k].append(k.parse_from_row(file, line))

        new_keys = [x.__name__ for x in field_dict.keys()]
        df = pd.DataFrame.from_dict(
            dict(zip(new_keys, field_dict.values())),
            dtype="category"
        )
        df.to_parquet(Path(pq_path, f"{file.__name__}.parquet"))


if __name__ == '__main__':
    extract_fields()
