from __future__ import annotations

from pathlib import Path
from typing import List
from dataclasses import dataclass
import csv

from .core import ComponentFlow, parse_empirical_formula
from .components import get_component_composition
from .input_utils import is_free_water_entry
from .input_units import (
    basis_time_mode,
    convert_component_flows_to_internal_molar_basis,
    convert_water_to_internal_molar_basis,
    internal_molar_basis_label,
)

@dataclass(frozen=True)
class CSVInputData:
    components: List[ComponentFlow]
    water_available_mol: float = 0.0
    input_basis_type: str = "molar"
    input_unit: str = "kmol"
    internal_molar_basis: str = "kmol"
    basis_time_mode: str = "amount"

def read_components_csv(
        path: str | Path,
        input_basis_type: str | None = None,
        input_unit: str | None = None,
    ) -> CSVInputData:
    """
    Read component inputs from a CSV file for programmatic use without Excel.

    The CSV reader supports the current input contract through
    input_quantity, input_basis_type, and input_unit, while preserving
    compatibility with the legacy name + molar_flow interface.

    Supported current columns
    -------------------------
    component_name:
        Component name. The legacy column name is also accepted as name.
    input_quantity:
        Numeric feed value. The legacy column name molar_flow is also accepted.
    input_basis_type:
        Global input basis: molar or mass.
    input_unit:
        Global input unit.

    Optional columns
    ----------------
    formula:
        Empirical formula. If empty, the component name is searched in the
        internal component database.
    degradable:
        true/false. If absent or empty, true is assumed.
    input_mode:
        Optional mode marker. WATER marks a free-water row.

    Returns
    -------
    CSVInputData
        Component records converted to the internal molar basis, plus free-water
        quantity converted to the same internal basis.
    """

    raw_records: List[ComponentFlow] = []
    raw_water_available = 0.0
    path = Path(path)

    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = set(reader.fieldnames or [])

        name_column = None
        if "component_name" in fieldnames:
            name_column = "component_name"
        elif "name" in fieldnames:
            name_column = "name"

        quantity_column = None
        if "input_quantity" in fieldnames:
            quantity_column = "input_quantity"
        elif "molar_flow" in fieldnames:
            quantity_column = "molar_flow"

        missing = []
        if name_column is None:
            missing.append("component_name or name")
        if quantity_column is None:
            missing.append("input_quantity or molar_flow")

        if missing:
            raise ValueError(f"Missing required CSV columns: {missing}")

        rows = list(reader)

        file_basis_values = {
            (row.get("input_basis_type") or "").strip().lower()
            for row in rows
            if (row.get("input_basis_type") or "").strip()
        }
        file_unit_values = {
            (row.get("input_unit") or "").strip()
            for row in rows
            if (row.get("input_unit") or "").strip()
        }

        if len(file_basis_values) > 1:
            raise ValueError(
                f"CSV input_basis_type must be global and consistent across rows."
            )

        if len(file_unit_values) > 1:
            raise ValueError(
                f"CSV input_unit must be global and consistent across rows."
            )

        resolved_input_basis_type = (
            input_basis_type
            or next(iter(file_basis_values), None)
            or "molar"
        )
        resolved_input_unit = (
            input_unit
            or next(iter(file_unit_values), None)
            or "kmol"
        )

        resolved_input_basis_type = str(resolved_input_basis_type).strip().lower()
        resolved_input_unit = str(resolved_input_unit).strip()

        for row_number, row in enumerate(rows, start=2):
            name = (row.get(name_column) or "").strip()
            quantity_text = (row.get(quantity_column) or "").strip()

            if not name:
                raise ValueError(f"Missing component name at CSV row {row_number}.")

            if quantity_text == "":
                raise ValueError(
                    f"Missing {quantity_column} for component {name!r} "
                    f"at CSV row {row_number}."
                )

            try:
                input_quantity = float(quantity_text)
            except ValueError as exc:
                raise ValueError(
                    f"Invalid {quantity_column} for component {name!r} "
                    f"at CSV row {row_number}: {quantity_text!r}"
                ) from exc

            formula = (row.get("formula") or "").strip()
            input_mode = (row.get("input_mode") or "").strip()

            if is_free_water_entry(name, formula, input_mode):
                raw_water_available += input_quantity
                continue

            if formula:
                try:
                    composition = parse_empirical_formula(formula)
                except ValueError as exc:
                    raise ValueError(
                        f"Invalid formula for component {name!r} at CSV row "
                        f"{row_number}: {formula!r}"
                    ) from exc
            else:
                try:
                    composition = get_component_composition(name)
                except ValueError as exc:
                    raise ValueError(
                        f"Unknown component {name!r} at CSV row {row_number}. "
                        f"Provide a formula or use a component name from the "
                        f"internal database."
                    ) from exc

            degradable_text = (row.get("degradable") or "true").strip().lower()
            degradable = degradable_text not in {"false", "0", "no", "não", "nao"}

            raw_records.append(
                ComponentFlow(
                    name=name,
                    molar_flow=input_quantity,
                    composition=composition,
                    degradable=degradable,
                )
            )

    converted_records = convert_component_flows_to_internal_molar_basis(
        raw_records,
        input_basis_type=resolved_input_basis_type,
        input_unit=resolved_input_unit,
    )

    converted_water_available = convert_water_to_internal_molar_basis(
        raw_water_available,
        input_basis_type=resolved_input_basis_type,
        input_unit=resolved_input_unit,
    )

    return CSVInputData(
        components=converted_records,
        water_available_mol=converted_water_available,
        input_basis_type=resolved_input_basis_type,
        input_unit=resolved_input_unit,
        internal_molar_basis=internal_molar_basis_label(resolved_input_unit),
        basis_time_mode=basis_time_mode(resolved_input_unit),
    )
