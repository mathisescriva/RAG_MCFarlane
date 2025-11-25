"""
Flag Comparison Module
Compares regulatory requirements across different flag states (REG vs MALTA)
"""

from typing import List, Dict, Any, Optional
from ..retriever.retriever import Retriever
from ..generator.generator import RegulatoryGenerator


class FlagComparison:
    """
    Compares regulatory requirements across different flag states.
    """
    
    TOPIC_MAPPINGS = {
        "intact_stability": [
            "intact stability", "inclination", "lightship displacement",
            "centre of gravity", "metacentric height", "GM", "KG"
        ],
        "damage_stability": [
            "damage stability", "damaged condition", "flooding",
            "subdivision", "residual stability", "righting lever"
        ],
        "stability_documentation": [
            "stability information", "stability booklet", "stability data",
            "information to master", "operational stability"
        ],
        "loading_damage_control": [
            "loading procedures", "damage control", "watertight",
            "loading information", "damage control information"
        ]
    }
    
    def __init__(self, retriever: Retriever, generator: RegulatoryGenerator):
        """
        Initialize flag comparison module.
        
        Args:
            retriever: Retriever instance
            generator: RegulatoryGenerator instance
        """
        self.retriever = retriever
        self.generator = generator
    
    def compare_requirements(self, topic: str, vessel_profile: str = "") -> List[Dict[str, Any]]:
        """
        Compare requirements between REG and MALTA for a given topic.
        
        Args:
            topic: One of "intact_stability", "damage_stability", 
                   "stability_documentation", "loading_damage_control"
            vessel_profile: Optional vessel specification (e.g., "50m yacht, 20 persons")
            
        Returns:
            List of comparison dictionaries with:
            - aspect: Aspect being compared
            - REG: REG requirement with citation
            - MALTA: MALTA requirement with citation
            - difference: Key differences
        """
        if topic not in self.TOPIC_MAPPINGS:
            raise ValueError(f"Topic must be one of: {list(self.TOPIC_MAPPINGS.keys())}")
        
        # Build query from topic keywords
        keywords = self.TOPIC_MAPPINGS[topic]
        query = " ".join(keywords)
        if vessel_profile:
            query = f"{query} {vessel_profile}"
        
        # Retrieve chunks for both flags - use more chunks for Malta as it may reference SOLAS
        reg_results = self.retriever.retrieve(query, top_k=10, flag_filter="REG")
        malta_results = self.retriever.retrieve(query, top_k=15, flag_filter="MALTA")
        
        # Also search for SOLAS references in Malta (Malta PYC often references SOLAS)
        if topic in ["intact_stability", "damage_stability"]:
            solas_query = f"SOLAS stability requirements {vessel_profile}"
            malta_solas_results = self.retriever.retrieve(solas_query, top_k=5, flag_filter="MALTA")
            # Merge results, avoiding duplicates
            existing_chunk_ids = {r["chunk"]["chunk_id"] for r in malta_results}
            for r in malta_solas_results:
                if r["chunk"]["chunk_id"] not in existing_chunk_ids:
                    malta_results.append(r)
        
        # Format contexts
        reg_context = self.retriever.format_context(reg_results) if reg_results else "No REG requirements found."
        malta_context = self.retriever.format_context(malta_results) if malta_results else "No MALTA requirements found."
        
        # Generate comparison using LLM
        comparison_prompt = f"""Compare the regulatory requirements for {topic} between REG Yacht Code Part B and Malta Passenger Yacht Code (PYC).

REG YACHT CODE PART B:
{reg_context}

MALTA PYC:
{malta_context}

VESSEL PROFILE: {vessel_profile if vessel_profile else "General passenger yacht"}

IMPORTANT NOTES:
- Malta PYC often references SOLAS requirements rather than providing detailed specifications
- If Malta PYC references SOLAS, state: "References SOLAS [specific regulation] - see Section 5.X"
- If a requirement is not explicitly stated in Malta PYC but references SOLAS, explain this in the difference
- REG has detailed specific requirements, while Malta PYC may delegate to SOLAS or classification rules

Generate a structured comparison table in JSON format. For each aspect, provide:
1. "aspect": The specific requirement aspect (e.g., "Minimum GM requirement", "Stability booklet content")
2. "REG": The REG requirement with exact citation (e.g., "Ref: 4.3(1)")
3. "MALTA": The MALTA requirement with exact citation. If it references SOLAS, state: "References SOLAS [regulation] - Ref: Section 5.X"
4. "difference": Key differences or similarities. If Malta references SOLAS, explain: "REG provides specific requirements; Malta references SOLAS standards"

Return ONLY a JSON array of objects, no additional text. Example format:
[
  {{
    "aspect": "Intact stability compliance",
    "REG": "Must comply with IS Code 2008 Part A. Ref: 4.3(1)",
    "MALTA": "References Intact Stability Code 2008 and SOLAS Ch.II-1 - Ref: Section 5.1.1.1",
    "difference": "REG provides direct requirements; Malta references IS Code and SOLAS standards"
  }}
]"""
        
        response = self.generator.generator.generate(
            comparison_prompt,
            system_prompt="""You are a maritime regulatory expert. Compare regulatory requirements accurately.
Always cite exact section numbers. If information is not available, state "Not found in provided text."
Return ONLY valid JSON, no markdown formatting."""
        )
        
        # Parse JSON response
        import json
        import re
        
        # Extract JSON from response (handle markdown code blocks)
        json_match = re.search(r'\[.*\]', response, re.DOTALL)
        if json_match:
            try:
                comparison_data = json.loads(json_match.group(0))
                return comparison_data
            except json.JSONDecodeError:
                pass
        
        # Fallback: return structured format
        return [{
            "aspect": f"{topic} requirement",
            "REG": reg_context[:200] + "..." if len(reg_context) > 200 else reg_context,
            "MALTA": malta_context[:200] + "..." if len(malta_context) > 200 else malta_context,
            "difference": "Comparison generated - see full response for details"
        }]

