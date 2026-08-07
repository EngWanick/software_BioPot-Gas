from __future__ import annotations

from dataclasses import replace
from typing import Iterable

from .constants import MOLECULAR_WEIGHTS_KG_PER_KMOL
from .core import ComponentFlow, ElementalComposition


SUPPORTED_MOLAR_UNITS = {"kmol", "mol", "kmol/h", "mol/h"}
SUPPORTED_MASS_UNITS = {"ton", "kg", "g", "ton/h", "kg/h", "g/h"}


def normalize_input_basis(input_basis_type: str, input_unit: str) -> tuple[str, str]:
    basis = str(input_basis_type).strip().lower()
    unit = str(input_unit).strip()

    if basis not in {"molar", "mass"}:
        raise ValueError(
            f"Unsupported input_basis_type {input_basis_type!r}. "
            "Use 'molar' or 'mass'."
        )

    if basis == "molar" and unit not in SUPPORTED_MOLAR_UNITS:
        raise ValueError(
            f"Unsupported input_unit {input_unit!r} for molar basis. "
            "Use one of: kmol, mol, kmol/h, mol/h."
        )

    if basis == "mass" and unit not in SUPPORTED_MASS_UNITS:
        raise ValueError(
            f"Unsupported input_unit {input_unit!r} for mass basis. "
            "Use one of: ton, kg, g, ton/h, kg/h, g/h."
        )

    return basis, unit


def molar_unit_factor_to_kmol(input_unit: str) -> float:
    if input_unit in {"kmol", "kmol/h"}:
        return 1.0
    if input_unit in {"mol", "mol/h"}:
        return 0.001

    raise ValueError(f"Unsupported molar input_unit {input_unit!r}.")


def mass_unit_factor_to_kg(input_unit: str) -> float:
    if input_unit in {"ton", "ton/h"}:
        return 1000.0
    if input_unit in {"kg", "kg/h"}:
        return 1.0
    if input_unit in {"g", "g/h"}:
        return 0.001

    raise ValueError(f"Unsupported mass input_unit {input_unit!r}.")


def basis_time_mode(input_unit: str) -> str:
    return "rate" if str(input_unit).strip().endswith("/h") else "amount"


def molecular_weight_kg_per_kmol(composition: ElementalComposition) -> float:
    return (
        composition.C * MOLECULAR_WEIGHTS_KG_PER_KMOL["C"]
        + composition.H * MOLECULAR_WEIGHTS_KG_PER_KMOL["H"]
        + composition.O * MOLECULAR_WEIGHTS_KG_PER_KMOL["O"]
        + composition.N * MOLECULAR_WEIGHTS_KG_PER_KMOL["N"]
        + composition.S * MOLECULAR_WEIGHTS_KG_PER_KMOL["S"]
    )


def convert_component_flows_to_internal_molar_basis(
    component_flows: Iterable[ComponentFlow],
    input_basis_type: str,
    input_unit: str,
) -> list[ComponentFlow]:
    basis, unit = normalize_input_basis(input_basis_type, input_unit)

    converted: list[ComponentFlow] = []

    if basis == "molar":
        factor = molar_unit_factor_to_kmol(unit)
        for component in component_flows:
            converted.append(
                replace(component, molar_flow=component.molar_flow * factor)
            )
        return converted

    mass_factor = mass_unit_factor_to_kg(unit)
    for component in component_flows:
        mw = molecular_weight_kg_per_kmol(component.composition)
        if mw <= 0:
            raise ValueError(
                f"Invalid molecular weight for component {component.name!r}: {mw}."
            )

        mass_kg = component.molar_flow * mass_factor
        converted.append(
            replace(component, molar_flow=mass_kg / mw)
        )

    return converted


def convert_water_to_internal_molar_basis(
    water_quantity: float,
    input_basis_type: str,
    input_unit: str,
) -> float:
    basis, unit = normalize_input_basis(input_basis_type, input_unit)

    if basis == "molar":
        return water_quantity * molar_unit_factor_to_kmol(unit)

    mass_kg = water_quantity * mass_unit_factor_to_kg(unit)
    return mass_kg / MOLECULAR_WEIGHTS_KG_PER_KMOL["H2O"]


def internal_molar_basis_label(input_unit: str) -> str:
    return "kmol/h" if basis_time_mode(input_unit) == "rate" else "kmol"