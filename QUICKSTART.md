# Quick Start Guide

## 🚀 Fastest Path to Demo

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Build the System
```bash
python poc_rag/build_rag_system.py
```

This extracts sections 4.3, 4.4, 4.22, 4.23, 4.24, 4.30 from the PDF and builds the vector store.

### 3. Run the Demo
```bash
python demo_poc.py
```

## 📋 What You'll See

The demo will show:
1. **3 Q&A examples** with citations
2. **1 compliance checklist** for GE50 yacht
3. **1 REG vs Malta comparison** table

## 🔑 Optional: Enable Full Features

For LLM generation (checklists, comparisons), set:
```bash
export OPENAI_API_KEY=your_key_here
```

Without it, the demo will show retrieval results only.

## 📁 Output Files

After building, check:
- `data/vectorstore/chunks_export.json` - All extracted chunks
- `data/vectorstore/` - Vector database files

## 🐛 Troubleshooting

**"Vector store not found"**
→ Run `python poc_rag/build_rag_system.py` first

**"PDF not found"**
→ Ensure `reg-yc-july-2024-edition-part-b.pdf` is in project root

**Import errors**
→ Make sure you're in the project root directory

## 📚 Next Steps

- Try your own questions by modifying `demo_poc.py`
- Add more sections by editing `PDFLoader.TARGET_SECTIONS`
- Extend to other regulatory documents




