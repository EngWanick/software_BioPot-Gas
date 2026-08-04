from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Any

from openpyxl import load_workbook

from .core import ComponentFlow, ElementalComposition, calculate_biogas_from_components, parse_empirical_formula
from .report import result_to_dict
from .validation import compare_experimental_to_theoretical


@dataclass(frozen=True)
class ExcelInputData:
    global_parameters: Dict[str, Any]
    components: List[ComponentFlow]
    database: Dict[str, ElementalComposition]


def _to_bool(value: Any, default: bool = True) -> bool:
    if value is None or value == "":
        return default
    if isinstance(value, bool):
        return value
    text = str(value).strip().lower()
    if text in {"true", "1", "yes", "sim", "s"}:
        return True
    if text in {"false", "0", "no", "não", "nao", "n"}:
        return False
    return default


def _to_float(value: Any, field_name: str, row_number: int | None = None) -> float:
    if value is None or value == "":
        return 0.0
    try:
        return float(value)
    except Exception as exc:
        location = f" at row {row_number}" if row_number else ""
        raise ValueError(f"Invalid numeric value for {field_name}{location}: {value!r}") from exc


def _get_header_map(ws, header_row: int) -> Dict[str, int]:
    values = [ws.cell(row=header_row, column=col).value for col in range(1, ws.max_column + 1)]
    return {str(v).strip(): idx + 1 for idx, v in enumerate(values) if v is not None and str(v).strip()}


def read_component_database(wb) -> Dict[str, ElementalComposition]:
    if "03_COMPONENT_DATABASE" not in wb.sheetnames:
        return {}

    ws = wb["03_COMPONENT_DATABASE"]
    header_row = None
    for row in range(1, ws.max_row + 1):
        row_values = [ws.cell(row=row, column=col).value for col in range(1, ws.max_column + 1)]
        normalized = [str(v).strip() if v is not None else "" for v in row_values]
        if "component_name" in normalized and "formula" in normalized:
            header_row = row
            break

    if header_row is None:
        return {}

    headers = _get_header_map(ws, header_row)
    database: Dict[str, ElementalComposition] = {}

    for row in range(header_row + 1, ws.max_row + 1):
        name = ws.cell(row=row, column=headers["component_name"]).value
        if name is None or str(name).strip() == "":
            continue

        active_col = headers.get("active")
        active = _to_bool(ws.cell(row=row, column=active_col).value, default=True) if active_col else True
        if not active:
            continue

        formula = ws.cell(row=row, column=headers["formula"]).value
        if formula is None or str(formula).strip() == "":
            continue

        database[str(name).strip().upper()] = parse_empirical_formula(str(formula).strip())

    return database


def read_biopotgas_excel(path: str | Path, sheet_name: str = "01_INPUTS") -> ExcelInputData:
    path = Path(path)
    wb = load_workbook(path, data_only=True)

    if sheet_name not in wb.sheetnames:
        raise ValueError(f"Sheet {sheet_name!r} was not found in {path.name}.")

    database = read_component_database(wb)
    ws = wb[sheet_name]

    global_parameters: Dict[str, Any] = {}
    for row in range(4, 18):
        key = ws[f"A{row}"].value
        value = ws[f"B{row}"].value
        if key:
            global_parameters[str(key).strip()] = value

    header_row = None
    headers: Dict[str, int] = {}
    for row in range(1, ws.max_row + 1):
        row_values = [ws.cell(row=row, column=col).value for col in range(1, ws.max_column + 1)]
        normalized = [str(v).strip() if v is not None else "" for v in row_values]
        if "component_name" in normalized and "molar_flow" in normalized:
            header_row = row
            headers = {name: idx + 1 for idx, name in enumerate(normalized) if name}
            break

    if header_row is None:
        raise ValueError("The component input table header was not found.")

    required_columns = {"component_name", "molar_flow", "degradable", "input_mode", "active_row"}
    missing = required_columns.difference(headers)
    if missing:
        raise ValueError(f"Missing required columns in input table: {sorted(missing)}")

    components: List[ComponentFlow] = []
    empty_rows = 0

    for row in range(header_row + 1, ws.max_row + 1):
        name_value = ws.cell(row=row, column=headers["component_name"]).value
        name_text = "" if name_value is None else str(name_value).strip()

        if name_text.lower().startswith("regras de preenchimento"):
            break

        row_values = [ws.cell(row=row, column=col).value for col in range(1, ws.max_column + 1)]
        if all(value is None or str(value).strip() == "" for value in row_values):
            empty_rows += 1
            if empty_rows >= 3:
                break
            continue

        empty_rows = 0

        if name_text == "":
            continue

        active = _to_bool(ws.cell(row=row, column=headers["active_row"]).value, default=True)
        if not active:
            continue

        name = name_text
        molar_flow = _to_float(ws.cell(row=row, column=headers["molar_flow"]).value, "molar_flow", row)
        degradable = _to_bool(ws.cell(row=row, column=headers["degradable"]).value, default=True)
        input_mode = str(ws.cell(row=row, column=headers["input_mode"]).value or "DATABASE").strip().upper()

        formula = ws.cell(row=row, column=headers["formula"]).value if "formula" in headers else None

        if input_mode == "DATABASE":
            key = name.strip().upper()
            if key not in database:
                raise KeyError(f"Component {name!r} was not found in 03_COMPONENT_DATABASE.")
            composition = database[key]
        elif input_mode == "FORMULA":
            if formula is None or str(formula).strip() == "":
                raise ValueError(f"Formula is required for component {name!r} at row {row}.")
            composition = parse_empirical_formula(str(formula).strip())
        elif input_mode == "ELEMENTS":
            composition = ElementalComposition(
                C=_to_float(ws.cell(row=row, column=headers["C_atoms"]).value, "C_atoms", row),
                H=_to_float(ws.cell(row=row, column=headers["H_atoms"]).value, "H_atoms", row),
                O=_to_float(ws.cell(row=row, column=headers["O_atoms"]).value, "O_atoms", row),
                N=_to_float(ws.cell(row=row, column=headers["N_atoms"]).value, "N_atoms", row),
                S=_to_float(ws.cell(row=row, column=headers["S_atoms"]).value, "S_atoms", row),
            )
        else:
            raise ValueError(f"Invalid input_mode for component {name!r} at row {row}: {input_mode!r}.")

        components.append(ComponentFlow(name=name, molar_flow=molar_flow, composition=composition, degradable=degradable))

    return ExcelInputData(global_parameters=global_parameters, components=components, database=database)


def calculate_from_excel(path: str | Path, sheet_name: str = "01_INPUTS") -> dict:
    data = read_biopotgas_excel(path, sheet_name=sheet_name)

    carbon_conversion = float(data.global_parameters.get("carbon_conversion", 0.95))
    include_non_degradable = _to_bool(data.global_parameters.get("include_non_degradable", False), default=False)
    normal_temperature_C = float(data.global_parameters.get("normal_temperature_C", 0.0))
    normal_pressure_kPa = float(data.global_parameters.get("normal_pressure_kPa", 101.325))
    ch4_lhv_mj_per_Nm3 = float(data.global_parameters.get("CH4_LHV_MJ_per_Nm3", 35.8))
    kwh_per_mj = float(data.global_parameters.get("kWh_per_MJ", 0.277778))

    result = calculate_biogas_from_components(
        data.components,
        carbon_conversion=carbon_conversion,
        include_non_degradable=include_non_degradable,
    )

    output = result_to_dict(
        result,
        normal_temperature_C=normal_temperature_C,
        normal_pressure_kPa=normal_pressure_kPa,
        ch4_lhv_mj_per_Nm3=ch4_lhv_mj_per_Nm3,
        kwh_per_mj=kwh_per_mj,
    )

    output["number_of_components_read"] = len(data.components)
    output["carbon_conversion"] = carbon_conversion
    output["include_non_degradable"] = include_non_degradable
    output["normal_temperature_C"] = normal_temperature_C
    output["normal_pressure_kPa"] = normal_pressure_kPa
    output["CH4_LHV_MJ_per_Nm3"] = ch4_lhv_mj_per_Nm3
    output["kWh_per_MJ"] = kwh_per_mj
    output["calculation_status"] = "Calculated successfully"
    output["warnings"] = ""

    return output


def write_outputs_to_excel(path: str | Path, output_path: str | Path | None = None, results: dict | None = None) -> Path:
    path = Path(path)
    if output_path is None:
        output_path = path.with_name(path.stem + "_calculated.xlsx")
    output_path = Path(output_path)

    if results is None:
        results = calculate_from_excel(path)

    wb = load_workbook(path)
    if "02_OUTPUTS" not in wb.sheetnames:
        wb.create_sheet("02_OUTPUTS")
    ws = wb["02_OUTPUTS"]

    for row in range(1, ws.max_row + 1):
        key = ws.cell(row=row, column=1).value
        if key is None:
            continue
        key = str(key).strip()
        if key in results:
            ws.cell(row=row, column=2).value = results[key]

    if "04_EXPERIMENTAL_VALIDATION" in wb.sheetnames:
        val = wb["04_EXPERIMENTAL_VALIDATION"]

        header_row = None
        for row in range(1, val.max_row + 1):
            values = [val.cell(row=row, column=col).value for col in range(1, val.max_column + 1)]
            normalized = [str(v).strip() if v is not None else "" for v in values]
            if "sample_id" in normalized and "experimental_CH4_Nm3" in normalized:
                header_row = row
                break

        calc_header_row = None
        for row in range(1, val.max_row + 1):
            values = [val.cell(row=row, column=col).value for col in range(1, val.max_column + 1)]
            normalized = [str(v).strip() if v is not None else "" for v in values]
            if "absolute_error_CH4_Nm3" in normalized and "validation_status" in normalized:
                calc_header_row = row
                break

        if header_row and calc_header_row:
            h = _get_header_map(val, header_row)
            ch = _get_header_map(val, calc_header_row)
            output_row = calc_header_row + 1

            for r in range(output_row, output_row + 100):
                for c in range(1, 11):
                    val.cell(row=r, column=c).value = None

            for r in range(header_row + 1, calc_header_row - 1):
                sample_id = val.cell(row=r, column=h["sample_id"]).value
                if sample_id is None or str(sample_id).strip() == "":
                    continue

                active_col = h.get("active_row")
                active = _to_bool(val.cell(row=r, column=active_col).value, default=True) if active_col else True
                if not active:
                    continue

                theoretical_ch4 = val.cell(row=r, column=h["theoretical_CH4_Nm3"]).value
                theoretical_biogas = val.cell(row=r, column=h["theoretical_biogas_Nm3"]).value

                if theoretical_ch4 in (None, ""):
                    theoretical_ch4 = results["CH4_Nm3"]
                    val.cell(row=r, column=h["theoretical_CH4_Nm3"]).value = theoretical_ch4

                if theoretical_biogas in (None, ""):
                    theoretical_biogas = results["total_biogas_Nm3"]
                    val.cell(row=r, column=h["theoretical_biogas_Nm3"]).value = theoretical_biogas

                comp = compare_experimental_to_theoretical(
                    experimental_ch4_nm3=val.cell(row=r, column=h["experimental_CH4_Nm3"]).value,
                    experimental_biogas_nm3=val.cell(row=r, column=h["experimental_biogas_Nm3"]).value,
                    experimental_ch4_percent=val.cell(row=r, column=h["experimental_CH4_percent"]).value,
                    theoretical_ch4_nm3=float(theoretical_ch4),
                    theoretical_biogas_nm3=float(theoretical_biogas),
                )

                val.cell(row=output_row, column=1).value = sample_id
                for field, col in ch.items():
                    if field == "sample_id":
                        continue
                    if field in comp:
                        val.cell(row=output_row, column=col).value = comp[field]
                output_row += 1

    wb.save(output_path)
    return output_path
