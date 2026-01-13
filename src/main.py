"""Main orchestration module for AI Document Sorter.

This module ties together all components (extraction, analysis, file management,
and monitoring) to create the complete document processing workflow.
"""

import logging
import sys
from pathlib import Path
from typing import Optional

from .config import Config
from .extractor import ContentExtractor
from .analyzer import OllamaAnalyzer
from .file_manager import FileSystemManager
from .monitor import DirectoryMonitor

# Configure logging
def setup_logging(log_level: str = Config.LOG_LEVEL, log_file: str = Config.LOG_FILE) -> None:
    """Configure application logging.

    Sets up logging to console and optionally to a file with appropriate
    formatting and log levels.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        log_file: Optional path to log file. Empty string disables file logging.
    """
    # Create formatter
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # File handler (optional)
    if log_file:
        try:
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)
            logging.info(f"Logging to file: {log_file}")
        except Exception as e:
            logging.error(f"Failed to setup file logging: {e}")

    logging.info(f"Logging initialized at {log_level} level")


logger = logging.getLogger(__name__)


class DocumentProcessor:
    """Main workflow orchestrator for document processing.

    This class integrates content extraction, AI analysis, and file management
    into a cohesive document processing pipeline.

    Attributes:
        extractor (ContentExtractor): Content extraction component.
        analyzer (OllamaAnalyzer): AI analysis component.
        file_manager (FileSystemManager): File system operations component.
    """

    def __init__(self):
        """Initialize the DocumentProcessor with all components."""
        logger.info("Initializing DocumentProcessor")

        self.extractor = ContentExtractor()
        self.analyzer = OllamaAnalyzer()
        self.file_manager = FileSystemManager()

        logger.info("DocumentProcessor initialization complete")

    def process_file(self, filepath: Path) -> bool:
        """Process a single document file through the complete pipeline.

        Args:
            filepath: Path to the document file to process.

        Returns:
            True if processing succeeded, False otherwise.
        """
        logger.info(f"Processing file: {filepath.name}")

        # Step 1: Validate file
        if not self.file_manager.validate_source_file(filepath):
            logger.info(f"File validation failed, skipping: {filepath.name}")
            return False

        try:
            # Step 2: Extract content
            logger.debug(f"Extracting content from: {filepath.name}")
            content = self.extractor.extract_content(filepath)

            if not content.strip():
                logger.warning(f"No content extracted from: {filepath.name}")
                # Still proceed with empty content - analyzer will handle it

            # Step 3: Analyze content with AI
            logger.debug(f"Analyzing content for: {filepath.name}")
            metadata = self.analyzer.analyze_document(content)

            # Step 4: Move file to target location
            logger.debug(f"Moving file to: {metadata.category}/{metadata.filename}")
            target_path = self.file_manager.move_file(filepath, metadata)

            if target_path:
                logger.info(
                    f"Successfully processed: {filepath.name} → "
                    f"{metadata.category}/{target_path.name}"
                )
                return True
            else:
                logger.error(f"Failed to move file: {filepath.name}")
                return False

        except Exception as e:
            logger.error(
                f"Error processing file {filepath.name}: {e}",
                exc_info=True
            )
            return False


def verify_prerequisites() -> bool:
    """Verify that all prerequisites are met before starting.

    Checks for:
    - Required directories
    - Ollama API connectivity
    - Required external tools (Tesseract)

    Returns:
        True if all prerequisites are met, False otherwise.
    """
    logger.info("Verifying prerequisites")

    # Check configuration validity
    if not Config.validate():
        logger.error("Configuration validation failed")
        return False

    # Ensure directories exist
    try:
        Config.ensure_directories()
        logger.info("Required directories verified")
    except Exception as e:
        logger.error(f"Failed to create directories: {e}")
        return False

    # Check Ollama connectivity
    analyzer = OllamaAnalyzer()
    if not analyzer.check_connection():
        logger.error(
            f"Cannot connect to Ollama API at {Config.OLLAMA_URL}. "
            "Make sure Ollama is running: 'ollama serve'"
        )
        return False

    logger.info("All prerequisites verified successfully")
    return True


def main() -> int:
    """Main entry point for the application.

    Returns:
        Exit code (0 for success, 1 for failure).
    """
    # Setup logging
    setup_logging()

    logger.info("="*60)
    logger.info("AI Document Sorter - Starting")
    logger.info("="*60)

    # Verify prerequisites
    if not verify_prerequisites():
        logger.error("Prerequisites check failed. Exiting.")
        return 1

    # Display configuration
    logger.info(f"Inbox Path: {Config.INBOX_PATH}")
    logger.info(f"Target Path: {Config.TARGET_ROOT}")
    logger.info(f"Ollama Model: {Config.MODEL_NAME}")
    logger.info(f"OCR Languages: {Config.OCR_LANGUAGES}")

    # Create the document processor
    processor = DocumentProcessor()

    # Create and configure the directory monitor
    monitor = DirectoryMonitor(
        inbox_path=Config.INBOX_PATH,
        process_callback=processor.process_file
    )

    # Run the monitor (this will block)
    try:
        monitor.run()
    except Exception as e:
        logger.error(f"Fatal error in main loop: {e}", exc_info=True)
        return 1

    logger.info("Application shutdown complete")
    return 0


if __name__ == "__main__":
    sys.exit(main())
