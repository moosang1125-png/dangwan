"""
PDF Processing Module
Handles extraction of text, images, and structured data from PDF files
"""

import os
import json
import hashlib
import io
from typing import Dict, List, Optional, Tuple
import fitz  # PyMuPDF
from PIL import Image
import pytesseract


class PDFProcessor:
    """
    Process PDF files to extract text, images, and structured data
    """
    
    def __init__(self, cache_dir: str = "cache"):
        """
        Initialize PDF processor
        
        Args:
            cache_dir: Directory to store cached extraction results
        """
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
    
    def _get_cache_key(self, pdf_path: str) -> str:
        """Generate a unique cache key for a PDF file"""
        with open(pdf_path, 'rb') as f:
            file_hash = hashlib.md5(f.read()).hexdigest()
        return f"{os.path.basename(pdf_path)}_{file_hash}"
    
    def _get_cache_path(self, cache_key: str) -> str:
        """Get the full path to the cache file"""
        return os.path.join(self.cache_dir, f"{cache_key}.json")
    
    def _load_from_cache(self, cache_key: str) -> Optional[Dict]:
        """Load extracted data from cache"""
        cache_path = self._get_cache_path(cache_key)
        if os.path.exists(cache_path):
            with open(cache_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None
    
    def _save_to_cache(self, cache_key: str, data: Dict):
        """Save extracted data to cache"""
        cache_path = self._get_cache_path(cache_key)
        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def extract_text_from_pdf(self, pdf_path: str, use_cache: bool = True) -> Dict:
        """
        Extract text content from PDF file
        
        Args:
            pdf_path: Path to the PDF file
            use_cache: Whether to use cached results if available
            
        Returns:
            Dictionary containing extracted text and metadata
        """
        cache_key = self._get_cache_key(pdf_path)
        
        # Check cache first
        if use_cache:
            cached_data = self._load_from_cache(cache_key)
            if cached_data:
                return cached_data
        
        # Extract text from PDF
        doc = fitz.open(pdf_path)
        pages_data = []
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text()
            
            # Extract images from page for potential OCR
            images = []
            image_list = page.get_images()
            
            for img_index, img in enumerate(image_list):
                xref = img[0]
                base_image = doc.extract_image(xref)
                images.append({
                    'index': img_index,
                    'width': base_image['width'],
                    'height': base_image['height'],
                    'ext': base_image['ext']
                })
            
            pages_data.append({
                'page_number': page_num + 1,
                'text': text,
                'images': images
            })
        
        doc.close()
        
        result = {
            'file_path': pdf_path,
            'file_name': os.path.basename(pdf_path),
            'total_pages': len(pages_data),
            'pages': pages_data
        }
        
        # Save to cache
        if use_cache:
            self._save_to_cache(cache_key, result)
        
        return result
    
    def extract_image_with_ocr(self, pdf_path: str, page_num: int, img_index: int) -> str:
        """
        Extract a specific image from PDF and perform OCR
        
        Args:
            pdf_path: Path to the PDF file
            page_num: Page number (1-indexed)
            img_index: Image index on the page
            
        Returns:
            Extracted text from image
        """
        doc = fitz.open(pdf_path)
        page = doc[page_num - 1]
        image_list = page.get_images()
        
        if img_index >= len(image_list):
            doc.close()
            return ""
        
        xref = image_list[img_index][0]
        base_image = doc.extract_image(xref)
        image_bytes = base_image["image"]
        
        # Convert to PIL Image
        image = Image.open(io.BytesIO(image_bytes))
        
        # Perform OCR
        text = pytesseract.image_to_string(image, lang='kor+eng')
        
        doc.close()
        return text
    
    def extract_chapter_structure(self, extracted_data: Dict) -> List[Dict]:
        """
        Analyze extracted text to identify chapter structure and key sections
        
        Args:
            extracted_data: Data returned from extract_text_from_pdf
            
        Returns:
            List of identified chapters with metadata
        """
        chapters = []
        current_chapter = None
        
        for page in extracted_data['pages']:
            text = page['text']
            lines = text.split('\n')
            
            for line in lines:
                line = line.strip()
                
                # Heuristic: Look for chapter markers
                # This can be customized based on actual PDF structure
                if self._is_chapter_heading(line):
                    if current_chapter:
                        chapters.append(current_chapter)
                    
                    current_chapter = {
                        'title': line,
                        'start_page': page['page_number'],
                        'content': []
                    }
                elif current_chapter:
                    current_chapter['content'].append(line)
        
        # Add the last chapter
        if current_chapter:
            chapters.append(current_chapter)
        
        return chapters
    
    def _is_chapter_heading(self, line: str) -> bool:
        """
        Determine if a line is a chapter heading
        
        This is a heuristic that can be customized based on the PDF structure
        """
        # Common patterns for chapter headings
        patterns = [
            line.startswith('Chapter'),
            line.startswith('제'),  # Korean chapter marker
            line.startswith('단원'),  # Korean unit marker
            (len(line) < 50 and line.isupper()),  # Short uppercase lines
        ]
        
        return any(patterns)
    
    def extract_metadata(self, extracted_data: Dict) -> Dict:
        """
        Extract metadata like learning goals, homework tasks, etc.
        
        Args:
            extracted_data: Data returned from extract_text_from_pdf
            
        Returns:
            Dictionary of extracted metadata
        """
        metadata = {
            'learning_goals': [],
            'homework_tasks': [],
            'review_questions': []
        }
        
        for page in extracted_data['pages']:
            text = page['text'].lower()
            
            # Look for learning goals
            if 'learning goal' in text or '학습 목표' in text:
                metadata['learning_goals'].append({
                    'page': page['page_number'],
                    'text': page['text']
                })
            
            # Look for homework indicators
            if 'homework' in text or '숙제' in text or '과제' in text:
                metadata['homework_tasks'].append({
                    'page': page['page_number'],
                    'text': page['text']
                })
            
            # Look for review questions
            if 'review' in text or 'question' in text or '복습' in text or '문제' in text:
                metadata['review_questions'].append({
                    'page': page['page_number'],
                    'text': page['text']
                })
        
        return metadata
