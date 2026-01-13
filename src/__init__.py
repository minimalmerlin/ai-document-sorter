"""AI Document Sorter - Privacy-first local document organization.

This package provides automated document sorting using local AI (Ollama)
and OCR technology. All processing happens locally for maximum privacy.
"""

__version__ = "1.0.0"
__author__ = "Merlin Mechler"

from .config import Config
from .extractor import ContentExtractor
from .analyzer import OllamaAnalyzer, DocumentMetadata
from .file_manager import FileSystemManager
from .monitor import DirectoryMonitor, DocumentEventHandler
from .main import DocumentProcessor, main

__all__ = [
    "Config",
    "ContentExtractor",
    "OllamaAnalyzer",
    "DocumentMetadata",
    "FileSystemManager",
    "DirectoryMonitor",
    "DocumentEventHandler",
    "DocumentProcessor",
    "main",
]
