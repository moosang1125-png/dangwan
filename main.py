#!/usr/bin/env python3
"""
Main script for automated unit management table creation
"""

import os
import sys
import argparse
from typing import Optional

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from pdf_processor import PDFProcessor
from sheets_writer import GoogleSheetsWriter
from data_processor import DataProcessor


class UnitManagementTableCreator:
    """
    Main orchestrator for creating unit management tables from PDFs
    """
    
    def __init__(self, cache_dir: str = "cache", credentials_path: str = "config/credentials.json"):
        """
        Initialize the creator
        
        Args:
            cache_dir: Directory for caching PDF extraction results
            credentials_path: Path to Google API credentials
        """
        self.pdf_processor = PDFProcessor(cache_dir=cache_dir)
        self.data_processor = DataProcessor(cache_dir=cache_dir)
        self.sheets_writer = None
        self.credentials_path = credentials_path
    
    def _init_sheets_writer(self):
        """Initialize sheets writer lazily"""
        if self.sheets_writer is None:
            try:
                self.sheets_writer = GoogleSheetsWriter(credentials_path=self.credentials_path)
            except FileNotFoundError as e:
                print(f"\nError: {e}")
                print("\nTo use Google Sheets integration, you need to:")
                print("1. Go to https://console.cloud.google.com/")
                print("2. Create a new project or select existing one")
                print("3. Enable Google Sheets API")
                print("4. Create OAuth 2.0 credentials")
                print("5. Download credentials and save as 'config/credentials.json'")
                print("\nFor now, the data will only be cached locally.")
                return False
        return True
    
    def process_pdf(self, pdf_path: str, spreadsheet_id: Optional[str] = None,
                   spreadsheet_title: Optional[str] = None, use_cache: bool = True) -> dict:
        """
        Process a PDF file and create/update spreadsheet
        
        Args:
            pdf_path: Path to PDF file
            spreadsheet_id: Existing spreadsheet ID (optional)
            spreadsheet_title: Title for new spreadsheet (optional)
            use_cache: Whether to use cached PDF extraction
            
        Returns:
            Dictionary with processing results
        """
        print(f"\n{'='*60}")
        print(f"Processing PDF: {pdf_path}")
        print(f"{'='*60}\n")
        
        # Validate PDF exists
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        # Step 1: Extract text and data from PDF
        print("Step 1: Extracting text from PDF...")
        extracted_data = self.pdf_processor.extract_text_from_pdf(pdf_path, use_cache=use_cache)
        print(f"  ✓ Extracted {extracted_data['total_pages']} pages")
        
        # Step 2: Extract chapter structure
        print("\nStep 2: Analyzing document structure...")
        chapters = self.pdf_processor.extract_chapter_structure(extracted_data)
        print(f"  ✓ Found {len(chapters)} chapters/units")
        for i, chapter in enumerate(chapters, 1):
            print(f"    {i}. {chapter['title'][:60]}..." if len(chapter['title']) > 60 else f"    {i}. {chapter['title']}")
        
        # Step 3: Extract metadata
        print("\nStep 3: Extracting metadata...")
        metadata = self.pdf_processor.extract_metadata(extracted_data)
        print(f"  ✓ Found {len(metadata['learning_goals'])} learning goal sections")
        print(f"  ✓ Found {len(metadata['homework_tasks'])} homework sections")
        print(f"  ✓ Found {len(metadata['review_questions'])} review question sections")
        
        # Step 4: Process data
        print("\nStep 4: Processing and organizing data...")
        rows = self.data_processor.process_pdf_data(extracted_data, chapters, metadata)
        print(f"  ✓ Created {len(rows)} rows for spreadsheet")
        
        # Step 5: Write to Google Sheets (if configured)
        result = {
            'pdf_file': pdf_path,
            'pages_processed': extracted_data['total_pages'],
            'chapters_found': len(chapters),
            'rows_created': len(rows),
            'spreadsheet_url': None
        }
        
        if self._init_sheets_writer():
            print("\nStep 5: Writing to Google Sheets...")
            
            # Create or use existing spreadsheet
            if not spreadsheet_id:
                if not spreadsheet_title:
                    spreadsheet_title = f"Unit Management - {os.path.basename(pdf_path)}"
                
                print(f"  Creating new spreadsheet: {spreadsheet_title}")
                spreadsheet_id = self.sheets_writer.create_spreadsheet(spreadsheet_title)
                print(f"  ✓ Spreadsheet created: {spreadsheet_id}")
                
                # Setup headers
                print("  Setting up headers...")
                self.sheets_writer.setup_headers(spreadsheet_id)
                print("  ✓ Headers configured")
            
            # Write data
            print("  Writing data rows...")
            self.sheets_writer.batch_append_rows(spreadsheet_id, "Sheet1", rows)
            print(f"  ✓ Written {len(rows)} rows")
            
            # Get URL
            spreadsheet_url = self.sheets_writer.get_spreadsheet_url(spreadsheet_id)
            result['spreadsheet_id'] = spreadsheet_id
            result['spreadsheet_url'] = spreadsheet_url
            
            print(f"\n{'='*60}")
            print(f"✓ Processing complete!")
            print(f"{'='*60}")
            print(f"\nSpreadsheet URL: {spreadsheet_url}")
        else:
            print("\nStep 5: Skipping Google Sheets (not configured)")
            print(f"\n{'='*60}")
            print(f"✓ PDF processing complete! (Data cached locally)")
            print(f"{'='*60}")
        
        # Show context summary
        context = self.data_processor.get_context_summary()
        print(f"\nContext Summary:")
        print(f"  - Total files processed: {context['processed_files_count']}")
        print(f"  - Total chapters: {context['chapters_count']}")
        print(f"  - Current session number: {context['current_session']}")
        
        return result
    
    def process_multiple_pdfs(self, pdf_paths: list, spreadsheet_title: str = "Unit Management Table") -> dict:
        """
        Process multiple PDF files into a single spreadsheet
        
        Args:
            pdf_paths: List of PDF file paths
            spreadsheet_title: Title for the spreadsheet
            
        Returns:
            Dictionary with processing results
        """
        if not pdf_paths:
            raise ValueError("No PDF files provided")
        
        print(f"\n{'='*60}")
        print(f"Processing {len(pdf_paths)} PDF files")
        print(f"{'='*60}\n")
        
        # Create spreadsheet first
        spreadsheet_id = None
        if self._init_sheets_writer():
            print(f"Creating spreadsheet: {spreadsheet_title}")
            spreadsheet_id = self.sheets_writer.create_spreadsheet(spreadsheet_title)
            self.sheets_writer.setup_headers(spreadsheet_id)
            print(f"✓ Spreadsheet created: {spreadsheet_id}\n")
        
        # Process each PDF
        total_rows = 0
        for i, pdf_path in enumerate(pdf_paths, 1):
            print(f"\n[{i}/{len(pdf_paths)}] Processing: {pdf_path}")
            result = self.process_pdf(pdf_path, spreadsheet_id=spreadsheet_id)
            total_rows += result['rows_created']
        
        result = {
            'pdf_files': pdf_paths,
            'total_pdfs': len(pdf_paths),
            'total_rows': total_rows,
            'spreadsheet_id': spreadsheet_id,
            'spreadsheet_url': self.sheets_writer.get_spreadsheet_url(spreadsheet_id) if spreadsheet_id else None
        }
        
        print(f"\n{'='*60}")
        print(f"✓ All PDFs processed!")
        print(f"{'='*60}")
        print(f"Total PDFs: {len(pdf_paths)}")
        print(f"Total rows: {total_rows}")
        if result['spreadsheet_url']:
            print(f"Spreadsheet: {result['spreadsheet_url']}")
        
        return result


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Automate unit management table creation from PDF files"
    )
    
    parser.add_argument(
        'pdf_files',
        nargs='+',
        help='Path to PDF file(s) to process'
    )
    
    parser.add_argument(
        '--spreadsheet-id',
        help='Existing Google Spreadsheet ID to append to'
    )
    
    parser.add_argument(
        '--spreadsheet-title',
        default='Unit Management Table',
        help='Title for new spreadsheet (default: "Unit Management Table")'
    )
    
    parser.add_argument(
        '--cache-dir',
        default='cache',
        help='Directory for caching (default: "cache")'
    )
    
    parser.add_argument(
        '--credentials',
        default='config/credentials.json',
        help='Path to Google API credentials (default: "config/credentials.json")'
    )
    
    parser.add_argument(
        '--no-cache',
        action='store_true',
        help='Disable caching and force re-extraction'
    )
    
    parser.add_argument(
        '--reset-context',
        action='store_true',
        help='Reset processing context (session counter, etc.)'
    )
    
    args = parser.parse_args()
    
    # Create creator
    creator = UnitManagementTableCreator(
        cache_dir=args.cache_dir,
        credentials_path=args.credentials
    )
    
    # Reset context if requested
    if args.reset_context:
        print("Resetting processing context...")
        creator.data_processor.reset_context()
        print("✓ Context reset\n")
    
    try:
        # Process PDFs
        if len(args.pdf_files) == 1:
            creator.process_pdf(
                args.pdf_files[0],
                spreadsheet_id=args.spreadsheet_id,
                spreadsheet_title=args.spreadsheet_title,
                use_cache=not args.no_cache
            )
        else:
            creator.process_multiple_pdfs(
                args.pdf_files,
                spreadsheet_title=args.spreadsheet_title
            )
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
