# RAG Pipeline for PDF Question Answering

A complete **Retrieval-Augmented Generation (RAG)** system for querying information from PDF documents. This implementation uses semantic search with ChromaDB and GPT-4o-mini to provide accurate, cited answers from your documents.

## Features

- **PDF Processing**: Extract and clean text from PDF documents
- **Intelligent Chunking**: Split text into optimal segments with overlap
- **Semantic Search**: Use sentence-transformers for embedding generation
- **Vector Storage**: Persistent storage with ChromaDB
- **LLM Generation**: GPT-4o-mini for accurate, grounded answers
- **Citation Support**: Automatic page number citations
- **Interactive CLI**: Easy-to-use command-line interface
- **Configurable**: Extensive configuration options

## Quick Start

### Prerequisites

- Python 3.8 or higher
- OpenAI API key
- ~2GB free disk space for models and data

### Installation

1. **Clone or download this repository**

2. **Install dependencies**

```bash
pip install -r requirements.txt
```

3. **Set up environment variables**

Copy the example environment file and add your OpenAI API key:

```bash
cp .env.example .env
```

Edit `.env` and add your API key:

```
OPENAI_API_KEY=your_api_key_here
```

4. **Verify your PDF is in place**

The default configuration expects `Cellular_Manufacturing.pdf` in the project root. If your PDF is elsewhere, update the `PDF_PATH` in `.env`.

### First Run

Build the index and start interactive mode:

```bash
python main.py
```

This will:
1. Extract text from the PDF
2. Create text chunks
3. Generate embeddings
4. Store vectors in ChromaDB
5. Start interactive Q&A mode

## Usage

### Interactive Mode

Run without arguments for an interactive session:

```bash
python main.py
```

Then type your questions:

```
Your question: What is cellular manufacturing?
```

Commands in interactive mode:
- Type your question to get an answer
- `stats` - Show pipeline statistics
- `help` - Show help message
- `quit` or `exit` - Exit the application

### Direct Query

Ask a single question:

```bash
python main.py --query "What are the benefits of cellular manufacturing?"
```

### Rebuild Index

Force rebuild the vector index:

```bash
python main.py --rebuild-index
```

### Show Statistics

Display pipeline statistics:

```bash
python main.py --stats
```

### Verbose Mode

Get detailed output with timing and sources:

```bash
python main.py --query "Your question" --verbose
```

### Custom Top-K

Retrieve more or fewer documents:

```bash
python main.py --query "Your question" --top-k 10
```

### Show Configuration

Display current configuration:

```bash
python main.py --config
```

## Configuration

Edit `.env` or `config.py` to customize the pipeline:

### Key Settings

| Setting | Default | Description |
|---------|---------|-------------|
| `EMBEDDING_MODEL` | all-MiniLM-L6-v2 | Sentence transformer model |
| `LLM_MODEL` | gpt-4o-mini | OpenAI model for generation |
| `CHUNK_SIZE` | 800 | Characters per chunk |
| `CHUNK_OVERLAP` | 150 | Overlap between chunks |
| `TOP_K` | 5 | Number of documents to retrieve |
| `SIMILARITY_THRESHOLD` | 0.7 | Minimum similarity score |
| `LLM_TEMPERATURE` | 0.1 | Temperature for generation |

### Alternative Embedding Models

Try different embedding models (edit in `.env` or `config.py`):

```bash
# Better quality (768 dimensions)
EMBEDDING_MODEL=BAAI/bge-base-en-v1.5

# Good for Q&A
EMBEDDING_MODEL=intfloat/e5-base-v2

# Advanced (requires more resources)
EMBEDDING_MODEL=nvidia/NV-Embed-v2
```

## Project Structure

```
RAG/
├── main.py                        # CLI application
├── config.py                      # Configuration
├── requirements.txt               # Dependencies
├── .env                          # Environment variables
├── claude.md                     # Detailed documentation
│
├── src/
│   ├── data_preparation/
│   │   ├── pdf_processor.py      # PDF extraction
│   │   └── text_chunker.py       # Text chunking
│   ├── indexing/
│   │   ├── embedder.py           # Embedding generation
│   │   └── vector_store.py       # ChromaDB operations
│   ├── retrieval/
│   │   └── retriever.py          # Query & search
│   ├── generation/
│   │   └── generator.py          # LLM generation
│   └── rag_pipeline.py           # Main orchestration
│
├── data/
│   ├── raw/                      # Original PDFs
│   └── processed/                # Processed chunks
│
└── chroma_db/                    # Vector database storage
```

## Examples

### Example 1: Basic Question

```bash
python main.py --query "What is cellular manufacturing?"
```

Output:
```
==============================================================
ANSWER
==============================================================
Cellular manufacturing is a production approach that organizes
machines and workers into cells containing all equipment needed
to produce a family of similar parts [Page 15].

==============================================================
SOURCES (3 documents)
==============================================================
1. Page 15 (Similarity: 0.892)
2. Page 16 (Similarity: 0.847)
3. Page 18 (Similarity: 0.823)
==============================================================
```

### Example 2: Interactive Session

```bash
$ python main.py

==============================================================
  RAG PIPELINE - Cellular Manufacturing Q&A System
==============================================================

Initializing RAG pipeline...
✓ RAG Pipeline initialized successfully

INDEXING PHASE
✓ Index already exists with 847 documents

==============================================================
INTERACTIVE MODE
==============================================================
Ask questions about cellular manufacturing.
Commands:
  - Type 'quit' or 'exit' to exit
  - Type 'stats' to show pipeline statistics
  - Type 'help' for more options
==============================================================

Your question: What are the main benefits?

[Answer with citations appears...]

Your question: quit
Goodbye!
```

## Performance

Typical performance on a standard laptop:

- **Indexing**: 2-5 minutes for a 200-page PDF
- **Query**: 2-4 seconds per question
  - Retrieval: 50-100ms
  - Generation: 1-3 seconds

## Troubleshooting

### Issue: "OPENAI_API_KEY is not set"

**Solution**: Make sure you have a `.env` file with your API key:

```bash
cp .env.example .env
# Edit .env and add your key
```

### Issue: "PDF file not found"

**Solution**: Check the PDF path in your `.env` file or move your PDF to the project root.

### Issue: Slow performance

**Solutions**:
- Enable GPU: Set `USE_GPU=true` in `.env` if you have CUDA
- Reduce chunk count: Increase `CHUNK_SIZE` in `.env`
- Use smaller embedding model (already using the smallest)

### Issue: Poor answer quality

**Solutions**:
- Increase `TOP_K` to retrieve more context
- Lower `SIMILARITY_THRESHOLD` to include more documents
- Try a different embedding model (see Configuration section)
- Increase `LLM_MAX_TOKENS` for longer answers

### Issue: Out of memory

**Solutions**:
- Reduce `BATCH_SIZE` in config.py
- Use CPU instead of GPU for embedding generation
- Process PDF in smaller sections

## Advanced Usage

### Programmatic Usage

Use the RAG pipeline in your own Python code:

```python
from config import Config
from src.rag_pipeline import RAGPipeline

# Initialize
Config.validate()
rag = RAGPipeline(Config)

# Build index
rag.build_index()

# Query
response = rag.query("What is cellular manufacturing?")
print(response["answer"])

# Get sources
for source in response["sources"]:
    print(f"Page {source['page']}: {source['text_preview']}")
```

### Batch Queries

Process multiple questions:

```python
questions = [
    "What is cellular manufacturing?",
    "What are the benefits?",
    "How are cells organized?"
]

responses = rag.query_batch(questions, top_k=5)

for resp in responses:
    print(f"Q: {resp['question']}")
    print(f"A: {resp['answer']}\n")
```

### Custom Retrieval

Use different retrieval strategies:

```python
from src.retrieval.retriever import Retriever

# MMR for diversity
results = retriever.retrieve_with_mmr(
    query="Your question",
    top_k=5,
    lambda_mult=0.5  # Balance relevance and diversity
)

# Hybrid search (semantic + keyword)
results = retriever.retrieve_hybrid(
    query="Your question",
    top_k=5,
    keyword_weight=0.3
)
```

## Development

### Running Tests

Individual components can be tested:

```bash
# Test PDF processor
python src/data_preparation/pdf_processor.py Cellular_Manufacturing.pdf

# Test embedder
python src/indexing/embedder.py

# Test vector store
python src/indexing/vector_store.py

# Test retriever
python src/retrieval/retriever.py

# Test generator
python src/generation/generator.py
```

### Adding New Features

The modular design makes it easy to extend:

1. **Custom chunking**: Modify `text_chunker.py`
2. **Different embeddings**: Update `EMBEDDING_MODEL` in config
3. **New retrieval strategies**: Extend `Retriever` class
4. **Custom prompts**: Modify `SYSTEM_PROMPT` in config

## Documentation

- **[claude.md](claude.md)** - Complete technical documentation
- **[todo.md](todo.md)** - Notes on alternative embedding models

## Cost Estimates

Using GPT-4o-mini:

- **Indexing**: ~$0.10-0.30 for a 200-page book (one-time)
- **Queries**: ~$0.001-0.003 per question
- **100 questions**: ~$0.10-0.30

Note: Embeddings are free (run locally) and stored permanently.

## FAQ

**Q: Can I use multiple PDFs?**
A: Yes, modify the code to process multiple PDFs into the same collection. Add a `source` metadata field to distinguish them.

**Q: Can I use a different LLM?**
A: Yes, modify `generator.py` to support other APIs (Anthropic, local models, etc.)

**Q: How do I improve answer quality?**
A: Try increasing `TOP_K`, experimenting with different embedding models, or adjusting chunk sizes.

**Q: Is this suitable for production?**
A: This is a solid foundation but add error handling, monitoring, API rate limiting, and security measures for production.

**Q: Can I use this offline?**
A: Partially. Embeddings can run offline, but generation requires OpenAI API (or switch to a local LLM).

## Contributing

Contributions are welcome! Areas for improvement:

- [ ] Support for multiple PDFs
- [ ] Web interface with FastAPI
- [ ] Evaluation metrics (RAGAS)
- [ ] Conversation history
- [ ] Hybrid search (BM25 + semantic)
- [ ] Local LLM support

## License

[Your License Here]

## Acknowledgments

- LangChain for RAG framework
- ChromaDB for vector storage
- sentence-transformers for embeddings
- OpenAI for GPT-4o-mini

## Support

For issues or questions:
1. Check [claude.md](claude.md) for detailed documentation
2. Review the troubleshooting section above
3. Open an issue with your question

---

**Built with Claude Code**
