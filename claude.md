# RAG Pipeline Documentation

## Overview

This project implements a **Retrieval-Augmented Generation (RAG)** pipeline for querying information from a PDF book (Cellular Manufacturing). The system combines semantic search with large language models to provide accurate, context-aware answers to user questions.

## Architecture

### High-Level Flow

```
User Query
    ↓
[Query Embedding] (MiniLM-L6-v2)
    ↓
[Vector Search] (ChromaDB)
    ↓
[Retrieved Context] (Top-K relevant chunks)
    ↓
[LLM Generation] (GPT-4o-mini)
    ↓
Generated Answer with Citations
```

### Components

#### 1. Data Preparation Pipeline
- **Input**: PDF document (Cellular_Manufacturing.pdf)
- **Processing**:
  - Text extraction using PyMuPDF
  - Cleaning and normalization
  - Text chunking with overlap
- **Output**: Structured text chunks with metadata

#### 2. Indexing System
- **Embedding Model**: sentence-transformers/all-MiniLM-L6-v2
  - 384-dimensional vectors
  - Optimized for semantic similarity
  - Fast inference speed
- **Vector Database**: ChromaDB
  - Persistent storage
  - Cosine similarity search
  - Metadata filtering

#### 3. Retrieval System
- **Process**:
  1. Convert user query to embedding
  2. Perform similarity search in vector database
  3. Retrieve top-k most relevant chunks
  4. Apply MMR for diversity (optional)
- **Configuration**:
  - Default top-k: 3-5 chunks
  - Similarity threshold: 0.7
  - Overlap handling

#### 4. Generation System
- **LLM**: OpenAI GPT-4o-mini
- **Prompt Structure**:
  ```
  System: You are an expert assistant...
  Context: [Retrieved passages]
  Question: [User query]
  Instructions: Answer based on context, cite sources
  ```
- **Output**: Generated answer with page citations

## Tech Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| Deep Learning | PyTorch | >=2.0.0 |
| Embeddings | sentence-transformers | >=2.2.2 |
| Transformers | Hugging Face transformers | >=4.36.0 |
| RAG Framework | LangChain | >=0.1.0 |
| Vector DB | ChromaDB | >=0.4.0 |
| PDF Processing | PyMuPDF | latest |
| LLM API | OpenAI | latest |
| Data Processing | pandas, numpy | latest |

## Project Structure

```
RAG/
├── claude.md                      # This file - complete documentation
├── requirements.txt               # Python dependencies
├── .env.example                   # Environment variables template
├── .env                          # Actual API keys (gitignored)
├── config.py                     # Centralized configuration
├── main.py                       # Application entry point
├── README.md                     # Setup and usage instructions
│
├── src/
│   ├── __init__.py
│   │
│   ├── data_preparation/
│   │   ├── __init__.py
│   │   ├── pdf_processor.py      # PDF text extraction
│   │   └── text_chunker.py       # Text splitting and chunking
│   │
│   ├── indexing/
│   │   ├── __init__.py
│   │   ├── embedder.py           # Embedding generation
│   │   └── vector_store.py       # ChromaDB operations
│   │
│   ├── retrieval/
│   │   ├── __init__.py
│   │   └── retriever.py          # Query processing and search
│   │
│   ├── generation/
│   │   ├── __init__.py
│   │   └── generator.py          # LLM integration
│   │
│   └── rag_pipeline.py           # End-to-end orchestration
│
├── data/
│   ├── raw/
│   │   └── Cellular_Manufacturing.pdf
│   └── processed/
│       ├── chunks.json           # Processed text chunks
│       └── metadata.json         # Chunk metadata
│
├── chroma_db/                    # ChromaDB persistent storage
│
└── notebooks/                    # Jupyter notebooks (optional)
    └── experimentation.ipynb
```

## Detailed Component Design

### 1. PDF Processor (`src/data_preparation/pdf_processor.py`)

**Purpose**: Extract and clean text from PDF documents

**Key Functions**:
```python
extract_text_from_pdf(pdf_path: str) -> List[Dict]
    """Extract text page by page with metadata"""

clean_text(text: str) -> str
    """Remove artifacts, normalize whitespace"""

process_pdf(pdf_path: str) -> List[Dict]
    """Main pipeline: extract + clean + structure"""
```

**Implementation Details**:
- Uses PyMuPDF (fitz) for robust PDF parsing
- Preserves page numbers for citation
- Handles various PDF encodings
- Removes headers/footers if detected
- Preserves paragraph structure

### 2. Text Chunker (`src/data_preparation/text_chunker.py`)

**Purpose**: Split text into optimal chunks for retrieval

**Strategy**:
- **Chunk Size**: 500-1000 characters
- **Overlap**: 100-200 characters
- **Method**: RecursiveCharacterTextSplitter (LangChain)
  - Splits on sentence boundaries first
  - Falls back to paragraphs, then characters

**Key Functions**:
```python
chunk_text(text: str, chunk_size: int, overlap: int) -> List[str]
    """Split text into overlapping chunks"""

create_chunks_with_metadata(pages: List[Dict]) -> List[Dict]
    """Create chunks with page numbers and IDs"""
```

**Output Format**:
```json
{
  "chunk_id": "chunk_001",
  "text": "Content of the chunk...",
  "page_num": 15,
  "char_count": 742,
  "metadata": {
    "source": "Cellular_Manufacturing.pdf",
    "section": "Chapter 3"
  }
}
```

### 3. Embedder (`src/indexing/embedder.py`)

**Purpose**: Convert text to vector embeddings

**Model**: sentence-transformers/all-MiniLM-L6-v2
- Output dimension: 384
- Max sequence length: 256 tokens
- Trained on 1B+ sentence pairs

**Key Functions**:
```python
class Embedder:
    def __init__(self, model_name: str)
    def embed_text(self, text: str) -> np.ndarray
    def embed_batch(self, texts: List[str]) -> np.ndarray
```

**Optimization**:
- Batch processing for efficiency
- GPU acceleration if available
- Caching for repeated queries

### 4. Vector Store (`src/indexing/vector_store.py`)

**Purpose**: Manage ChromaDB operations

**Key Functions**:
```python
class VectorStore:
    def __init__(self, collection_name: str, persist_dir: str)
    def add_documents(self, chunks: List[Dict], embeddings: np.ndarray)
    def search(self, query_embedding: np.ndarray, top_k: int) -> List[Dict]
    def delete_collection(self)
    def get_collection_stats(self) -> Dict
```

**ChromaDB Configuration**:
- Collection: "cellular_manufacturing"
- Distance metric: Cosine similarity
- Persistence: Local disk storage
- Metadata filtering: Enabled

### 5. Retriever (`src/retrieval/retriever.py`)

**Purpose**: Process queries and retrieve relevant context

**Retrieval Strategies**:
1. **Basic Similarity Search**: Top-k by cosine similarity
2. **MMR (Maximal Marginal Relevance)**: Balance relevance and diversity
3. **Threshold Filtering**: Only return chunks above similarity threshold

**Key Functions**:
```python
class Retriever:
    def __init__(self, embedder: Embedder, vector_store: VectorStore)
    def retrieve(self, query: str, top_k: int = 5) -> List[Dict]
    def retrieve_with_mmr(self, query: str, top_k: int, lambda_mult: float)
```

**Output Format**:
```json
[
  {
    "chunk_id": "chunk_042",
    "text": "Retrieved passage...",
    "page_num": 25,
    "similarity_score": 0.87,
    "metadata": {...}
  }
]
```

### 6. Generator (`src/generation/generator.py`)

**Purpose**: Generate answers using LLM with retrieved context

**LLM**: OpenAI GPT-4o-mini
- Cost-effective
- Fast response time
- Strong reasoning capabilities

**Prompt Template**:
```python
SYSTEM_PROMPT = """You are an expert assistant specializing in cellular
manufacturing. Answer questions based ONLY on the provided context.
Always cite page numbers when referencing information."""

USER_PROMPT = """Context:
{context}

Question: {question}

Instructions:
1. Answer based solely on the context above
2. Cite page numbers in format [Page X]
3. If the answer is not in the context, say so
4. Be concise but complete

Answer:"""
```

**Key Functions**:
```python
class Generator:
    def __init__(self, api_key: str, model: str = "gpt-4o-mini")
    def generate(self, query: str, context: List[Dict]) -> str
    def format_context(self, retrieved_chunks: List[Dict]) -> str
```

### 7. RAG Pipeline (`src/rag_pipeline.py`)

**Purpose**: Orchestrate end-to-end RAG workflow

**Pipeline Flow**:
```python
class RAGPipeline:
    def __init__(self, config: Config)

    def build_index(self, pdf_path: str):
        """One-time indexing: PDF → chunks → embeddings → store"""

    def query(self, question: str, top_k: int = 5) -> Dict:
        """Main query flow: question → retrieval → generation"""

    def get_stats(self) -> Dict:
        """Return pipeline statistics"""
```

**Query Response Format**:
```json
{
  "question": "What is cellular manufacturing?",
  "answer": "Cellular manufacturing is... [Page 12]",
  "sources": [
    {"page": 12, "chunk_id": "chunk_042", "score": 0.89},
    {"page": 15, "chunk_id": "chunk_057", "score": 0.85}
  ],
  "retrieval_time_ms": 45,
  "generation_time_ms": 1200
}
```

## Configuration (`config.py`)

**Centralized Settings**:
```python
class Config:
    # Embedding settings
    EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
    EMBEDDING_DIM = 384

    # Chunking settings
    CHUNK_SIZE = 800
    CHUNK_OVERLAP = 150

    # Retrieval settings
    TOP_K = 7
    SIMILARITY_THRESHOLD = 0.65
    USE_MMR = False

    # Generation settings
    LLM_MODEL = "gpt-4o-mini"
    LLM_TEMPERATURE = 0.2
    MAX_TOKENS = 800

    # Storage paths
    CHROMA_PERSIST_DIR = "./chroma_db"
    DATA_DIR = "./data"
```

## Usage Examples

### 1. Initial Setup and Indexing

```python
from src.rag_pipeline import RAGPipeline
from config import Config

# Initialize pipeline
config = Config()
rag = RAGPipeline(config)

# Build index from PDF (one-time operation)
rag.build_index("data/raw/Cellular_Manufacturing.pdf")
```

### 2. Querying the System

```python
# Ask a question
response = rag.query("What are the benefits of cellular manufacturing?")

print(f"Question: {response['question']}")
print(f"Answer: {response['answer']}")
print(f"\nSources:")
for source in response['sources']:
    print(f"  - Page {source['page']} (score: {source['score']:.2f})")
```

### 3. Command-Line Interface

```bash
# Run interactive CLI
python main.py

# Direct query
python main.py --query "What is cellular manufacturing?"

# Rebuild index
python main.py --rebuild-index
```

## Performance Considerations

### Indexing Performance
- **Time**: ~2-5 minutes for 200-page book
- **Factors**: PDF complexity, chunk size, GPU availability
- **Optimization**: Batch embedding generation

### Query Performance
- **Retrieval**: 20-100ms (depending on collection size)
- **Generation**: 1-3 seconds (GPT-4o-mini)
- **Total latency**: <5 seconds per query

### Scalability
- **Current**: Single book (~200 pages, ~1000 chunks)
- **Scaling**: ChromaDB can handle millions of vectors
- **Considerations**:
  - Multiple books: Add source filtering
  - Larger documents: Consider hierarchical retrieval

## Alternative Embeddings (From todo.md)

### Future Experiments

1. **BAAI/bge-base-en-v1.5**
   - Dimension: 768
   - Better semantic understanding
   - Slightly slower inference

2. **intfloat/e5-base-v2**
   - Dimension: 768
   - Strong on question-answering tasks
   - Good alternative to MiniLM

3. **NVIDIA NV-Embed-v2** (Advanced)
   - State-of-the-art performance
   - Requires more compute
   - Best for production

4. **BAAI/bge-m3** (Advanced)
   - Multilingual support
   - Larger model size
   - Higher accuracy

## Evaluation Metrics

### Retrieval Quality
- **Recall@K**: Are relevant chunks in top-K results?
- **MRR (Mean Reciprocal Rank)**: Position of first relevant result
- **NDCG**: Ranking quality with relevance grades

### Generation Quality
- **Faithfulness**: Is answer grounded in context?
- **Relevance**: Does answer address the question?
- **Citation Accuracy**: Are page numbers correct?

### Tools
- Manual evaluation on sample queries
- RAGAS framework (future integration)
- User feedback collection

## Troubleshooting

### Common Issues

1. **Slow Indexing**
   - Enable GPU: Set `device='cuda'` in embedder
   - Reduce chunk count: Increase chunk size
   - Use batch processing

2. **Poor Retrieval Quality**
   - Adjust chunk size and overlap
   - Try different embedding models
   - Increase top-k parameter
   - Check PDF extraction quality

3. **Irrelevant Answers**
   - Improve prompt engineering
   - Increase similarity threshold
   - Use MMR for diversity
   - Verify retrieved chunks are relevant

4. **OpenAI API Errors**
   - Check API key in .env
   - Verify rate limits
   - Handle network timeouts
   - Monitor token usage

## Security and Best Practices

### API Key Management
- Never commit .env to git
- Use environment variables
- Rotate keys periodically
- Monitor API usage

### Data Privacy
- PDFs may contain sensitive information
- Store vector DB securely
- Consider data retention policies

### Error Handling
- Graceful degradation
- Retry logic for API calls
- Logging and monitoring
- User-friendly error messages

## Future Enhancements

### Short-term
- [ ] Web interface with PDF.js viewer
- [ ] Conversation history/memory
- [ ] Query caching
- [ ] Better citation formatting

### Medium-term
- [ ] Support for multiple PDFs
- [ ] Hybrid search (keyword + semantic)
- [ ] Fine-tune embedding model
- [ ] Evaluation dashboard

### Long-term
- [ ] Production deployment (FastAPI + React)
- [ ] User authentication
- [ ] Advanced analytics
- [ ] Integration with other data sources

## References

- [LangChain Documentation](https://python.langchain.com/)
- [ChromaDB Documentation](https://docs.trychroma.com/)
- [Sentence Transformers](https://www.sbert.net/)
- [OpenAI API Reference](https://platform.openai.com/docs/)
- [PyMuPDF Documentation](https://pymupdf.readthedocs.io/)

## License

[Specify your license here]

## Contact

[Your contact information]

---

**Last Updated**: 2025-11-17
**Version**: 1.0.0
