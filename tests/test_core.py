from biopotgas.core import parse_empirical_formula, calculate_biogas_from_formula


def test_parse_formula():
    comp = parse_empirical_formula("CH1.57O0.31N0.29S0.007")
    assert comp.C == 1.0
    assert comp.H == 1.57
    assert comp.O == 0.31
    assert comp.N == 0.29
    assert comp.S == 0.007


def test_cellulose_like_formula_generates_methane():
    result = calculate_biogas_from_formula("C6H10O5", molar_flow=1.0)
    assert result.ch4_mol > 0
    assert result.co2_mol > 0
