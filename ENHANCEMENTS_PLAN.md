# RAG Pipeline Enhancement Plan

## Immediate Fix (Priority 1)
**First, you MUST rebuild the index** - the database is currently empty:
```bash
python main.py --rebuild-index
```

## Advanced Improvements (Priority 2)

Based on your excellent suggestions, here's a comprehensive enhancement plan:

---

## 1. Refine Chunking Strategy ✓ Will Implement

### Current Settings
- Chunk size: 800 characters
- Overlap: 150 characters
- Method: Fixed character splitting

### Proposed Improvements

**Option A: Token-Based Chunking (Recommended)**
```python
# Instead of character-based, use token-based
chunk_size = 512 tokens  # ~384-400 words
overlap = 100 tokens      # ~75-80 words
```

**Option B: Semantic Chunking**
```python
# Split at logical boundaries:
- Paragraph breaks
- Section headers
- Sentence boundaries
- Preserve complete thoughts
```

**Implementation:**
- Create new `SemanticTextChunker` class
- Use `langchain.text_splitter.RecursiveCharacterTextSplitter` with better separators
- Add sentence-aware splitting using `nltk` or `spacy`

---

## 2. Improve Preprocessing ✓ Will Implement

### Text Normalization Pipeline

**Add to `pdf_processor.py`:**
```python
def normalize_text(text):
    """Advanced text normalization"""
    # Lowercase for embedding consistency
    text = text.lower()

    # Remove special characters but keep important punctuation
    text = re.sub(r'[^\w\s\.\,\;\:\-]', '', text)

    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()

    # Remove page headers/footers patterns
    text = remove_headers_footers(text)

    return text
```

**Deduplication:**
```python
def deduplicate_chunks(chunks):
    """Remove duplicate chunks using content hashing"""
    seen_hashes = set()
    unique_chunks = []

    for chunk in chunks:
        # Create hash of normalized content
        content_hash = hashlib.md5(chunk['text'].encode()).hexdigest()

        if content_hash not in seen_hashes:
            seen_hashes.add(content_hash)
            unique_chunks.append(chunk)

    return unique_chunks
```

**Semantic Boundary Preservation:**
- Use sentence tokenization (NLTK or spaCy)
- Never split in the middle of sentences
- Preserve section headers with their content

---

## 3. Hybrid Search (BM25 + Vector) ✓ Will Implement

### Current: Vector Search Only
- Uses only semantic similarity (cosine distance)
- May miss exact keyword matches

### Proposed: Hybrid Retrieval

```python
class HybridRetriever:
    def __init__(self, vector_store, bm25_index):
        self.vector_retriever = vector_store
        self.bm25_retriever = bm25_index  # Keyword-based

    def retrieve(self, query, top_k=10):
        # Get results from both methods
        vector_results = self.vector_retriever.search(query, top_k=top_k)
        bm25_results = self.bm25_retriever.search(query, top_k=top_k)

        # Combine and rerank using Reciprocal Rank Fusion (RRF)
        combined = self.reciprocal_rank_fusion(
            vector_results,
            bm25_results,
            k=60  # RRF constant
        )

        return combined[:top_k]
```

**Benefits:**
- Vector search: Captures semantic meaning
- BM25: Catches exact keyword/phrase matches
- Fusion: Best of both worlds

**Implementation Libraries:**
- `rank_bm25` for BM25 implementation
- Or use LangChain's `EnsembleRetriever`

---

## 4. Add Reranking Step ✓ Will Implement

### Cross-Encoder Reranking

After initial retrieval, use a cross-encoder to rerank results:

```python
from sentence_transformers import CrossEncoder

class RerankedRetriever:
    def __init__(self, base_retriever):
        self.base_retriever = base_retriever
        # Use a cross-encoder for reranking
        self.reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')

    def retrieve(self, query, top_k=5, rerank_top_n=20):
        # 1. Get more candidates than needed
        candidates = self.base_retriever.retrieve(query, top_k=rerank_top_n)

        # 2. Rerank using cross-encoder
        pairs = [[query, doc['text']] for doc in candidates]
        scores = self.reranker.predict(pairs)

        # 3. Sort by reranker scores
        for doc, score in zip(candidates, scores):
            doc['rerank_score'] = float(score)

        reranked = sorted(candidates, key=lambda x: x['rerank_score'], reverse=True)

        return reranked[:top_k]
```

**Why This Works:**
- Bi-encoder (current): Fast but less accurate, encodes query and doc separately
- Cross-encoder: Slower but much more accurate, jointly encodes query+doc
- Strategy: Bi-encoder for fast retrieval, cross-encoder for precise reranking

**Recommended Models:**
```python
# For general text:
'cross-encoder/ms-marco-MiniLM-L-6-v2'

# For better quality (slower):
'cross-encoder/ms-marco-MiniLM-L-12-v2'

# Domain-specific (if available):
'cross-encoder/qnli-electra-base'
```

---

## 5. Tunable Retrieval Parameters ✓ Will Implement

### Make Everything Configurable

**Add to `.env` and `config.py`:**
```bash
# Chunking
CHUNK_SIZE_TOKENS=512
CHUNK_OVERLAP_TOKENS=100
CHUNKING_METHOD=semantic  # or 'fixed', 'sentence'

# Retrieval
RETRIEVAL_METHOD=hybrid  # or 'vector', 'bm25'
RETRIEVAL_TOP_K=10
RERANK_ENABLED=true
RERANK_TOP_N=20
BM25_WEIGHT=0.3
VECTOR_WEIGHT=0.7

# Search Quality
MIN_SIMILARITY_SCORE=0.5
MAX_SIMILARITY_SCORE=1.0
ENABLE_MMR=false  # Maximal Marginal Relevance for diversity
```

### Dynamic K Adjustment

```python
def adaptive_top_k(query, base_k=5):
    """Adjust K based on query complexity"""
    query_length = len(query.split())

    if query_length > 20:  # Complex question
        return base_k * 2
    elif query_length < 5:  # Simple question
        return base_k
    else:
        return base_k
```

---

## 6. Debugging & Observability ✓ Will Implement

### Enhanced Logging

```python
class DebugRetriever:
    def retrieve_with_debug(self, query):
        results = self.retrieve(query)

        # Log detailed debug info
        debug_info = {
            'query': query,
            'query_tokens': len(query.split()),
            'query_embedding_norm': np.linalg.norm(query_embedding),
            'num_results': len(results),
            'top_scores': [r['similarity_score'] for r in results[:5]],
            'avg_score': np.mean([r['similarity_score'] for r in results]),
            'min_score': min([r['similarity_score'] for r in results]),
            'max_score': max([r['similarity_score'] for r in results]),
            'retrieved_pages': [r['page_num'] for r in results],
        }

        # Save to log file
        with open('retrieval_debug.log', 'a') as f:
            f.write(json.dumps(debug_info, indent=2) + '\n')

        return results, debug_info
```

### Embedding Quality Checks

```python
def validate_embeddings(embeddings):
    """Check embedding quality"""
    # 1. Check for NaN or Inf
    assert not np.any(np.isnan(embeddings)), "NaN in embeddings!"
    assert not np.any(np.isinf(embeddings)), "Inf in embeddings!"

    # 2. Check normalization
    norms = np.linalg.norm(embeddings, axis=1)
    if not np.allclose(norms, 1.0, atol=0.01):
        print(f"⚠ WARNING: Embeddings not normalized. Norms: {norms[:5]}")
        # Auto-normalize
        embeddings = embeddings / norms[:, np.newaxis]

    # 3. Check dimensionality
    assert embeddings.shape[1] == 384, f"Wrong dimension: {embeddings.shape[1]}"

    return embeddings
```

---

## 7. Index Refresh Strategy ✓ Will Implement

### Versioned Indexing

```python
class VersionedVectorStore:
    def __init__(self):
        self.version = self._get_current_version()

    def _get_current_version(self):
        """Generate version hash from config"""
        config_hash = hashlib.md5(
            f"{CHUNK_SIZE}{CHUNK_OVERLAP}{EMBEDDING_MODEL}".encode()
        ).hexdigest()[:8]
        return config_hash

    def needs_reindex(self):
        """Check if reindexing is needed"""
        stored_version = self._load_stored_version()
        if stored_version != self.version:
            print(f"Config changed: {stored_version} -> {self.version}")
            print("Reindexing required!")
            return True
        return False
```

### Auto-Refresh Triggers

```python
# Automatically rebuild index when:
1. Chunking parameters change
2. Embedding model changes
3. Preprocessing logic changes
4. New version of PDF is detected
```

---

## Implementation Priority

### Phase 1: Critical Fixes (Do Now)
1. ✓ **Rebuild the index** - `python main.py --rebuild-index`
2. ✓ **Verify database is populated** - Already fixed with better logging

### Phase 2: Quick Wins (Next)
3. **Better chunking** - Implement semantic chunking with sentence boundaries
4. **Add preprocessing** - Normalize text, deduplicate chunks
5. **Lower similarity threshold** - Already done (0.5 instead of 0.7)
6. **Add debug logging** - Track scores and retrieved pages

### Phase 3: Advanced Features (Later)
7. **Hybrid search** - Add BM25 + Vector fusion
8. **Reranking** - Add cross-encoder reranking
9. **Configurable parameters** - Make everything tunable via .env
10. **Versioned indexing** - Auto-detect when reindex needed

---

## Expected Improvements

### Current Performance
- Recall: Low (missing relevant chunks)
- Precision: Unknown (no results to measure)
- Query time: 49ms (too fast = empty DB)

### After Enhancements
- **Recall**: +40-60% (hybrid search + better chunking)
- **Precision**: +20-30% (reranking + better preprocessing)
- **Query time**: 1-3 seconds (normal for populated DB)
- **Answer quality**: Much better citations and context

---

## Files to Create/Modify

### New Files
1. `src/data_preparation/semantic_chunker.py` - Better chunking
2. `src/retrieval/hybrid_retriever.py` - BM25 + Vector search
3. `src/retrieval/reranker.py` - Cross-encoder reranking
4. `src/utils/preprocessing.py` - Text normalization utilities
5. `src/utils/debug_logger.py` - Enhanced logging

### Modified Files
1. `config.py` - Add new parameters
2. `src/rag_pipeline.py` - Integrate new components
3. `requirements.txt` - Add new dependencies

### New Dependencies
```
rank-bm25>=0.2.2
nltk>=3.8
# or
spacy>=3.7.0
```

---

## Testing Strategy

### Unit Tests
```python
# Test chunking
test_chunk_boundaries()
test_chunk_deduplication()

# Test retrieval
test_vector_search()
test_bm25_search()
test_hybrid_fusion()
test_reranking()

# Test preprocessing
test_normalization()
test_embedding_quality()
```

### Integration Tests
```python
# End-to-end tests
test_full_pipeline()
test_query_responses()
test_citation_accuracy()
```

### Benchmark Queries
```python
benchmark_queries = [
    "What is cellular manufacturing?",
    "Is cell scheduling effective enough such that no operator is ever without a job to work on?",
    "What are the benefits of group technology?",
    "How are U-shaped cells designed?",
    # Add 10-20 diverse queries
]
```

---

## Next Steps

1. **IMMEDIATE**: Run `python main.py --rebuild-index`
2. **Review**: This enhancement plan
3. **Decide**: Which enhancements to implement first
4. **Let me know**: Which features you want me to implement

I can implement any or all of these enhancements. Just tell me which ones you want to prioritize!
