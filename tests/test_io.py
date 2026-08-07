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

    data = read_components_csv(csv_file)

    assert len(data.components) == 1
    assert data.components[0].name == "Cellulose"
    assert data.components[0].molar_flow == pytest.approx(1.5)
    assert data.components[0].composition.C == pytest.approx(6.0)
    assert data.components[0].degradable is True


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

def test_read_components_csv_separates_free_water(tmp_path):
    csv_path = tmp_path / "components.csv"
    csv_path.write_text(
        "\n".join(
            [
                "name,molar_flow,formula,degradable,input_mode",
                "WATER,10,H2O,false,WATER",
                "GLUCOSE,1,C6H12O6,true,FORMULA",
            ]
        ),
        encoding="utf-8",
    )

    data = read_components_csv(csv_path)

    assert data.water_available_mol == 10
    assert len(data.components) == 1
    assert data.components[0].name == "GLUCOSE"