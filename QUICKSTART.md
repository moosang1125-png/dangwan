# Quick Start Guide

## 🚀 Getting Started in 3 Steps

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: (Optional) Set up Google Sheets
If you want to write to Google Sheets:
1. Visit https://console.cloud.google.com/
2. Create project → Enable Google Sheets API → Create OAuth 2.0 credentials
3. Download credentials as `config/credentials.json`

### Step 3: Process Your PDFs
```bash
python main.py your_textbook.pdf
```

## 📋 Common Commands

```bash
# Process single PDF
python main.py document.pdf

# Process multiple PDFs (they will be combined)
python main.py part1.pdf part2.pdf part3.pdf

# Start fresh (reset session counter)
python main.py document.pdf --reset-context

# Force re-extraction (ignore cache)
python main.py document.pdf --no-cache

# Custom spreadsheet title
python main.py document.pdf --spreadsheet-title "My Study Plan 2024"
```

## 🎯 What Gets Extracted

The system automatically identifies and extracts:

- ✅ **Chapter/Unit titles** → Major Unit column
- ✅ **Section headings** → Subtopic/Theme column
- ✅ **Page numbers** → Page Range column
- ✅ **Learning objectives** → Learning Goals column
- ✅ **Practice problems** → Homework column
- ✅ **Review questions** → Check Test column

## 📊 Output Format

Creates Google Sheets with these columns:

| 차수 | 대단원 | 소주제/테마 | 페이지 범위 | 학습 목표 | 숙제 | 체크 테스트 | 날짜 | 완료 상태 |
|------|--------|-------------|-------------|----------|------|-------------|------|----------|

(Session, Major Unit, Subtopic, Pages, Learning Goals, Homework, Check Test, Date, Status)

## 🔍 Verifying Without Google Sheets

Even without Google Sheets credentials, you can:
1. Process PDFs to test extraction
2. Check `cache/` directory for extracted data
3. View `cache/document_context.json` for session info

## 💡 Tips

- **Multi-part PDFs**: Process in order, context is maintained automatically
- **Caching**: First run extracts, subsequent runs use cache for speed
- **Korean + English**: System handles bilingual content
- **Debugging**: Check cache files to see what was extracted

## 🎬 Run Demo

```bash
cd examples
./demo.sh
```

This demonstrates all features using sample PDFs.
