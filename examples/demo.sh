#!/bin/bash
# Demonstration script for Dangwan features

echo "============================================"
echo "Dangwan Feature Demonstration"
echo "============================================"
echo ""

# Clean up from previous runs
echo "1. Cleaning up cache..."
rm -rf cache/
echo "   ✓ Cache cleared"
echo ""

# Feature 1: Basic PDF processing
echo "2. Processing single PDF file..."
python main.py examples/sample_textbook.pdf
echo ""

# Feature 2: Multi-part PDF processing
echo "3. Processing second PDF (context continuation)..."
python main.py examples/sample_textbook_part2.pdf
echo ""

# Feature 3: Show cache contents
echo "4. Showing cached data..."
echo "   Files in cache:"
ls -lh cache/
echo ""
echo "   Document context:"
cat cache/document_context.json
echo ""

# Feature 4: Multiple PDFs at once
echo "5. Resetting and processing multiple PDFs together..."
python main.py examples/sample_textbook.pdf examples/sample_textbook_part2.pdf --reset-context --spreadsheet-title "Complete Textbook"
echo ""

# Feature 5: Test help
echo "6. Available command-line options:"
python main.py --help
echo ""

echo "============================================"
echo "Demonstration Complete!"
echo "============================================"
echo ""
echo "Summary:"
echo "- ✓ PDF text extraction"
echo "- ✓ Chapter structure detection"
echo "- ✓ Metadata extraction (learning goals, homework, questions)"
echo "- ✓ Context preservation across PDFs"
echo "- ✓ Data caching"
echo "- ✓ Ready for Google Sheets integration (add credentials.json)"
