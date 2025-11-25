"""
RAG System Extended Demo POC
Complete demonstration of all 4 client requirements:
1. Generating compliance checklists
2. Comparing requirements across flag states
3. Highlighting gaps between internal procedures and regulations
4. Producing structured summaries
"""

import os
import sys
import json
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
from poc_rag.demo.demo_functions import answer_question, generate_checklist
from poc_rag.comparison.flag_comparison import FlagComparison
from poc_rag.gap_analysis.gap_analyzer import GapAnalyzer
from poc_rag.summary.structured_summary import StructuredSummary


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


def print_comparison_table(comparison_data: list):
    """Print comparison table in readable format."""
    if not comparison_data:
        print("No comparison data available.")
        return
    
    print("\n" + "=" * 100)
    print(f"{'Aspect':<40} | {'REG':<25} | {'MALTA':<25} | {'Difference'}")
    print("=" * 100)
    
    for item in comparison_data:
        aspect = item.get("aspect", "N/A")[:38]
        reg = item.get("REG", "N/A")[:23]
        malta = item.get("MALTA", "N/A")[:23]
        diff = item.get("difference", "N/A")[:50]
        
        print(f"{aspect:<40} | {reg:<25} | {malta:<25} | {diff}")
    
    print("=" * 100 + "\n")


def print_gap_analysis(gap_data: list):
    """Print gap analysis in readable format."""
    if not gap_data:
        print("No gap analysis data available.")
        return
    
    print("\n" + "=" * 100)
    print(f"{'Requirement':<50} | {'Reference':<15} | {'Status':<20} | {'Comment'}")
    print("=" * 100)
    
    for item in gap_data:
        req = item.get("requirement", "N/A")[:48]
        ref = item.get("reference", "N/A")[:13]
        status = item.get("status", "unknown")
        comment = item.get("comment", "N/A")[:40]
        
        # Color code status
        status_symbol = "✅" if status == "covered" else "⚠️" if status == "partially_covered" else "❌"
        
        print(f"{req:<50} | {ref:<15} | {status_symbol} {status:<17} | {comment}")
    
    print("=" * 100 + "\n")


def main():
    """Main extended demo function."""
    print_section("🚢 REG Yacht Code Part B - Extended RAG System Demo", "=")
    print("Maritime Regulatory Assistant - Complete POC")
    print("Demonstrating all 4 client requirements\n")
    
    # Configuration
    project_root = Path(__file__).parent
    vectorstore_dir = project_root / "data/vectorstore"
    use_openai = os.getenv("USE_OPENAI", "false").lower() == "true"
    vessel_profile = "50m yacht GE50 with 20 persons under Red Ensign Group"
    
    # Check if vector store exists
    if not vectorstore_dir.exists():
        print("❌ Vector store not found!")
        print(f"   Please run: python poc_rag/build_multi_flag_system.py")
        print(f"   Or set up the system first.")
        return
    
    print(f"✓ Loading vector store from {vectorstore_dir}...")
    
    # Load vector store
    vector_store = FAISSStore()
    vector_store.load(str(vectorstore_dir))
    print(f"✓ Loaded {len(vector_store.chunks)} chunks")
    
    # Count chunks by flag
    flag_counts = {}
    for metadata in vector_store.metadata:
        flag = metadata.get("flag", "REG")
        flag_counts[flag] = flag_counts.get(flag, 0) + 1
    print(f"✓ Flags available: {', '.join(flag_counts.keys())} ({', '.join([f'{k}: {v}' for k, v in flag_counts.items()])})")
    
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
        generator = RegulatoryGenerator(base_generator)
    else:
        print("⚠️  No OpenAI API key found. Install openai package and set OPENAI_API_KEY")
        print("   For demo purposes, showing retrieval results only.")
        generator = None
    
    # Initialize new modules
    if generator:
        flag_comparison = FlagComparison(retriever, generator)
        gap_analyzer = GapAnalyzer(retriever, generator)
        structured_summary = StructuredSummary(retriever, generator)
    else:
        flag_comparison = None
        gap_analyzer = None
        structured_summary = None
    
    # ============================================================
    # DEMO 1: Compliance Checklists (REG and MALTA)
    # ============================================================
    print_section("✅ DEMO 1: Generating Compliance Checklists", "-")
    
    if generator:
        # REG Checklist
        print("\n[1.1] REG Compliance Checklist for GE50:")
        checklist_reg = generate_checklist(
            retriever, 
            generator,
            yacht_spec=vessel_profile,
            sections=["4.3", "4.4", "4.30"]
        )
        print(f"Yacht Specification: {checklist_reg['yacht_spec']}\n")
        print("REG Compliance Checklist:")
        print(checklist_reg['checklist'])
        print(f"\n📚 Sections covered: {', '.join(checklist_reg['sections_covered'])}")
        
        # MALTA Checklist (if available)
        if "MALTA" in flag_counts:
            print("\n[1.2] MALTA PYC Compliance Checklist for GE50:")
            # Retrieve MALTA chunks for checklist
            malta_results = retriever.retrieve(
                f"stability requirements for {vessel_profile}",
                top_k=10,
                flag_filter="MALTA"
            )
            if malta_results:
                malta_context = retriever.format_context(malta_results)
                malta_checklist = generator.generate_checklist(malta_context, vessel_profile)
                print("MALTA PYC Compliance Checklist:")
                print(malta_checklist)
            else:
                print("⚠️  No MALTA content available for checklist generation.")
        else:
            print("\n[1.2] MALTA PYC not available (no MALTA chunks in vector store)")
    else:
        print("⚠️  Generator not available. Skipping checklist generation.")
    
    # ============================================================
    # DEMO 2: Flag Comparison (REG vs MALTA)
    # ============================================================
    print_section("🔍 DEMO 2: Comparing Requirements Across Flag States", "-")
    
    if flag_comparison and "MALTA" in flag_counts:
        print("\n[2.1] Comparing Intact Stability Requirements:")
        comparison_intact = flag_comparison.compare_requirements(
            topic="intact_stability",
            vessel_profile=vessel_profile
        )
        print_comparison_table(comparison_intact)
        
        print("\n[2.2] Comparing Damage Stability Requirements:")
        comparison_damage = flag_comparison.compare_requirements(
            topic="damage_stability",
            vessel_profile=vessel_profile
        )
        print_comparison_table(comparison_damage)
    else:
        print("⚠️  Flag comparison not available.")
        if not generator:
            print("   (Generator required)")
        if "MALTA" not in flag_counts:
            print("   (MALTA chunks not found in vector store)")
    
    # ============================================================
    # DEMO 3: Gap Analysis (INTERNAL vs REG/MALTA)
    # ============================================================
    print_section("📊 DEMO 3: Gap Analysis - Internal Procedures vs Regulations", "-")
    
    if gap_analyzer:
        if "INTERNAL" in flag_counts:
            print("\n[3.1] Gap Analysis: INTERNAL vs REG:")
            gaps_reg = gap_analyzer.analyze_gaps(vessel_profile, flag="REG")
            print_gap_analysis(gaps_reg)
            
            if "MALTA" in flag_counts:
                print("\n[3.2] Gap Analysis: INTERNAL vs MALTA:")
                gaps_malta = gap_analyzer.analyze_gaps(vessel_profile, flag="MALTA")
                print_gap_analysis(gaps_malta)
        else:
            print("⚠️  Internal procedures not available (no INTERNAL chunks in vector store)")
            print("   To enable gap analysis, add internal procedures PDF to vector store.")
    else:
        print("⚠️  Gap analyzer not available. (Generator required)")
    
    # ============================================================
    # DEMO 4: Structured Summaries
    # ============================================================
    print_section("📝 DEMO 4: Structured Summaries of Complex Texts", "-")
    
    if structured_summary:
        print("\n[4.1] Structured Summary of REG Section 4.30 (Stability in Damaged Condition):")
        summary_reg_430 = structured_summary.summarize_section("REG", "4.30")
        print(f"\nSection: {summary_reg_430['section_id']} - {summary_reg_430['title']}")
        print(f"Flag: {summary_reg_430['flag']}")
        print(f"Chunks used: {summary_reg_430['chunks_used']}")
        print(f"\n{summary_reg_430['summary']}")
        print(f"\n📚 Citations: {', '.join(summary_reg_430['citations'])}")
        
        if "MALTA" in flag_counts:
            print("\n[4.2] Structured Summary of MALTA Stability Section:")
            # Try to find a MALTA stability section
            malta_results = retriever.retrieve("stability", top_k=5, flag_filter="MALTA")
            if malta_results:
                malta_section = malta_results[0]["metadata"]["section_number"]
                summary_malta = structured_summary.summarize_section("MALTA", malta_section)
                print(f"\nSection: {summary_malta['section_id']} - {summary_malta['title']}")
                print(f"\n{summary_malta['summary']}")
    else:
        print("⚠️  Structured summary not available. (Generator required)")
    
    # ============================================================
    # DEMO 5: Additional Technical Questions
    # ============================================================
    print_section("❓ DEMO 5: Additional Technical Questions", "-")
    
    additional_questions = [
        "What stability documentation is required for a 50m yacht carrying 20 persons under Malta PYC?",
        "What operational stability information must be available on the bridge?",
        "Which damage control information is required under REG for yachts <36 pax?"
    ]
    
    for i, question in enumerate(additional_questions, 1):
        print(f"\n[{i}/{len(additional_questions)}] Processing question...")
        
        if generator:
            result = answer_question(question, retriever, generator, top_k=5)
            print_answer(result)
        else:
            # Show retrieval results if no generator
            results = retriever.retrieve(question, top_k=3)
            print(f"Q: {question}\n")
            print("Retrieved chunks:")
            for j, r in enumerate(results, 1):
                flag = r['metadata'].get('flag', 'REG')
                print(f"\n  [{j}] [{flag}] Section {r['metadata']['section_number']} - {r['metadata']['title']}")
                print(f"      Score: {r['score']:.3f}")
                print(f"      Text preview: {r['chunk']['text'][:200]}...")
    
    # ============================================================
    # Summary
    # ============================================================
    print_section("✨ Extended Demo Complete", "=")
    print("\nSystem Capabilities Demonstrated:")
    print("  ✅ 1. Generating compliance checklists (REG & MALTA)")
    print("  ✅ 2. Comparing requirements across flag states (REG vs MALTA)")
    print("  ✅ 3. Highlighting gaps (INTERNAL vs REG/MALTA)")
    print("  ✅ 4. Producing structured summaries")
    print("  ✅ 5. Answering technical questions with citations")
    print("\n" + "=" * 80)
    print("\n📊 System Statistics:")
    print(f"  - Total chunks: {len(vector_store.chunks)}")
    print(f"  - Flags: {', '.join(flag_counts.keys())}")
    for flag, count in flag_counts.items():
        print(f"  - {flag}: {count} chunks")
    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()




