"""Random Forest ELF malware detector."""

from .config import ElfRfDetectorConfig
from .detector import ElfRfDetector

__all__ = ["ElfRfDetector", "ElfRfDetectorConfig"]
__version__ = "0.1.1"
