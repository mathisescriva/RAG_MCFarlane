"""
Text Chunker Module
Splits extracted sections into meaningful chunks with metadata
"""

import re
from typing import List, Dict, Any
from dataclasses import dataclass


@dataclass
class Chunk:
    """Represents a text chunk with metadata."""
    chunk_id: str
    section_number: str
    title: str
    text: str
    page: int
    chunk_index: int  # Index within the section
    flag: str = "REG"  # Flag state: REG, MALTA, INTERNAL
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert chunk to dictionary."""
        return {
            "chunk_id": self.chunk_id,
            "section_number": self.section_number,
            "title": self.title,
            "text": self.text,
            "page": self.page,
            "chunk_index": self.chunk_index,
            "flag": self.flag
        }


class TextChunker:
    """
    Splits text into meaningful chunks of approximately 500-800 tokens.
    Preserves section boundaries and avoids mid-article cuts.
    """
    
    def __init__(self, chunk_size: int = 600, overlap: int = 100):
        """
        Initialize chunker.
        
        Args:
            chunk_size: Target chunk size in tokens (approximate)
            overlap: Overlap between chunks in tokens
        """
        self.chunk_size = chunk_size
        self.overlap = overlap
    
    def estimate_tokens(self, text: str) -> int:
        """
        Rough token estimation (1 token ≈ 4 characters for English).
        
        Args:
            text: Input text
            
        Returns:
            Estimated token count
        """
        return len(text) // 4
    
    def split_into_sentences(self, text: str) -> List[str]:
        """
        Split text into sentences while preserving structure.
        
        Args:
            text: Input text
            
        Returns:
            List of sentences
        """
        # Split on sentence boundaries (., !, ?) followed by space and capital
        sentences = re.split(r'([.!?])\s+(?=[A-Z])', text)
        
        # Recombine sentences with their punctuation
        result = []
        for i in range(0, len(sentences) - 1, 2):
            if i + 1 < len(sentences):
                result.append(sentences[i] + sentences[i + 1])
            else:
                result.append(sentences[i])
        
        if len(sentences) % 2 == 1:
            result.append(sentences[-1])
        
        return [s.strip() for s in result if s.strip()]
    
    def chunk_section(self, section: Dict[str, Any]) -> List[Chunk]:
        """
        Chunk a section into multiple chunks with metadata.
        
        Args:
            section: Dictionary with keys:
                - section_number: str
                - title: str
                - text: str
                - page_start: int
                - page_end: int
                - flag: str (optional, default "REG")
                
        Returns:
            List of Chunk objects
        """
        chunks = []
        text = section["text"]
        section_num = section["section_number"]
        title = section["title"]
        page_start = section.get("page_start", 1)
        flag = section.get("flag", "REG")
        
        # Split into sentences
        sentences = self.split_into_sentences(text)
        
        current_chunk = []
        current_tokens = 0
        chunk_index = 0
        
        for sentence in sentences:
            sentence_tokens = self.estimate_tokens(sentence)
            
            # If adding this sentence would exceed chunk size, save current chunk
            if current_tokens + sentence_tokens > self.chunk_size and current_chunk:
                chunk_text = " ".join(current_chunk)
                chunk_id = f"{section_num}_chunk_{chunk_index}"
                
                chunks.append(Chunk(
                    chunk_id=chunk_id,
                    section_number=section_num,
                    title=title,
                    text=chunk_text,
                    page=page_start,  # Approximate page
                    chunk_index=chunk_index,
                    flag=flag
                ))
                
                # Start new chunk with overlap
                if self.overlap > 0:
                    # Keep last few sentences for overlap
                    overlap_tokens = 0
                    overlap_sentences = []
                    for s in reversed(current_chunk):
                        s_tokens = self.estimate_tokens(s)
                        if overlap_tokens + s_tokens <= self.overlap:
                            overlap_sentences.insert(0, s)
                            overlap_tokens += s_tokens
                        else:
                            break
                    current_chunk = overlap_sentences
                    current_tokens = overlap_tokens
                else:
                    current_chunk = []
                    current_tokens = 0
                
                chunk_index += 1
            
            # Add sentence to current chunk
            current_chunk.append(sentence)
            current_tokens += sentence_tokens
        
        # Add remaining chunk
        if current_chunk:
            chunk_text = " ".join(current_chunk)
            chunk_id = f"{section_num}_chunk_{chunk_index}"
            chunks.append(Chunk(
                chunk_id=chunk_id,
                section_number=section_num,
                title=title,
                text=chunk_text,
                page=page_start,
                chunk_index=chunk_index,
                flag=flag
            ))
        
        return chunks
    
    def chunk_all_sections(self, sections: List[Dict[str, Any]]) -> List[Chunk]:
        """
        Chunk all sections into a unified list of chunks.
        
        Args:
            sections: List of section dictionaries
            
        Returns:
            List of all Chunk objects
        """
        all_chunks = []
        for section in sections:
            chunks = self.chunk_section(section)
            all_chunks.extend(chunks)
        
        return all_chunks

