from pathlib import Path
import json

from biopotgas.excel_reader import calculate_from_excel, write_outputs_to_excel


INPUT_FILE = Path("BioPot-Gas_Input_Template_v6_validation_benchmarks.xlsx")

if not INPUT_FILE.exists():
    INPUT_FILE = Path("../BioPot-Gas_Input_Template_v6_validation_benchmarks.xlsx")

if not INPUT_FILE.exists():
    raise FileNotFoundError(
        "Input spreadsheet not found. Place BioPot-Gas_Input_Template_v6_validation_benchmarks.xlsx "
        "next to this script or one folder above it."
    )

result = calculate_from_excel(INPUT_FILE)
output_file = write_outputs_to_excel(INPUT_FILE)

print("BioPot-Gas v0.6 result from Excel input")
print(json.dumps(result, indent=2, ensure_ascii=False))
print(f"Calculated workbook saved as: {output_file}")
