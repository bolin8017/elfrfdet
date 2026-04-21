"""CLI entry point. Auto-generated from maldet spec."""

from maldet import create_cli

from .detector import ElfRfDetector

app = create_cli(ElfRfDetector)


if __name__ == "__main__":
    app()
