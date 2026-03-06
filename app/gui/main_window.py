from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QPlainTextEdit,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from app.gui.controls_panel import ControlsPanel
from app.gui.data_preview import DataPreviewTable
from app.gui.plot_widget import PlotWidget
from app.model.config_model import SpectrumConfig
from app.service.csv_loader import CSVLoader, CSVLoaderError
from app.service.export_service import export_plot, export_spectrum_csv
from app.service.plot_style_service import apply_plot_style
from app.service.spectrum_service import SpectrumServiceError, compute_spectrum
from app.util.validators import ConfigValidationError, validate_config


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Noise Spectrum Analyzer")
        self.resize(1400, 900)

        self.csv_loader = CSVLoader()
        self.last_result = None

        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)

        file_row = QHBoxLayout()
        self.csv_path = QLineEdit()
        self.csv_path.setPlaceholderText("Select CSV file")
        self.csv_path.editingFinished.connect(self.on_reload_preview)
        self.browse_btn = QPushButton("Browse")
        self.browse_btn.clicked.connect(self.on_browse)

        self.has_header = QCheckBox("Header")
        self.has_header.setChecked(True)
        self.has_header.toggled.connect(self.on_reload_preview)

        self.delimiter = QComboBox()
        self.delimiter.addItems(["auto", ",", ";", "\\t"])
        self.delimiter.currentTextChanged.connect(self.on_reload_preview)

        self.column_box = QComboBox()

        file_row.addWidget(QLabel("CSV"))
        file_row.addWidget(self.csv_path, stretch=1)
        file_row.addWidget(self.browse_btn)
        file_row.addWidget(self.has_header)
        file_row.addWidget(QLabel("Delimiter"))
        file_row.addWidget(self.delimiter)
        file_row.addWidget(QLabel("Column"))
        file_row.addWidget(self.column_box)

        root.addLayout(file_row)

        body_splitter = QSplitter(Qt.Horizontal)

        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        self.preview = DataPreviewTable()
        self.controls = ControlsPanel()

        left_layout.addWidget(QLabel("CSV Preview"))
        left_layout.addWidget(self.preview, stretch=2)
        left_layout.addWidget(self.controls, stretch=3)

        self.plot = PlotWidget()

        body_splitter.addWidget(left_panel)
        body_splitter.addWidget(self.plot)
        body_splitter.setSizes([480, 920])
        root.addWidget(body_splitter, stretch=1)

        action_row = QHBoxLayout()
        self.generate_btn = QPushButton("Generate Spectrum")
        self.generate_btn.clicked.connect(self.on_generate)
        self.clear_btn = QPushButton("clear")
        self.clear_btn.clicked.connect(self.on_clear)
        self.export_png_btn = QPushButton("Export PNG")
        self.export_png_btn.clicked.connect(self.on_export_png)
        self.export_svg_btn = QPushButton("Export SVG")
        self.export_svg_btn.clicked.connect(self.on_export_svg)
        self.export_csv_btn = QPushButton("Export CSV")
        self.export_csv_btn.clicked.connect(self.on_export_csv)

        action_row.addWidget(self.generate_btn)
        action_row.addWidget(self.clear_btn)
        action_row.addWidget(self.export_png_btn)
        action_row.addWidget(self.export_svg_btn)
        action_row.addWidget(self.export_csv_btn)
        action_row.addStretch(1)

        root.addLayout(action_row)

        self.summary = QPlainTextEdit()
        self.summary.setReadOnly(True)
        self.summary.setPlaceholderText("Analysis summary")
        root.addWidget(self.summary, stretch=0)

    def log(self, message: str) -> None:
        self.summary.appendPlainText(message)

    def show_error(self, message: str) -> None:
        QMessageBox.critical(self, "Error", message)
        self.log(f"ERROR: {message}")

    def on_browse(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Open CSV", "", "CSV Files (*.csv);;All Files (*)")
        if not path:
            return
        self.csv_path.setText(path)
        self.load_preview()

    def on_reload_preview(self, *_args) -> None:
        if self.csv_path.text().strip():
            self.load_preview()

    def load_preview(self) -> None:
        csv_path = self.csv_path.text().strip()
        if not csv_path:
            return

        try:
            loaded = self.csv_loader.read_preview(
                csv_path=csv_path,
                has_header=self.has_header.isChecked(),
                delimiter=self.delimiter.currentText(),
                nrows=30,
            )
        except CSVLoaderError as exc:
            self.show_error(str(exc))
            return

        self.preview.set_dataframe(loaded.preview)
        self.column_box.clear()
        for col in loaded.columns:
            self.column_box.addItem(f"{col.index}: {col.name}", col.index)
        if self.column_box.count() > 0:
            self.column_box.setCurrentIndex(0)

        self.log(f"Preview loaded: {Path(csv_path).name}, columns={len(loaded.columns)}")

    def build_config(self) -> SpectrumConfig:
        state = self.controls.get_state()
        if self.column_box.count() == 0 and self.csv_path.text().strip():
            self.load_preview()
        if self.column_box.currentData() is None:
            raise ConfigValidationError("Please select a data column.")

        config = SpectrumConfig(
            csv_path=self.csv_path.text().strip(),
            data_column=int(self.column_box.currentData()),
            has_header=self.has_header.isChecked(),
            delimiter=self.delimiter.currentText(),
            sampling_rate_hz=state.sampling_rate_hz,
            sample_count=state.sample_count,
            data_unit=state.data_unit,
            remove_dc=state.remove_dc,
            filter_mode=state.filter_mode,
            window_type=state.window_type,
            average_mode=state.average_mode,
            welch_segment_length=state.welch_segment_length,
            welch_overlap=state.welch_overlap,
            fft_size=state.fft_size,
            x_min_hz=state.x_min_hz,
            x_max_hz=state.x_max_hz,
            y_min_nv_root_hz=state.y_min_nv_root_hz,
            y_max_nv_root_hz=state.y_max_nv_root_hz,
            show_grid=state.show_grid,
            show_annotation=state.show_annotation,
            annotation_text=state.annotation_text,
            title_text=state.title_text,
            line_width=state.line_width,
        )
        validate_config(config)
        return config

    def on_generate(self) -> None:
        try:
            config = self.build_config()
            values = self.csv_loader.load_column_values(
                csv_path=config.csv_path,
                column_index=config.data_column,
                has_header=config.has_header,
                delimiter=config.delimiter,
            )
            result = compute_spectrum(config, values)
        except (ConfigValidationError, CSVLoaderError, SpectrumServiceError, ValueError, NotImplementedError) as exc:
            self.show_error(str(exc))
            return

        self.last_result = result
        apply_plot_style(self.plot.ax, config, result)
        self.plot.redraw()

        self.summary.clear()
        self.summary.setPlainText(result.summary_text)
        self.log("Spectrum generated.")

    def on_clear(self) -> None:
        self.last_result = None
        self.csv_path.clear()
        self.column_box.clear()
        self.preview.clear()
        self.preview.setRowCount(0)
        self.preview.setColumnCount(0)
        self.plot.ax.clear()
        self.plot.redraw()
        self.summary.clear()

    def _export_plot(self, ext: str) -> None:
        if self.last_result is None:
            self.show_error("Please generate spectrum before exporting.")
            return

        path, _ = QFileDialog.getSaveFileName(self, f"Export {ext.upper()}", "", f"{ext.upper()} Files (*.{ext})")
        if not path:
            return
        if not path.lower().endswith(f".{ext}"):
            path = f"{path}.{ext}"

        try:
            export_plot(self.plot.figure, path)
        except Exception as exc:
            self.show_error(f"Export failed: {exc}")
            return
        self.log(f"Exported plot: {path}")

    def on_export_png(self) -> None:
        self._export_plot("png")

    def on_export_svg(self) -> None:
        self._export_plot("svg")

    def on_export_csv(self) -> None:
        if self.last_result is None:
            self.show_error("Please generate spectrum before exporting.")
            return

        path, _ = QFileDialog.getSaveFileName(self, "Export CSV", "", "CSV Files (*.csv)")
        if not path:
            return
        if not path.lower().endswith(".csv"):
            path = f"{path}.csv"

        try:
            export_spectrum_csv(self.last_result, path)
        except Exception as exc:
            self.show_error(f"Export failed: {exc}")
            return

        self.log(f"Exported data: {path}")
