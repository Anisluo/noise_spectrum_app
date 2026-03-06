from dataclasses import dataclass


@dataclass(slots=True)
class SpectrumConfig:
    csv_path: str
    data_column: int
    has_header: bool
    delimiter: str
    sampling_rate_hz: float
    sample_count: int | None
    data_unit: str
    remove_dc: bool
    filter_mode: str
    window_type: str
    average_mode: str
    welch_segment_length: int | None
    welch_overlap: float
    fft_size: int | None
    x_min_hz: float
    x_max_hz: float
    y_min_nv_root_hz: float | None
    y_max_nv_root_hz: float | None
    show_grid: bool
    show_annotation: bool
    annotation_text: str
    title_text: str
    line_width: float
