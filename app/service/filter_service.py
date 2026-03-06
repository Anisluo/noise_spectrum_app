import numpy as np


def apply_filter(values: np.ndarray, mode: str) -> np.ndarray:
    normalized = mode.strip().lower()
    if normalized in {"none", "no filter", "off"}:
        return values
    raise NotImplementedError(f"Filter mode '{mode}' is reserved for future versions.")
