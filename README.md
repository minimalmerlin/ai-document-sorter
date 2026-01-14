# AI Document Sorter

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Privacy](https://img.shields.io/badge/privacy-100%25%20local-brightgreen.svg)
![AI](https://img.shields.io/badge/AI-Ollama-orange.svg)
![OCR](https://img.shields.io/badge/OCR-Tesseract-blue.svg)

**Privacy-First Local Document Organization using AI and OCR**

A Python application that automatically organizes your scanned documents using local AI (Ollama) for intelligent categorization and OCR (Tesseract) for text extraction. All processing happens locally on your machine—no cloud services, no data sharing, complete privacy.

## Features

- **100% Local Processing**: All AI analysis and OCR happens on your machine using Ollama and Tesseract
- **Automatic Organization**: Monitors a folder and automatically sorts documents into categorized folders
- **Intelligent Naming**: Uses LLM to generate meaningful filenames in format `YYYY-MM-DD_Topic_Keywords`
- **Multi-Format Support**: Handles PDFs (text and scanned), JPG, PNG, and JPEG files
- **Smart Text Extraction**: Attempts native PDF text extraction first, falls back to OCR when needed
- **Conflict Resolution**: Automatically handles duplicate filenames
- **iCloud Compatible**: Properly handles iCloud Drive placeholder files
- **Startup Catch-Up**: Processes files that arrived while the application wasn't running
- **Professional Logging**: Comprehensive logging with configurable levels

## How It Works

```
┌─────────────────┐
│  Scanned File   │
│  (Inbox Folder) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Content Extract │ ◄─── PDF Text or OCR (Tesseract)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  AI Analysis    │ ◄─── Local Ollama LLM
│  (Categorize &  │
│   Name)         │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Auto-Sort to   │
│  Category Folder│
└─────────────────┘
```

**Example:**
- Input: Scanned receipt → `scan_12345.pdf`
- AI Analysis: Identifies as grocery receipt from 2026-01-13
- Output: `Sorted_Documents/Rechnungen/2026-01-13_Supermarkt_Einkauf.pdf`

## Prerequisites

### 1. Python
Python 3.8 or higher is required.

```bash
python --version
```

### 2. Tesseract OCR
Tesseract is needed for optical character recognition.

**macOS:**
```bash
brew install tesseract tesseract-lang
```

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr tesseract-ocr-deu tesseract-ocr-eng
```

**Windows:**
Download and install from [UB-Mannheim/tesseract](https://github.com/UB-Mannheim/tesseract/wiki)

### 3. Poppler (for PDF to Image Conversion)

**macOS:**
```bash
brew install poppler
```

**Ubuntu/Debian:**
```bash
sudo apt-get install poppler-utils
```

**Windows:**
Download from [poppler-windows releases](https://github.com/oschwartz10612/poppler-windows/releases)

### 4. Ollama
Ollama provides the local LLM for document analysis.

**Installation:**
1. Visit [ollama.ai](https://ollama.ai) and download for your OS
2. Install and start Ollama
3. Pull a model:

```bash
ollama pull llama3.2
```

**Alternative models:**
- `llama2` - Older but stable
- `mistral` - Good performance
- `phi` - Lightweight option

## Installation

### 1. Clone or Download the Repository

```bash
git clone https://github.com/yourusername/ai-document-sorter.git
cd ai-document-sorter
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` with your preferred settings:

```bash
# Example configuration
INBOX_PATH=/Users/yourusername/Documents/Inbox_Scan
TARGET_ROOT=/Users/yourusername/Documents/Sorted_Documents
MODEL_NAME=llama3.2
OCR_LANGUAGES=deu+eng
LOG_LEVEL=INFO
```

**Important Configuration Options:**

- `INBOX_PATH`: Folder to monitor for new documents
- `TARGET_ROOT`: Where sorted documents will be stored
- `MODEL_NAME`: Ollama model to use (must be pulled first)
- `OCR_LANGUAGES`: Languages for OCR (`deu` for German, `eng` for English, combine with `+`)

## Usage

### Start the Application

```bash
python -m src.main
```

Or create a convenience script `run.py`:

```python
#!/usr/bin/env python
from src.main import main
import sys

if __name__ == "__main__":
    sys.exit(main())
```

Then run:
```bash
python run.py
```

### What Happens

1. **Initial Scan**: Processes all existing files in the inbox folder
2. **Monitoring**: Watches for new files continuously
3. **Processing Pipeline**:
   - Extracts text (PDF native text or OCR)
   - Analyzes content with Ollama
   - Generates filename and category
   - Moves file to organized folder structure
4. **Stop**: Press `Ctrl+C` to gracefully shutdown

### Example Output

```
2026-01-13 10:30:45 - root - INFO - ============================================================
2026-01-13 10:30:45 - root - INFO - AI Document Sorter - Starting
2026-01-13 10:30:45 - root - INFO - ============================================================
2026-01-13 10:30:45 - root - INFO - Inbox Path: /Users/merlin/Documents/Inbox_Scan
2026-01-13 10:30:45 - root - INFO - Target Path: /Users/merlin/Documents/Sorted_Documents
2026-01-13 10:30:45 - root - INFO - Ollama Model: llama3.2
2026-01-13 10:30:46 - monitor - INFO - Starting initial directory scan (catch-up mode)
2026-01-13 10:30:46 - monitor - INFO - Found 3 files in inbox for initial processing
2026-01-13 10:30:48 - main - INFO - Processing file: scan_001.pdf
2026-01-13 10:30:52 - analyzer - INFO - Analysis successful: 2026-01-10_Stromrechnung → Rechnungen
2026-01-13 10:30:52 - file_manager - INFO - File moved successfully: scan_001.pdf → .../Rechnungen/2026-01-10_Stromrechnung.pdf
2026-01-13 10:30:53 - monitor - INFO - Directory monitoring started
2026-01-13 10:30:53 - monitor - INFO - Monitor is now active. Press Ctrl+C to stop.
```

## Project Structure

```
ai-document-sorter/
├── src/
│   ├── __init__.py         # Package initialization
│   ├── config.py           # Configuration management (loads .env)
│   ├── extractor.py        # OCR & PDF text extraction (Input)
│   ├── analyzer.py         # Ollama LLM integration (Process)
│   ├── file_manager.py     # File operations (Output)
│   ├── monitor.py          # Watchdog directory monitoring
│   └── main.py             # Application orchestration
├── .env.example            # Environment variable template
├── .gitignore              # Git ignore rules
├── requirements.txt        # Python dependencies
└── README.md               # This file
```

## Architecture

The application follows the **EVA Principle** (Input-Process-Output):

- **Input** (`extractor.py`): Content extraction from documents
- **Process** (`analyzer.py`): AI-powered analysis and categorization
- **Output** (`file_manager.py`): File organization and storage

**Key Design Principles:**

- ✅ Separation of Concerns (each module has single responsibility)
- ✅ Type Hints (full type annotation for better IDE support)
- ✅ Professional Logging (replacing all print statements)
- ✅ Environment-based Configuration (no hardcoded paths)
- ✅ Comprehensive Error Handling (graceful degradation)
- ✅ Google-style Docstrings (clear documentation)

## Configuration Deep Dive

### Supported File Types

By default: `.pdf`, `.jpg`, `.png`, `.jpeg`

Modify in [config.py](src/config.py) if needed:
```python
SUPPORTED_EXTENSIONS: Set[str] = {".pdf", ".jpg", ".png", ".jpeg", ".tiff"}
```

### OCR Languages

Configure via `OCR_LANGUAGES` in `.env`:

```bash
# German only
OCR_LANGUAGES=deu

# English only
OCR_LANGUAGES=eng

# Multiple languages
OCR_LANGUAGES=deu+eng+fra
```

Check available languages:
```bash
tesseract --list-langs
```

### File Stabilization Delay

Time to wait after file creation before processing (ensures file is fully written):

```bash
FILE_STABILIZATION_DELAY=2.0  # seconds
```

### Logging

**Log Levels:** `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`

**Console Only:**
```bash
LOG_LEVEL=INFO
LOG_FILE=
```

**File Logging:**
```bash
LOG_LEVEL=DEBUG
LOG_FILE=/Users/yourusername/logs/document-sorter.log
```

## Troubleshooting

### Ollama Connection Failed

**Error:** `Cannot connect to Ollama API`

**Solutions:**
1. Check if Ollama is running: `ollama serve`
2. Verify the model is pulled: `ollama pull llama3.2`
3. Test API manually: `curl http://localhost:11434/api/tags`
4. Check `OLLAMA_URL` in `.env`

### Tesseract Not Found

**Error:** `pytesseract.pytesseract.TesseractNotFoundError`

**Solutions:**
1. Install Tesseract (see Prerequisites)
2. On Windows, add Tesseract to PATH or specify location:
   ```python
   pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
   ```

### PDF Conversion Issues

**Error:** Related to `pdf2image`

**Solutions:**
1. Install Poppler (see Prerequisites)
2. On Windows, add Poppler `bin` folder to PATH

### No Text Extracted

**Possible Causes:**
- Document is truly blank
- OCR language not installed
- Image quality too poor

**Solutions:**
1. Check OCR languages: `tesseract --list-langs`
2. Install missing language packs
3. Review logs with `LOG_LEVEL=DEBUG`

### iCloud Files Not Processing

**Symptom:** Files with `.icloud` extension are skipped

**Explanation:** This is intentional. iCloud placeholder files are not yet downloaded.

**Solution:** Ensure files are downloaded (right-click → Download) or enable "Download Originals to this Mac" in iCloud settings.

## Privacy & Security

### Why Local Processing Matters

- **No Data Sharing**: Your documents never leave your computer
- **No Cloud Costs**: No API fees or subscription services
- **Full Control**: You control the model and the data
- **Offline Capable**: Works without internet connection (after initial setup)

### What Data is Processed

- Document text is sent to **local** Ollama instance only
- No external API calls
- No telemetry or analytics
- No network traffic (except to localhost)

## Customization

### Change Category Suggestions

Edit the prompt in [analyzer.py](src/analyzer.py#L113):

```python
f"2. category: Eine Kategorie für die Ordnerstruktur "
f"(z.B. 'Rechnungen', 'Verträge', 'Steuer', 'Privat', 'Gesundheit', 'Versicherung', 'YOUR_CATEGORY'). "
```

### Add Custom File Types

Edit [config.py](src/config.py):

```python
SUPPORTED_EXTENSIONS: Set[str] = {".pdf", ".jpg", ".png", ".jpeg", ".tiff", ".bmp"}
```

Ensure appropriate handlers exist in [extractor.py](src/extractor.py).

### Adjust LLM Behavior

Modify the prompt template in [analyzer.py](src/analyzer.py) method `_build_prompt()`.

### Change Filename Format

Edit the prompt to request different formats, or post-process in [file_manager.py](src/file_manager.py).

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

**Guidelines:**
- Follow existing code style (type hints, docstrings, logging)
- Add tests for new features
- Update documentation as needed

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Ollama](https://ollama.ai) - Local LLM runtime
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) - Open source OCR engine
- [Watchdog](https://github.com/gorakhargosh/watchdog) - File system monitoring
- [pypdf](https://github.com/py-pdf/pypdf) - PDF processing library

## Support

For issues, questions, or suggestions:

- Open an issue on GitHub
- Check existing issues for solutions
- Review logs with `LOG_LEVEL=DEBUG` for detailed diagnostics

## Roadmap

Potential future enhancements:

- [ ] Web UI for configuration and monitoring
- [ ] Support for additional file types (Word, Excel, etc.)
- [ ] Custom rules engine for categorization
- [ ] Duplicate detection
- [ ] Automated backup integration
- [ ] Mobile app integration (scan directly to inbox)
- [ ] Multi-language UI
- [ ] Training mode to improve categorization

---

**Made with privacy in mind. Your documents, your machine, your control.**
