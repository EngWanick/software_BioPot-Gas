import pytest
from openpyxl import Workbook

from biopotgas.excel_reader import read_biopotgas_excel
from biopotgas.pipeline import calculate_from_excel

def make_input_workbook(path):
    wb = Workbook()

    ws = wb.active
    ws.title = "01_INPUTS"

    ws.append(["parameter", "value"])
    ws.append(["carbon_conversion", 1.0])
    ws.append(["include_non_degradable", False])
    ws.append(["normal_temperature_C", 0.0])
    ws.append(["normal_pressure_kPa", 101.325])
    ws.append(["CH4_LHV_MJ_per_Nm3", 35.8])
    ws.append(["kWh_per_MJ", 0.277778])
    ws.append([])
    ws.append(
        [
            "component_name",
            "molar_flow",
            "degradable",
            "input_mode",
            "active_row",
            "formula",
            "C_atoms",
            "H_atoms",
            "O_atoms",
            "N_atoms",
            "S_atoms",
        ]
    )
    ws.append(["CELLULOSE", 1.0, True, "FORMULA", True, "C6H10O5", None, None, None, None, None])
    ws.append(["WATER", 2.0, True, "FORMULA", True, "H2O", None, None, None, None, None])

    wb.save(path)

def test_excel_reader_treats_water_as_available_water(tmp_path):
    # adicionar uma linha ativa:
    # component_name = WATER
    # molar_flow = 2.0
    # degradable = True
    # input_mode = FORMULA
    # formula = H2O
    workbook_path = tmp_path / "input.xlsx"
    make_input_workbook(workbook_path)

    data = read_biopotgas_excel(workbook_path)

    assert data.water_available_mol == pytest.approx(2.0)
    assert len(data.components) == 1
    assert data.components[0].name == "CELLULOSE"

def test_calculate_from_excel_reports_net_water_balance(tmp_path):
    workbook_path = tmp_path / "input.xlsx"
    make_input_workbook(workbook_path)

    result = calculate_from_excel(workbook_path)

    assert result["water_available_mol"] == pytest.approx(2.0)
    assert result["net_water_balance_mol"] == pytest.approx(
        result["water_available_mol"] - result["H2O_mol"]
    )
    assert result["net_water_balance_mass"] == pytest.approx(
        result["net_water_balance_mol"] * 18.015
    )