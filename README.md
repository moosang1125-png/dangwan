# Dangwan - Automated Unit Management Table Creation

This project automates the creation of unit management tables based on educational PDF materials. It analyzes split PDF files, extracts relevant data such as chapter titles, page ranges, and key concepts, and organizes them into a structured Google Spreadsheet format.

## Features

1. **PDF Analysis**: Process split PDF files to extract text, images, and structured data using PyMuPDF (fitz)
2. **Document Caching**: Cache extracted data locally for efficient processing of multi-part documents
3. **Spreadsheet Integration**: Automatically create and populate Google Sheets with standardized headers
4. **Contextual Processing**: Reference previous PDF sections when processing multi-part documents
5. **Error Handling & Validation**: Validate data extraction for accuracy

## Installation

### Prerequisites
- Python 3.8 or higher
- Tesseract OCR (for image text extraction)

### Install Tesseract
- **Ubuntu/Debian**: `sudo apt-get install tesseract-ocr tesseract-ocr-kor`
- **macOS**: `brew install tesseract tesseract-lang`
- **Windows**: Download from https://github.com/UB-Mannheim/tesseract/wiki

### Install Python Dependencies

```bash
pip install -r requirements.txt
```

## Setup

### Google Sheets API Configuration

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google Sheets API
4. Create OAuth 2.0 credentials (Desktop application type)
5. Download the credentials JSON file
6. Save it as `config/credentials.json`

On first run, the script will open a browser for authentication. After authentication, a token will be saved for future use.

## Usage

### Basic Usage

Process a single PDF:
```bash
python main.py path/to/document.pdf
```

Process multiple PDFs into one spreadsheet:
```bash
python main.py part1.pdf part2.pdf part3.pdf
```

### Advanced Options

```bash
# Custom spreadsheet title
python main.py document.pdf --spreadsheet-title "My Study Plan"

# Append to existing spreadsheet
python main.py document.pdf --spreadsheet-id "YOUR_SPREADSHEET_ID"

# Reset processing context
python main.py document.pdf --reset-context

# Force re-extraction (ignore cache)
python main.py document.pdf --no-cache

# Custom cache directory
python main.py document.pdf --cache-dir /path/to/cache

# Custom credentials path
python main.py document.pdf --credentials /path/to/credentials.json
```

## Output Format

The script creates a Google Spreadsheet with the following columns:

| Column | Header | Description |
|--------|--------|-------------|
| A | 차수 (Session) | Session/comma number |
| B | 대단원 (Major Unit) | Chapter heading |
| C | 소주제/테마 (Subtopic/Theme) | Subtopic or theme |
| D | 페이지 범위 (Page Range) | Page range (e.g., "10-15") |
| E | 학습 목표 및 튜터 코칭 포인트 (Learning Goals) | Learning objectives and coaching points |
| F | 숙제 (Homework) | 90-minute self-study tasks |
| G | 체크 테스트 (Check Test) | Review questions |
| H | 날짜 (Date) | Date (to be filled manually) |
| I | 완료 상태 (Status) | Completion status (to be filled manually) |

## Project Structure

```
dangwan/
├── main.py                 # Main entry point
├── requirements.txt        # Python dependencies
├── src/
│   ├── __init__.py
│   ├── pdf_processor.py    # PDF extraction and analysis
│   ├── sheets_writer.py    # Google Sheets integration
│   └── data_processor.py   # Data transformation and context handling
├── config/
│   ├── README.md           # Configuration instructions
│   └── credentials.json    # Google API credentials (you provide this)
├── cache/                  # Cached extraction results
├── examples/
│   └── USAGE.md           # Usage examples
└── README.md              # This file
```

## How It Works

1. **PDF Extraction**: The script reads PDF files and extracts text from each page
2. **Structure Analysis**: Identifies chapter headings, sections, and key elements
3. **Metadata Extraction**: Finds learning goals, homework tasks, and review questions
4. **Context Management**: Maintains state across multiple PDF files for continuity
5. **Data Transformation**: Organizes extracted data into spreadsheet rows
6. **Spreadsheet Writing**: Creates/updates Google Sheets with formatted data

## Caching

The system caches PDF extraction results to improve performance:
- Cache is stored in the `cache/` directory
- Each PDF is hashed to detect changes
- Use `--no-cache` to force re-extraction
- Use `--reset-context` to clear processing state

## Multi-Part PDFs

When processing multiple PDFs that are parts of the same document:
1. Process them in order
2. The system maintains context between parts
3. Session numbers increment automatically
4. Chapter continuations are detected

## Troubleshooting

### Google Sheets Authentication Issues
- Delete `config/token.pickle` and re-authenticate
- Verify credentials.json is valid
- Check that Google Sheets API is enabled

### PDF Extraction Issues
- Ensure PDF is not password protected
- Verify PDF contains readable text (not just images)
- For image-based PDFs, ensure Tesseract is installed

### OCR Not Working
- Install Tesseract OCR and language packs
- Verify Tesseract is in system PATH
- For Korean text, install `tesseract-ocr-kor`

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## License

This project is available for educational purposes.