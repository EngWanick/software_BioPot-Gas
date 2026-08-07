from __future__ import annotations

from pathlib import Path
from typing import List
from dataclasses import dataclass
import csv

from .core import ComponentFlow, parse_empirical_formula
from .components import get_component_composition
from .input_utils import is_free_water_entry

@dataclass(frozen=True)
class CSVInputData:
    components: List[ComponentFlow]
    water_available_mol: float = 0.0

def read_components_csv(path: str | Path) -> CSVInputData:
    """
    Read component flows from a CSV file for programmatic use without Excel.

    This function is an alternative input adapter for users who want to call
    the BioPot-Gas computational core directly, without the XLSX template.

    Required columns
    ----------------
    name:
        Component name.
    molar_flow:
        Component molar flow in any consistent molar unit.

    Optional columns
    ----------------
    formula:
        Empirical formula. If empty, the component name is searched in the
        internal component database.
    degradable:
        true/false. If absent or empty, true is assumed.

    Returns
    -------
    CSVInputData
        Component records and free-water quantity read from CSV. Component records
        are suitable for calculate_biogas_from_components().
    """

    records: List[ComponentFlow] = []
    water_available_mol = 0.0
    path = Path(path)

    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)

        required = {"name", "molar_flow"}
        missing = required.difference(reader.fieldnames or [])
        if missing:
            raise ValueError(f"Missing required CSV columns: {sorted(missing)}")

        for row_number, row in enumerate(reader, start=2):
            name = row["name"].strip()
            molar_flow_text = (row.get("molar_flow") or "").strip()

            if molar_flow_text == "":
                raise ValueError(
                    f"Missing molar_flow for component {name!r} at CSV row {row_number}."
                )

            try:
                molar_flow = float(molar_flow_text)
            except ValueError as exc:
                raise ValueError(
                    f"Invalid molar_flow for component {name!r} at CSV row {row_number}: "
                    f"{molar_flow_text!r}"
                ) from exc

            formula = (row.get("formula") or "").strip()
            input_mode = (row.get("input_mode") or "").strip()

            if is_free_water_entry(name, formula, input_mode):
                water_available_mol += molar_flow
                continue

            if formula:
                try:
                    composition = parse_empirical_formula(formula)
                except ValueError as exc:
                    raise ValueError(
                        f"Invalid formula for component {name!r} at CSV row {row_number}: "
                        f"{formula!r}"
                    ) from exc
            else:
                try:
                    composition = get_component_composition(name)
                except ValueError as exc:
                    raise ValueError(
                        f"Unknown component {name!r} at CSV row {row_number}. "
                        f"Provide a formula or use a component name from the internal database."
                    ) from exc

            degradable_text = (row.get("degradable") or "true").strip().lower()
            degradable = degradable_text not in {"false", "0", "no", "não", "nao"}

            records.append(
                ComponentFlow(
                    name=name,
                    molar_flow=molar_flow,
                    composition=composition,
                    degradable=degradable,
                )
            )

    return CSVInputData(
        components=records,
        water_available_mol=water_available_mol,
    )
