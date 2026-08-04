from pathlib import Path
import shutil

from biopotgas.excel_writer import write_outputs_to_excel


TEMPLATE_FILE = Path("BioPot-Gas_Input_Template_v6_validation_benchmarks.xlsx")


def test_excel_writer_default_output_path_does_not_overwrite_input(tmp_path):
    input_copy = tmp_path / TEMPLATE_FILE.name
    shutil.copy2(TEMPLATE_FILE, input_copy)

    original_input_bytes = input_copy.read_bytes()

    output_file = write_outputs_to_excel(input_copy)

    assert output_file == input_copy.with_name(input_copy.stem + "_calculated.xlsx")
    assert output_file.exists()
    assert input_copy.read_bytes() == original_input_bytes