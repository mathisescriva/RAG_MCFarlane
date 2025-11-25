"""
PDF Loader for Malta Passenger Yacht Code (PYC)
Extracts specific sections from the Malta PYC PDF document
"""

import re
from typing import List, Dict, Any
import pdfplumber
from pathlib import Path


class MaltaPYCLoader:
    """
    Loads and extracts specific sections from Malta Passenger Yacht Code PDF.
    
    Target sections:
    - Section 2 – Application and Interpretation (for context)
    - Section 5 – Construction, Subdivision, Intact and Damage Stability
    """
    
    TARGET_SECTIONS = [
        "2",   # Application and Interpretation
        "5",   # Construction, Subdivision, Intact and Damage Stability
    ]
    
    def __init__(self, pdf_path: str):
        """
        Initialize Malta PYC loader.
        
        Args:
            pdf_path: Path to the Malta PYC PDF file
        """
        self.pdf_path = Path(pdf_path)
        if not self.pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
    
    def extract_sections(self) -> List[Dict[str, Any]]:
        """
        Extract target sections from Malta PYC PDF.
        
        Returns:
            List of dictionaries containing:
            - section_number: str (e.g., "2", "5")
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
            
            # Pattern to match MAIN section headers for Malta PYC
            # We want to match "SECTION 2" or "SECTION 5" as main headers
            # Then capture content until next "SECTION X"
            section_header_pattern = re.compile(
                r'^SECTION\s+(' + '|'.join(re.escape(s) for s in self.TARGET_SECTIONS) + r')\s*$',
                re.IGNORECASE
            )
            
            # Also match "2 APPLICATION AND INTERPRETATION" or "5 CONSTRUCTION..." style headers
            section_title_pattern = re.compile(
                r'^(' + '|'.join(re.escape(s) for s in self.TARGET_SECTIONS) + r')\s+([A-Z][A-Z\s]{15,})(?:\s|$)',
                re.IGNORECASE
            )
            
            for page_num, page_text in all_text_pages:
                lines = page_text.split('\n')
                page_has_section_header = False
                
                for line_idx, line in enumerate(lines):
                    line_stripped = line.strip()
                    if not line_stripped:
                        if current_section:
                            current_text_parts.append("")
                        continue
                    
                    # Check if this page has a "SECTION X" header (for detection)
                    section_header_match = re.match(r'^SECTION\s+(\d+)', line_stripped, re.IGNORECASE)
                    if section_header_match:
                        page_has_section_header = True
                    
                    # Check for "SECTION X" pattern (main section header)
                    section_num = None
                    title = None
                    
                    match = section_header_pattern.match(line_stripped)
                    if match:
                        section_num = match.group(1)
                        # Look for title in next 1-3 lines (some titles span multiple lines)
                        for next_line in lines[line_idx + 1:line_idx + 4]:
                            next_stripped = next_line.strip()
                            if next_stripped and (next_stripped.isupper() or next_stripped.startswith('CONSTRUCTION')):
                                if len(next_stripped) > 10:
                                    if title:
                                        title += " " + next_stripped
                                    else:
                                        title = next_stripped
                                    # Stop if we've found a complete title (usually 1-2 lines)
                                    if len(title) > 30:
                                        break
                    
                    # If not found, try "X TITLE" pattern (like "2 APPLICATION AND INTERPRETATION")
                    if not section_num:
                        match = section_title_pattern.match(line_stripped)
                        if match:
                            section_num = match.group(1)
                            title = match.group(2).strip()
                    
                    # If we found a target section header
                    if section_num and section_num in self.TARGET_SECTIONS:
                        # Save previous section if we have one
                        if current_section:
                            full_text = "\n".join(current_text_parts)
                            cleaned = self.clean_text(full_text)
                            # Only save if substantial content (avoid table of contents, etc.)
                            if cleaned.strip() and len(cleaned) > 1000:
                                extracted_sections.append({
                                    "section_number": current_section,
                                    "title": current_title or f"Section {current_section}",
                                    "text": cleaned,
                                    "page_start": page_start,
                                    "page_end": page_num - 1
                                })
                        
                        # Start new section
                        current_section = section_num
                        current_title = title or f"Section {section_num}"
                        current_text_parts = [line_stripped]
                        page_start = page_num
                    else:
                        # Check if we've hit a new main section (not a target)
                        # Look for "SECTION X" where X is not in our targets
                        if section_header_match:
                            new_section = section_header_match.group(1)
                            # If it's a new main section and we're collecting a target section, stop
                            if current_section and new_section not in self.TARGET_SECTIONS:
                                # Save current section (don't include the "SECTION X" line)
                                full_text = "\n".join(current_text_parts)
                                cleaned = self.clean_text(full_text)
                                if cleaned.strip() and len(cleaned) > 1000:
                                    extracted_sections.append({
                                        "section_number": current_section,
                                        "title": current_title or f"Section {current_section}",
                                        "text": cleaned,
                                        "page_start": page_start,
                                        "page_end": page_num - 1
                                    })
                                current_section = None
                                current_text_parts = []
                                current_title = None
                                page_start = None
                        else:
                            # Regular line - add to current section if we're collecting one
                            if current_section:
                                current_text_parts.append(line_stripped)
                
                # If we're in a section and this page doesn't have a new section header,
                # make sure we capture all content from the page
                if current_section and not page_has_section_header:
                    # Already added lines above, but ensure we have the full page text if needed
                    pass
            
            # Save the last section
            if current_section:
                full_text = "\n".join(current_text_parts)
                cleaned = self.clean_text(full_text)
                if cleaned.strip() and len(cleaned) > 1000:
                    extracted_sections.append({
                        "section_number": current_section,
                        "title": current_title or f"Section {current_section}",
                        "text": cleaned,
                        "page_start": page_start,
                        "page_end": all_text_pages[-1][0] if all_text_pages else page_start
                    })
        
        # Remove duplicates (keep the longest version of each section)
        seen_sections = {}
        for section in extracted_sections:
            section_num = section["section_number"]
            if section_num not in seen_sections or len(section["text"]) > len(seen_sections[section_num]["text"]):
                seen_sections[section_num] = section
        
        return list(seen_sections.values())
    
    def clean_text(self, text: str) -> str:
        """
        Clean extracted text by removing headers, footers, and excessive whitespace.
        
        Args:
            text: Raw extracted text
            
        Returns:
            Cleaned text
        """
        # Remove page numbers and headers/footers
        text = re.sub(r'^\d+\s*$', '', text, flags=re.MULTILINE)
        text = re.sub(r'Passenger Yacht Code.*?PYC', '', text, flags=re.IGNORECASE)
        text = re.sub(r'Malta.*?Administration', '', text, flags=re.IGNORECASE)
        
        # Normalize whitespace
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = re.sub(r'[ \t]+', ' ', text)
        
        return text.strip()

