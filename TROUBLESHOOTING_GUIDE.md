# Troubleshooting Guide

## Code Analysis Summary

I've analyzed the RAG pipeline code and identified potential issues and solutions.

### ✅ What's Working

1. **Code Structure**: All modules are properly structured with correct imports
2. **Configuration**: The `.env` file is properly configured with your OpenAI API key
3. **PDF File**: `Cellular_Manufacturing.pdf` exists in the project root
4. **Logic Flow**: The pipeline logic is sound (PDF → Chunks → Embeddings → Vector Store → Retrieval → Generation)

### ⚠️ Potential Issues

## Issue 1: Dependencies Not Installed

**Symptom**: ImportError or ModuleNotFoundError when running the code

**Diagnosis**: Run the test script to check which packages are missing:

```bash
python test_imports.py
# or
python3 test_imports.py
```

**Solution**: Install all required dependencies:

```bash
pip install -r requirements.txt
# or
pip3 install -r requirements.txt
```

**Alternative** (if the above is slow or fails):

```bash
# Install core packages individually
pip install torch
pip install sentence-transformers
pip install transformers
pip install langchain
pip install chromadb
pip install PyMuPDF
pip install openai
pip install python-dotenv
pip install pandas numpy tqdm
```

---

## Issue 2: Python Version Compatibility

**Symptom**: Syntax errors or "feature not available" errors

**Diagnosis**: Check your Python version:

```bash
python --version
# or
python3 --version
```

**Requirement**: Python 3.8 or higher

**Solution**: If you have an older version, upgrade Python or use a virtual environment with the correct version.

---

## Issue 3: ChromaDB Version Compatibility

**Symptom**: Errors related to `chromadb.PersistentClient` or `Settings`

**Root Cause**: ChromaDB has had API changes between versions

**Solution**: The code is written for ChromaDB >= 0.4.0. If you have issues:

```bash
# Upgrade to latest
pip install --upgrade chromadb

# Or use specific version that's known to work
pip install chromadb==0.4.22
```

**Alternative Fix**: If the issue persists, update the VectorStore initialization in `src/indexing/vector_store.py`:

For older ChromaDB versions (< 0.4.0):
```python
# Replace line 36-42 with:
self.client = chromadb.Client(
    Settings(
        chroma_db_impl="duckdb+parquet",
        persist_directory=str(self.persist_directory),
        anonymized_telemetry=False
    )
)
```

---

## Issue 4: LangChain Import Errors

**Symptom**: `ImportError: cannot import name 'RecursiveCharacterTextSplitter'`

**Root Cause**: LangChain package structure changed in newer versions

**Solution**: Update the import in `src/data_preparation/text_chunker.py` line 8:

For LangChain >= 0.1.0:
```python
from langchain.text_splitter import RecursiveCharacterTextSplitter
```

For LangChain >= 0.2.0 (newer versions):
```python
from langchain_text_splitters import RecursiveCharacterTextSplitter
```

---

## Issue 5: OpenAI API Key Issues

**Symptom**: "OPENAI_API_KEY is not set" or authentication errors

**Diagnosis**: Verify your API key is loaded:

```bash
python -c "from config import Config; print('API Key:', 'SET' if Config.OPENAI_API_KEY else 'NOT SET')"
```

**Solutions**:

1. **Check .env file exists**:
   ```bash
   ls -la .env
   ```

2. **Verify .env format** (no quotes, no spaces around =):
   ```bash
   OPENAI_API_KEY=sk-proj-...
   ```

3. **Alternative**: Set environment variable directly:
   ```bash
   export OPENAI_API_KEY="your-key-here"
   python main.py
   ```

4. **Check API key validity**:
   - Go to https://platform.openai.com/api-keys
   - Verify the key is active
   - Create a new key if needed

---

## Issue 6: PDF Processing Errors

**Symptom**: "PDF file not found" or errors during extraction

**Solutions**:

1. **Verify PDF path**:
   ```bash
   ls -la Cellular_Manufacturing.pdf
   ```

2. **Update PDF_PATH in .env if needed**:
   ```bash
   PDF_PATH=/absolute/path/to/your/pdf.pdf
   ```

3. **Test PDF extraction directly**:
   ```bash
   python src/data_preparation/pdf_processor.py Cellular_Manufacturing.pdf
   ```

---

## Issue 7: Memory Issues

**Symptom**: Out of memory errors, system freezes

**Root Cause**: Loading large models + processing large PDFs

**Solutions**:

1. **Reduce batch size** in `config.py`:
   ```python
   BATCH_SIZE = 8  # Instead of 32
   ```

2. **Use CPU instead of GPU** (if GPU memory is limited):
   ```bash
   # In .env
   USE_GPU=false
   ```

3. **Increase chunk size to reduce total chunks**:
   ```bash
   # In .env
   CHUNK_SIZE=1200
   CHUNK_OVERLAP=200
   ```

4. **Close other applications** to free up RAM

---

## Issue 8: Slow Performance

**Symptom**: Indexing takes >10 minutes, queries take >10 seconds

**Solutions**:

1. **Enable GPU if available**:
   ```bash
   # In .env
   USE_GPU=true
   ```

2. **Check CUDA is working** (for GPU):
   ```python
   import torch
   print(torch.cuda.is_available())
   ```

3. **Use smaller embedding model** (faster but lower quality):
   ```bash
   # In .env - NOT recommended, but faster
   EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L12-v2
   ```

---

## Common Error Messages & Solutions

### Error: "No module named 'fitz'"

**Solution**:
```bash
pip install PyMuPDF
```

### Error: "No module named 'sentence_transformers'"

**Solution**:
```bash
pip install sentence-transformers
```

### Error: "chromadb.errors.ChromaError"

**Solutions**:
1. Delete existing ChromaDB and rebuild:
   ```bash
   rm -rf chroma_db/
   python main.py --rebuild-index
   ```

2. Update ChromaDB:
   ```bash
   pip install --upgrade chromadb
   ```

### Error: "openai.error.RateLimitError"

**Solutions**:
- You've exceeded OpenAI API rate limits
- Wait a few minutes and try again
- Upgrade your OpenAI account tier
- Reduce number of queries

### Error: "AssertionError: Torch not compiled with CUDA enabled"

**Solution**: Your PyTorch doesn't support GPU. Either:
1. Set `USE_GPU=false` in .env
2. Install GPU-enabled PyTorch from https://pytorch.org/get-started/locally/

---

## Step-by-Step Debugging

If the code still doesn't work, follow these steps:

### Step 1: Test Python Installation

```bash
python --version
# or
python3 --version
```

Expected: Python 3.8 or higher

### Step 2: Test Dependencies

```bash
python test_imports.py
```

All packages should show ✓. If any show ✗, install them:

```bash
pip install <missing-package>
```

### Step 3: Test Configuration

```bash
python -c "from config import Config; Config.validate(); Config.display()"
```

Should show configuration without errors.

### Step 4: Test Individual Components

```bash
# Test PDF processing
python src/data_preparation/pdf_processor.py Cellular_Manufacturing.pdf

# Test embedding
python src/indexing/embedder.py

# Test vector store
python src/indexing/vector_store.py

# Test retrieval
python src/retrieval/retriever.py

# Test generation (requires API key)
python src/generation/generator.py
```

### Step 5: Run Main Application

```bash
python main.py --config
```

Then:

```bash
python main.py --rebuild-index
```

---

## Quick Fixes

### Fix 1: Start Fresh

```bash
# Remove existing data
rm -rf chroma_db/
rm -rf data/processed/

# Reinstall dependencies
pip install --upgrade -r requirements.txt

# Rebuild index
python main.py --rebuild-index
```

### Fix 2: Use Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate it
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Run application
python main.py
```

### Fix 3: Simplify Configuration

Create a minimal `.env` file:

```bash
OPENAI_API_KEY=your-key-here
```

All other settings will use defaults.

---

## Code-Specific Issues

### Issue: "Collection doesn't exist" error

The code has been updated to handle this automatically. The error handler in `vector_store.py` line 49 catches `ValueError` when a collection doesn't exist and creates it.

**If you still see this**: Update `src/indexing/vector_store.py` line 49:

```python
except ValueError:  # Instead of generic except
```

### Issue: "Loaded existing collection: cellular_manufacturing (0 documents)"

This is **normal** on first run. The warning message tells you to run:

```bash
python main.py --rebuild-index
```

---

## Getting Help

If issues persist:

1. **Run diagnostic script**:
   ```bash
   python test_imports.py > diagnostic_output.txt 2>&1
   ```

2. **Check versions**:
   ```bash
   pip list | grep -E "(torch|transformers|langchain|chromadb|openai)"
   ```

3. **Check logs**: Look for error messages in the terminal output

4. **Simplify the test**: Try with a smaller PDF first

5. **Check system resources**:
   - RAM: Need at least 4GB free
   - Disk: Need at least 2GB free
   - CPU: Any modern processor works

---

## Expected Behavior

### First Run (Indexing)

```
Initializing RAG pipeline...
Loading embedding model: sentence-transformers/all-MiniLM-L6-v2
Using device: cpu
Embedding dimension: 384
✓ Created new collection: cellular_manufacturing

[1/4] Extracting text from PDF...
Extracting PDF pages: 100%|████| 195/195 [00:15<00:00]
✓ Extracted 195 pages

[2/4] Chunking text...
✓ Created 847 chunks

[3/4] Generating embeddings...
Batches: 100%|████| 27/27 [00:45<00:00]
✓ Generated 847 embeddings

[4/4] Storing in vector database...
✓ Successfully added 847 documents

INDEXING COMPLETE
Total documents: 847
Total time: 68.23 seconds
```

### Query

```
Your question: What is cellular manufacturing?

[1/2] Retrieving relevant documents...
✓ Retrieved 5 documents

[2/2] Generating answer...
✓ Answer generated

ANSWER
Cellular manufacturing is a production approach... [Page 15]

SOURCES (5 documents)
1. Page 15 (Similarity: 0.892)
...
```

---

## Still Not Working?

Create an issue with:
1. Output of `python test_imports.py`
2. Python version (`python --version`)
3. Operating system
4. Full error message
5. What you were trying to do

**Remember**: The most common issues are:
1. ❌ Dependencies not installed → `pip install -r requirements.txt`
2. ❌ Wrong Python version → Use Python 3.8+
3. ❌ Missing API key → Check `.env` file
4. ❌ Index not built → Run `python main.py --rebuild-index`
