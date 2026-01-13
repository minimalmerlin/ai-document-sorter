# Quick Start Guide - AI Document Sorter

Get up and running in 5 minutes!

## Prerequisites Check

Before you start, ensure you have:

- [ ] Python 3.8+ installed
- [ ] Tesseract OCR installed
- [ ] Poppler installed (for PDF conversion)
- [ ] Ollama installed and running

### Quick Install Commands

**macOS:**
```bash
# Install prerequisites
brew install tesseract tesseract-lang poppler

# Install Ollama from https://ollama.ai, then:
ollama pull llama3.2
```

**Ubuntu/Debian:**
```bash
# Install prerequisites
sudo apt-get update
sudo apt-get install tesseract-ocr tesseract-ocr-deu tesseract-ocr-eng poppler-utils

# Install Ollama
curl https://ollama.ai/install.sh | sh
ollama pull llama3.2
```

## Installation (3 Steps)

### 1. Setup Python Environment

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Settings

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your paths (use a text editor)
# Minimum required: INBOX_PATH and TARGET_ROOT
```

**Example `.env` (minimal):**
```bash
INBOX_PATH=/Users/yourname/Documents/Inbox_Scan
TARGET_ROOT=/Users/yourname/Documents/Sorted_Documents
MODEL_NAME=llama3.2
```

### 3. Create Directories

```bash
# Create the directories specified in .env
mkdir -p ~/Documents/Inbox_Scan
mkdir -p ~/Documents/Sorted_Documents
```

## Running the Application

### Start Ollama (if not running)

```bash
ollama serve
```

### Run the Document Sorter

**Option 1: Using run.py**
```bash
python run.py
```

**Option 2: Using module**
```bash
python -m src.main
```

### What You Should See

```
============================================================
AI Document Sorter - Starting
============================================================
INFO - Inbox Path: /Users/yourname/Documents/Inbox_Scan
INFO - Target Path: /Users/yourname/Documents/Sorted_Documents
INFO - Ollama Model: llama3.2
INFO - Starting initial directory scan (catch-up mode)
INFO - Directory monitoring started
INFO - Monitor is now active. Press Ctrl+C to stop.
```

## Test It!

1. Drop a PDF or image file into your inbox folder
2. Watch the logs - you should see:
   - Content extraction
   - AI analysis
   - File moved to categorized folder

**Example:**
```
INFO - New file detected: receipt_scan.pdf
INFO - Processing file: receipt_scan.pdf
INFO - Analysis successful: 2026-01-13_Grocery_Receipt → Rechnungen
INFO - File moved successfully: receipt_scan.pdf → .../Rechnungen/2026-01-13_Grocery_Receipt.pdf
```

## Troubleshooting

### "Cannot connect to Ollama API"

**Solution:**
```bash
# Start Ollama in a separate terminal
ollama serve

# Verify it's running
curl http://localhost:11434/api/tags
```

### "TesseractNotFoundError"

**Solution:**
```bash
# macOS
brew install tesseract

# Ubuntu
sudo apt-get install tesseract-ocr

# Verify installation
tesseract --version
```

### "pdf2image errors"

**Solution:**
```bash
# macOS
brew install poppler

# Ubuntu
sudo apt-get install poppler-utils
```

### No files are being processed

**Check:**
1. Files are in the correct inbox directory
2. Files have supported extensions (`.pdf`, `.jpg`, `.png`, `.jpeg`)
3. Files are not iCloud placeholders (`.icloud`)
4. Check logs with `LOG_LEVEL=DEBUG` in `.env`

## Stop the Application

Press `Ctrl+C` in the terminal where the app is running.

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Customize categories by editing the prompt in `src/analyzer.py`
- Add custom file types in `src/config.py`
- Set up automatic startup (see README.md)

## Running in Background (Advanced)

**macOS/Linux:**
```bash
# Using nohup
nohup python run.py > document-sorter.log 2>&1 &

# Check it's running
ps aux | grep run.py

# Stop it
pkill -f run.py
```

**Using screen:**
```bash
screen -S document-sorter
python run.py
# Press Ctrl+A, then D to detach

# Reattach later
screen -r document-sorter
```

## File Organization Example

After processing, your folder structure will look like:

```
Sorted_Documents/
├── Rechnungen/
│   ├── 2026-01-10_Stromrechnung.pdf
│   ├── 2026-01-12_Supermarkt_Einkauf.pdf
│   └── 2026-01-13_Amazon_Bestellung.pdf
├── Verträge/
│   ├── 2025-12-01_Mietvertrag_Wohnung.pdf
│   └── 2026-01-05_Versicherung_Auto.pdf
├── Steuer/
│   ├── 2025-12-31_Jahresabschluss.pdf
│   └── 2026-01-15_Spendenbescheinigung.pdf
└── Privat/
    └── 2026-01-01_Geburtsurkunde.pdf
```

---

**Need Help?** Check [README.md](README.md) or open an issue on GitHub.
