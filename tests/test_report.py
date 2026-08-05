import pytest

from biopotgas.core import BiogasResult
from biopotgas.report import molar_volume_m3_per_kmol, result_to_dict


def test_molar_volume_at_normal_conditions():
    volume = molar_volume_m3_per_kmol(
        temperature_C=0.0,
        pressure_kPa=101.325,
    )

    assert volume == pytest.approx(22.4139695446)


def test_result_to_dict_converts_molar_outputs_to_report_values():
    result = BiogasResult(
        ch4_mol=1.0,
        co2_mol=1.0,
        nh3_mol=0.0,
        h2s_mol=0.0,
        inert_carbon_mol=0.0,
        c_available_mol=2.0,
        c_total_mol=2.0,
        h_total_mol=8.0,
        o_total_mol=2.0,
        n_total_mol=0.0,
        s_total_mol=0.0,
    )

    output = result_to_dict(result)

    assert output["CH4_Nm3"] == pytest.approx(22.4139695446)
    assert output["CO2_Nm3"] == pytest.approx(22.4139695446)
    assert output["total_biogas_Nm3"] == pytest.approx(44.8279390892)
    assert output["CH4_vol_percent"] == pytest.approx(50.0)
    assert output["CH4_mass"] == pytest.approx(16.043)
    assert output["CO2_mass"] == pytest.approx(44.01)


def test_result_to_dict_energy_uses_ch4_only():
    result = BiogasResult(
        ch4_mol=1.0,
        co2_mol=9.0,
        nh3_mol=0.0,
        h2s_mol=0.0,
        inert_carbon_mol=0.0,
        c_available_mol=10.0,
        c_total_mol=10.0,
        h_total_mol=4.0,
        o_total_mol=18.0,
        n_total_mol=0.0,
        s_total_mol=0.0,
    )

    output = result_to_dict(result)

    expected_ch4_nm3 = 22.4139695446
    expected_energy_mj = expected_ch4_nm3 * 35.8

    assert output["CH4_Nm3"] == pytest.approx(expected_ch4_nm3)
    assert output["CH4_energy_LHV_MJ"] == pytest.approx(expected_energy_mj)

def test_print_result_outputs_report_fields(capsys):
    from biopotgas.core import BiogasResult
    from biopotgas.report import print_result

    result = BiogasResult(
        ch4_mol=1.0,
        co2_mol=1.0,
        nh3_mol=0.0,
        h2s_mol=0.0,
        inert_carbon_mol=0.0,
        c_available_mol=2.0,
        c_total_mol=2.0,
        h_total_mol=8.0,
        o_total_mol=2.0,
        n_total_mol=0.0,
        s_total_mol=0.0,
    )

    print_result(result)

    captured = capsys.readouterr()

    assert "CH4_Nm3" in captured.out
    assert "CO2_Nm3" in captured.out
    assert "total_biogas_Nm3" in captured.out
    assert "CH4_vol_percent" in captured.out