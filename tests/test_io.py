from pathlib import Path

import pytest

from biopotgas.io import read_components_csv


def test_read_components_csv_reads_formula_rows(tmp_path):
    csv_file = tmp_path / "components.csv"
    csv_file.write_text(
        "name,molar_flow,formula,degradable\n"
        "Cellulose,1.5,C6H10O5,true\n",
        encoding="utf-8",
    )

    components = read_components_csv(csv_file)

    assert len(components) == 1
    assert components[0].name == "Cellulose"
    assert components[0].molar_flow == pytest.approx(1.5)
    assert components[0].composition.C == pytest.approx(6.0)
    assert components[0].degradable is True


def test_read_components_csv_rejects_missing_molar_flow(tmp_path):
    csv_file = tmp_path / "components.csv"
    csv_file.write_text(
        "name,molar_flow,formula,degradable\n"
        "Cellulose,,C6H10O5,true\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Missing molar_flow"):
        read_components_csv(csv_file)


def test_read_components_csv_rejects_invalid_molar_flow(tmp_path):
    csv_file = tmp_path / "components.csv"
    csv_file.write_text(
        "name,molar_flow,formula,degradable\n"
        "Cellulose,abc,C6H10O5,true\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Invalid molar_flow"):
        read_components_csv(csv_file)