"""Content extraction module for document processing.

This module handles text extraction from various file formats including
PDF files (both text-based and scanned) and images using OCR technology.
"""

import logging
from pathlib import Path
from typing import Optional

import pytesseract
from pdf2image import convert_from_path
from pypdf import PdfReader
from PIL import Image

from .config import Config

logger = logging.getLogger(__name__)


class ContentExtractor:
    """Extracts text content from PDF and image files.

    This class implements a two-stage extraction strategy:
    1. For PDFs: Attempt native text extraction first
    2. Fallback: Use OCR (Tesseract) for scanned documents or images

    Attributes:
        ocr_languages (str): Languages to use for OCR processing.
        min_content_length (int): Minimum text length before triggering OCR fallback.
    """

    def __init__(
        self,
        ocr_languages: str = Config.OCR_LANGUAGES,
        min_content_length: int = Config.MIN_CONTENT_LENGTH
    ):
        """Initialize the ContentExtractor.

        Args:
            ocr_languages: Language codes for Tesseract OCR (e.g., 'deu+eng').
            min_content_length: Minimum characters before considering OCR fallback.
        """
        self.ocr_languages = ocr_languages
        self.min_content_length = min_content_length
        logger.info(f"ContentExtractor initialized with OCR languages: {ocr_languages}")

    def extract_content(self, filepath: Path) -> str:
        """Extract text content from a document file.

        Attempts native PDF text extraction first, then falls back to OCR
        if the extracted text is too short or the file is an image.

        Args:
            filepath: Path to the document file.

        Returns:
            Extracted text content as a string.

        Raises:
            FileNotFoundError: If the specified file does not exist.
        """
        if not filepath.exists():
            logger.error(f"File not found: {filepath}")
            raise FileNotFoundError(f"File not found: {filepath}")

        logger.debug(f"Starting content extraction for: {filepath.name}")

        text = ""

        # Stage 1: Try native PDF text extraction
        if filepath.suffix.lower() == '.pdf':
            text = self._extract_pdf_text(filepath)

        # Stage 2: OCR fallback for insufficient text or image files
        if len(text.strip()) < self.min_content_length:
            logger.info(
                f"Text extraction yielded {len(text)} chars. Attempting OCR fallback."
            )
            ocr_text = self._extract_via_ocr(filepath)
            text += ocr_text

        logger.info(
            f"Content extraction completed. Total characters: {len(text)}"
        )
        return text

    def _extract_pdf_text(self, filepath: Path) -> str:
        """Extract text from PDF using native PDF text extraction.

        Args:
            filepath: Path to the PDF file.

        Returns:
            Extracted text or empty string if extraction fails.
        """
        text = ""
        try:
            reader = PdfReader(str(filepath))
            page_count = len(reader.pages)
            logger.debug(f"PDF has {page_count} pages")

            for i, page in enumerate(reader.pages, 1):
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
                    logger.debug(f"Extracted {len(extracted)} chars from page {i}")

            logger.info(f"PDF text extraction successful: {len(text)} characters")
        except Exception as e:
            logger.warning(f"PDF text extraction failed: {e}")

        return text

    def _extract_via_ocr(self, filepath: Path) -> str:
        """Extract text using Tesseract OCR.

        Handles both image files directly and PDF files by converting
        them to images first.

        Args:
            filepath: Path to the file (PDF or image).

        Returns:
            OCR-extracted text or empty string if OCR fails.
        """
        text = ""
        try:
            images = []

            if filepath.suffix.lower() == '.pdf':
                logger.debug("Converting PDF to images for OCR")
                images = convert_from_path(str(filepath))
                logger.info(f"PDF converted to {len(images)} images")
            else:
                logger.debug(f"Loading image file: {filepath.name}")
                images = [Image.open(str(filepath))]

            for i, img in enumerate(images, 1):
                ocr_result = pytesseract.image_to_string(
                    img,
                    lang=self.ocr_languages
                )
                text += ocr_result
                logger.debug(f"OCR processed image {i}: {len(ocr_result)} chars")

            logger.info(f"OCR extraction successful: {len(text)} characters")

        except Exception as e:
            logger.error(f"OCR extraction failed: {e}", exc_info=True)

        return text

    @staticmethod
    def is_supported_file(filepath: Path) -> bool:
        """Check if a file type is supported for processing.

        Args:
            filepath: Path to the file to check.

        Returns:
            True if file extension is supported, False otherwise.
        """
        return filepath.suffix.lower() in Config.SUPPORTED_EXTENSIONS
