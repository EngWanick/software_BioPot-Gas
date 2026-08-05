from pathlib import Path

from run_from_excel import file_sha256


def test_file_sha256_returns_expected_digest(tmp_path):
    file_path = tmp_path / "sample.txt"
    file_path.write_bytes(b"BioPot-Gas\n")

    assert file_sha256(file_path) == (
        "44154cdb6eb97853b2bc4e96f8fdb4cf2127e2df47f197c895016098f17e4292"
    )