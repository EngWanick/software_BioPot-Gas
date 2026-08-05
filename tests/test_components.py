import pytest

from biopotgas.components import COMPONENT_FORMULAS, get_component_composition


def test_component_database_does_not_include_water():
    assert "WATER" not in COMPONENT_FORMULAS


def test_get_component_composition_rejects_water_name():
    with pytest.raises(KeyError, match="WATER"):
        get_component_composition("WATER")


def test_get_component_composition_reads_known_organic_component():
    composition = get_component_composition("GLUCOSE")

    assert composition.C == pytest.approx(6.0)
    assert composition.H == pytest.approx(12.0)
    assert composition.O == pytest.approx(6.0)