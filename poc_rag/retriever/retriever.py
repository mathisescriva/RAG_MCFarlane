"""
Retriever Module
Semantic search with cosine similarity and section filtering
"""

from typing import List, Dict, Any, Optional
from ..embedder.embedder import Embedder
from ..vectorstore.faiss_store import FAISSStore


class Retriever:
    """
    Retrieves relevant chunks from vector store based on query.
    Uses cosine similarity and optional section filtering.
    """
    
    def __init__(self, vector_store: FAISSStore, embedder: Embedder):
        """
        Initialize retriever.
        
        Args:
            vector_store: FAISSStore instance
            embedder: Embedder instance for query embeddings
        """
        self.vector_store = vector_store
        self.embedder = embedder
    
    def retrieve(self, query: str, top_k: int = 5, 
                 section_filter: Optional[str] = None,
                 flag_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Retrieve relevant chunks for a query.
        
        Args:
            query: Search query text
            top_k: Number of results to return
            section_filter: Optional section number to filter by (e.g., "4.3")
            flag_filter: Optional flag to filter by (e.g., "REG", "MALTA", "INTERNAL")
            
        Returns:
            List of dictionaries with chunk data, scores, and metadata
        """
        # Generate query embedding
        query_embedding = self.embedder.embed(query)
        
        # Search vector store
        results = self.vector_store.search(
            query_embedding=query_embedding,
            top_k=top_k,
            section_filter=section_filter,
            flag_filter=flag_filter
        )
        
        return results
    
    def get_chunk_texts(self, results: List[Dict[str, Any]]) -> List[str]:
        """
        Extract just the text from retrieval results.
        
        Args:
            results: Results from retrieve()
            
        Returns:
            List of chunk texts
        """
        return [r["chunk"]["text"] for r in results]
    
    def format_context(self, results: List[Dict[str, Any]]) -> str:
        """
        Format retrieval results as context for LLM.
        
        Args:
            results: Results from retrieve()
            
        Returns:
            Formatted context string with citations
        """
        context_parts = []
        for i, result in enumerate(results, 1):
            chunk = result["chunk"]
            metadata = result["metadata"]
            section = metadata["section_number"]
            title = metadata["title"]
            
            context_parts.append(
                f"[{i}] Section {section} - {title}\n"
                f"Ref: {section}\n"
                f"{chunk['text']}\n"
            )
        
        return "\n---\n".join(context_parts)

