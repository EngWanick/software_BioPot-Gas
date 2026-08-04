from pathlib import Path
import shutil

from openpyxl import load_workbook

from biopotgas.excel_reader import calculate_from_excel, write_outputs_to_excel


TEMPLATE_FILE = Path("BioPot-Gas_Input_Template_v6_validation_benchmarks.xlsx")


def test_excel_pipeline_generates_calculated_workbook_without_overwriting_input(tmp_path):
    input_copy = tmp_path / TEMPLATE_FILE.name
    output_file = tmp_path / "calculated_output.xlsx"

    shutil.copy2(TEMPLATE_FILE, input_copy)
    original_input_bytes = input_copy.read_bytes()

    results = calculate_from_excel(input_copy)
    written_file = write_outputs_to_excel(
        input_copy,
        output_path=output_file,
        results=results,
    )

    assert written_file == output_file
    assert output_file.exists()
    assert input_copy.read_bytes() == original_input_bytes

    assert results["calculation_status"] == "Calculated successfully"
    assert results["number_of_components_read"] > 0
    assert results["CH4_Nm3"] > 0
    assert results["total_biogas_Nm3"] > 0

    workbook = load_workbook(output_file, data_only=False)

    assert "02_OUTPUTS" in workbook.sheetnames
    assert "04_EXPERIMENTAL_VALIDATION" in workbook.sheetnames
    assert "06_VALIDATION_BENCHMARKS" in workbook.sheetnames