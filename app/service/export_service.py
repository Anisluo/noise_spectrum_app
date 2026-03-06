from pathlib import Path

import pandas as pd
from matplotlib.figure import Figure

from app.model.result_model import SpectrumResult


def export_plot(figure: Figure, output_path: str) -> None:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(path, dpi=300, bbox_inches="tight")


def export_spectrum_csv(result: SpectrumResult, output_path: str) -> None:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(
        {
            "frequency_hz": result.freqs_hz,
            "psd_v2_per_hz": result.psd_v2_per_hz,
            "asd_v_per_root_hz": result.asd_v_per_root_hz,
            "asd_nv_per_root_hz": result.asd_nv_per_root_hz,
        }
    )
    df.to_csv(path, index=False)
