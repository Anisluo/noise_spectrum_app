from dataclasses import dataclass

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)


@dataclass(slots=True)
class ControlsState:
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


class ControlsPanel(QWidget):
    changed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        root = QVBoxLayout(self)

        sampling_group = QGroupBox("Sampling")
        sampling_form = QFormLayout(sampling_group)

        self.fs = QDoubleSpinBox()
        self.fs.setRange(1e-9, 1e12)
        self.fs.setValue(100000)
        self.fs.setDecimals(6)
        sampling_form.addRow("Fs (Hz)", self.fs)

        self.sample_count = QSpinBox()
        self.sample_count.setRange(0, 2_000_000_000)
        self.sample_count.setValue(0)
        self.sample_count.setSpecialValueText("Auto")
        sampling_form.addRow("Sample count", self.sample_count)

        self.data_unit = QComboBox()
        self.data_unit.addItems(["V", "mV", "uV", "nV"])
        self.data_unit.setCurrentText("V")
        sampling_form.addRow("Input unit", self.data_unit)

        self.remove_dc = QCheckBox("Remove DC")
        self.remove_dc.setChecked(True)
        sampling_form.addRow(self.remove_dc)

        spectrum_group = QGroupBox("Spectrum")
        spectrum_form = QFormLayout(spectrum_group)

        self.filter_mode = QComboBox()
        self.filter_mode.addItems(["No Filter", "LPF (Reserved)", "HPF (Reserved)", "BPF (Reserved)", "BSF (Reserved)"])
        self.filter_mode.setCurrentIndex(0)
        spectrum_form.addRow("Filter", self.filter_mode)

        self.window_type = QComboBox()
        self.window_type.addItems(["Rectangular", "Hann", "Hamming", "Blackman", "Flat Top"])
        self.window_type.setCurrentText("Hann")
        spectrum_form.addRow("Window", self.window_type)

        self.average_mode = QComboBox()
        self.average_mode.addItems(["Welch", "None"])
        spectrum_form.addRow("Average", self.average_mode)

        self.welch_segment = QSpinBox()
        self.welch_segment.setRange(0, 2_000_000_000)
        self.welch_segment.setValue(1024)
        self.welch_segment.setSpecialValueText("Auto")
        spectrum_form.addRow("Welch segment", self.welch_segment)

        self.welch_overlap = QDoubleSpinBox()
        self.welch_overlap.setRange(0.0, 0.95)
        self.welch_overlap.setSingleStep(0.05)
        self.welch_overlap.setValue(0.5)
        spectrum_form.addRow("Welch overlap", self.welch_overlap)

        self.fft_size = QSpinBox()
        self.fft_size.setRange(0, 2_000_000_000)
        self.fft_size.setValue(0)
        self.fft_size.setSpecialValueText("Auto")
        spectrum_form.addRow("FFT size", self.fft_size)

        plot_group = QGroupBox("Plot")
        plot_form = QFormLayout(plot_group)

        self.x_min = QDoubleSpinBox()
        self.x_min.setRange(1e-9, 1e12)
        self.x_min.setValue(10)
        self.x_min.setDecimals(6)
        plot_form.addRow("X min (Hz)", self.x_min)

        self.x_max = QDoubleSpinBox()
        self.x_max.setRange(1e-9, 1e12)
        self.x_max.setValue(100000)
        self.x_max.setDecimals(6)
        plot_form.addRow("X max (Hz)", self.x_max)

        self.y_min = QLineEdit()
        self.y_min.setPlaceholderText("Auto")
        plot_form.addRow("Y min (nV/sqrt(Hz))", self.y_min)

        self.y_max = QLineEdit()
        self.y_max.setPlaceholderText("Auto")
        plot_form.addRow("Y max (nV/sqrt(Hz))", self.y_max)

        self.show_grid = QCheckBox("Show grid")
        self.show_grid.setChecked(True)
        plot_form.addRow(self.show_grid)

        self.show_annotation = QCheckBox("Show annotation")
        self.show_annotation.setChecked(False)
        plot_form.addRow(self.show_annotation)

        self.annotation = QLineEdit()
        self.annotation.setPlaceholderText("Io = 10 mA\\nTA = 25C")
        plot_form.addRow("Annotation", self.annotation)

        self.title = QLineEdit()
        self.title.setText("Equivalent Input Noise Voltage vs Frequency")
        plot_form.addRow("Title", self.title)

        self.line_width = QDoubleSpinBox()
        self.line_width.setRange(0.1, 10)
        self.line_width.setSingleStep(0.1)
        self.line_width.setValue(1.6)
        plot_form.addRow("Line width", self.line_width)

        root.addWidget(sampling_group)
        root.addWidget(spectrum_group)
        root.addWidget(plot_group)
        root.addStretch(1)

        controls = [
            self.fs,
            self.sample_count,
            self.data_unit,
            self.remove_dc,
            self.filter_mode,
            self.window_type,
            self.average_mode,
            self.welch_segment,
            self.welch_overlap,
            self.fft_size,
            self.x_min,
            self.x_max,
            self.y_min,
            self.y_max,
            self.show_grid,
            self.show_annotation,
            self.annotation,
            self.title,
            self.line_width,
        ]

        for w in controls:
            if hasattr(w, "valueChanged"):
                w.valueChanged.connect(lambda *_: self.changed.emit())
            elif hasattr(w, "currentTextChanged"):
                w.currentTextChanged.connect(lambda *_: self.changed.emit())
            elif hasattr(w, "toggled"):
                w.toggled.connect(lambda *_: self.changed.emit())
            elif hasattr(w, "textChanged"):
                w.textChanged.connect(lambda *_: self.changed.emit())

    def _optional_int(self, value: int) -> int | None:
        return value if value > 0 else None

    def _optional_float(self, text: str) -> float | None:
        text = text.strip()
        if not text:
            return None
        return float(text)

    def get_state(self) -> ControlsState:
        return ControlsState(
            sampling_rate_hz=float(self.fs.value()),
            sample_count=self._optional_int(self.sample_count.value()),
            data_unit=self.data_unit.currentText(),
            remove_dc=self.remove_dc.isChecked(),
            filter_mode=self.filter_mode.currentText(),
            window_type=self.window_type.currentText(),
            average_mode=self.average_mode.currentText(),
            welch_segment_length=self._optional_int(self.welch_segment.value()),
            welch_overlap=float(self.welch_overlap.value()),
            fft_size=self._optional_int(self.fft_size.value()),
            x_min_hz=float(self.x_min.value()),
            x_max_hz=float(self.x_max.value()),
            y_min_nv_root_hz=self._optional_float(self.y_min.text()),
            y_max_nv_root_hz=self._optional_float(self.y_max.text()),
            show_grid=self.show_grid.isChecked(),
            show_annotation=self.show_annotation.isChecked(),
            annotation_text=self.annotation.text(),
            title_text=self.title.text(),
            line_width=float(self.line_width.value()),
        )
