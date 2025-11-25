#!/usr/bin/env python3
"""
Script interactif pour tester le système RAG en direct
Permet de poser des questions et obtenir des réponses avec citations
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
from poc_rag.demo.demo_functions import answer_question


def print_header():
    """Affiche l'en-tête du script interactif."""
    print("\n" + "=" * 80)
    print("  🚢 SYSTÈME RAG MARITIME - MODE INTERACTIF")
    print("=" * 80)
    print("\n💡 Commandes disponibles:")
    print("   - Posez votre question directement")
    print("   - Tapez 'quit' ou 'exit' pour quitter")
    print("   - Tapez 'help' pour voir des exemples de questions")
    print("   - Tapez 'info' pour voir les informations du système")
    print("\n" + "-" * 80 + "\n")


def print_help():
    """Affiche des exemples de questions."""
    print("\n📋 Exemples de questions que vous pouvez poser:\n")
    examples = [
        "What intact stability requirements apply to a 50m yacht carrying 20 persons?",
        "What stability information must be supplied to the Master?",
        "What are the requirements for stability in damaged condition?",
        "What damage control information must be available on the navigation bridge?",
        "Compare REG Part B and Malta PYC requirements for intact stability",
        "What are the complete damage stability requirements under REG Section 4.30?",
        "Generate a compliance checklist for a 50m yacht carrying 20 persons",
    ]
    for i, example in enumerate(examples, 1):
        print(f"   {i}. {example}")
    print()


def print_system_info(vector_store, embedder, generator):
    """Affiche les informations du système."""
    print("\n📊 Informations du système:\n")
    
    # Comptage des chunks par flag
    flag_counts = {}
    for metadata in vector_store.metadata:
        flag = metadata.get("flag", "REG")
        flag_counts[flag] = flag_counts.get(flag, 0) + 1
    
    print(f"   • Total de chunks: {len(vector_store.chunks)}")
    print(f"   • Flags disponibles: {', '.join(flag_counts.keys())}")
    for flag, count in flag_counts.items():
        print(f"     - {flag}: {count} chunks")
    
    # Informations sur l'embedder
    embedder_type = "OpenAI" if isinstance(embedder, OpenAIEmbedder) else "SentenceTransformer (local)"
    print(f"   • Embedder: {embedder_type}")
    
    # Informations sur le générateur
    if generator:
        generator_type = "OpenAI GPT" if hasattr(generator.generator, 'model') else "Unknown"
        print(f"   • Générateur: {generator_type}")
    else:
        print(f"   • Générateur: Non disponible (pas de clé API OpenAI)")
    
    print()


def format_answer(result: dict):
    """Formate et affiche la réponse."""
    print("\n" + "=" * 80)
    print("  RÉPONSE")
    print("=" * 80)
    print(f"\n❓ Question: {result['question']}\n")
    print("💬 Réponse:\n")
    print(result['answer'])
    print(f"\n📚 Citations: {', '.join([f'Section {s}' for s in result['citations']])}")
    print(f"📄 Chunks utilisés: {len(result['chunks_used'])}")
    print("\n" + "-" * 80 + "\n")


def main():
    """Fonction principale du script interactif."""
    print_header()
    
    # Configuration
    vectorstore_dir = project_root / "data/vectorstore"
    
    # Vérifier si le vector store existe
    if not vectorstore_dir.exists():
        print("❌ Erreur: Vector store non trouvé!")
        print(f"   Veuillez d'abord exécuter: python poc_rag/build_multi_flag_system.py")
        return
    
    print("⏳ Chargement du système RAG...")
    
    # Charger le vector store
    try:
        vector_store = FAISSStore()
        vector_store.load(str(vectorstore_dir))
        print(f"✓ Vector store chargé ({len(vector_store.chunks)} chunks)")
    except Exception as e:
        print(f"❌ Erreur lors du chargement du vector store: {e}")
        return
    
    # Initialiser l'embedder
    use_openai = os.getenv("USE_OPENAI", "false").lower() == "true"
    if use_openai and os.getenv("OPENAI_API_KEY"):
        print("✓ Utilisation d'OpenAI embeddings...")
        embedder = OpenAIEmbedder()
    else:
        print("✓ Utilisation de SentenceTransformer embeddings (local)...")
        embedder = SentenceTransformerEmbedder()
    
    # Initialiser le retriever
    retriever = Retriever(vector_store, embedder)
    print("✓ Retriever initialisé")
    
    # Initialiser le générateur
    if os.getenv("OPENAI_API_KEY"):
        print("✓ Utilisation d'OpenAI GPT pour la génération...")
        base_generator = OpenAIGenerator(model="gpt-4o-mini", temperature=0.1)
        generator = RegulatoryGenerator(base_generator)
    else:
        print("⚠️  Aucune clé API OpenAI trouvée.")
        print("   Le système fonctionnera en mode retrieval uniquement (pas de génération LLM)")
        print("   Pour activer la génération, configurez OPENAI_API_KEY dans .env")
        generator = None
    
    print("\n✅ Système prêt!\n")
    
    # Boucle interactive
    while True:
        try:
            # Lire la question de l'utilisateur
            question = input("🔍 Votre question (ou 'help'/'info'/'quit'): ").strip()
            
            # Commandes spéciales
            if question.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Au revoir!\n")
                break
            
            if question.lower() == 'help':
                print_help()
                continue
            
            if question.lower() == 'info':
                print_system_info(vector_store, embedder, generator)
                continue
            
            if not question:
                print("⚠️  Veuillez entrer une question.\n")
                continue
            
            # Traiter la question
            print("\n⏳ Recherche et génération en cours...")
            
            if generator:
                try:
                    result = answer_question(question, retriever, generator, top_k=5)
                    format_answer(result)
                except Exception as e:
                    print(f"\n❌ Erreur lors de la génération: {e}\n")
                    print("   Vérifiez votre connexion internet et votre clé API OpenAI.\n")
            else:
                # Mode retrieval uniquement
                print("\n⚠️  Mode retrieval uniquement (pas de génération LLM)\n")
                results = retriever.retrieve(question, top_k=5)
                print(f"📚 {len(results)} chunks trouvés:\n")
                for i, r in enumerate(results, 1):
                    print(f"  [{i}] Section {r['metadata']['section_number']} - {r['metadata']['title']}")
                    print(f"      Score: {r['score']:.3f}")
                    print(f"      Flag: {r['metadata'].get('flag', 'REG')}")
                    print(f"      Aperçu: {r['chunk']['text'][:150]}...\n")
                print("-" * 80 + "\n")
        
        except KeyboardInterrupt:
            print("\n\n👋 Interruption - Au revoir!\n")
            break
        except EOFError:
            print("\n\n👋 Au revoir!\n")
            break
        except Exception as e:
            print(f"\n❌ Erreur: {e}\n")


if __name__ == "__main__":
    main()

