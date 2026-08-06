import subprocess
import sys
from pathlib import Path


def test_csv_example_runs_successfully():
    example_script = Path("examples/example_csv.py")

    completed = subprocess.run(
        [sys.executable, str(example_script)],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "BioPot-Gas CSV example" in completed.stdout
    assert "CH4_Nm3:" in completed.stdout
    assert "total_biogas_Nm3:" in completed.stdout