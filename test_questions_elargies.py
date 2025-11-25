"""
Test des 10 Questions Élargies
Validation approfondie du système RAG
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Load environment variables
env_file = project_root / ".env"
if env_file.exists():
    with open(env_file, "r") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                os.environ[key.strip()] = value.strip()

from poc_rag.vectorstore.faiss_store import FAISSStore
from poc_rag.embedder.embedder import SentenceTransformerEmbedder
from poc_rag.retriever.retriever import Retriever
from poc_rag.generator.generator import OpenAIGenerator, RegulatoryGenerator
from poc_rag.demo.demo_functions import answer_question, generate_checklist
from poc_rag.comparison.flag_comparison import FlagComparison
from poc_rag.summary.structured_summary import StructuredSummary


def print_question_header(num, question):
    """Print formatted question header."""
    print("\n" + "=" * 100)
    print(f"QUESTION {num}: {question}")
    print("=" * 100 + "\n")


def analyze_retrieval(question, retriever, flag_filter=None):
    """Analyze retrieval quality for a question."""
    results = retriever.retrieve(question, top_k=5, flag_filter=flag_filter)
    
    print("📊 Analyse de la Recherche:")
    print(f"   Nombre de résultats: {len(results)}")
    
    if results:
        flags_found = set()
        sections_found = set()
        avg_score = sum(r['score'] for r in results) / len(results)
        
        for i, r in enumerate(results, 1):
            flag = r['metadata'].get('flag', 'REG')
            section = r['metadata'].get('section_number', 'N/A')
            flags_found.add(flag)
            sections_found.add(section)
            print(f"   [{i}] [{flag}] Section {section} - Score: {r['score']:.3f}")
        
        print(f"   Score moyen: {avg_score:.3f}")
        print(f"   Flags trouvés: {', '.join(flags_found)}")
        print(f"   Sections trouvées: {', '.join(sorted(sections_found))}")
        
        return {
            'count': len(results),
            'avg_score': avg_score,
            'flags': flags_found,
            'sections': sections_found,
            'quality': 'excellent' if avg_score > 0.5 else 'good' if avg_score > 0.4 else 'fair'
        }
    else:
        print("   ⚠️  Aucun résultat trouvé")
        return {'count': 0, 'quality': 'poor'}


def main():
    """Test des 10 questions élargies."""
    print("=" * 100)
    print("  TEST DES 10 QUESTIONS ÉLARGIES - VALIDATION APPROFONDIE")
    print("=" * 100)
    
    # Load system
    vectorstore_dir = project_root / "data/vectorstore"
    if not vectorstore_dir.exists():
        print("❌ Vector store not found!")
        return
    
    print("\n✓ Chargement du système...")
    vector_store = FAISSStore()
    vector_store.load(str(vectorstore_dir))
    embedder = SentenceTransformerEmbedder()
    retriever = Retriever(vector_store, embedder)
    
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  OPENAI_API_KEY non défini - tests de recherche uniquement")
        generator = None
        flag_comparison = None
        structured_summary = None
    else:
        base_generator = OpenAIGenerator(model="gpt-4o-mini", temperature=0.1)
        generator = RegulatoryGenerator(base_generator)
        flag_comparison = FlagComparison(retriever, generator)
        structured_summary = StructuredSummary(retriever, generator)
    
    results_summary = []
    
    # ============================================================
    # QUESTION 1: Compliance Checklist
    # ============================================================
    print_question_header(1, "Compliance Checklist REG Part B")
    question1 = "Generate a full REG Part B stability compliance checklist for a 50m yacht carrying 20 persons."
    
    retrieval_analysis = analyze_retrieval(question1, retriever, flag_filter="REG")
    
    if generator:
        checklist = generate_checklist(
            retriever, generator,
            yacht_spec="50m yacht carrying 20 persons",
            sections=["4.3", "4.4", "4.30", "4.22"]
        )
        print("\n📋 Checklist générée:")
        print(checklist['checklist'])
        print(f"\n✅ Sections couvertes: {', '.join(checklist['sections_covered'])}")
        
        results_summary.append({
            'question': 1,
            'type': 'checklist',
            'retrieval_quality': retrieval_analysis['quality'],
            'sections_found': list(retrieval_analysis.get('sections', set())),
            'status': 'success'
        })
    else:
        print("⚠️  Génération non disponible (pas de clé API)")
        results_summary.append({'question': 1, 'status': 'retrieval_only'})
    
    # ============================================================
    # QUESTION 2: Re-inclination Conditions
    # ============================================================
    print_question_header(2, "Re-inclination Conditions")
    question2 = "According to REG Part B sections 4.3 and 4.4, under which conditions must a yacht be re-inclined, and what stability information must be amended?"
    
    retrieval_analysis = analyze_retrieval(question2, retriever, flag_filter="REG")
    
    if generator:
        result = answer_question(question2, retriever, generator, top_k=8)
        print("\n💬 Réponse générée:")
        print(result['answer'])
        print(f"\n📚 Citations: {', '.join([f'Section {s}' for s in result['citations']])}")
        
        # Vérifier si la réponse contient les bonnes sections
        has_43 = '4.3' in result['citations']
        has_44 = '4.4' in result['citations']
        has_reinclination = 're-inclin' in result['answer'].lower()
        
        print(f"\n✅ Vérification:")
        print(f"   Section 4.3 citée: {has_43}")
        print(f"   Section 4.4 citée: {has_44}")
        print(f"   Mention re-inclination: {has_reinclination}")
        
        results_summary.append({
            'question': 2,
            'type': 'qa',
            'retrieval_quality': retrieval_analysis['quality'],
            'sections_found': list(retrieval_analysis.get('sections', set())),
            'has_43': has_43,
            'has_44': has_44,
            'has_reinclination': has_reinclination,
            'status': 'success' if (has_43 and has_44 and has_reinclination) else 'partial'
        })
    else:
        results_summary.append({'question': 2, 'status': 'retrieval_only'})
    
    # ============================================================
    # QUESTION 3: Summary Intact Stability
    # ============================================================
    print_question_header(3, "Summary Intact Stability Requirements")
    question3 = "Summarize all intact stability requirements for yachts under REG Part B, with explicit references to subsections."
    
    retrieval_analysis = analyze_retrieval(question3, retriever, flag_filter="REG")
    
    if generator:
        result = answer_question(question3, retriever, generator, top_k=10)
        print("\n💬 Réponse générée:")
        print(result['answer'][:1000] + "..." if len(result['answer']) > 1000 else result['answer'])
        print(f"\n📚 Citations: {', '.join([f'Section {s}' for s in result['citations']])}")
        print(f"📄 Longueur réponse: {len(result['answer'])} caractères")
        
        # Compter les références de sous-sections
        import re
        subsection_refs = re.findall(r'4\.\d+\(\d+\)', result['answer'])
        print(f"✅ Références de sous-sections trouvées: {len(subsection_refs)}")
        if subsection_refs:
            print(f"   Exemples: {', '.join(subsection_refs[:5])}")
        
        results_summary.append({
            'question': 3,
            'type': 'summary',
            'retrieval_quality': retrieval_analysis['quality'],
            'subsection_refs': len(subsection_refs),
            'status': 'success'
        })
    else:
        results_summary.append({'question': 3, 'status': 'retrieval_only'})
    
    # ============================================================
    # QUESTION 4: Complete Damage Stability
    # ============================================================
    print_question_header(4, "Complete Damage Stability Requirements")
    question4 = "What are the complete damage stability requirements under REG Section 4.30, including righting lever curve, heeling moments, and final conditions?"
    
    retrieval_analysis = analyze_retrieval(question4, retriever, flag_filter="REG")
    
    if generator:
        result = answer_question(question4, retriever, generator, top_k=10)
        print("\n💬 Réponse générée (extrait):")
        print(result['answer'][:1500] + "..." if len(result['answer']) > 1500 else result['answer'])
        print(f"\n📚 Citations: {', '.join([f'Section {s}' for s in result['citations']])}")
        print(f"📄 Longueur réponse: {len(result['answer'])} caractères")
        
        # Vérifier les éléments clés
        has_righting = 'righting lever' in result['answer'].lower()
        has_heeling = 'heeling moment' in result['answer'].lower()
        has_final = 'final condition' in result['answer'].lower()
        has_430 = '4.30' in result['citations']
        
        print(f"\n✅ Vérification des éléments clés:")
        print(f"   Righting lever curve: {has_righting}")
        print(f"   Heeling moments: {has_heeling}")
        print(f"   Final conditions: {has_final}")
        print(f"   Section 4.30 citée: {has_430}")
        
        results_summary.append({
            'question': 4,
            'type': 'qa_complex',
            'retrieval_quality': retrieval_analysis['quality'],
            'has_righting': has_righting,
            'has_heeling': has_heeling,
            'has_final': has_final,
            'status': 'success' if (has_righting and has_heeling and has_final) else 'partial'
        })
    else:
        results_summary.append({'question': 4, 'status': 'retrieval_only'})
    
    # ============================================================
    # QUESTION 5: Comparaison Intact Stability
    # ============================================================
    print_question_header(5, "Comparaison REG vs Malta - Intact Stability")
    question5 = "Compare REG Part B and Malta PYC requirements for intact stability, listing similarities and differences with citations."
    
    retrieval_reg = analyze_retrieval(question5, retriever, flag_filter="REG")
    retrieval_malta = analyze_retrieval(question5, retriever, flag_filter="MALTA")
    
    if flag_comparison:
        comparison = flag_comparison.compare_requirements(
            topic="intact_stability",
            vessel_profile="50m yacht, 20 persons"
        )
        print("\n🔍 Comparaison générée:")
        print(f"   Nombre d'aspects comparés: {len(comparison)}")
        for i, item in enumerate(comparison[:3], 1):
            print(f"\n   Aspect {i}: {item.get('aspect', 'N/A')[:60]}")
            print(f"      REG: {item.get('REG', 'N/A')[:60]}...")
            print(f"      MALTA: {item.get('MALTA', 'N/A')[:60]}...")
        
        # Vérifier que Malta référence SOLAS
        malta_refs_solas = any('SOLAS' in str(item.get('MALTA', '')).upper() for item in comparison)
        print(f"\n✅ Malta référence SOLAS: {malta_refs_solas}")
        
        results_summary.append({
            'question': 5,
            'type': 'comparison',
            'retrieval_reg': retrieval_reg['quality'],
            'retrieval_malta': retrieval_malta['quality'],
            'aspects_compared': len(comparison),
            'malta_refs_solas': malta_refs_solas,
            'status': 'success'
        })
    else:
        results_summary.append({'question': 5, 'status': 'retrieval_only'})
    
    # ============================================================
    # QUESTION 6: Comparaison Damage Stability
    # ============================================================
    print_question_header(6, "Comparaison REG vs Malta - Damage Stability")
    question6 = "Compare damage stability requirements between REG and Malta PYC, especially regarding reference to SOLAS."
    
    retrieval_reg = analyze_retrieval(question6, retriever, flag_filter="REG")
    retrieval_malta = analyze_retrieval(question6, retriever, flag_filter="MALTA")
    
    if flag_comparison:
        comparison = flag_comparison.compare_requirements(
            topic="damage_stability",
            vessel_profile="50m yacht, 20 persons"
        )
        print("\n🔍 Comparaison générée:")
        print(f"   Nombre d'aspects comparés: {len(comparison)}")
        
        # Compter les références SOLAS dans Malta
        solas_refs = sum(1 for item in comparison if 'SOLAS' in str(item.get('MALTA', '')).upper())
        print(f"   Références SOLAS dans Malta: {solas_refs}/{len(comparison)}")
        
        results_summary.append({
            'question': 6,
            'type': 'comparison',
            'retrieval_reg': retrieval_reg['quality'],
            'retrieval_malta': retrieval_malta['quality'],
            'aspects_compared': len(comparison),
            'solas_refs_count': solas_refs,
            'status': 'success'
        })
    else:
        results_summary.append({'question': 6, 'status': 'retrieval_only'})
    
    # ============================================================
    # QUESTION 7: Malta PYC Requirements
    # ============================================================
    print_question_header(7, "Malta PYC Stability Requirements")
    question7 = "Under Malta PYC, what stability requirements apply to a 50m yacht carrying 20 persons, and which parts refer to SOLAS rather than PYC internal rules?"
    
    retrieval_analysis = analyze_retrieval(question7, retriever, flag_filter="MALTA")
    
    if generator:
        result = answer_question(question7, retriever, generator, top_k=8)
        print("\n💬 Réponse générée:")
        print(result['answer'])
        print(f"\n📚 Citations: {', '.join([f'Section {s}' for s in result['citations']])}")
        
        # Vérifier la distinction Malta vs SOLAS
        has_malta = 'Malta' in result['answer'] or 'PYC' in result['answer']
        has_solas = 'SOLAS' in result['answer']
        distinguishes = 'refer' in result['answer'].lower() or 'delegat' in result['answer'].lower()
        
        print(f"\n✅ Vérification:")
        print(f"   Mention Malta/PYC: {has_malta}")
        print(f"   Mention SOLAS: {has_solas}")
        print(f"   Distingue délégation: {distinguishes}")
        
        results_summary.append({
            'question': 7,
            'type': 'qa_malta',
            'retrieval_quality': retrieval_analysis['quality'],
            'has_malta': has_malta,
            'has_solas': has_solas,
            'distinguishes': distinguishes,
            'status': 'success' if (has_malta and has_solas and distinguishes) else 'partial'
        })
    else:
        results_summary.append({'question': 7, 'status': 'retrieval_only'})
    
    # ============================================================
    # QUESTION 8: Damage Control Information (Section 4.22)
    # ============================================================
    print_question_header(8, "Damage Control Information - Section 4.22")
    question8 = "What damage control information must be permanently available on the navigation bridge under REG Part B Section 4.22?"
    
    retrieval_analysis = analyze_retrieval(question8, retriever, flag_filter="REG")
    
    if generator:
        result = answer_question(question8, retriever, generator, top_k=5)
        print("\n💬 Réponse générée:")
        print(result['answer'])
        print(f"\n📚 Citations: {', '.join([f'Section {s}' for s in result['citations']])}")
        
        # Vérifier Section 4.22
        has_422 = '4.22' in result['citations']
        has_bridge = 'bridge' in result['answer'].lower() or 'navigation' in result['answer'].lower()
        
        print(f"\n✅ Vérification:")
        print(f"   Section 4.22 citée: {has_422}")
        print(f"   Mention bridge/navigation: {has_bridge}")
        
        results_summary.append({
            'question': 9,
            'type': 'qa_specific',
            'retrieval_quality': retrieval_analysis['quality'],
            'has_422': has_422,
            'has_bridge': has_bridge,
            'status': 'success' if (has_422 and has_bridge) else 'partial'
        })
    else:
        results_summary.append({'question': 8, 'status': 'retrieval_only'})
    
    # ============================================================
    # QUESTION 9: Structured Summary Section 4.30
    # ============================================================
    print_question_header(9, "Structured Summary Section 4.30")
    question9 = "Produce a structured technical summary of REG Section 4.30 with headings, subpoints, and citations."
    
    if structured_summary:
        summary = structured_summary.summarize_section("REG", "4.30")
        print("\n📝 Résumé structuré généré:")
        print(f"   Longueur: {len(summary['summary'])} caractères")
        print(f"   Chunks utilisés: {summary['chunks_used']}")
        print(f"\n{summary['summary'][:2000]}...")
        print(f"\n📚 Citations: {', '.join(summary['citations'])}")
        
        # Vérifier la structure
        has_headings = '##' in summary['summary'] or '###' in summary['summary']
        has_citations = 'Ref:' in summary['summary'] or '4.30' in summary['summary']
        
        print(f"\n✅ Vérification:")
        print(f"   Structure avec headings: {has_headings}")
        print(f"   Citations présentes: {has_citations}")
        
        results_summary.append({
            'question': 9,
            'type': 'structured_summary',
            'has_headings': has_headings,
            'has_citations': has_citations,
            'chunks_used': summary['chunks_used'],
            'status': 'success' if (has_headings and has_citations) else 'partial'
        })
    else:
        results_summary.append({'question': 9, 'status': 'not_available'})
    
    # ============================================================
    # QUESTION 10: Zero Hallucination Test
    # ============================================================
    print_question_header(10, "Test Zéro Hallucination - GM Values Malta")
    question10 = "Does Malta PYC specify minimum GM values for yachts below 80m, or does it delegate entirely to SOLAS? Provide only what is explicitly in the text."
    
    retrieval_analysis = analyze_retrieval(question10, retriever, flag_filter="MALTA")
    
    if generator:
        result = answer_question(question10, retriever, generator, top_k=5)
        print("\n💬 Réponse générée:")
        print(result['answer'])
        print(f"\n📚 Citations: {', '.join([f'Section {s}' for s in result['citations']])}")
        
        # Vérifier zéro hallucination
        has_gm_value = any(char.isdigit() for char in result['answer']) and 'GM' in result['answer']
        mentions_solas = 'SOLAS' in result['answer']
        mentions_delegation = 'delegat' in result['answer'].lower() or 'refer' in result['answer'].lower()
        no_hallucination = not has_gm_value or mentions_solas  # Si GM value trouvé, doit mentionner SOLAS
        
        print(f"\n✅ Vérification Zéro Hallucination:")
        print(f"   Valeur GM spécifique inventée: {has_gm_value and not mentions_solas}")
        print(f"   Mention SOLAS: {mentions_solas}")
        print(f"   Mention délégation: {mentions_delegation}")
        print(f"   ✅ Zéro hallucination: {not (has_gm_value and not mentions_solas)}")
        
        results_summary.append({
            'question': 10,
            'type': 'zero_hallucination',
            'retrieval_quality': retrieval_analysis['quality'],
            'mentions_solas': mentions_solas,
            'mentions_delegation': mentions_delegation,
            'no_hallucination': not (has_gm_value and not mentions_solas),
            'status': 'success' if (mentions_solas or mentions_delegation) else 'check_needed'
        })
    else:
        results_summary.append({'question': 10, 'status': 'retrieval_only'})
    
    # ============================================================
    # RÉSUMÉ FINAL
    # ============================================================
    print("\n" + "=" * 100)
    print("  RÉSUMÉ DES TESTS")
    print("=" * 100)
    
    print(f"\n📊 Résultats par question:")
    for res in results_summary:
        q_num = res.get('question', 'N/A')
        status = res.get('status', 'unknown')
        q_type = res.get('type', 'unknown')
        print(f"   Q{q_num} ({q_type}): {status}")
    
    success_count = sum(1 for r in results_summary if r.get('status') == 'success')
    total_count = len(results_summary)
    
    print(f"\n✅ Taux de succès: {success_count}/{total_count} ({success_count*100//total_count}%)")
    print("\n" + "=" * 100)


if __name__ == "__main__":
    main()




