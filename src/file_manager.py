"""File management module for document organization.

This module handles all file system operations including moving files,
creating directory structures, and managing file naming conflicts.
"""

import logging
import shutil
from pathlib import Path
from typing import Optional

from .analyzer import DocumentMetadata
from .config import Config

logger = logging.getLogger(__name__)


class FileSystemManager:
    """Manages file system operations for document organization.

    This class handles moving files to their target locations based on
    metadata, creating necessary directories, and resolving naming conflicts.

    Attributes:
        root_dir (Path): Root directory for sorted documents.
    """

    def __init__(self, root_dir: str = Config.TARGET_ROOT):
        """Initialize the FileSystemManager.

        Args:
            root_dir: Root directory path where files will be organized.
        """
        self.root_dir = Path(root_dir)
        logger.info(f"FileSystemManager initialized with root: {self.root_dir}")

    def move_file(
        self,
        source_path: Path,
        metadata: DocumentMetadata
    ) -> Optional[Path]:
        """Move a file to its target location based on metadata.

        Creates necessary directory structure and handles filename conflicts
        by appending a counter to duplicate names.

        Args:
            source_path: Path to the source file.
            metadata: DocumentMetadata containing category and filename info.

        Returns:
            Path to the moved file, or None if move failed.
        """
        if not source_path.exists():
            logger.error(f"Source file does not exist: {source_path}")
            return None

        try:
            # Prepare target directory and filename
            target_dir = self._prepare_target_directory(metadata.category)
            target_path = self._resolve_target_path(
                target_dir,
                metadata.filename,
                source_path.suffix
            )

            # Perform the move operation
            shutil.move(str(source_path), str(target_path))

            logger.info(
                f"File moved successfully: {source_path.name} → {target_path}"
            )
            return target_path

        except Exception as e:
            logger.error(
                f"Failed to move file {source_path.name}: {e}",
                exc_info=True
            )
            return None

    def _prepare_target_directory(self, category: str) -> Path:
        """Prepare and create target directory based on category.

        Sanitizes category name and creates directory if it doesn't exist.

        Args:
            category: Category name for the subdirectory.

        Returns:
            Path object for the target directory.
        """
        # Sanitize category name (remove invalid path characters)
        safe_category = self._sanitize_path_component(category)

        target_dir = self.root_dir / safe_category

        # Create directory if it doesn't exist
        target_dir.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Target directory prepared: {target_dir}")

        return target_dir

    def _resolve_target_path(
        self,
        target_dir: Path,
        filename: str,
        extension: str
    ) -> Path:
        """Resolve target file path, handling naming conflicts.

        If a file with the same name exists, appends a counter (_1, _2, etc.)
        to make the filename unique.

        Args:
            target_dir: Target directory path.
            filename: Base filename (without extension).
            extension: File extension (including the dot).

        Returns:
            Unique Path object for the target file.
        """
        # Sanitize filename
        safe_filename = self._sanitize_path_component(filename)

        target_path = target_dir / f"{safe_filename}{extension}"

        # Handle naming conflicts
        counter = 1
        while target_path.exists():
            target_path = target_dir / f"{safe_filename}_{counter}{extension}"
            counter += 1
            if counter > 1000:  # Safety limit
                logger.warning(f"Unusually high counter for filename: {safe_filename}")
                break

        if counter > 1:
            logger.debug(f"Filename conflict resolved with counter: {counter - 1}")

        return target_path

    @staticmethod
    def _sanitize_path_component(name: str) -> str:
        """Sanitize a filename or directory name.

        Removes or replaces characters that are invalid in file paths.

        Args:
            name: The name to sanitize.

        Returns:
            Sanitized name safe for use in file paths.
        """
        # Replace forward slashes and backslashes
        safe_name = name.replace("/", "_").replace("\\", "_")

        # Replace other potentially problematic characters
        invalid_chars = ['<', '>', ':', '"', '|', '?', '*']
        for char in invalid_chars:
            safe_name = safe_name.replace(char, "_")

        # Remove leading/trailing whitespace and dots
        safe_name = safe_name.strip('. ')

        # Ensure the name is not empty
        if not safe_name:
            safe_name = "Unnamed"

        return safe_name

    def validate_source_file(self, filepath: Path) -> bool:
        """Validate if a source file should be processed.

        Checks for iCloud placeholders, hidden files, and supported extensions.

        Args:
            filepath: Path to the file to validate.

        Returns:
            True if file should be processed, False otherwise.
        """
        # Skip hidden files (starting with dot)
        if filepath.name.startswith('.'):
            logger.debug(f"Skipping hidden file: {filepath.name}")
            return False

        # Skip iCloud placeholder files
        if filepath.name.endswith('.icloud'):
            logger.info(f"Skipping iCloud placeholder: {filepath.name}")
            return False

        # Check if extension is supported
        if filepath.suffix.lower() not in Config.SUPPORTED_EXTENSIONS:
            logger.debug(
                f"Skipping unsupported file type: {filepath.name} "
                f"({filepath.suffix})"
            )
            return False

        # Check if file is readable
        if not filepath.exists() or not filepath.is_file():
            logger.warning(f"File not accessible: {filepath}")
            return False

        return True

    def get_file_size(self, filepath: Path) -> int:
        """Get file size in bytes.

        Args:
            filepath: Path to the file.

        Returns:
            File size in bytes, or 0 if file doesn't exist.
        """
        try:
            return filepath.stat().st_size
        except Exception as e:
            logger.error(f"Cannot get file size for {filepath}: {e}")
            return 0
