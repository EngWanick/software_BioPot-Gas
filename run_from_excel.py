from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json

from biopotgas.excel_reader import calculate_from_excel, write_outputs_to_excel


INPUT_FILE = Path("BioPot-Gas_Input_Template_v6_validation_benchmarks.xlsx")

def resolve_input_file() -> Path:
    input_file = INPUT_FILE

    if not input_file.exists():
        input_file = Path("../BioPot-Gas_Input_Template_v6_validation_benchmarks.xlsx")

    if not input_file.exists():
        raise FileNotFoundError(
            "Input spreadsheet not found. Place BioPot-Gas_Input_Template_v6_validation_benchmarks.xlsx "
            "next to this script or one folder above it."
        )
    return input_file

def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()

def main() -> None:
    input_file = resolve_input_file()

    result = calculate_from_excel(input_file)
    output_file = write_outputs_to_excel(input_file, results=result)

    result_for_print = dict(result)
    result_for_print["_run_metadata"] = {
        "input_path": str(input_file.resolve()),
        "input_sha256": file_sha256(input_file),
        "output_path": str(output_file.resolve()),
        "run_timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "biopotgas_version": "0.6.1",
}

    print("BioPot-Gas v0.6 result from Excel input")
    print(json.dumps(result_for_print, indent=2, ensure_ascii=False))
    print(f"Calculated workbook saved as: {output_file}")

if __name__ == "__main__":
    main()