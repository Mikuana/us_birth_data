import json
from pathlib import Path

folder = Path(__file__).parent
full_data = Path(folder, 'us_birth_data.parquet')
gzip_data = Path(full_data.as_posix() + '.gz')

hashes = json.loads(Path(folder, 'hashes.json').read_text())
