from pathlib import Path

from app.service.csv_loader import CSVLoader


def test_csv_loader_basic(tmp_path: Path):
    p = tmp_path / "data.csv"
    p.write_text("t,v\n0,1\n1,2\n2,3\n", encoding="utf-8")

    loader = CSVLoader()
    preview = loader.read_preview(str(p), has_header=True, delimiter="auto")
    assert len(preview.columns) == 2

    values = loader.load_column_values(str(p), column_index=1, has_header=True, delimiter="auto")
    assert values.tolist() == [1.0, 2.0, 3.0]
