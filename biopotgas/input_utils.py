from __future__ import annotations

def is_free_water_entry(
    name: object,
    formula: object = None,
    input_mode: object = None,
) -> bool:
    name_text = str(name or "").strip().upper()
    formula_text = str(formula or "").strip().upper()
    mode_text = str(input_mode or "").strip().upper()

    return (
        name_text in {"WATER", "H2O", "ÁGUA", "AGUA"}
        or formula_text == "H2O"
        or mode_text == "WATER"
    )
