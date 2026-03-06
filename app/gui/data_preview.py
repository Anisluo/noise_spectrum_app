import pandas as pd
from PySide6.QtWidgets import QTableWidget, QTableWidgetItem


class DataPreviewTable(QTableWidget):
    def set_dataframe(self, df: pd.DataFrame) -> None:
        self.clear()
        self.setRowCount(len(df.index))
        self.setColumnCount(len(df.columns))
        self.setHorizontalHeaderLabels([str(c) for c in df.columns])

        for row_idx, row in enumerate(df.itertuples(index=False)):
            for col_idx, value in enumerate(row):
                self.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))

        self.resizeColumnsToContents()
