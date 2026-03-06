import numpy as np
from matplotlib.figure import Figure

from app.model.config_model import SpectrumConfig
from app.model.result_model import SpectrumResult
from app.service.plot_style_service import apply_plot_style


def test_plot_style_labels():
    fig = Figure()
    ax = fig.add_subplot(111)

    cfg = SpectrumConfig(
        csv_path="dummy.csv",
        data_column=0,
        has_header=False,
        delimiter=",",
        sampling_rate_hz=1.0,
        sample_count=None,
        data_unit="V",
        remove_dc=False,
        filter_mode="No Filter",
        window_type="Hann",
        average_mode="Welch",
        welch_segment_length=256,
        welch_overlap=0.5,
        fft_size=None,
        x_min_hz=10.0,
        x_max_hz=100000.0,
        y_min_nv_root_hz=None,
        y_max_nv_root_hz=None,
        show_grid=True,
        show_annotation=True,
        annotation_text="Io = 10 mA",
        title_text="Title",
        line_width=1.2,
    )

    result = SpectrumResult(
        freqs_hz=np.array([10.0, 100.0, 1000.0]),
        psd_v2_per_hz=np.array([1.0, 1.0, 1.0]),
        asd_v_per_root_hz=np.array([1.0, 1.0, 1.0]),
        asd_nv_per_root_hz=np.array([1.0, 2.0, 3.0]),
        frequency_resolution_hz=90.0,
        effective_sample_count=3,
        window_type="Hann",
        average_mode="Welch",
        filter_mode="No Filter",
        summary_text="",
    )

    apply_plot_style(ax, cfg, result)
    assert ax.get_xscale() == "log"
    assert "Frequency" in ax.get_xlabel()
    assert "Equivalent Input Noise Voltage" in ax.get_ylabel()
