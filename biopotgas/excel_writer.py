from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any

from openpyxl import load_workbook

from .excel_reader import calculate_from_excel
from .excel_utils import get_header_map, to_bool
from .validation import compare_experimental_to_theoretical


def write_outputs_to_excel(
        input_path: str | Path,
        output_path: str | Path | None = None,
        results: Mapping[str, Any] | None = None,
    ) -> Path:
    input_path = Path(input_path)
    if output_path is None:
        output_path = input_path.with_name(input_path.stem + "_calculated.xlsx")
    output_path = Path(output_path)

    if results is None:
        results = calculate_from_excel(input_path)

    wb = load_workbook(input_path)
    if "02_OUTPUTS" not in wb.sheetnames:
        wb.create_sheet("02_OUTPUTS")
    ws = wb["02_OUTPUTS"]

    output_rows: dict[str, int] = {}

    for row in range(1, ws.max_row + 1):
        key = ws.cell(row=row, column=1).value
        if key is None:
            continue

        key = str(key).strip()
        if key == "":
            continue

        output_rows[key] = row

    unknown_output_keys = sorted(set(output_rows).difference(results))
    unwritten_result_keys = sorted(set(results).difference(output_rows))

    output_warnings: list[str] = []
    if results.get("warnings"):
        output_warnings.append(str(results["warnings"]))

    if unwritten_result_keys:
        output_warnings.append(
            "Calculated result keys not written to 02_OUTPUTS: "
            + ", ".join(unwritten_result_keys)
            + "."
        )

    if unknown_output_keys:
        output_warnings.append(
            "02_OUTPUTS keys not found in calculated results: "
            + ", ".join(unknown_output_keys)
            + "."
        )

    if output_warnings:
        results = dict(results)
        results["warnings"] = "; ".join(output_warnings)

    for key, row in output_rows.items():
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
            h = get_header_map(val, header_row)
            ch = get_header_map(val, calc_header_row)
            output_row = calc_header_row + 1

            last_row = max(val.max_row, output_row)
            last_col = max(val.max_column, 10)

            for r in range(output_row, last_row + 1):
                for c in range(1, last_col + 1):
                    val.cell(row=r, column=c).value = None

            for r in range(header_row + 1, calc_header_row - 1):
                sample_id = val.cell(row=r, column=h["sample_id"]).value
                if sample_id is None or str(sample_id).strip() == "":
                    continue

                active_col = h.get("active_row")
                active = to_bool(val.cell(row=r, column=active_col).value, default=True) if active_col else True
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