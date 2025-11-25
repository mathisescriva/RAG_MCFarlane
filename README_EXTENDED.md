# RAG System Extended - Guide Complet

## 🎯 Vue d'Ensemble

Ce système RAG étendu répond aux **4 besoins exacts du client** :

1. ✅ **Generating compliance checklists** directly from digitized regulations
2. ✅ **Comparing requirements** across different flag states (REG vs MALTA)
3. ✅ **Highlighting gaps** between internal procedures and regulatory obligations
4. ✅ **Producing structured summaries** of complex regulatory texts

---

## 📁 Structure des Nouveaux Modules

```
poc_rag/
├── comparison/              # Module de comparaison inter-flags
│   ├── __init__.py
│   └── flag_comparison.py
├── gap_analysis/            # Module d'analyse de gaps
│   ├── __init__.py
│   └── gap_analyzer.py
├── summary/                 # Module de résumés structurés
│   ├── __init__.py
│   └── structured_summary.py
└── build_multi_flag_system.py  # Script de construction multi-flags
```

---

## 🚀 Installation et Configuration

### 1. Prérequis

```bash
pip install -r requirements.txt
```

### 2. Configuration des Chemins PDF

Les chemins des PDFs peuvent être configurés via :
- Variables d'environnement
- Arguments de ligne de commande
- Valeurs par défaut

**Variables d'environnement:**
```bash
export MALTA_PYC_PATH="/mnt/data/malta-pyc.pdf"
export INTERNAL_PROCEDURES_PATH="/mnt/data/internal_procedures.pdf"
```

### 3. Construction du Système Multi-Flags

```bash
# Avec tous les documents
python poc_rag/build_multi_flag_system.py \
    reg-yc-july-2024-edition-part-b.pdf \
    /mnt/data/malta-pyc.pdf \
    /mnt/data/internal_procedures.pdf

# Ou avec variables d'environnement
export MALTA_PYC_PATH="/mnt/data/malta-pyc.pdf"
export INTERNAL_PROCEDURES_PATH="/mnt/data/internal_procedures.pdf"
python poc_rag/build_multi_flag_system.py reg-yc-july-2024-edition-part-b.pdf
```

**Note:** Si un PDF n'est pas disponible, le système continuera avec les PDFs disponibles.

---

## 📊 Utilisation des Modules

### Module 1: Flag Comparison

**Fonction:** `compare_requirements(topic, vessel_profile)`

**Topics disponibles:**
- `"intact_stability"`
- `"damage_stability"`
- `"stability_documentation"`
- `"loading_damage_control"`

**Exemple:**
```python
from poc_rag.comparison.flag_comparison import FlagComparison

comparison = FlagComparison(retriever, generator)
result = comparison.compare_requirements(
    topic="intact_stability",
    vessel_profile="50m yacht, 20 persons"
)

# Retourne une liste de dictionnaires:
# [
#   {
#     "aspect": "...",
#     "REG": "... (citation)",
#     "MALTA": "... (citation)",
#     "difference": "..."
#   }
# ]
```

---

### Module 2: Gap Analysis

**Fonction:** `analyze_gaps(vessel_profile, flag)`

**Exemple:**
```python
from poc_rag.gap_analysis.gap_analyzer import GapAnalyzer

analyzer = GapAnalyzer(retriever, generator)
gaps = analyzer.analyze_gaps(
    vessel_profile="50m yacht, 20 persons",
    flag="REG"  # ou "MALTA"
)

# Retourne une liste de dictionnaires:
# [
#   {
#     "requirement": "...",
#     "reference": "REG 4.3(1)",
#     "status": "covered|partially_covered|missing",
#     "internal_evidence": "...",
#     "comment": "..."
#   }
# ]
```

---

### Module 3: Structured Summary

**Fonction:** `summarize_section(flag, section_id)`

**Exemple:**
```python
from poc_rag.summary.structured_summary import StructuredSummary

summary_gen = StructuredSummary(retriever, generator)
summary = summary_gen.summarize_section("REG", "4.30")

# Retourne un dictionnaire:
# {
#   "section_id": "4.30",
#   "flag": "REG",
#   "title": "...",
#   "summary": "... (texte structuré markdown)",
#   "citations": ["4.30", ...],
#   "chunks_used": 20
# }
```

---

## 🎬 Demo Complet

### Lancer le Demo Étendu

```bash
# Avec clé OpenAI
source .env
python demo_poc_extended.py
```

### Ce que le Demo Montre

1. **Checklists de Conformité**
   - Checklist REG pour GE50
   - Checklist MALTA pour GE50 (si disponible)

2. **Comparaison Inter-Flags**
   - Comparaison intact_stability (REG vs MALTA)
   - Comparaison damage_stability (REG vs MALTA)

3. **Analyse de Gaps**
   - Gaps INTERNAL vs REG
   - Gaps INTERNAL vs MALTA (si disponible)

4. **Résumés Structurés**
   - Résumé de REG Section 4.30
   - Résumé de section MALTA (si disponible)

5. **Questions Techniques Supplémentaires**
   - Documentation de stabilité Malta PYC
   - Information opérationnelle sur le pont
   - Information de contrôle des avaries REG

---

## 🔧 Configuration Avancée

### Ajouter un Nouveau Flag

1. Préparer le PDF du nouveau flag
2. Créer une fonction de chargement (voir `load_malta_pyc` comme exemple)
3. Ajouter le flag dans `build_multi_flag_system.py`
4. Le système gérera automatiquement le flag dans le vector store

### Personnaliser les Topics de Comparaison

Modifier `TOPIC_MAPPINGS` dans `flag_comparison.py`:

```python
TOPIC_MAPPINGS = {
    "votre_topic": [
        "keyword1", "keyword2", ...
    ]
}
```

---

## 📝 Format des Données

### Métadonnées des Chunks

Chaque chunk inclut maintenant un champ `flag`:
```json
{
  "chunk_id": "4.3_chunk_0",
  "section_number": "4.3",
  "title": "Intact Stability",
  "text": "...",
  "page": 53,
  "chunk_index": 0,
  "flag": "REG"  // ou "MALTA", "INTERNAL"
}
```

### Filtrage par Flag

Le retriever supporte maintenant le filtrage par flag:
```python
results = retriever.retrieve(
    query="stability requirements",
    top_k=5,
    flag_filter="MALTA"  # Filtre uniquement les chunks MALTA
)
```

---

## ⚠️ Notes Importantes

1. **Zéro Hallucination:** Tous les modules respectent la contrainte de zéro hallucination
2. **Citations Obligatoires:** Toutes les réponses incluent des citations exactes
3. **Rétrocompatibilité:** Le système existant continue de fonctionner (flag par défaut = "REG")
4. **Gestion des Erreurs:** Si un PDF n'est pas disponible, le système continue avec les PDFs disponibles

---

## 🐛 Dépannage

**Problème:** "MALTA chunks not found"
- **Solution:** Vérifier que le PDF Malta PYC a été chargé dans le vector store

**Problème:** "INTERNAL chunks not found"
- **Solution:** Ajouter le PDF des procédures internes lors de la construction

**Problème:** Erreur JSON dans les comparaisons
- **Solution:** Le système utilise un fallback si le JSON ne peut pas être parsé

---

## 📚 Exemples d'Utilisation

Voir `demo_poc_extended.py` pour des exemples complets d'utilisation de tous les modules.




