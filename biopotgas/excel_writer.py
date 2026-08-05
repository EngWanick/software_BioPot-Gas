from __future__ import annotations

from pathlib import Path
from typing import Mapping, Any

from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

from .excel_reader import calculate_from_excel

OUTPUT_SHEET = "02_OUTPUTS"

SUMMARY_CELLS = {
    "CH4_mol": "E4",
    "CO2_mol": "E5",
    "NH3_mol": "E6",
    "H2S_mol": "E7",
    "total_gas_mol": "E8",
    "CH4_mol_fraction": "E9",
    "inert_carbon_mol": "E10",
    "number_of_components_read": "E11",
    "calculation_status": "E12",
}

MASS_BALANCE_CELLS = {
    "CH4_mol": "B14",
    "CH4_mass": "C14",
    "CO2_mol": "B15",
    "CO2_mass": "C15",
    "NH3_mol": "B16",
    "NH3_mass": "C16",
    "H2S_mol": "B17",
    "H2S_mass": "C17",
    "inert_carbon_mol": "B18",
    "inert_carbon_mass": "C18",
}


def _ensure_outputs_sheet(wb):
    if OUTPUT_SHEET in wb.sheetnames:
        return wb[OUTPUT_SHEET]

    ws = wb.create_sheet(OUTPUT_SHEET)
    ws["A1"] = "BioPot-Gas | Saídas Automáticas do Software"
    ws.merge_cells("A1:H1")

    ws["A3"] = "Campo"
    ws["B3"] = "Valor"
    ws["D3"] = "Resumo dos resultados"
    ws["E3"] = "Valor"
    ws["F3"] = "Unidade"
    ws["G3"] = "Descrição"
    ws["H3"] = "Observação"

    labels = [
        ("D4", "CH4_mol", "F4", "base molar da entrada", "G4", "Produção teórica de metano"),
        ("D5", "CO2_mol", "F5", "base molar da entrada", "G5", "Produção teórica de dióxido de carbono"),
        ("D6", "NH3_mol", "F6", "base molar da entrada", "G6", "Produção teórica de amônia"),
        ("D7", "H2S_mol", "F7", "base molar da entrada", "G7", "Produção teórica de sulfeto de hidrogênio"),
        ("D8", "total_gas_mol", "F8", "base molar da entrada", "G8", "Soma dos gases calculados"),
        ("D9", "CH4_mol_fraction", "F9", "mol/mol", "G9", "Fração molar de metano no gás teórico"),
        ("D10", "inert_carbon_mol", "F10", "base molar da entrada", "G10", "Carbono não convertido em biogás"),
        ("D11", "number_of_components_read", "F11", "componentes", "G11", "Número de componentes ativos lidos"),
        ("D12", "calculation_status", "F12", "-", "G12", "Status da última execução"),
    ]
    for label_cell, label, unit_cell, unit, desc_cell, desc in labels:
        ws[label_cell] = label
        ws[unit_cell] = unit
        ws[desc_cell] = desc
        ws[f"H{label_cell[1:]}"] = "Preenchido pelo Python"

    ws["A13"] = "Produto"
    ws["B13"] = "Quantidade molar"
    ws["C13"] = "Massa estimada"
    ws["D13"] = "Unidade molar"
    ws["E13"] = "Unidade de massa"
    for row, product in enumerate(["CH4", "CO2", "NH3", "H2S", "C_inert"], start=14):
        ws[f"A{row}"] = product
        ws[f"D{row}"] = "base molar da entrada"
        ws[f"E{row}"] = "kg se entrada for kmol"

    _format_outputs_sheet(ws)
    return ws


def _format_outputs_sheet(ws) -> None:
    title_fill = PatternFill("solid", fgColor="1F4E78")
    header_fill = PatternFill("solid", fgColor="BDD7EE")
    output_fill = PatternFill("solid", fgColor="FFF2CC")
    thin = Side(style="thin", color="808080")
    border = Border(left=thin, right=thin, top=thin, bottom=thin)

    ws["A1"].fill = title_fill
    ws["A1"].font = Font(color="FFFFFF", bold=True, size=14)
    ws["A1"].alignment = Alignment(horizontal="center")

    for row_cells in (ws["A3:B3"], ws["D3:H3"], ws["A13:E13"]):
        for cell in row_cells[0]:
            cell.fill = header_fill
            cell.font = Font(bold=True)
            cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

    for row in ws.iter_rows(min_row=1, max_row=25, min_col=1, max_col=8):
        for cell in row:
            cell.border = border
            cell.alignment = Alignment(vertical="top", wrap_text=True)

    for cell in ["E4", "E5", "E6", "E7", "E8", "E9", "E10", "E11", "E12", "B14", "C14", "B15", "C15", "B16", "C16", "B17", "C17", "B18", "C18"]:
        ws[cell].fill = output_fill

    widths = {"A": 22, "B": 22, "C": 18, "D": 28, "E": 18, "F": 18, "G": 34, "H": 26}
    for col, width in widths.items():
        ws.column_dimensions[col].width = width


def write_outputs_to_excel(input_path: str | Path, output_path: str | Path | None = None, result: Mapping[str, Any] | None = None) -> Path:
    input_path = Path(input_path)

    if output_path is None:
        output_path = input_path.with_name(input_path.stem + "_calculated.xlsx")

    output_path = Path(output_path)

    if result is None:
        result = calculate_from_excel(input_path)

    wb = load_workbook(input_path)

    # Rebuild the output sheet to avoid writing into merged cells from older templates.
    if OUTPUT_SHEET in wb.sheetnames:
        old_ws = wb[OUTPUT_SHEET]
        wb.remove(old_ws)
    ws = _ensure_outputs_sheet(wb)

    for key, cell in SUMMARY_CELLS.items():
        ws[cell] = result.get(key, "OK" if key == "calculation_status" else None)

    for key, cell in MASS_BALANCE_CELLS.items():
        ws[cell] = result.get(key)

    ws["E12"] = "OK"

    numeric_cells = ["E4", "E5", "E6", "E7", "E8", "E10", "B14", "C14", "B15", "C15", "B16", "C16", "B17", "C17", "B18", "C18"]
    for cell in numeric_cells:
        ws[cell].number_format = "0.000000"
    ws["E9"].number_format = "0.0000%"
    ws["E11"].number_format = "0"

    _format_outputs_sheet(ws)
    wb.save(output_path)
    return output_path
