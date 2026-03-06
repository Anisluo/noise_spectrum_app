from app.model.config_model import SpectrumConfig


class ConfigValidationError(ValueError):
    pass


def validate_config(config: SpectrumConfig) -> None:
    if config.sampling_rate_hz <= 0:
        raise ConfigValidationError("Sampling rate must be > 0.")
    if config.sample_count is not None and config.sample_count <= 1:
        raise ConfigValidationError("Sample count must be > 1 when provided.")
    if config.welch_segment_length is not None and config.welch_segment_length <= 1:
        raise ConfigValidationError("Welch segment length must be > 1 when provided.")
    if not (0 <= config.welch_overlap < 1):
        raise ConfigValidationError("Welch overlap must be in [0, 1).")
    if config.fft_size is not None and config.fft_size <= 1:
        raise ConfigValidationError("FFT size must be > 1 when provided.")
    if config.x_min_hz <= 0 or config.x_max_hz <= 0:
        raise ConfigValidationError("X axis limits must be > 0 for log scale.")
    if config.x_min_hz >= config.x_max_hz:
        raise ConfigValidationError("X axis min must be smaller than max.")
    if (
        config.y_min_nv_root_hz is not None
        and config.y_max_nv_root_hz is not None
        and config.y_min_nv_root_hz >= config.y_max_nv_root_hz
    ):
        raise ConfigValidationError("Y axis min must be smaller than max.")
    if config.line_width <= 0:
        raise ConfigValidationError("Line width must be > 0.")
