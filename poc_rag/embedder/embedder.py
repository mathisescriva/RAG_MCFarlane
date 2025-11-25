"""
Embedder Module
Abstract interface for generating embeddings from text
"""

from abc import ABC, abstractmethod
from typing import List
import os


class Embedder(ABC):
    """Abstract base class for embedders."""
    
    @abstractmethod
    def embed(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.
        
        Args:
            text: Input text
            
        Returns:
            List of floats representing the embedding vector
        """
        pass
    
    @abstractmethod
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts (batch processing).
        
        Args:
            texts: List of input texts
            
        Returns:
            List of embedding vectors
        """
        pass


class OpenAIEmbedder(Embedder):
    """
    OpenAI text-embedding-ada-002 or text-embedding-3-small embedder.
    """
    
    def __init__(self, model: str = "text-embedding-3-small", api_key: str = None):
        """
        Initialize OpenAI embedder.
        
        Args:
            model: OpenAI embedding model name
            api_key: OpenAI API key (or set OPENAI_API_KEY env var)
        """
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError("openai package required. Install with: pip install openai")
        
        self.model = model
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key required. Set OPENAI_API_KEY env var or pass api_key.")
        
        self.client = OpenAI(api_key=self.api_key)
    
    def embed(self, text: str) -> List[float]:
        """Generate embedding for a single text."""
        response = self.client.embeddings.create(
            model=self.model,
            input=text
        )
        return response.data[0].embedding
    
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts."""
        response = self.client.embeddings.create(
            model=self.model,
            input=texts
        )
        return [item.embedding for item in response.data]


class SentenceTransformerEmbedder(Embedder):
    """
    SentenceTransformer embedder (local, no API needed).
    Uses all-MiniLM-L6-v2 by default (384 dimensions).
    """
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize SentenceTransformer embedder.
        
        Args:
            model_name: SentenceTransformer model name
        """
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError:
            raise ImportError("sentence-transformers required. Install with: pip install sentence-transformers")
        
        self.model = SentenceTransformer(model_name)
        self.model_name = model_name
    
    def embed(self, text: str) -> List[float]:
        """Generate embedding for a single text."""
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding.tolist()
    
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts."""
        embeddings = self.model.encode(texts, convert_to_numpy=True)
        return embeddings.tolist()




