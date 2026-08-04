from __future__ import annotations

from .core import ElementalComposition, parse_empirical_formula


# Initial component database based on common components used in lignocellulosic
# and anaerobic digestion models. This file can be expanded with the exact
# component set adopted in each project.
COMPONENT_FORMULAS = {
    "WATER": "H2O",
    "GLUCOSE": "C6H12O6",
    "SUCROSE": "C12H22O11",
    "ACETIC_ACID": "C2H4O2",
    "XYLOSE": "C5H10O5",
    "GALACTOSE": "C6H12O6",
    "ARABINOSE": "C5H10O5",
    "GLUCAN": "C6H10O5",
    "XYLAN": "C5H8O4",
    "GALACTAN": "C6H10O5",
    "ARABINAN": "C5H8O4",
    "ETHANOL": "C2H6O",
    "FURFURAL": "C5H4O2",
    "GLYCEROL": "C3H8O3",
    "GLUTARIC_ACID": "C5H8O4",
    "DEXTROSE": "C6H12O6",
    "PROTEIN_GENERIC": "CH1.57O0.31N0.29S0.007",
    "LIGNIN_GENERIC": "C7.3H13.9O1.3",
    "BIOMASS_GENERIC": "CH1.64O0.39N0.23S0.0035",
    "ENZYME_GENERIC": "CH1.8O0.5N0.2",
}


def get_component_composition(component_name: str) -> ElementalComposition:
    """Return elemental composition for a component available in the database."""

    key = component_name.strip().upper()
    if key not in COMPONENT_FORMULAS:
        raise KeyError(
            f"Component {component_name!r} not found. "
            "Add it to COMPONENT_FORMULAS or provide an empirical formula directly."
        )

    return parse_empirical_formula(COMPONENT_FORMULAS[key])
