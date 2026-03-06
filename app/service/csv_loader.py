import csv
import re
from pathlib import Path

import numpy as np
import pandas as pd

from app.model.data_model import DataColumn, LoadedData


class CSVLoaderError(ValueError):
    pass


class CSVLoader:
    SUPPORTED_DELIMITERS = [",", ";", "\t"]
    ENCODINGS = ("utf-8-sig", "utf-8", "gb18030", "gbk", "cp936")

    _ENG_SUFFIX_SCALE = {
        "p": 1e-12,
        "n": 1e-9,
        "u": 1e-6,
        "m": 1e-3,
        "k": 1e3,
        "M": 1e6,
        "G": 1e9,
    }
    _ENG_PATTERN = re.compile(r"^\s*([-+]?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?)\s*([pnumkMG]?)\s*$")

    def _normalize_delimiter(self, delimiter: str) -> str:
        if delimiter == "\\t":
            return "\t"
        return delimiter

    def _parse_engineering_series(self, series: pd.Series) -> pd.Series:
        def _parse_one(value):
            if value is None:
                return np.nan
            text = str(value).strip()
            if not text:
                return np.nan
            m = self._ENG_PATTERN.match(text)
            if not m:
                return np.nan
            number = float(m.group(1))
            suffix = m.group(2)
            scale = self._ENG_SUFFIX_SCALE.get(suffix, 1.0)
            return number * scale

        parsed = series.map(_parse_one)
        return pd.to_numeric(parsed, errors="coerce")

    def _read_text_sample(self, csv_path: str, size: int = 4096) -> str:
        with open(csv_path, "rb") as f:
            raw = f.read(size)
        for enc in self.ENCODINGS:
            try:
                return raw.decode(enc)
            except UnicodeDecodeError:
                continue
        raise CSVLoaderError("Cannot decode CSV. Please convert file to UTF-8/GBK.")

    def _read_csv_with_fallback(self, csv_path: str, **kwargs) -> pd.DataFrame:
        last_exc = None
        for enc in self.ENCODINGS:
            try:
                return pd.read_csv(csv_path, encoding=enc, **kwargs)
            except UnicodeDecodeError as exc:
                last_exc = exc
                continue
            except Exception as exc:
                last_exc = exc
                break
        raise CSVLoaderError(f"Failed to parse CSV: {last_exc}")

    def detect_delimiter(self, csv_path: str) -> str:
        try:
            sample = self._read_text_sample(csv_path, size=4096)
        except OSError as exc:
            raise CSVLoaderError(f"Cannot read CSV: {exc}") from exc

        if not sample.strip():
            raise CSVLoaderError("CSV file is empty.")

        sniffer = csv.Sniffer()
        try:
            dialect = sniffer.sniff(sample, delimiters=self.SUPPORTED_DELIMITERS)
            return dialect.delimiter
        except csv.Error:
            return ","

    def read_preview(
        self,
        csv_path: str,
        has_header: bool,
        delimiter: str = "auto",
        nrows: int = 20,
    ) -> LoadedData:
        path = Path(csv_path)
        if not path.exists():
            raise CSVLoaderError(f"CSV file not found: {csv_path}")

        sep = self.detect_delimiter(csv_path) if delimiter == "auto" else self._normalize_delimiter(delimiter)
        header = 0 if has_header else None

        try:
            preview_df = self._read_csv_with_fallback(
                csv_path,
                sep=sep,
                header=header,
                nrows=nrows,
                engine="python",
            )
        except CSVLoaderError as exc:
            raise CSVLoaderError(f"Failed to parse CSV preview: {exc}") from exc

        if preview_df.empty:
            raise CSVLoaderError("CSV contains no rows.")

        columns = []
        for idx, col in enumerate(preview_df.columns):
            columns.append(DataColumn(index=idx, name=str(col)))

        return LoadedData(preview=preview_df, columns=columns, values=np.array([]))

    def load_column_values(
        self,
        csv_path: str,
        column_index: int,
        has_header: bool,
        delimiter: str = "auto",
    ) -> np.ndarray:
        sep = self.detect_delimiter(csv_path) if delimiter == "auto" else self._normalize_delimiter(delimiter)
        header = 0 if has_header else None

        try:
            df = self._read_csv_with_fallback(csv_path, sep=sep, header=header, engine="python")
        except CSVLoaderError as exc:
            raise CSVLoaderError(f"Failed to parse CSV: {exc}") from exc

        if df.empty:
            raise CSVLoaderError("CSV contains no rows.")

        if column_index < 0 or column_index >= df.shape[1]:
            raise CSVLoaderError("Selected column index is out of range.")

        series = pd.to_numeric(df.iloc[:, column_index], errors="coerce").dropna()
        if series.empty:
            series = self._parse_engineering_series(df.iloc[:, column_index]).dropna()
        if series.empty:
            raise CSVLoaderError("Selected column has no numeric data.")

        values = series.to_numpy(dtype=float)
        if values.size < 2:
            raise CSVLoaderError("Not enough numeric samples for spectrum analysis.")

        return values
