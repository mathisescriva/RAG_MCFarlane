#!/bin/bash
# Script pour configurer la clé API OpenAI de manière sécurisée

echo "Configuration de la clé API OpenAI"
echo "===================================="
echo ""

# Demander la clé API
read -sp "Entrez votre clé API OpenAI: " api_key
echo ""

if [ -z "$api_key" ]; then
    echo "❌ Clé API vide. Abandon."
    exit 1
fi

# Ajouter à .env (ne sera pas commité grâce à .gitignore)
echo "OPENAI_API_KEY=$api_key" > .env
echo ""
echo "✅ Clé API sauvegardée dans .env"
echo ""
echo "Pour utiliser la clé, exécutez:"
echo "  source .env"
echo "  python3 demo_poc.py"
echo ""
echo "Ou ajoutez cette ligne à votre ~/.zshrc ou ~/.bashrc:"
echo "  export OPENAI_API_KEY=\"$api_key\""




