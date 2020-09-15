import logging
from hashlib import sha256
from pathlib import Path
from typing import Union

import pandas as pd


class QueryCache:

    _FILE_EXT = 'pkl'

    def __init__(self, cache_dir: Union[Path, str]):
        self.cache_dir = Path(cache_dir)

    def _hash(self, s: str):
        return sha256(s.encode()).hexdigest()

    def file_path(self, s: str):
        return self.cache_dir / f"{self._hash(s)}.{self._FILE_EXT}"

    def read(self, query: str):
        path = self.file_path(query)
        if not path.exists():
            raise FileNotFoundError
        logging.info(f"Reading query from cache: {self.file_path(query)}")
        return pd.read_pickle(self.file_path(query))

    def save(self, query: str, df: pd.DataFrame):
        path = self.file_path(query)
        path.parent.mkdir(exist_ok=True)
        logging.info(f"Caching {query} to {path}")
        df.to_pickle(self.file_path(query))
