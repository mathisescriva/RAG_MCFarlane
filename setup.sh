#!/bin/bash
# Setup script for RAG System POC

echo "=========================================="
echo "RAG System Setup"
echo "=========================================="
echo ""

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt

# Check if PDF exists
if [ ! -f "reg-yc-july-2024-edition-part-b.pdf" ]; then
    echo ""
    echo "⚠️  Warning: PDF file not found!"
    echo "   Expected: reg-yc-july-2024-edition-part-b.pdf"
    echo "   Please ensure the PDF is in the project root."
    exit 1
fi

# Build RAG system
echo ""
echo "Building RAG system..."
python3 poc_rag/build_rag_system.py

echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "To run the demo:"
echo "  python3 demo_poc.py"
echo ""
echo "For OpenAI features, set:"
echo "  export OPENAI_API_KEY=your_key_here"
echo ""




