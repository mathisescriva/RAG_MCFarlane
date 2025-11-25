"""
PDF Loader for REG Yacht Code Part B
Extracts specific sections from the PDF document
"""

import re
from typing import List, Dict, Tuple
import pdfplumber
from pathlib import Path


class PDFLoader:
    """
    Loads and extracts specific sections from REG Yacht Code Part B PDF.
    
    Target sections:
    - 4.3 – Intact Stability and Information
    - 4.4 – Stability Information to be Supplied to the Master
    - 4.22 – Damage Control Information
    - 4.23 – Loading Procedures
    - 4.24 – Watertight Door Inspection and Operation
    - 4.30 – Stability in Damaged Condition
    """
    
    TARGET_SECTIONS = [
        "4.3",  # Intact Stability and Information
        "4.4",  # Stability Information to be Supplied to the Master
        "4.22",  # Damage Control Information
        "4.23",  # Loading Procedures
        "4.24",  # Watertight Door Inspection and Operation
        "4.30",  # Stability in Damaged Condition
    ]
    
    def __init__(self, pdf_path: str):
        """
        Initialize PDF loader.
        
        Args:
            pdf_path: Path to the REG Yacht Code Part B PDF file
        """
        self.pdf_path = Path(pdf_path)
        if not self.pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
    
    def extract_sections(self) -> List[Dict[str, any]]:
        """
        Extract target sections from PDF.
        
        Returns:
            List of dictionaries containing:
            - section_number: str (e.g., "4.3")
            - title: str (section title)
            - text: str (full section text)
            - page_start: int (first page of section)
            - page_end: int (last page of section)
        """
        extracted_sections = []
        
        with pdfplumber.open(self.pdf_path) as pdf:
            # Collect all text with page numbers
            all_text_pages = []
            for page_num, page in enumerate(pdf.pages, start=1):
                text = page.extract_text()
                if text:
                    all_text_pages.append((page_num, text))
            
            # Track current section being collected
            current_section = None
            current_text_parts = []
            current_title = None
            page_start = None
            
            # Pattern to match MAIN section headers (exactly matches target sections)
            # Matches: "4.3 Intact Stability...", "4.3 – Title", "4.4 Stability..."
            # NOT: "4.3.1", "4.3: 0", "4.3: 1", etc.
            # The pattern ensures the section number is followed by space/dash and title (not colon or dot)
            # Also filters out lines that are just numbers (page numbers)
            main_section_pattern = re.compile(
                r'^(' + '|'.join(re.escape(s) for s in self.TARGET_SECTIONS) + r')\s+([A-Z].+?)(?:\d*$|\n)',
                re.IGNORECASE
            )
            
            for page_num, page_text in all_text_pages:
                lines = page_text.split('\n')
                
                for line in lines:
                    line_stripped = line.strip()
                    if not line_stripped:
                        if current_section:
                            current_text_parts.append("")  # Preserve paragraph breaks
                        continue
                    
                    # Check if this line is a main section header
                    match = main_section_pattern.match(line_stripped)
                    if match:
                        section_num = match.group(1)
                        title = match.group(2).strip() if match.group(2) else ""
                        
                        # Save previous section if we have one
                        if current_section:
                            full_text = "\n".join(current_text_parts)
                            if full_text.strip():
                                extracted_sections.append({
                                    "section_number": current_section,
                                    "title": current_title or f"Section {current_section}",
                                    "text": self.clean_text(full_text),
                                    "page_start": page_start,
                                    "page_end": page_num - 1
                                })
                        
                        # Start new section
                        current_section = section_num
                        current_title = title or f"Section {section_num}"
                        current_text_parts = [line_stripped]
                        page_start = page_num
                    else:
                        # Regular line - add to current section if we're collecting one
                        if current_section:
                            current_text_parts.append(line_stripped)
            
            # Save the last section
            if current_section:
                full_text = "\n".join(current_text_parts)
                if full_text.strip():
                    extracted_sections.append({
                        "section_number": current_section,
                        "title": current_title or f"Section {current_section}",
                        "text": self.clean_text(full_text),
                        "page_start": page_start,
                        "page_end": all_text_pages[-1][0] if all_text_pages else page_start
                    })
        
        return extracted_sections
    
    def clean_text(self, text: str) -> str:
        """
        Clean extracted text by removing headers, footers, and excessive whitespace.
        
        Args:
            text: Raw extracted text
            
        Returns:
            Cleaned text
        """
        # Remove page numbers and headers/footers (common patterns)
        text = re.sub(r'^\d+\s*$', '', text, flags=re.MULTILINE)  # Standalone page numbers
        text = re.sub(r'REG Yacht Code.*?Part B', '', text, flags=re.IGNORECASE)
        text = re.sub(r'July 2024', '', text, flags=re.IGNORECASE)
        
        # Normalize whitespace
        text = re.sub(r'\n{3,}', '\n\n', text)  # Max 2 consecutive newlines
        text = re.sub(r'[ \t]+', ' ', text)  # Multiple spaces to single
        
        return text.strip()

