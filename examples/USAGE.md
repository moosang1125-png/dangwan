# Example usage of Dangwan

## Basic Usage

### Process a single PDF
```bash
python main.py path/to/document.pdf
```

### Process multiple PDFs into one spreadsheet
```bash
python main.py part1.pdf part2.pdf part3.pdf --spreadsheet-title "Math Curriculum"
```

### Append to existing spreadsheet
```bash
python main.py new_chapter.pdf --spreadsheet-id "YOUR_SPREADSHEET_ID"
```

### Reset context (start fresh)
```bash
python main.py document.pdf --reset-context
```

### Force re-extraction (ignore cache)
```bash
python main.py document.pdf --no-cache
```

## Expected Output

The script will create a Google Spreadsheet with these columns:

| A | B | C | D | E | F | G | H | I |
|---|---|---|---|---|---|---|---|---|
| 차수 | 대단원 | 소주제/테마 | 페이지 범위 | 학습 목표 및 튜터 코칭 포인트 | 숙제 | 체크 테스트 | 날짜 | 완료 상태 |
| Session | Major Unit | Subtopic | Pages | Learning Goals | Homework | Check Test | Date | Status |

Example row:
```
1 | Chapter 1: Introduction | Basic Concepts | 1-10 | Understand fundamental principles | Practice problems 1-5 | Review questions 1-3 | | 
```
