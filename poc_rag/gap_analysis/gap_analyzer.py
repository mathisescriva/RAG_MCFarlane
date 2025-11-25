"""
Gap Analysis Module
Analyzes gaps between internal procedures and regulatory requirements
"""

from typing import List, Dict, Any, Optional
from ..retriever.retriever import Retriever
from ..generator.generator import RegulatoryGenerator


class GapAnalyzer:
    """
    Analyzes gaps between internal procedures and regulatory requirements.
    """
    
    def __init__(self, retriever: Retriever, generator: RegulatoryGenerator):
        """
        Initialize gap analyzer.
        
        Args:
            retriever: Retriever instance
            generator: RegulatoryGenerator instance
        """
        self.retriever = retriever
        self.generator = generator
    
    def analyze_gaps(self, vessel_profile: str, flag: str = "REG") -> List[Dict[str, Any]]:
        """
        Analyze gaps between internal procedures and regulatory requirements.
        
        Args:
            vessel_profile: Vessel specification (e.g., "50m yacht, 20 persons")
            flag: Regulatory flag to compare against ("REG" or "MALTA")
            
        Returns:
            List of gap analysis dictionaries with:
            - requirement: Regulatory requirement text
            - reference: Regulatory reference (e.g., "REG 4.3(1)")
            - status: "covered", "partially_covered", or "missing"
            - internal_evidence: Evidence from internal procedures
            - comment: Analysis comment
        """
        # Retrieve regulatory requirements
        reg_query = f"stability requirements {vessel_profile}"
        reg_results = self.retriever.retrieve(reg_query, top_k=10, flag_filter=flag)
        reg_context = self.retriever.format_context(reg_results)
        
        # Retrieve internal procedures
        internal_results = self.retriever.retrieve(reg_query, top_k=10, flag_filter="INTERNAL")
        internal_context = self.retriever.format_context(internal_results) if internal_results else "No internal procedures found."
        
        # Generate gap analysis
        gap_analysis_prompt = f"""Analyze the gaps between {flag} regulatory requirements and internal procedures.

{flag.upper()} REGULATORY REQUIREMENTS:
{reg_context}

INTERNAL PROCEDURES:
{internal_context}

VESSEL PROFILE: {vessel_profile}

For each regulatory requirement found, determine:
1. Is it fully covered in internal procedures? (status: "covered")
2. Is it partially covered? (status: "partially_covered")
3. Is it missing? (status: "missing")

Return a JSON array with this structure:
[
  {{
    "requirement": "Exact regulatory requirement text",
    "reference": "{flag} 4.3(1)",
    "status": "covered|partially_covered|missing",
    "internal_evidence": "Evidence from internal procedures (or 'Not found')",
    "comment": "Brief analysis of the gap"
  }}
]

Return ONLY valid JSON array, no additional text."""
        
        response = self.generator.generator.generate(
            gap_analysis_prompt,
            system_prompt="""You are a maritime compliance expert. Analyze gaps accurately.
Be strict: only mark as "covered" if fully addressed. Use "partially_covered" if partially addressed.
Always cite exact references. Return ONLY valid JSON."""
        )
        
        # Parse JSON response
        import json
        import re
        
        json_match = re.search(r'\[.*\]', response, re.DOTALL)
        if json_match:
            try:
                gap_data = json.loads(json_match.group(0))
                return gap_data
            except json.JSONDecodeError:
                pass
        
        # Fallback: return basic structure
        return [{
            "requirement": "Regulatory requirement",
            "reference": f"{flag} Section",
            "status": "unknown",
            "internal_evidence": internal_context[:200] if internal_context else "Not found",
            "comment": "Gap analysis generated - see full response for details"
        }]




