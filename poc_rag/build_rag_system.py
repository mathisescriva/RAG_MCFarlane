"""
Build RAG System Script
Processes PDF and builds vector store
"""

import json
import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from poc_rag.loader.pdf_loader import PDFLoader
from poc_rag.chunker.text_chunker import TextChunker
from poc_rag.embedder.embedder import SentenceTransformerEmbedder
from poc_rag.vectorstore.faiss_store import FAISSStore


def build_rag_system(pdf_path: str, output_dir: str = "data/vectorstore", 
                    embedder_type: str = "sentence_transformer"):
    """
    Build the complete RAG system from PDF.
    
    Args:
        pdf_path: Path to REG Yacht Code Part B PDF
        output_dir: Directory to save vector store
        embedder_type: "sentence_transformer" or "openai"
    """
    print("=" * 60)
    print("Building RAG System for REG Yacht Code Part B")
    print("=" * 60)
    
    # Step 1: Load PDF sections
    print("\n[1/4] Loading PDF sections...")
    loader = PDFLoader(pdf_path)
    sections = loader.extract_sections()
    print(f"   ✓ Extracted {len(sections)} sections")
    for section in sections:
        print(f"     - Section {section['section_number']}: {section['title']}")
    
    # Step 2: Chunk sections
    print("\n[2/4] Chunking sections...")
    chunker = TextChunker(chunk_size=600, overlap=100)
    chunks = chunker.chunk_all_sections(sections)
    print(f"   ✓ Created {len(chunks)} chunks")
    
    # Step 3: Generate embeddings
    print("\n[3/4] Generating embeddings...")
    if embedder_type == "sentence_transformer":
        embedder = SentenceTransformerEmbedder()
        dimension = 384
    elif embedder_type == "openai":
        from poc_rag.embedder.embedder import OpenAIEmbedder
        embedder = OpenAIEmbedder()
        dimension = 1536
    else:
        raise ValueError(f"Unknown embedder_type: {embedder_type}")
    
    chunk_texts = [chunk.text for chunk in chunks]
    print(f"   ✓ Embedding {len(chunk_texts)} chunks...")
    embeddings = embedder.embed_batch(chunk_texts)
    print(f"   ✓ Generated {len(embeddings)} embeddings (dim={dimension})")
    
    # Step 4: Build vector store
    print("\n[4/4] Building vector store...")
    vector_store = FAISSStore(dimension=dimension)
    chunk_dicts = [chunk.to_dict() for chunk in chunks]
    vector_store.add_chunks(chunk_dicts, embeddings)
    print(f"   ✓ Added {len(chunks)} chunks to vector store")
    
    # Save vector store
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    vector_store.save(str(output_path))
    print(f"   ✓ Saved vector store to {output_dir}")
    
    # Export chunks to JSON for inspection
    chunks_export = {
        "total_chunks": len(chunks),
        "chunks": chunk_dicts
    }
    export_path = output_path / "chunks_export.json"
    with open(export_path, "w") as f:
        json.dump(chunks_export, f, indent=2)
    print(f"   ✓ Exported chunks to {export_path}")
    
    print("\n" + "=" * 60)
    print("RAG System Build Complete!")
    print("=" * 60)
    print(f"\nVector store location: {output_dir}")
    print(f"Total chunks: {len(chunks)}")
    print(f"Embedding dimension: {dimension}")
    
    return vector_store, embedder, chunks


if __name__ == "__main__":
    # Get PDF path relative to project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    pdf_path = sys.argv[1] if len(sys.argv) > 1 else str(project_root / "reg-yc-july-2024-edition-part-b.pdf")
    embedder_type = sys.argv[2] if len(sys.argv) > 2 else "sentence_transformer"
    output_dir = sys.argv[3] if len(sys.argv) > 3 else "data/vectorstore"
    
    # Make output_dir relative to project root
    output_dir = str(project_root / output_dir)
    
    build_rag_system(pdf_path, output_dir=output_dir, embedder_type=embedder_type)

