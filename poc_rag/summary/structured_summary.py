"""
Structured Summary Module
Generates structured summaries of regulatory sections
"""

from typing import Dict, Any, Optional
from ..retriever.retriever import Retriever
from ..generator.generator import RegulatoryGenerator


class StructuredSummary:
    """
    Generates structured summaries of regulatory sections.
    """
    
    def __init__(self, retriever: Retriever, generator: RegulatoryGenerator):
        """
        Initialize structured summary generator.
        
        Args:
            retriever: Retriever instance
            generator: RegulatoryGenerator instance
        """
        self.retriever = retriever
        self.generator = generator
    
    def summarize_section(self, flag: str, section_id: str) -> Dict[str, Any]:
        """
        Generate a structured summary of a regulatory section.
        
        Args:
            flag: Flag state ("REG", "MALTA", "INTERNAL")
            section_id: Section identifier (e.g., "4.3", "4.30")
            
        Returns:
            Dictionary with:
            - section_id: Section identifier
            - flag: Flag state
            - title: Section title
            - summary: Structured summary text
            - citations: List of citations used
        """
        # Retrieve all chunks for this section and flag
        query = f"section {section_id}"
        results = self.retriever.retrieve(
            query, 
            top_k=20, 
            section_filter=section_id,
            flag_filter=flag
        )
        
        if not results:
            return {
                "section_id": section_id,
                "flag": flag,
                "title": f"Section {section_id}",
                "summary": f"No content found for {flag} Section {section_id}",
                "citations": []
            }
        
        # Format context
        context = self.retriever.format_context(results)
        
        # Get section title from first result
        title = results[0]["metadata"].get("title", f"Section {section_id}")
        
        # Generate structured summary
        summary_prompt = f"""Generate a structured, comprehensive summary of {flag} Section {section_id}: {title}

REGULATORY TEXT:
{context}

Requirements:
1. Create a clear, readable summary for a maritime engineer
2. Use structured headings and subheadings
3. Include all key requirements, procedures, and specifications
4. Always cite section numbers (e.g., Ref: {section_id}(1), Ref: {section_id}(2))
5. Organize by logical topics (e.g., "General Requirements", "Technical Specifications", "Operational Procedures")
6. Highlight important numerical values, thresholds, and compliance criteria
7. Make it easy to scan and understand

Format the summary with markdown headings (##, ###) for structure."""
        
        summary = self.generator.generator.generate(
            summary_prompt,
            system_prompt="""You are a maritime regulatory documentation expert.
Create clear, structured summaries that are easy to read and understand.
Always include citations. Use professional technical language appropriate for engineers."""
        )
        
        # Extract citations
        citations = list(set([r["metadata"]["section_number"] for r in results]))
        
        return {
            "section_id": section_id,
            "flag": flag,
            "title": title,
            "summary": summary,
            "citations": citations,
            "chunks_used": len(results)
        }




