"""Configuration module for AI Document Sorter.

This module handles all configuration settings, environment variables,
and application constants using python-dotenv for secure configuration management.
"""

import os
from pathlib import Path
from typing import Set
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Central configuration class for the document sorting application.

    Loads settings from environment variables with sensible defaults.
    All paths and sensitive settings should be configured via .env file.
    """

    # Path Configuration
    USER_HOME: str = str(Path.home())
    INBOX_PATH: str = os.getenv(
        "INBOX_PATH",
        os.path.join(USER_HOME, "Documents/Inbox_Scan")
    )
    TARGET_ROOT: str = os.getenv(
        "TARGET_ROOT",
        os.path.join(USER_HOME, "Documents/Sorted_Documents")
    )

    # Ollama/LLM Configuration
    OLLAMA_URL: str = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
    MODEL_NAME: str = os.getenv("MODEL_NAME", "llama3.2")

    # Processing Configuration
    SUPPORTED_EXTENSIONS: Set[str] = {".pdf", ".jpg", ".png", ".jpeg"}
    MIN_CONTENT_LENGTH: int = int(os.getenv("MIN_CONTENT_LENGTH", "50"))
    OCR_LANGUAGES: str = os.getenv("OCR_LANGUAGES", "deu+eng")

    # Logging Configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", "")  # Empty string means no file logging

    # File Processing Settings
    FILE_STABILIZATION_DELAY: float = float(os.getenv("FILE_STABILIZATION_DELAY", "2.0"))
    CONTENT_PREVIEW_LENGTH: int = int(os.getenv("CONTENT_PREVIEW_LENGTH", "2000"))

    @classmethod
    def validate(cls) -> bool:
        """Validate configuration settings.

        Returns:
            bool: True if configuration is valid, False otherwise.
        """
        required_paths = [cls.INBOX_PATH, cls.TARGET_ROOT]
        for path in required_paths:
            parent = Path(path).parent
            if not parent.exists():
                return False
        return True

    @classmethod
    def ensure_directories(cls) -> None:
        """Create required directories if they don't exist."""
        os.makedirs(cls.INBOX_PATH, exist_ok=True)
        os.makedirs(cls.TARGET_ROOT, exist_ok=True)
