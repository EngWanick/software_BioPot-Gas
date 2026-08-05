from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable
import re


@dataclass(frozen=True)
class ElementalComposition:
    """Elemental composition in mol of atoms per mol of component."""

    C: float
    H: float
    O: float
    N: float = 0.0
    S: float = 0.0


@dataclass(frozen=True)
class ComponentFlow:
    """Component molar flow and elemental composition."""

    name: str
    molar_flow: float
    composition: ElementalComposition
    degradable: bool = True


@dataclass(frozen=True)
class BiogasResult:
    """Theoretical biogas result in molar basis."""

    ch4_mol: float
    co2_mol: float
    nh3_mol: float
    h2s_mol: float
    h2o_mol: float
    inert_carbon_mol: float
    c_available_mol: float
    c_total_mol: float
    h_total_mol: float
    o_total_mol: float
    n_total_mol: float
    s_total_mol: float

    @property
    def total_gas_mol(self) -> float:
        return self.ch4_mol + self.co2_mol + self.nh3_mol + self.h2s_mol

    @property
    def methane_fraction_mol(self) -> float:
        if self.total_gas_mol <= 0:
            return 0.0
        return self.ch4_mol / self.total_gas_mol


def parse_empirical_formula(formula: str) -> ElementalComposition:
    """
    Parse an empirical formula containing C, H, O, N and S.

    Examples
    --------
    C6H10O5
    CH1.57O0.31N0.29S0.007
    C7.3H13.9O1.3
    """

    if not formula or not isinstance(formula, str):
        raise ValueError("The empirical formula must be a non-empty string.")

    pattern = r"([CHONS])([0-9]*\.?[0-9]*)"
    matches = re.findall(pattern, formula.strip())

    if not matches:
        raise ValueError(f"Invalid empirical formula: {formula!r}")

    values = {"C": 0.0, "H": 0.0, "O": 0.0, "N": 0.0, "S": 0.0}

    consumed = "".join(element + number for element, number in matches)
    if consumed != formula.strip():
        raise ValueError(
            "The formula contains unsupported elements or invalid characters. "
            "Only C, H, O, N and S are currently supported."
        )

    for element, number in matches:
        values[element] += float(number) if number else 1.0

    if values["C"] <= 0:
        raise ValueError("The empirical formula must contain carbon.")

    return ElementalComposition(**values)


def calculate_biogas_from_elements(
    c_mol: float,
    h_mol: float,
    o_mol: float,
    n_mol: float = 0.0,
    s_mol: float = 0.0,
    carbon_conversion: float = 0.95,
    validate_non_negative: bool = True,
) -> BiogasResult:
    """
    Estimate theoretical biogas production by the modified Buswell equation.

    The calculation uses elemental molar amounts of C, H, O, N and S and returns
    the theoretical molar production of CH4, CO2, NH3 and H2S.

    Parameters
    ----------
    c_mol, h_mol, o_mol, n_mol, s_mol:
        Elemental molar amounts in the degradable substrate.
    carbon_conversion:
        Fraction of carbon routed to biogas formation. Default is 0.95.
        The remaining carbon is reported as inert_carbon_mol.
    validate_non_negative:
        If True, raises an error when CH4 or CO2 becomes negative.

    Notes
    -----
    Modified Buswell form:

    CcHhOoNnSs + water -> CO2 + CH4 + NH3 + H2S

    CO2 = c/2 - h/8 + o/4 + 3n/8 + s/4
    CH4 = c/2 + h/8 - o/4 - 3n/8 - s/4
    NH3 = n
    H2S = s
    H2O = c - h/4 - o/2 + 3n/4 + s/2

    Positive H2O means net water consumption. Negative H2O means net water production.
    """

    values = [c_mol, h_mol, o_mol, n_mol, s_mol]
    if any(v < 0 for v in values):
        raise ValueError("Elemental molar amounts must be non-negative.")

    if not (0.0 <= carbon_conversion <= 1.0):
        raise ValueError("carbon_conversion must be between 0 and 1.")

    c_available = c_mol * carbon_conversion
    inert_carbon = c_mol * (1.0 - carbon_conversion)

    co2 = (
        (c_available / 2.0)
        - (h_mol / 8.0)
        + (o_mol / 4.0)
        + (3.0 * n_mol / 8.0)
        + (s_mol / 4.0)
    )
    ch4 = (
        (c_available / 2.0)
        + (h_mol / 8.0)
        - (o_mol / 4.0)
        - (3.0 * n_mol / 8.0)
        - (s_mol / 4.0)
    )

    nh3 = n_mol
    h2s = s_mol

    h2o = (
        c_available
        - (h_mol / 4.0)
        - (o_mol / 2.0)
        + (3.0 * n_mol / 4.0)
        + (s_mol / 2.0)
    )

    if validate_non_negative and (ch4 < -1e-12 or co2 < -1e-12):
        raise ValueError(
            "Negative CH4 or CO2 was calculated. Check the elemental composition, "
            "basis, and degradable fraction."
        )

    ch4 = max(ch4, 0.0)
    co2 = max(co2, 0.0)

    return BiogasResult(
        ch4_mol=ch4,
        co2_mol=co2,
        nh3_mol=nh3,
        h2s_mol=h2s,
        h2o_mol=h2o,
        inert_carbon_mol=inert_carbon,
        c_available_mol=c_available,
        c_total_mol=c_mol,
        h_total_mol=h_mol,
        o_total_mol=o_mol,
        n_total_mol=n_mol,
        s_total_mol=s_mol,
    )


def calculate_biogas_from_formula(
    formula: str,
    molar_flow: float = 1.0,
    carbon_conversion: float = 0.95,
) -> BiogasResult:
    """
    Estimate biogas from an empirical formula and molar flow.

    Parameters
    ----------
    formula:
        Empirical formula, for example C6H10O5 or CH1.57O0.31N0.29S0.007.
    molar_flow:
        Moles of substrate represented by the empirical formula.
    carbon_conversion:
        Fraction of carbon available for biogas formation.
    """

    if molar_flow < 0:
        raise ValueError("molar_flow must be non-negative.")

    comp = parse_empirical_formula(formula)

    return calculate_biogas_from_elements(
        c_mol=comp.C * molar_flow,
        h_mol=comp.H * molar_flow,
        o_mol=comp.O * molar_flow,
        n_mol=comp.N * molar_flow,
        s_mol=comp.S * molar_flow,
        carbon_conversion=carbon_conversion,
    )


def calculate_biogas_from_components(
    component_flows: Iterable[ComponentFlow],
    carbon_conversion: float = 0.95,
    include_non_degradable: bool = False,
) -> BiogasResult:
    """
    Estimate biogas from a list of components with molar flows and formulas.

    Parameters
    ----------
    component_flows:
        Iterable of ComponentFlow records.
    carbon_conversion:
        Fraction of carbon available for biogas formation.
    include_non_degradable:
        If False, only degradable components enter the Buswell calculation.
    """

    C = H = O = N = S = 0.0

    for item in component_flows:
        if (not include_non_degradable) and (not item.degradable):
            continue

        if item.molar_flow < 0:
            raise ValueError(f"Negative molar flow for component {item.name!r}.")

        C += item.composition.C * item.molar_flow
        H += item.composition.H * item.molar_flow
        O += item.composition.O * item.molar_flow
        N += item.composition.N * item.molar_flow
        S += item.composition.S * item.molar_flow

    return calculate_biogas_from_elements(
        c_mol=C,
        h_mol=H,
        o_mol=O,
        n_mol=N,
        s_mol=S,
        carbon_conversion=carbon_conversion,
    )
