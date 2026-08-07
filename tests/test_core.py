import pytest

from biopotgas.core import (
    calculate_biogas_from_elements,
    calculate_biogas_from_formula,
    parse_empirical_formula,
    calculate_biogas_from_components,
    ComponentFlow,
    ElementalComposition,
)

def test_parse_formula():
    comp = parse_empirical_formula("CH1.57O0.31N0.29S0.007")

    assert comp.C == pytest.approx(1.0)
    assert comp.H == pytest.approx(1.57)
    assert comp.O == pytest.approx(0.31)
    assert comp.N == pytest.approx(0.29)
    assert comp.S == pytest.approx(0.007)


def test_cellulose_like_formula_generates_methane():
    result = calculate_biogas_from_formula("C6H10O5", molar_flow=1.0)

    assert result.ch4_mol > 0
    assert result.co2_mol > 0

def test_cellulose_buswell_at_full_carbon_conversion():
    result = calculate_biogas_from_formula(
        "C6H10O5",
        molar_flow=1.0,
        carbon_conversion=1.0,
    )

    assert result.ch4_mol == pytest.approx(3.0)
    assert result.co2_mol == pytest.approx(3.0)
    assert result.nh3_mol == pytest.approx(0.0)
    assert result.h2s_mol == pytest.approx(0.0)
    assert result.inert_carbon_mol == pytest.approx(0.0)


@pytest.mark.parametrize("carbon_conversion", [-0.1, 1.1])
def test_invalid_carbon_conversion_raises_value_error(carbon_conversion):
    with pytest.raises(ValueError):
        calculate_biogas_from_elements(
            c_mol=1.0,
            h_mol=4.0,
            o_mol=0.0,
            carbon_conversion=carbon_conversion,
        )


def test_formula_without_carbon_is_rejected():
    with pytest.raises(ValueError):
        parse_empirical_formula("H2O")

def test_cellulose_buswell_reports_water_consumption():
    result = calculate_biogas_from_formula(
        "C6H10O5",
        molar_flow=1.0,
        carbon_conversion=1.0,
    )

    assert result.ch4_mol == pytest.approx(3.0)
    assert result.co2_mol == pytest.approx(3.0)
    assert result.h2o_mol == pytest.approx(1.0)


def test_glucose_buswell_reports_no_net_water_balance():
    result = calculate_biogas_from_formula(
        "C6H12O6",
        molar_flow=1.0,
        carbon_conversion=1.0,
    )

    assert result.ch4_mol == pytest.approx(3.0)
    assert result.co2_mol == pytest.approx(3.0)
    assert result.h2o_mol == pytest.approx(0.0)


def test_acetic_acid_buswell_reports_no_net_water_balance():
    result = calculate_biogas_from_formula(
        "C2H4O2",
        molar_flow=1.0,
        carbon_conversion=1.0,
    )

    assert result.ch4_mol == pytest.approx(1.0)
    assert result.co2_mol == pytest.approx(1.0)
    assert result.h2o_mol == pytest.approx(0.0)

def test_non_degradable_components_are_excluded_from_buswell_calculation():
    degradable = ComponentFlow(
        name="DEGRADABLE",
        molar_flow=1.0,
        composition=ElementalComposition(C=1, H=4, O=0, N=0, S=0),
        degradable=True,
    )
    non_degradable = ComponentFlow(
        name="NON_DEGRADABLE",
        molar_flow=1.0,
        composition=ElementalComposition(C=1, H=4, O=0, N=0, S=0),
        degradable=False,
    )

    result = calculate_biogas_from_components(
        [degradable, non_degradable],
        carbon_conversion=1.0,
    )

    reference = calculate_biogas_from_components(
        [degradable],
        carbon_conversion=1.0,
    )

    assert result.ch4_mol == reference.ch4_mol
    assert result.co2_mol == reference.co2_mol
    assert result.inert_carbon_mol == reference.inert_carbon_mol

import pytest

from biopotgas.core import ElementalComposition, ComponentFlow, calculate_biogas_from_components


def test_negative_elemental_composition_is_rejected():
    component = ComponentFlow(
        name="INVALID",
        molar_flow=1.0,
        composition=ElementalComposition(C=-1, H=4, O=0, N=0, S=0),
        degradable=True,
    )

    with pytest.raises(ValueError):
        calculate_biogas_from_components([component])