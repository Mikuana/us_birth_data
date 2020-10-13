import gzip
import shutil
import subprocess
from ftplib import FTP
from pathlib import Path
from tempfile import TemporaryDirectory

from tqdm import tqdm

zip_path = Path('zip')
gzip_path = Path('gz')
pdf_path = Path('pdf')


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
    """ Unzip CDC file, move docs and recompress data as gz, then remove zip """
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


if __name__ == '__main__':
    zip_path.mkdir(exist_ok=True)
    gzip_path.mkdir(exist_ok=True)
    pdf_path.mkdir(exist_ok=True)

    for q in get_queue():
        zf = get_data_set(q)
        zip_convert(zf)
