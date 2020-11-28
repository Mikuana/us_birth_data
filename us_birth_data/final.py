import gzip
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import List, Union
from urllib import request, error

import pandas as pd
import semver

from us_birth_data.data import full_data, gzip_data, hashes
from us_birth_data.fields import Target


def load_full_data(columns: List[Union[str, Target]] = None, **kwargs) -> pd.DataFrame:
    """
    A convenience wrapper over the pandas.read_parquet method, to load the full
    us_birth_data set into a DataFrame. This data set is not installed with this
    package, so the first time you run this package it will prompt you to download
    it.

    :param columns: If not None, only these columns will be read from the file.
    :param kwargs: passes kwargs directly to the underlying pandas function
    :return: a pandas DataFrame
    """
    if columns:
        columns = [c.name() if issubclass(c, Target) else c for c in columns]

    assert full_data.exists(), f"File {full_data.as_posix()} does not exist. Download it."
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
    url += f'{semver.parse_version_info(v).replace(patch=0)}/{gzip_data.name}'
    with TemporaryDirectory() as td:
        gzp = Path(td, gzip_data.stem)

        try:
            request.urlretrieve(url, gzp)
        except error.HTTPError as te:
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
