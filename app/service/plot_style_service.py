from matplotlib import ticker

from app.model.config_model import SpectrumConfig
from app.model.result_model import SpectrumResult


def _freq_formatter(val, _pos):
    if val >= 1e6:
        return f"{val / 1e6:g}M"
    if val >= 1e3:
        return f"{val / 1e3:g}k"
    return f"{val:g}"


def apply_plot_style(ax, config: SpectrumConfig, result: SpectrumResult) -> None:
    ax.clear()
    ax.set_facecolor("#ffffff")
    ax.figure.set_facecolor("#f7f7f7")

    ax.plot(
        result.freqs_hz,
        result.asd_nv_per_root_hz,
        color="#222222",
        linewidth=config.line_width,
    )

    ax.set_xscale("log")
    ax.set_xlim(config.x_min_hz, config.x_max_hz)

    if config.y_min_nv_root_hz is not None and config.y_max_nv_root_hz is not None:
        ax.set_ylim(config.y_min_nv_root_hz, config.y_max_nv_root_hz)

    ax.grid(config.show_grid, which="both", color="#d0d0d0", linestyle="-", linewidth=0.7)

    ax.set_xlabel("f - Frequency - Hz")
    ax.set_ylabel("Vn - Equivalent Input Noise Voltage - nV/sqrt(Hz)")

    ax.xaxis.set_major_locator(ticker.LogLocator(base=10.0))
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(_freq_formatter))

    if config.title_text.strip():
        ax.set_title(config.title_text.strip(), fontsize=11)

    if config.show_annotation and config.annotation_text.strip():
        ax.text(
            0.02,
            0.98,
            config.annotation_text.strip(),
            transform=ax.transAxes,
            va="top",
            ha="left",
            fontsize=9,
            color="#111111",
            bbox={"boxstyle": "square,pad=0.2", "facecolor": "#ffffff", "alpha": 0.85, "edgecolor": "#cccccc"},
        )

    for spine in ax.spines.values():
        spine.set_linewidth(1.0)
        spine.set_color("#333333")
