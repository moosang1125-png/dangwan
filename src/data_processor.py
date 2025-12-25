"""
Data Processor Module
Handles contextual processing and data transformation between PDF extraction and spreadsheet writing
"""

from typing import List, Dict, Optional
import os
import json


class DataProcessor:
    """
    Process extracted PDF data and prepare it for spreadsheet writing
    """
    
    def __init__(self, cache_dir: str = "cache"):
        """
        Initialize data processor
        
        Args:
            cache_dir: Directory for persistent context storage
        """
        self.cache_dir = cache_dir
        self.context_file = os.path.join(cache_dir, "document_context.json")
        self.context = self._load_context()
    
    def _load_context(self) -> Dict:
        """Load persistent context from previous processing"""
        if os.path.exists(self.context_file):
            with open(self.context_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            'processed_files': [],
            'chapters': [],
            'current_chapter': None,
            'session_counter': 0
        }
    
    def _save_context(self):
        """Save context for future processing"""
        os.makedirs(os.path.dirname(self.context_file), exist_ok=True)
        with open(self.context_file, 'w', encoding='utf-8') as f:
            json.dump(self.context, f, ensure_ascii=False, indent=2)
    
    def process_pdf_data(self, extracted_data: Dict, chapters: List[Dict], 
                        metadata: Dict) -> List[List]:
        """
        Process extracted PDF data and create rows for spreadsheet
        
        Args:
            extracted_data: Data from PDFProcessor.extract_text_from_pdf
            chapters: Chapter structure from PDFProcessor.extract_chapter_structure
            metadata: Metadata from PDFProcessor.extract_metadata
            
        Returns:
            List of rows ready to be written to spreadsheet
        """
        rows = []
        
        # Update context with current file
        file_name = extracted_data['file_name']
        if file_name not in self.context['processed_files']:
            self.context['processed_files'].append(file_name)
        
        # Process each chapter
        for chapter in chapters:
            self.context['session_counter'] += 1
            
            # Determine if this is a continuation of previous chapter
            is_continuation = self._is_chapter_continuation(chapter)
            
            # Extract page range
            page_range = self._extract_page_range(chapter, extracted_data)
            
            # Extract learning goals
            learning_goals = self._extract_learning_goals(chapter, metadata)
            
            # Extract homework
            homework = self._extract_homework(chapter, metadata)
            
            # Extract check test questions
            check_test = self._extract_check_test(chapter, metadata)
            
            # Create row
            row = [
                str(self.context['session_counter']),  # Session number
                chapter.get('title', ''),  # Major Unit
                self._extract_subtopic(chapter),  # Subtopic/Theme
                page_range,  # Page Range
                learning_goals,  # Learning Goals
                homework,  # Homework
                check_test,  # Check Test
                '',  # Date (to be filled manually)
                ''   # Completion status (to be filled manually)
            ]
            
            rows.append(row)
            
            # Update context
            self.context['current_chapter'] = chapter.get('title', '')
            if chapter not in self.context['chapters']:
                self.context['chapters'].append({
                    'title': chapter.get('title', ''),
                    'session': self.context['session_counter']
                })
        
        # Save updated context
        self._save_context()
        
        return rows
    
    def _is_chapter_continuation(self, chapter: Dict) -> bool:
        """
        Determine if current chapter is a continuation of a previous one
        
        Args:
            chapter: Chapter data
            
        Returns:
            True if this chapter continues a previous topic
        """
        if not self.context['current_chapter']:
            return False
        
        # Simple heuristic: check if chapter titles are similar
        current_title = chapter.get('title', '').lower()
        previous_title = self.context['current_chapter'].lower()
        
        # If titles share significant words, it might be a continuation
        current_words = set(current_title.split())
        previous_words = set(previous_title.split())
        
        if len(current_words & previous_words) >= 2:
            return True
        
        return False
    
    def _extract_page_range(self, chapter: Dict, extracted_data: Dict) -> str:
        """
        Extract page range for a chapter
        
        Args:
            chapter: Chapter data
            extracted_data: Full PDF extraction data
            
        Returns:
            Page range string (e.g., "10-15")
        """
        start_page = chapter.get('start_page', 1)
        
        # Find end page (either next chapter or last page)
        end_page = extracted_data['total_pages']
        
        # In a real implementation, you'd find the next chapter's start
        # For now, estimate based on content
        
        return f"{start_page}-{end_page}"
    
    def _extract_subtopic(self, chapter: Dict) -> str:
        """
        Extract subtopic or theme from chapter content
        
        Args:
            chapter: Chapter data
            
        Returns:
            Subtopic string
        """
        # Analyze first few lines of content for subtopic
        content = chapter.get('content', [])
        if content and len(content) > 0:
            # First non-empty line after title might be subtopic
            for line in content[:5]:
                if line and len(line) > 5 and len(line) < 100:
                    return line
        
        return ""
    
    def _extract_learning_goals(self, chapter: Dict, metadata: Dict) -> str:
        """
        Extract learning goals from chapter
        
        Args:
            chapter: Chapter data
            metadata: Extracted metadata
            
        Returns:
            Learning goals string
        """
        # Look for learning goals in metadata that match this chapter's pages
        start_page = chapter.get('start_page', 0)
        goals = []
        
        for goal_data in metadata.get('learning_goals', []):
            if goal_data['page'] >= start_page:
                # Extract relevant text
                text = goal_data['text']
                # Simple extraction - take first relevant line
                lines = text.split('\n')
                for line in lines:
                    if 'goal' in line.lower() or '목표' in line:
                        goals.append(line.strip())
                        break
        
        return ' | '.join(goals) if goals else ""
    
    def _extract_homework(self, chapter: Dict, metadata: Dict) -> str:
        """
        Extract homework tasks from chapter
        
        Args:
            chapter: Chapter data
            metadata: Extracted metadata
            
        Returns:
            Homework string
        """
        start_page = chapter.get('start_page', 0)
        homework = []
        
        for hw_data in metadata.get('homework_tasks', []):
            if hw_data['page'] >= start_page:
                text = hw_data['text']
                lines = text.split('\n')
                for line in lines:
                    if any(keyword in line.lower() for keyword in ['homework', '숙제', '과제', 'practice']):
                        homework.append(line.strip())
                        break
        
        return ' | '.join(homework) if homework else ""
    
    def _extract_check_test(self, chapter: Dict, metadata: Dict) -> str:
        """
        Extract check test questions from chapter
        
        Args:
            chapter: Chapter data
            metadata: Extracted metadata
            
        Returns:
            Check test string
        """
        start_page = chapter.get('start_page', 0)
        questions = []
        
        for question_data in metadata.get('review_questions', []):
            if question_data['page'] >= start_page:
                text = question_data['text']
                lines = text.split('\n')
                for line in lines:
                    if any(keyword in line.lower() for keyword in ['question', 'review', '문제', '복습']):
                        questions.append(line.strip())
                        break
        
        return ' | '.join(questions) if questions else ""
    
    def reset_context(self):
        """Reset the processing context"""
        self.context = {
            'processed_files': [],
            'chapters': [],
            'current_chapter': None,
            'session_counter': 0
        }
        self._save_context()
    
    def get_context_summary(self) -> Dict:
        """Get a summary of current context"""
        return {
            'processed_files_count': len(self.context['processed_files']),
            'chapters_count': len(self.context['chapters']),
            'current_session': self.context['session_counter'],
            'files': self.context['processed_files']
        }
