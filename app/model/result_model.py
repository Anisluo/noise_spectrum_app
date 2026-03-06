from dataclasses import dataclass

import numpy as np


@dataclass(slots=True)
class SpectrumResult:
    freqs_hz: np.ndarray
    psd_v2_per_hz: np.ndarray
    asd_v_per_root_hz: np.ndarray
    asd_nv_per_root_hz: np.ndarray
    frequency_resolution_hz: float
    effective_sample_count: int
    window_type: str
    average_mode: str
    filter_mode: str
    summary_text: str
