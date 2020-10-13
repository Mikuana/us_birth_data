import pandas as pd
from typing import List
from pathlib import Path
from tqdm import tqdm
import files
import fields

import gzip

gzip_path = Path('gz')
pq_path = Path('pq')


def extract_fields(field_list: List[fields.Field]):
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
        df = pd.DataFrame.from_dict(dict(zip(new_keys, field_dict.values())))
        # df.to_parquet(pq_path.as_posix())
        return df


if __name__ == '__main__':
    df = extract_fields([fields.RECWT])
