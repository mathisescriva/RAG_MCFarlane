"""
Demo Functions Module
High-impact demo functions for showcasing RAG capabilities
"""

from typing import List, Dict, Any
from ..retriever.retriever import Retriever
from ..generator.generator import RegulatoryGenerator


def answer_question(question: str, retriever: Retriever, 
                   generator: RegulatoryGenerator, top_k: int = 5) -> Dict[str, Any]:
    """
    Answer a regulatory question with citations.
    
    Args:
        question: User question
        retriever: Retriever instance
        generator: RegulatoryGenerator instance
        top_k: Number of chunks to retrieve
        
    Returns:
        Dictionary with:
        - answer: str (generated answer)
        - citations: List[str] (section numbers cited)
        - chunks_used: List[Dict] (retrieved chunks)
    """
    # Retrieve relevant chunks
    results = retriever.retrieve(question, top_k=top_k)
    
    # Format context
    context = retriever.format_context(results)
    
    # Generate answer
    answer = generator.answer_with_context(question, context)
    
    # Extract citations
    citations = []
    for result in results:
        section = result["metadata"]["section_number"]
        if section not in citations:
            citations.append(section)
    
    return {
        "question": question,
        "answer": answer,
        "citations": citations,
        "chunks_used": [r["chunk"] for r in results]
    }


def generate_checklist(retriever: Retriever, generator: RegulatoryGenerator,
                      yacht_spec: str = "50m yacht GE50 with 20 persons",
                      sections: List[str] = None) -> Dict[str, Any]:
    """
    Generate a structured compliance checklist.
    
    Args:
        retriever: Retriever instance
        generator: RegulatoryGenerator instance
        yacht_spec: Yacht specification
        sections: Optional list of section numbers to focus on
        
    Returns:
        Dictionary with checklist and metadata
    """
    # Build query to retrieve stability-related chunks
    query = f"stability requirements for {yacht_spec} intact stability damaged condition"
    
    # Retrieve chunks (more for comprehensive checklist)
    results = retriever.retrieve(query, top_k=10)
    
    # Filter by sections if specified
    if sections:
        results = [r for r in results if r["metadata"]["section_number"] in sections]
    
    # Format context
    context = retriever.format_context(results)
    
    # Generate checklist
    checklist = generator.generate_checklist(context, yacht_spec)
    
    return {
        "yacht_spec": yacht_spec,
        "checklist": checklist,
        "sections_covered": list(set(r["metadata"]["section_number"] for r in results))
    }


def compare_with_malta_stub(retriever: Retriever, generator: RegulatoryGenerator) -> Dict[str, Any]:
    """
    Compare REG regulations with Malta PYC (stub implementation).
    Uses hardcoded Malta PYC sample text for demonstration.
    
    Args:
        retriever: Retriever instance
        generator: RegulatoryGenerator instance
        
    Returns:
        Dictionary with comparison results
    """
    # Retrieve REG chunks
    query = "stability requirements intact stability damaged condition"
    reg_results = retriever.retrieve(query, top_k=8)
    reg_context = retriever.format_context(reg_results)
    
    # Hardcoded Malta PYC stub text (for demo purposes)
    malta_stub = """MALTA PYC STABILITY REQUIREMENTS (Sample):

Section 4.3 - Intact Stability:
- Passenger yachts must demonstrate positive stability up to 30 degrees heel angle.
- Minimum GM (metacentric height) of 0.15m for yachts under 50m.
- Stability calculations must account for all loading conditions.

Section 4.4 - Stability Information:
- Master must receive stability booklet with loading instructions.
- Stability information must be updated after any modifications affecting stability.

Section 4.30 - Damage Stability:
- Yachts must remain stable with one compartment flooded.
- Damage stability calculations required for all passenger yachts.
- Minimum residual stability criteria: positive righting moment up to 20 degrees.

Section 4.22 - Damage Control:
- Damage control plans must be posted in key locations.
- Crew training required for damage control procedures.

Section 4.23 - Loading Procedures:
- Loading procedures must be documented and approved.
- Master must verify compliance before departure.

Section 4.24 - Watertight Integrity:
- Watertight doors must be tested monthly.
- Inspection records must be maintained."""
    
    # Generate comparison
    comparison = generator.compare_regulations(reg_context, malta_stub)
    
    return {
        "comparison": comparison,
        "reg_sections": list(set(r["metadata"]["section_number"] for r in reg_results)),
        "note": "Malta PYC text is a demonstration stub for comparison purposes"
    }




