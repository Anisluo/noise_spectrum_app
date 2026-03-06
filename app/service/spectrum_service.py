import numpy as np
from scipy import signal

from app.model.config_model import SpectrumConfig
from app.model.result_model import SpectrumResult
from app.service.filter_service import apply_filter
from app.util.units import convert_to_volts


WINDOW_MAP = {
    "Rectangular": "boxcar",
    "Hann": "hann",
    "Hamming": "hamming",
    "Blackman": "blackman",
    "Flat Top": "flattop",
}


class SpectrumServiceError(ValueError):
    pass


def _resolve_window(window_type: str) -> str:
    return WINDOW_MAP.get(window_type, "hann")


def compute_spectrum(config: SpectrumConfig, values: np.ndarray) -> SpectrumResult:
    x = np.asarray(values, dtype=float)
    if config.sample_count is not None:
        if config.sample_count > x.size:
            raise SpectrumServiceError("Sample count is larger than loaded data length.")
        x = x[: config.sample_count]

    if x.size < 2:
        raise SpectrumServiceError("At least 2 points are required for spectrum analysis.")

    x = convert_to_volts(x, config.data_unit)

    if config.remove_dc:
        x = x - np.mean(x)

    x = apply_filter(x, config.filter_mode)

    fs = config.sampling_rate_hz
    window = _resolve_window(config.window_type)
    nfft = config.fft_size

    average_mode = config.average_mode.strip().lower()
    if average_mode == "welch":
        nperseg = config.welch_segment_length or min(1024, x.size)
        if nperseg > x.size:
            raise SpectrumServiceError("Welch segment length cannot exceed sample length.")
        noverlap = int(nperseg * config.welch_overlap)
        freqs_hz, psd = signal.welch(
            x,
            fs=fs,
            window=window,
            nperseg=nperseg,
            noverlap=noverlap,
            nfft=nfft,
            detrend=False,
            scaling="density",
            return_onesided=True,
        )
    else:
        freqs_hz, psd = signal.periodogram(
            x,
            fs=fs,
            window=window,
            nfft=nfft,
            detrend=False,
            scaling="density",
            return_onesided=True,
        )

    positive = freqs_hz > 0
    freqs_hz = freqs_hz[positive]
    psd = psd[positive]

    if freqs_hz.size == 0:
        raise SpectrumServiceError("No positive frequency bins produced.")

    asd = np.sqrt(psd)
    asd_nv = asd * 1e9
    freq_res = float(np.mean(np.diff(freqs_hz))) if freqs_hz.size > 1 else float(freqs_hz[0])

    summary = "\n".join(
        [
            f"Sampling rate: {fs:g} Hz",
            f"Effective samples: {x.size}",
            f"Frequency bins: {freqs_hz.size}",
            f"Frequency resolution: {freq_res:.6g} Hz",
            f"Window: {config.window_type}",
            f"Average mode: {config.average_mode}",
            f"Filter: {config.filter_mode}",
            "Output: ASD in nV/sqrt(Hz)",
        ]
    )

    return SpectrumResult(
        freqs_hz=freqs_hz,
        psd_v2_per_hz=psd,
        asd_v_per_root_hz=asd,
        asd_nv_per_root_hz=asd_nv,
        frequency_resolution_hz=freq_res,
        effective_sample_count=x.size,
        window_type=config.window_type,
        average_mode=config.average_mode,
        filter_mode=config.filter_mode,
        summary_text=summary,
    )
