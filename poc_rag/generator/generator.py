"""
Generator Module
LLM wrapper with regulatory system prompt and citation enforcement
"""

from abc import ABC, abstractmethod
from typing import Optional
import os


class Generator(ABC):
    """Abstract base class for LLM generators."""
    
    @abstractmethod
    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        Generate text from prompt.
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            
        Returns:
            Generated text
        """
        pass


class OpenAIGenerator(Generator):
    """
    OpenAI GPT model generator.
    """
    
    def __init__(self, model: str = "gpt-4o-mini", api_key: Optional[str] = None, temperature: float = 0.1):
        """
        Initialize OpenAI generator.
        
        Args:
            model: OpenAI model name (gpt-4o-mini, gpt-4, etc.)
            api_key: OpenAI API key (or set OPENAI_API_KEY env var)
            temperature: Sampling temperature (lower = more deterministic)
        """
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError("openai package required. Install with: pip install openai")
        
        self.model = model
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key required. Set OPENAI_API_KEY env var or pass api_key.")
        
        self.temperature = temperature
        self.client = OpenAI(api_key=self.api_key)
    
    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate text from prompt."""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature
        )
        
        return response.choices[0].message.content


class RegulatoryGenerator:
    """
    Wrapper around Generator with regulatory-specific system prompt.
    Enforces citation requirements and prevents hallucination.
    """
    
    SYSTEM_PROMPT = """You are a maritime regulatory assistant specializing in the REG Yacht Code Part B (July 2024).

Your role is to answer technical compliance questions using ONLY the provided regulatory text extracts.

CRITICAL RULES:
1. Answer ONLY using information from the provided chunks. Never use external knowledge.
2. ALWAYS cite section numbers in your answers (e.g., "Ref: 4.3.1", "According to Section 4.4").
3. If the answer is not present in the provided chunks, explicitly state: "The answer is not found in the provided regulatory text."
4. Be precise and technical. Use exact regulatory language when possible.
5. For yacht specifications (e.g., GE50, 50m, 20 persons), apply the rules from the relevant sections.
6. Structure your answers clearly with bullet points or numbered lists when appropriate.

Answer format:
- Provide a clear, concise answer
- Include specific section references (e.g., Ref: 4.3.2)
- Quote relevant regulatory text when helpful
- If multiple sections apply, cite all relevant sections"""
    
    def __init__(self, generator: Generator):
        """
        Initialize regulatory generator.
        
        Args:
            generator: Base Generator instance (OpenAI, etc.)
        """
        self.generator = generator
    
    def answer_with_context(self, question: str, context: str) -> str:
        """
        Generate answer using question and retrieved context.
        
        Args:
            question: User question
            context: Formatted context from retriever
            
        Returns:
            Generated answer with citations
        """
        prompt = f"""Based on the following regulatory text extracts from REG Yacht Code Part B (July 2024), answer the question.

REGULATORY TEXT EXTRACTS:
{context}

QUESTION: {question}

Provide a detailed answer with specific section citations."""
        
        return self.generator.generate(prompt, system_prompt=self.SYSTEM_PROMPT)
    
    def generate_checklist(self, context: str, yacht_spec: str = "50m yacht GE50 with 20 persons") -> str:
        """
        Generate a structured compliance checklist.
        
        Args:
            context: Formatted context from retriever
            yacht_spec: Yacht specification string
            
        Returns:
            Formatted checklist
        """
        prompt = f"""Based on the following regulatory text extracts from REG Yacht Code Part B (July 2024), generate a structured compliance checklist for: {yacht_spec}

REGULATORY TEXT EXTRACTS:
{context}

Generate a checklist with:
1. Each compliance criterion
2. The relevant section reference (e.g., Ref: 4.3.1)
3. Whether it applies to a passenger yacht with <36 persons
4. Brief description of the requirement

Format as a clear, numbered list."""
        
        return self.generator.generate(prompt, system_prompt=self.SYSTEM_PROMPT)
    
    def compare_regulations(self, reg_context: str, malta_context: str) -> str:
        """
        Compare REG regulations with Malta PYC regulations.
        
        Args:
            reg_context: REG regulatory text extracts
            malta_context: Malta PYC regulatory text extracts
            
        Returns:
            Comparison table/analysis
        """
        prompt = f"""Compare the following two sets of regulatory requirements:

REG YACHT CODE PART B (July 2024):
{reg_context}

MALTA PYC REGULATIONS:
{malta_context}

Generate a comparison table showing:
1. Requirement/criterion
2. REG requirement
3. Malta PYC requirement
4. Key differences (if any)
5. Section references

Format as a clear comparison table."""
        
        return self.generator.generate(prompt, system_prompt=self.SYSTEM_PROMPT)




