import gzip
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import List, Union

import pandas as pd
import requests
import semver
from tqdm import tqdm

from us_birth_data.data import full_data, gzip_data, hashes
from us_birth_data.fields import Target, Births


def load_full_data(columns: List[Union[str, Target]] = None, **kwargs) -> pd.DataFrame:
    """
    A convenience wrapper over the pandas.read_parquet method, to load the full
    us_birth_data set into a DataFrame. This data set is not installed with this
    package, so the first time you run this package it will prompt you to download
    it.

    Note: the birth count field will always be included, even if you do not
    specify it to be loaded.

    :param columns: If not None, only these columns will be read from the file.
    :param kwargs: passes kwargs directly to the underlying pandas function
    :return: a pandas DataFrame
    """
    if columns:
        columns = [c.name() if issubclass(c, Target) else c for c in columns]
        if Births.name() not in columns:
            columns.append(Births.name())

    msg = (
        f"File {full_data.as_posix()} does not exist. You can download it using"
        f" the download_full_data method included in this package."
    )
    assert full_data.exists(), msg
    return pd.read_parquet(path=full_data, columns=columns, **kwargs)


def download_full_data(destination: [Union, str] = None) -> Path:
    """
    Download Full US Birth Data

    Download complete US Birth data set from project repository. A SHA256 check
    sum is performed against the compressed and inflated files, and compared to
    the hash stored with this code, to ensure that the exact expected file is
    retrieved. Download of the initial gzip file is performed in a temporary
    directory which is discarded on success or failure of the function. 

    :param destination: (optional) path to land the file. Recommend leaving this
        blank, which will use the package installation location, making the data
        available to the load_full_data function.
    :return: path to downloaded birth data file
    """

    from us_birth_data import __version__ as v
    destination = destination or full_data
    url = 'https://github.com/Mikuana/us_birth_data/releases/download/'
    url += f'v{semver.parse_version_info(v).replace(patch=0)}/{gzip_data.name}'
    with TemporaryDirectory() as td:
        gzp = Path(td, gzip_data.name)
        try:
            print('Downloading from URL:\n' + url)
            response = requests.get(url, stream=True)
            tqdm_kwargs = dict(
                total=int(response.headers.get('content-length', 0)),
                desc=gzp.name,
                miniters=1
            )
            with gzp.open('wb') as f:
                with tqdm.wrapattr(f, "write", **tqdm_kwargs) as stream:
                    for chunk in response.iter_content(chunk_size=4096):
                        stream.write(chunk)

        except requests.HTTPError as te:
            print(f'Received HTTP error while attempting to download {url}')
            raise te

        h = sha256()
        h.update(gzp.read_bytes())
        actual = f"sha256::" + h.hexdigest()
        expected = hashes[gzip_data.name]

        msg = (
            f"Downloaded {url}\n"
            f"Expected {expected}\n"
            f"Received {actual}"
        )
        assert actual == expected, msg

        with gzip.open(gzp, 'rb') as f:
            destination.write_bytes(f.read())

            h = sha256()
            h.update(destination.read_bytes())
            actual = f"sha256::" + h.hexdigest()
            expected = hashes[full_data.name]

            msg = (
                f"Inflated {gzp.as_posix()}\n"
                f"Expected {expected}\n"
                f"Received {actual}"
            )
            assert actual == expected, msg

    return destination
