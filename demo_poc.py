"""
RAG System Demo POC
End-to-end demonstration of maritime regulatory assistant
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Load environment variables from .env file if it exists
env_file = project_root / ".env"
if env_file.exists():
    with open(env_file, "r") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                os.environ[key.strip()] = value.strip()

from poc_rag.vectorstore.faiss_store import FAISSStore
from poc_rag.embedder.embedder import SentenceTransformerEmbedder, OpenAIEmbedder
from poc_rag.retriever.retriever import Retriever
from poc_rag.generator.generator import OpenAIGenerator, RegulatoryGenerator
from poc_rag.demo.demo_functions import answer_question, generate_checklist, compare_with_malta_stub


def print_section(title: str, char: str = "="):
    """Print a formatted section header."""
    print("\n" + char * 80)
    print(f"  {title}")
    print(char * 80 + "\n")


def print_answer(result: dict):
    """Print formatted Q&A result."""
    print(f"Q: {result['question']}\n")
    print("A:", result['answer'])
    print(f"\n📚 Citations: {', '.join([f'Section {s}' for s in result['citations']])}")
    print(f"📄 Chunks used: {len(result['chunks_used'])}\n")


def main():
    """Main demo function."""
    print_section("🚢 REG Yacht Code Part B - RAG System Demo", "=")
    print("Maritime Regulatory Assistant POC")
    print("Demonstrating retrieval-augmented generation for compliance questions\n")
    
    # Configuration
    project_root = Path(__file__).parent
    vectorstore_dir = project_root / "data/vectorstore"
    use_openai = os.getenv("USE_OPENAI", "false").lower() == "true"
    
    # Check if vector store exists
    if not vectorstore_dir.exists():
        print("❌ Vector store not found!")
        print(f"   Please run: python poc_rag/build_rag_system.py")
        print(f"   Or set up the system first.")
        return
    
    print(f"✓ Loading vector store from {vectorstore_dir}...")
    
    # Load vector store
    vector_store = FAISSStore()
    vector_store.load(str(vectorstore_dir))
    print(f"✓ Loaded {len(vector_store.chunks)} chunks")
    
    # Initialize embedder
    if use_openai and os.getenv("OPENAI_API_KEY"):
        print("✓ Using OpenAI embeddings...")
        embedder = OpenAIEmbedder()
    else:
        print("✓ Using SentenceTransformer embeddings (local)...")
        embedder = SentenceTransformerEmbedder()
    
    # Initialize retriever
    retriever = Retriever(vector_store, embedder)
    
    # Initialize generator
    if os.getenv("OPENAI_API_KEY"):
        print("✓ Using OpenAI GPT for generation...")
        base_generator = OpenAIGenerator(model="gpt-4o-mini", temperature=0.1)
    else:
        print("⚠️  No OpenAI API key found. Install openai package and set OPENAI_API_KEY")
        print("   For demo purposes, showing retrieval results only.")
        base_generator = None
    
    if base_generator:
        generator = RegulatoryGenerator(base_generator)
    else:
        generator = None
    
    # ============================================================
    # DEMO 1: Answer Questions
    # ============================================================
    print_section("📋 DEMO 1: Answering Regulatory Questions", "-")
    
    questions = [
        "What intact stability information must be determined for ships under REG Part B?",
        "What stability information must be supplied to the Master?",
        "What are the requirements for stability in damaged condition?"
    ]
    
    for i, question in enumerate(questions, 1):
        print(f"\n[{i}/{len(questions)}] Processing question...")
        
        if generator:
            result = answer_question(question, retriever, generator, top_k=5)
            print_answer(result)
        else:
            # Show retrieval results if no generator
            results = retriever.retrieve(question, top_k=3)
            print(f"Q: {question}\n")
            print("Retrieved chunks:")
            for j, r in enumerate(results, 1):
                print(f"\n  [{j}] Section {r['metadata']['section_number']} - {r['metadata']['title']}")
                print(f"      Score: {r['score']:.3f}")
                print(f"      Text preview: {r['chunk']['text'][:200]}...")
    
    # ============================================================
    # DEMO 2: Generate Checklist
    # ============================================================
    print_section("✅ DEMO 2: Generating Compliance Checklist", "-")
    
    if generator:
        checklist_result = generate_checklist(
            retriever, 
            generator,
            yacht_spec="50m yacht GE50 with 20 persons under Red Ensign Group",
            sections=["4.3", "4.4", "4.30"]
        )
        
        print(f"Yacht Specification: {checklist_result['yacht_spec']}\n")
        print("Compliance Checklist:")
        print(checklist_result['checklist'])
        print(f"\n📚 Sections covered: {', '.join(checklist_result['sections_covered'])}")
    else:
        print("⚠️  Generator not available. Skipping checklist generation.")
        print("   (Set OPENAI_API_KEY to enable full functionality)")
    
    # ============================================================
    # DEMO 3: Compare REG vs Malta
    # ============================================================
    print_section("🔍 DEMO 3: REG vs Malta PYC Comparison", "-")
    
    if generator:
        comparison_result = compare_with_malta_stub(retriever, generator)
        
        print("Comparison Table:")
        print(comparison_result['comparison'])
        print(f"\n📚 REG sections analyzed: {', '.join(comparison_result['reg_sections'])}")
        print(f"ℹ️  {comparison_result['note']}")
    else:
        print("⚠️  Generator not available. Skipping comparison.")
        print("   (Set OPENAI_API_KEY to enable full functionality)")
    
    # ============================================================
    # Summary
    # ============================================================
    print_section("✨ Demo Complete", "=")
    print("\nSystem Capabilities Demonstrated:")
    print("  ✓ PDF extraction and chunking")
    print("  ✓ Semantic search with cosine similarity")
    print("  ✓ Regulatory Q&A with citations")
    print("  ✓ Compliance checklist generation")
    print("  ✓ Cross-flag regulation comparison")
    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()

