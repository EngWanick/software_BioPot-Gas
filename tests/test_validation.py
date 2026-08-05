import pytest

from biopotgas.validation import (
    classify_conversion_efficiency,
    compare_experimental_to_theoretical,
)


@pytest.mark.parametrize(
    ("efficiency", "expected"),
    [
        (None, "Não calculado"),
        (49.9, "Baixa conversão experimental"),
        (50.0, "Conversão intermediária"),
        (79.9, "Conversão intermediária"),
        (80.0, "Conversão elevada"),
        (100.0, "Conversão elevada"),
        (100.1, "Verificar base experimental ou composição de entrada"),
    ],
)
def test_classify_conversion_efficiency_thresholds(efficiency, expected):
    assert classify_conversion_efficiency(efficiency) == expected


def test_compare_experimental_to_theoretical_calculates_signed_errors():
    result = compare_experimental_to_theoretical(
        experimental_ch4_nm3=90.0,
        experimental_biogas_nm3=180.0,
        experimental_ch4_percent=50.0,
        theoretical_ch4_nm3=100.0,
        theoretical_biogas_nm3=200.0,
    )

    assert result["absolute_error_CH4_Nm3"] == pytest.approx(10.0)
    assert result["signed_error_CH4_Nm3"] == pytest.approx(-10.0)
    assert result["relative_error_CH4_percent"] == pytest.approx(10.0)
    assert result["signed_relative_error_CH4_percent"] == pytest.approx(-10.0)
    assert result["conversion_efficiency_percent"] == pytest.approx(90.0)

    assert result["absolute_error_biogas_Nm3"] == pytest.approx(20.0)
    assert result["signed_error_biogas_Nm3"] == pytest.approx(-20.0)
    assert result["relative_error_biogas_percent"] == pytest.approx(10.0)
    assert result["signed_relative_error_biogas_percent"] == pytest.approx(-10.0)

    assert result["validation_status"] == "Conversão elevada"

    assert result["validation_basis_note"] == (
        "conversion_efficiency_percent is calculated as experimental CH4_Nm3 "
        "divided by theoretical CH4_Nm3. Error fields are signed deviations "
        "computed as experimental minus theoretical values."
    )

def test_compare_experimental_to_theoretical_handles_missing_experimental_data():
    result = compare_experimental_to_theoretical(
        experimental_ch4_nm3=None,
        experimental_biogas_nm3=None,
        experimental_ch4_percent=None,
        theoretical_ch4_nm3=100.0,
        theoretical_biogas_nm3=200.0,
    )

    assert result["absolute_error_CH4_Nm3"] is None
    assert result["relative_error_CH4_percent"] is None
    assert result["conversion_efficiency_percent"] is None
    assert result["absolute_error_biogas_Nm3"] is None
    assert result["relative_error_biogas_percent"] is None
    assert result["CH4_percent_deviation"] is None
    assert result["signed_error_CH4_Nm3"] is None
    assert result["signed_relative_error_CH4_percent"] is None
    assert result["signed_error_biogas_Nm3"] is None
    assert result["signed_relative_error_biogas_percent"] is None
    assert result["validation_status"] == "Não calculado"


def test_compare_experimental_to_theoretical_classifies_efficiency_above_100():
    result = compare_experimental_to_theoretical(
        experimental_ch4_nm3=120.0,
        experimental_biogas_nm3=220.0,
        experimental_ch4_percent=55.0,
        theoretical_ch4_nm3=100.0,
        theoretical_biogas_nm3=200.0,
    )

    assert result["conversion_efficiency_percent"] == pytest.approx(120.0)
    assert result["validation_status"] == (
        "Verificar base experimental ou composição de entrada"
    )

def test_compare_experimental_to_theoretical_warns_about_invalid_experimental_values():
    result = compare_experimental_to_theoretical(
        experimental_ch4_nm3="abc",
        experimental_biogas_nm3=200.0,
        experimental_ch4_percent=50.0,
        theoretical_ch4_nm3=100.0,
        theoretical_biogas_nm3=200.0,
    )

    assert result["absolute_error_CH4_Nm3"] is None
    assert result["conversion_efficiency_percent"] is None
    assert "Invalid experimental_CH4_Nm3 value ignored: 'abc'." in result["warning"]