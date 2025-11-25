# Maritime Regulatory Assistant - RAG System POC

A complete Retrieval-Augmented Generation (RAG) system for answering technical compliance questions using the REG Yacht Code Part B (July 2024).

## 🎯 Purpose

This POC demonstrates a production-ready RAG system that can:
- Extract and understand complex regulatory text
- Answer precise technical questions with citations
- Generate structured compliance checklists
- Compare regulations across different flag states (REG vs Malta)

## 📁 Project Structure

```
RAG_MCFarlane/
├── poc_rag/                    # Main RAG system modules
│   ├── loader/                 # PDF extraction
│   ├── chunker/                # Text chunking
│   ├── embedder/               # Embedding generation
│   ├── vectorstore/            # FAISS vector database
│   ├── retriever/              # Semantic search
│   ├── generator/              # LLM generation
│   ├── demo/                   # Demo functions
│   └── build_rag_system.py    # System builder
├── demo_poc.py                 # End-to-end demo script
├── requirements.txt            # Python dependencies
└── reg-yc-july-2024-edition-part-b.pdf  # Source PDF
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Build the RAG System

First, extract sections from the PDF and build the vector store:

```bash
cd poc_rag
python build_rag_system.py ../reg-yc-july-2024-edition-part-b.pdf
```

This will:
- Extract sections 4.3, 4.4, 4.22, 4.23, 4.24, 4.30 from the PDF
- Chunk the text into ~600 token pieces
- Generate embeddings (using SentenceTransformer by default)
- Build and save the FAISS vector store to `data/vectorstore/`

### 3. Run the Demo

```bash
cd ..
python demo_poc.py
```

The demo will:
1. Answer 3 regulatory questions with citations
2. Generate a compliance checklist for GE50 yacht
3. Compare REG vs Malta PYC regulations

## 🔧 Configuration

### Embedding Models

**Option 1: SentenceTransformer (Local, Recommended for POC)**
- No API key needed
- Uses `all-MiniLM-L6-v2` (384 dimensions)
- Fast and free

**Option 2: OpenAI Embeddings**
```bash
export OPENAI_API_KEY=your_key_here
export USE_OPENAI=true
python poc_rag/build_rag_system.py ../reg-yc-july-2024-edition-part-b.pdf openai
```

### Generation Models

**OpenAI GPT (Recommended)**
```bash
export OPENAI_API_KEY=your_key_here
python demo_poc.py
```

The system uses `gpt-4o-mini` by default for cost-effective generation.

## 📊 Extracted Sections

The system extracts only these sections from the PDF:
- **4.3** – Intact Stability and Information
- **4.4** – Stability Information to be Supplied to the Master
- **4.22** – Damage Control Information
- **4.23** – Loading Procedures
- **4.24** – Watertight Door Inspection and Operation
- **4.30** – Stability in Damaged Condition

Total: ~20-35 pages of regulatory text.

## 🎨 Demo Functions

### 1. `answer_question(question: str)`
Answers regulatory questions with citations.

**Example:**
```python
result = answer_question(
    "What intact stability rule applies to GE50 with 20 persons?",
    retriever, generator
)
```

### 2. `generate_checklist()`
Generates structured compliance checklists.

**Example:**
```python
checklist = generate_checklist(
    retriever, generator,
    yacht_spec="50m yacht GE50 with 20 persons"
)
```

### 3. `compare_with_malta_stub()`
Compares REG regulations with Malta PYC (stub implementation).

**Example:**
```python
comparison = compare_with_malta_stub(retriever, generator)
```

## 📝 Output Files

After building the system, you'll find:

- `data/vectorstore/index.faiss` - FAISS vector index
- `data/vectorstore/metadata.json` - Chunk metadata
- `data/vectorstore/chunks.json` - Full chunk text
- `data/vectorstore/chunks_export.json` - Complete export for inspection

## 🔍 System Architecture

```
PDF → Loader → Chunker → Embedder → Vector Store
                                         ↓
                                    Retriever
                                         ↓
                                    Generator → Answer
```

1. **Loader**: Extracts specific sections from PDF
2. **Chunker**: Splits text into 500-800 token chunks with metadata
3. **Embedder**: Generates embeddings (SentenceTransformer or OpenAI)
4. **Vector Store**: FAISS index for fast similarity search
5. **Retriever**: Semantic search with cosine similarity
6. **Generator**: LLM with regulatory system prompt and citation enforcement

## 🎯 Key Features

- ✅ **Modular Architecture**: Clean separation of concerns
- ✅ **Citation Enforcement**: Always cites section numbers
- ✅ **No Hallucination**: Only uses provided regulatory text
- ✅ **Section Filtering**: Can filter by section number
- ✅ **Extensible**: Easy to add new regulations or flags

## 📚 Example Questions

The system can answer questions like:
- "What intact stability rule applies to GE50 with 20 persons?"
- "What stability information must be supplied to the Master?"
- "What are the requirements for stability in damaged condition?"
- "What are the loading procedure requirements?"
- "What watertight door inspection requirements exist?"

## 🔐 API Keys

For full functionality, set:
```bash
export OPENAI_API_KEY=your_key_here
```

For local-only operation (embeddings only):
- Uses SentenceTransformer (no API key needed)
- Generation will be skipped in demo

## 🐛 Troubleshooting

**PDF extraction fails:**
- Ensure `pdfplumber` is installed: `pip install pdfplumber`
- Check PDF path is correct

**FAISS import error:**
- Install: `pip install faiss-cpu`

**OpenAI errors:**
- Verify API key is set: `echo $OPENAI_API_KEY`
- Check you have API credits

**Vector store not found:**
- Run `build_rag_system.py` first
- Check `data/vectorstore/` directory exists

## 📄 License

This is a POC demonstration system.

## 🚢 Next Steps

To extend this system:
1. Add more sections from the PDF
2. Add other regulatory documents (Malta PYC, MCA, etc.)
3. Implement multi-document comparison
4. Add web interface
5. Deploy as API service

---

**Built for maritime regulatory compliance assistance.**




