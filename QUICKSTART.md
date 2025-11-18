# Quick Start Guide

## Setup (5 minutes)

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- PyTorch (for embeddings)
- sentence-transformers (MiniLM-L6-v2)
- transformers (Hugging Face)
- LangChain (RAG framework)
- ChromaDB (vector database)
- PyMuPDF (PDF processing)
- OpenAI (LLM API)
- Other utilities

### 2. Configure API Key

```bash
# Copy the example file
cp .env.example .env

# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=sk-your-key-here
```

Get your API key from: https://platform.openai.com/api-keys

### 3. Verify PDF Location

Make sure `Cellular_Manufacturing.pdf` is in the project root directory.

## First Run

```bash
python main.py
```

This will:
1. ✓ Load the embedding model (MiniLM-L6-v2)
2. ✓ Extract text from the PDF
3. ✓ Create ~800 character chunks with 150 character overlap
4. ✓ Generate embeddings for all chunks
5. ✓ Store in ChromaDB
6. ✓ Start interactive mode

**Expected time**: 2-5 minutes for initial indexing

## Using the System

### Interactive Mode (Recommended)

```bash
python main.py
```

Then type your questions:

```
Your question: What is cellular manufacturing?
Your question: What are the main benefits?
Your question: stats
Your question: quit
```

### Direct Query

```bash
python main.py --query "What is cellular manufacturing?"
```

### With Verbose Output

```bash
python main.py --query "What are the benefits?" --verbose
```

## Common Tasks

### Rebuild the Index

If you modify the PDF or want to change chunking parameters:

```bash
python main.py --rebuild-index
```

### Check Statistics

```bash
python main.py --stats
```

### View Configuration

```bash
python main.py --config
```

### Get More Context

Retrieve more documents for better answers:

```bash
python main.py --query "Your question" --top-k 10
```

## Customization

### Change Chunk Size

Edit `.env`:

```bash
CHUNK_SIZE=1000        # Larger chunks (default: 800)
CHUNK_OVERLAP=200      # More overlap (default: 150)
```

Then rebuild:

```bash
python main.py --rebuild-index
```

### Try Different Embedding Model

Edit `.env`:

```bash
# Better quality, slower
EMBEDDING_MODEL=BAAI/bge-base-en-v1.5

# Or for Q&A tasks
EMBEDDING_MODEL=intfloat/e5-base-v2
```

### Adjust Retrieval

Edit `.env`:

```bash
TOP_K=10                      # Retrieve more documents
SIMILARITY_THRESHOLD=0.6      # Lower threshold = more results
```

### Tweak LLM Settings

Edit `.env`:

```bash
LLM_MODEL=gpt-4o-mini         # Or gpt-4, gpt-3.5-turbo
LLM_TEMPERATURE=0.0           # More deterministic
LLM_MAX_TOKENS=800            # Longer answers
```

## Troubleshooting

### "OPENAI_API_KEY is not set"

```bash
# Make sure .env exists and has your key
cat .env | grep OPENAI_API_KEY
```

### "PDF file not found"

```bash
# Check PDF location
ls -la Cellular_Manufacturing.pdf

# Or update path in .env
echo "PDF_PATH=./path/to/your.pdf" >> .env
```

### Slow Performance

```bash
# Enable GPU if available
echo "USE_GPU=true" >> .env

# Or reduce batch size
# Edit config.py: BATCH_SIZE = 16
```

### Out of Memory

```bash
# Use CPU only
echo "USE_GPU=false" >> .env

# Reduce batch size in config.py
# BATCH_SIZE = 8
```

## File Structure

```
RAG/
├── main.py                    # Run this!
├── config.py                  # Configuration
├── .env                      # Your API key
├── requirements.txt          # Dependencies
│
├── src/
│   ├── data_preparation/     # PDF & chunking
│   ├── indexing/            # Embeddings & storage
│   ├── retrieval/           # Search
│   ├── generation/          # LLM
│   └── rag_pipeline.py      # Orchestration
│
└── chroma_db/               # Vector database (auto-created)
```

## What's Happening Under the Hood

1. **PDF Processing**: PyMuPDF extracts text page-by-page
2. **Chunking**: LangChain splits text into 800-char chunks with 150-char overlap
3. **Embedding**: sentence-transformers converts chunks to 384-dim vectors
4. **Storage**: ChromaDB stores vectors with metadata (page numbers, etc.)
5. **Query**: Your question → embedding → similarity search → top-K chunks
6. **Generation**: GPT-4o-mini receives chunks + question → generates answer with citations

## Next Steps

1. ✓ Get it running (you are here!)
2. Try asking questions about cellular manufacturing
3. Experiment with different settings
4. Read [README.md](README.md) for advanced usage
5. Check [claude.md](claude.md) for technical details

## Example Session

```bash
$ python main.py

==============================================================
  RAG PIPELINE - Cellular Manufacturing Q&A System
==============================================================

Initializing RAG pipeline...
Loading embedding model: sentence-transformers/all-MiniLM-L6-v2
Using device: cpu
Embedding dimension: 384
✓ RAG Pipeline initialized successfully

==============================================================
INDEXING PHASE
==============================================================

[1/4] Extracting text from PDF...
Extracting PDF pages: 100%|████████| 195/195 [00:12<00:00]
✓ Extracted 195 pages

[2/4] Chunking text...
✓ Created 847 chunks

[3/4] Generating embeddings...
Batches: 100%|████████| 27/27 [00:45<00:00]
✓ Generated 847 embeddings

[4/4] Storing in vector database...
✓ Successfully added 847 documents

==============================================================
INDEXING COMPLETE
==============================================================
Total documents: 847
Total time: 68.23 seconds
==============================================================

==============================================================
INTERACTIVE MODE
==============================================================

Your question: What is cellular manufacturing?

==============================================================
QUERY PHASE
==============================================================
Question: What is cellular manufacturing?

[1/2] Retrieving relevant documents...
✓ Retrieved 5 documents
  Average similarity: 0.8234
  Pages: [15, 16, 18, 22, 25]

[2/2] Generating answer...
✓ Answer generated

==============================================================
QUERY COMPLETE
==============================================================
Total time: 2847ms
==============================================================

==============================================================
ANSWER
==============================================================
Cellular manufacturing is a production approach that organizes
machines and workers into cells, where each cell contains all
the equipment needed to produce a family of similar parts [Page 15].
This method is based on group technology principles and aims to
improve efficiency by reducing setup times and work-in-progress
inventory [Page 16].

==============================================================
SOURCES (5 documents)
==============================================================

1. Page 15 (Similarity: 0.892)
2. Page 16 (Similarity: 0.847)
3. Page 18 (Similarity: 0.823)
4. Page 22 (Similarity: 0.801)
5. Page 25 (Similarity: 0.789)
==============================================================

Your question: quit
Goodbye!
```

## Support

- Read [README.md](README.md) for detailed documentation
- Check [claude.md](claude.md) for technical architecture
- Review [todo.md](todo.md) for alternative embedding models

**Happy querying!** 🚀
