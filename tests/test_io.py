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

def test_read_components_csv_legacy_molar_flow_still_works(tmp_path):
    csv_file = tmp_path / "components.csv"
    csv_file.write_text(
        "\n".join(
            [
                "name,molar_flow,formula,degradable",
                "GLUCOSE,1,C6H12O6,true",
            ]
        ),
        encoding="utf-8",
    )

    data = read_components_csv(csv_file)

    assert data.input_basis_type == "molar"
    assert data.input_unit == "kmol"
    assert len(data.components) == 1
    assert data.components[0].name == "GLUCOSE"
    assert data.components[0].molar_flow == 1

def test_read_components_csv_supports_input_quantity_mol(tmp_path):
    csv_file = tmp_path / "components.csv"
    csv_file.write_text(
        "\n".join(
            [
                "component_name,input_quantity,input_basis_type,input_unit,formula,degradable,input_mode",
                "GLUCOSE,1000,molar,mol,C6H12O6,true,FORMULA",
            ]
        ),
        encoding="utf-8",
    )

    data = read_components_csv(csv_file)

    assert data.input_basis_type == "molar"
    assert data.input_unit == "mol"
    assert data.internal_molar_basis == "kmol"
    assert len(data.components) == 1
    assert data.components[0].molar_flow == 1

def test_read_components_csv_supports_mass_basis_and_free_water(tmp_path):
    csv_file = tmp_path / "components.csv"
    csv_file.write_text(
        "\n".join(
            [
                "component_name,input_quantity,input_basis_type,input_unit,formula,degradable,input_mode",
                "WATER,18.015,mass,kg,H2O,false,WATER",
                "GLUCOSE,180.156,mass,kg,C6H12O6,true,FORMULA",
            ]
        ),
        encoding="utf-8",
    )

    data = read_components_csv(csv_file)

    assert data.input_basis_type == "mass"
    assert data.input_unit == "kg"
    assert data.water_available_mol == pytest.approx(1.0)
    assert len(data.components) == 1
    assert data.components[0].name == "GLUCOSE"
    assert data.components[0].molar_flow == pytest.approx(1.0, rel=1e-3)