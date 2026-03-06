from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(slots=True)
class DataColumn:
    index: int
    name: str


@dataclass(slots=True)
class LoadedData:
    preview: pd.DataFrame
    columns: list[DataColumn]
    values: np.ndarray
