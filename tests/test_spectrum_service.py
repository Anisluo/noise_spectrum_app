import numpy as np

from app.model.config_model import SpectrumConfig
from app.service.spectrum_service import compute_spectrum


def test_welch_output_shape():
    rng = np.random.default_rng(0)
    x = rng.normal(0, 1e-6, size=4096)

    cfg = SpectrumConfig(
        csv_path="dummy.csv",
        data_column=0,
        has_header=False,
        delimiter=",",
        sampling_rate_hz=100000.0,
        sample_count=None,
        data_unit="V",
        remove_dc=True,
        filter_mode="No Filter",
        window_type="Hann",
        average_mode="Welch",
        welch_segment_length=1024,
        welch_overlap=0.5,
        fft_size=None,
        x_min_hz=10.0,
        x_max_hz=50000.0,
        y_min_nv_root_hz=None,
        y_max_nv_root_hz=None,
        show_grid=True,
        show_annotation=False,
        annotation_text="",
        title_text="",
        line_width=1.5,
    )

    result = compute_spectrum(cfg, x)
    assert result.freqs_hz.size > 0
    assert result.freqs_hz.shape == result.asd_nv_per_root_hz.shape
    assert np.all(result.freqs_hz > 0)
