"""Unit tests for text256 feature extraction."""

import shutil
from pathlib import Path

import numpy as np
import pytest

from elfrfdet.text256 import extract_text256


def _system_elf() -> Path:
    """Pick a small ELF binary present on any Linux dev host."""
    for candidate in ("/bin/ls", "/usr/bin/ls", "/bin/cat"):
        p = Path(candidate)
        if p.is_file():
            return p
    pytest.skip("no system ELF available")


def test_returns_uint8_vector_of_requested_size():
    vec = extract_text256(_system_elf(), size=256)
    assert vec.dtype == np.uint8
    assert vec.shape == (256,)


def test_zero_pads_short_sections() -> None:
    """Pad when the requested size exceeds actual .text length."""
    from elftools.elf.elffile import ELFFile

    elf_path = _system_elf()
    with open(elf_path, "rb") as f:
        text_len = len(ELFFile(f).get_section_by_name(".text").data())

    # Ask for 1024 bytes more than .text contains → the last 1024 must be
    # zero-padded by extract_text256.
    vec = extract_text256(elf_path, size=text_len + 1024)
    assert vec.shape == (text_len + 1024,)
    assert vec[text_len:].sum() == 0


def test_raises_on_non_elf(tmp_path: Path) -> None:
    garbage = tmp_path / "notelf.bin"
    garbage.write_bytes(b"hello world\n")
    with pytest.raises(ValueError, match="not a valid ELF"):
        extract_text256(garbage)


def test_raises_on_missing_file(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        extract_text256(tmp_path / "nope")
