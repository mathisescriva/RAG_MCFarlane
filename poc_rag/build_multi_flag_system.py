"""
Build Multi-Flag RAG System
Processes multiple PDFs (REG, MALTA, INTERNAL) and builds unified vector store
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


def load_malta_pyc(pdf_path: str, target_sections: list = None) -> list:
    """
    Load Malta PYC sections.
    
    Args:
        pdf_path: Path to Malta PYC PDF
        target_sections: List of section numbers to extract (if None, extracts 2 and 5)
        
    Returns:
        List of section dictionaries with flag="MALTA"
    """
    if not Path(pdf_path).exists():
        print(f"⚠️  Malta PYC PDF not found: {pdf_path}")
        print("   Skipping Malta PYC ingestion.")
        return []
    
    # Use Malta PYC specific loader
    from poc_rag.loader.malta_pyc_loader import MaltaPYCLoader
    
    loader = MaltaPYCLoader(pdf_path)
    
    # Extract sections 2 and 5 (default)
    sections = loader.extract_sections()
    
    # Add flag to each section
    for section in sections:
        section["flag"] = "MALTA"
    
    return sections


def load_internal_procedures(pdf_path: str) -> list:
    """
    Load internal procedures PDF.
    
    Args:
        pdf_path: Path to internal procedures PDF
        
    Returns:
        List of section dictionaries with flag="INTERNAL"
    """
    if not Path(pdf_path).exists():
        print(f"⚠️  Internal procedures PDF not found: {pdf_path}")
        print("   Skipping internal procedures ingestion.")
        return []
    
    # For internal procedures, we'll extract all content
    # In production, you might want more sophisticated extraction
    loader = PDFLoader(pdf_path)
    
    # Extract all sections (no specific targets for internal procedures)
    # This is simplified - in production, you'd have a custom loader
    sections = loader.extract_sections()
    
    # Add flag to each section
    for section in sections:
        section["flag"] = "INTERNAL"
        # If no section number, assign a generic one
        if not section.get("section_number"):
            section["section_number"] = "INTERNAL"
    
    return sections


def build_multi_flag_rag_system(
    reg_pdf_path: str,
    malta_pdf_path: str = None,
    internal_pdf_path: str = None,
    output_dir: str = "data/vectorstore",
    embedder_type: str = "sentence_transformer"
):
    """
    Build RAG system with multiple flags (REG, MALTA, INTERNAL).
    
    Args:
        reg_pdf_path: Path to REG Yacht Code Part B PDF
        malta_pdf_path: Optional path to Malta PYC PDF
        internal_pdf_path: Optional path to internal procedures PDF
        output_dir: Directory to save vector store
        embedder_type: "sentence_transformer" or "openai"
    """
    print("=" * 70)
    print("Building Multi-Flag RAG System")
    print("=" * 70)
    
    all_sections = []
    all_chunks = []
    
    # Step 1: Load REG sections
    print("\n[1/5] Loading REG Yacht Code Part B sections...")
    reg_loader = PDFLoader(reg_pdf_path)
    reg_sections = reg_loader.extract_sections()
    for section in reg_sections:
        section["flag"] = "REG"
    all_sections.extend(reg_sections)
    print(f"   ✓ Extracted {len(reg_sections)} REG sections")
    
    # Step 2: Load Malta PYC sections (if provided)
    if malta_pdf_path:
        print("\n[2/5] Loading Malta PYC sections...")
        malta_sections = load_malta_pyc(malta_pdf_path)
        all_sections.extend(malta_sections)
        print(f"   ✓ Extracted {len(malta_sections)} MALTA sections")
    else:
        print("\n[2/5] Skipping Malta PYC (path not provided)")
    
    # Step 3: Load Internal Procedures (if provided)
    if internal_pdf_path:
        print("\n[3/5] Loading Internal Procedures...")
        internal_sections = load_internal_procedures(internal_pdf_path)
        all_sections.extend(internal_sections)
        print(f"   ✓ Extracted {len(internal_sections)} INTERNAL sections")
    else:
        print("\n[3/5] Skipping Internal Procedures (path not provided)")
    
    # Step 4: Chunk all sections
    print("\n[4/5] Chunking all sections...")
    chunker = TextChunker(chunk_size=600, overlap=100)
    all_chunks = chunker.chunk_all_sections(all_sections)
    print(f"   ✓ Created {len(all_chunks)} chunks total")
    
    # Count by flag
    flag_counts = {}
    for chunk in all_chunks:
        flag = chunk.flag
        flag_counts[flag] = flag_counts.get(flag, 0) + 1
    for flag, count in flag_counts.items():
        print(f"     - {flag}: {count} chunks")
    
    # Step 5: Generate embeddings and build vector store
    print("\n[5/5] Generating embeddings and building vector store...")
    if embedder_type == "sentence_transformer":
        embedder = SentenceTransformerEmbedder()
        dimension = 384
    elif embedder_type == "openai":
        from poc_rag.embedder.embedder import OpenAIEmbedder
        embedder = OpenAIEmbedder()
        dimension = 1536
    else:
        raise ValueError(f"Unknown embedder_type: {embedder_type}")
    
    chunk_texts = [chunk.text for chunk in all_chunks]
    print(f"   ✓ Embedding {len(chunk_texts)} chunks...")
    embeddings = embedder.embed_batch(chunk_texts)
    print(f"   ✓ Generated {len(embeddings)} embeddings (dim={dimension})")
    
    # Build vector store
    vector_store = FAISSStore(dimension=dimension)
    chunk_dicts = [chunk.to_dict() for chunk in all_chunks]
    vector_store.add_chunks(chunk_dicts, embeddings)
    print(f"   ✓ Added {len(all_chunks)} chunks to vector store")
    
    # Save vector store
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    vector_store.save(str(output_path))
    print(f"   ✓ Saved vector store to {output_dir}")
    
    # Export chunks to JSON
    chunks_export = {
        "total_chunks": len(all_chunks),
        "flags": flag_counts,
        "chunks": chunk_dicts
    }
    export_path = output_path / "chunks_export.json"
    with open(export_path, "w") as f:
        json.dump(chunks_export, f, indent=2)
    print(f"   ✓ Exported chunks to {export_path}")
    
    print("\n" + "=" * 70)
    print("Multi-Flag RAG System Build Complete!")
    print("=" * 70)
    print(f"\nVector store location: {output_dir}")
    print(f"Total chunks: {len(all_chunks)}")
    print(f"Flags: {', '.join(flag_counts.keys())}")
    print(f"Embedding dimension: {dimension}")
    
    return vector_store, embedder, all_chunks


if __name__ == "__main__":
    import sys
    
    reg_pdf = sys.argv[1] if len(sys.argv) > 1 else "../reg-yc-july-2024-edition-part-b.pdf"
    malta_pdf = sys.argv[2] if len(sys.argv) > 2 else None
    internal_pdf = sys.argv[3] if len(sys.argv) > 3 else None
    
    # Check for environment variables or default paths
    if not malta_pdf:
        malta_pdf = os.getenv("MALTA_PYC_PATH", "/mnt/data/malta-pyc.pdf")
    if not internal_pdf:
        internal_pdf = os.getenv("INTERNAL_PROCEDURES_PATH", "/mnt/data/internal_procedures.pdf")
    
    build_multi_flag_rag_system(reg_pdf, malta_pdf, internal_pdf)

