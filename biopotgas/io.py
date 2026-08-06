from __future__ import annotations

from pathlib import Path
from typing import List
import csv

from .core import ComponentFlow, parse_empirical_formula
from .components import get_component_composition


def read_components_csv(path: str | Path) -> List[ComponentFlow]:
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
    list[ComponentFlow]
        Component records suitable for calculate_biogas_from_components().
    """

    records: List[ComponentFlow] = []
    path = Path(path)

    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)

        required = {"name", "molar_flow"}
        missing = required.difference(reader.fieldnames or [])
        if missing:
            raise ValueError(f"Missing required CSV columns: {sorted(missing)}")

        for row in reader:
            name = row["name"].strip()
            molar_flow_text = (row.get("molar_flow") or "").strip()

            if molar_flow_text == "":
                raise ValueError(f"Missing molar_flow for component {name!r}.")

            try:
                molar_flow = float(molar_flow_text)
            except ValueError as exc:
                raise ValueError(
                    f"Invalid molar_flow for component {name!r}: {molar_flow_text!r}"
                ) from exc

            formula = (row.get("formula") or "").strip()
            if formula:
                composition = parse_empirical_formula(formula)
            else:
                composition = get_component_composition(name)

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

    return records
