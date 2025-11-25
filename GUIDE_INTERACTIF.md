# Guide d'utilisation - Mode Interactif

## 🚀 Lancement

```bash
python interactive_rag.py
```

ou

```bash
python3 interactive_rag.py
```

## 📋 Commandes disponibles

### Questions normales
Posez simplement votre question et appuyez sur Entrée. Le système va :
1. Rechercher les chunks pertinents
2. Générer une réponse avec citations
3. Afficher les sections utilisées

**Exemples:**
```
🔍 Votre question: What intact stability requirements apply to a 50m yacht?
```

### Commandes spéciales

- **`help`** - Affiche des exemples de questions
- **`info`** - Affiche les informations du système (nombre de chunks, flags disponibles, etc.)
- **`quit`** ou **`exit`** - Quitte le programme

## 💡 Exemples de questions

### Questions techniques simples
- "What intact stability requirements apply to a 50m yacht carrying 20 persons?"
- "What stability information must be supplied to the Master?"
- "What are the requirements for stability in damaged condition?"

### Questions sur des sections spécifiques
- "What damage control information must be available on the navigation bridge?"
- "What are the complete damage stability requirements under REG Section 4.30?"

### Questions de comparaison
- "Compare REG Part B and Malta PYC requirements for intact stability"

### Questions de checklist
- "Generate a compliance checklist for a 50m yacht carrying 20 persons"

## ⚙️ Configuration

### Avec génération LLM (recommandé)
1. Configurez votre clé API OpenAI dans `.env`:
   ```
   OPENAI_API_KEY=sk-...
   ```

2. Lancez le script - la génération sera automatiquement activée

### Sans génération LLM (retrieval uniquement)
Si vous n'avez pas de clé API, le système fonctionnera en mode "retrieval uniquement":
- Il affichera les chunks trouvés
- Pas de réponse générée par LLM
- Utile pour vérifier la qualité de la recherche

## 📊 Format de sortie

Chaque réponse inclut:
- ✅ La question posée
- ✅ La réponse générée (avec citations)
- ✅ Les sections citées (ex: Section 4.3, Section 4.30)
- ✅ Le nombre de chunks utilisés

## 🔧 Dépannage

### Erreur: "Vector store non trouvé"
```bash
# Construisez d'abord le système RAG
python poc_rag/build_multi_flag_system.py
```

### Erreur: "Aucune clé API OpenAI"
- Le système fonctionnera en mode retrieval uniquement
- Pour activer la génération, ajoutez `OPENAI_API_KEY` dans `.env`

### Erreur de connexion
- Vérifiez votre connexion internet
- Vérifiez que votre clé API OpenAI est valide

## 🎯 Astuces

1. **Questions précises** = meilleures réponses
   - ✅ "What are the intact stability requirements for a 50m yacht?"
   - ❌ "stability"

2. **Utilisez des termes techniques** du domaine maritime
   - "intact stability", "damage stability", "metacentric height", etc.

3. **Spécifiez le contexte** quand c'est pertinent
   - "50m yacht", "20 persons", "under REG Part B", etc.

4. **Commandes rapides**
   - `Ctrl+C` pour interrompre une génération en cours
   - `quit` pour quitter proprement

