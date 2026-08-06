from datetime import datetime, timezone
from pathlib import Path
import hashlib

from biopotgas.pipeline import calculate_from_excel
from biopotgas.excel_writer import write_outputs_to_excel


INPUT_FILE = Path("BioPot-Gas_Input_Template_v6_validation_benchmarks.xlsx")
LOG_OPEN = "<" + "=" * 78 + ">"
LOG_CLOSE = ">" + "=" * 78 + "<"

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

def print_summary(result: dict, input_file: Path, output_file: Path) -> None:
    """Print a concise operational summary for command-line execution."""

    run_timestamp_utc = datetime.now(timezone.utc).isoformat()
    input_hash = file_sha256(input_file)
    warnings = result.get("warnings") or "none"

    print(LOG_OPEN)
    print("BioPot-Gas v0.6.1 result from Excel input")
    print()
    print("Input:")
    print(f"  {input_file}")
    print()
    print("Main results:")
    print(f"  CH4: {result['CH4_Nm3']:.6f} Nm3")
    print(f"  CO2: {result['CO2_Nm3']:.6f} Nm3")
    print(f"  Total biogas: {result['total_biogas_Nm3']:.6f} Nm3")
    print(f"  CH4: {result['CH4_vol_percent']:.6f} %")
    print()
    print("Water balance:")
    print(f"  Stoichiometric H2O: {result['H2O_mol']:.6f}")
    print(f"  Available water: {result['water_available_mol']:.6f}")
    print(f"  Net water balance: {result['net_water_balance_mol']:.6f}")
    print(f"  Net water balance mass: {result['net_water_balance_mass']:.6f} kg")
    print()
    print("Run metadata:")
    print(f"  Status: {result['calculation_status']}")
    print(f"  Warnings: {warnings}")
    print(f"  Input SHA256: {input_hash}")
    print(f"  Run timestamp UTC: {run_timestamp_utc}")
    print()
    print("Output workbook:")
    print(f"  {output_file}")
    print(LOG_CLOSE)

def main() -> None:
    input_file = resolve_input_file()

    result = calculate_from_excel(input_file)
    output_file = write_outputs_to_excel(input_file, results=result)

    print_summary(result, input_file, output_file)

if __name__ == "__main__":
    main()