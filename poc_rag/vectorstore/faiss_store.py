"""
FAISS Vector Store Module
Stores and retrieves document chunks using FAISS
"""

import json
import pickle
from pathlib import Path
from typing import List, Dict, Any, Optional
import numpy as np

try:
    import faiss
except ImportError:
    raise ImportError("faiss-cpu required. Install with: pip install faiss-cpu")


class FAISSStore:
    """
    FAISS-based vector store for document chunks.
    Stores embeddings and metadata for semantic search.
    """
    
    def __init__(self, dimension: int = 384):
        """
        Initialize FAISS store.
        
        Args:
            dimension: Dimension of embedding vectors (384 for all-MiniLM-L6-v2, 1536 for OpenAI)
        """
        self.dimension = dimension
        self.index = faiss.IndexFlatL2(dimension)  # L2 distance (can convert to cosine)
        self.metadata: List[Dict[str, Any]] = []
        self.chunks: List[Dict[str, Any]] = []
    
    def add_chunks(self, chunks: List[Dict[str, Any]], embeddings: List[List[float]]):
        """
        Add chunks with their embeddings to the store.
        
        Args:
            chunks: List of chunk dictionaries (from Chunk.to_dict())
            embeddings: List of embedding vectors
        """
        if len(chunks) != len(embeddings):
            raise ValueError("Number of chunks must match number of embeddings")
        
        # Normalize embeddings for cosine similarity
        embeddings_array = np.array(embeddings, dtype=np.float32)
        faiss.normalize_L2(embeddings_array)  # Normalize for cosine similarity
        
        # Add to FAISS index
        self.index.add(embeddings_array)
        
        # Store metadata and chunks
        for chunk, embedding in zip(chunks, embeddings):
            self.metadata.append({
                "chunk_id": chunk["chunk_id"],
                "section_number": chunk["section_number"],
                "title": chunk["title"],
                "page": chunk["page"],
                "chunk_index": chunk["chunk_index"],
                "flag": chunk.get("flag", "REG")  # Default to REG for backward compatibility
            })
            self.chunks.append(chunk)
    
    def search(self, query_embedding: List[float], top_k: int = 5, 
               section_filter: Optional[str] = None,
               flag_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Search for similar chunks using cosine similarity.
        
        Args:
            query_embedding: Query embedding vector
            top_k: Number of results to return
            section_filter: Optional section number to filter by (e.g., "4.3")
            flag_filter: Optional flag to filter by (e.g., "REG", "MALTA", "INTERNAL")
            
        Returns:
            List of dictionaries with:
            - chunk: Dict with chunk data
            - score: Similarity score (higher is better)
            - metadata: Chunk metadata
        """
        # Normalize query embedding
        query_array = np.array([query_embedding], dtype=np.float32)
        faiss.normalize_L2(query_array)
        
        # Search
        k = min(top_k * 3, len(self.chunks)) if section_filter else top_k  # Get more if filtering
        distances, indices = self.index.search(query_array, k)
        
        results = []
        for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
            if idx >= len(self.chunks):
                continue
            
            metadata = self.metadata[idx]
            
            # Apply section filter if specified
            if section_filter and metadata["section_number"] != section_filter:
                continue
            
            # Apply flag filter if specified
            if flag_filter and metadata.get("flag", "REG") != flag_filter:
                continue
            
            # Convert L2 distance to cosine similarity (1 - distance/2 for normalized vectors)
            similarity = 1 - (distance / 2)
            
            results.append({
                "chunk": self.chunks[idx],
                "score": float(similarity),
                "metadata": metadata
            })
            
            if len(results) >= top_k:
                break
        
        return results
    
    def save(self, directory: str):
        """
        Save the vector store to disk.
        
        Args:
            directory: Directory path to save to
        """
        dir_path = Path(directory)
        dir_path.mkdir(parents=True, exist_ok=True)
        
        # Save FAISS index
        faiss.write_index(self.index, str(dir_path / "index.faiss"))
        
        # Save metadata and chunks
        with open(dir_path / "metadata.json", "w") as f:
            json.dump(self.metadata, f, indent=2)
        
        with open(dir_path / "chunks.json", "w") as f:
            json.dump(self.chunks, f, indent=2)
    
    def load(self, directory: str):
        """
        Load the vector store from disk.
        
        Args:
            directory: Directory path to load from
        """
        dir_path = Path(directory)
        
        # Load FAISS index
        self.index = faiss.read_index(str(dir_path / "index.faiss"))
        
        # Load metadata and chunks
        with open(dir_path / "metadata.json", "r") as f:
            self.metadata = json.load(f)
        
        with open(dir_path / "chunks.json", "r") as f:
            self.chunks = json.load(f)
        
        # Update dimension from index
        self.dimension = self.index.d

