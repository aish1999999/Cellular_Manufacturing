# RAG Pipeline Diagnostic Guide

## Current Situation

Your RAG pipeline is returning "I cannot find relevant information" because the ChromaDB vector database appears to be **empty or not properly loaded**.

### Files Status
✓ **PDF exists**: `Cellular_Manufacturing.pdf` (200+ pages)
✓ **Chunks exist**: `data/processed/chunks.json` (contains chunked text)
✓ **ChromaDB files exist**: `chroma_db/` directory with database files
✗ **Problem**: ChromaDB collection is either empty or misnamed

---

## Root Cause Analysis

Based on the evidence:

1. **Fast query time (49ms)**: Searching an empty database is instant
2. **No context retrieved**: The retriever finds 0 documents
3. **Collection mismatch**: ChromaDB has a UUID-based collection (`353132f3-a61e-4c46-ae2c-6f31c71e2422`) but your code expects a collection named `cellular_manufacturing`

### Why This Happened

The original code had a **bare `except:` clause** that silently failed when trying to load the collection. Instead of loading the existing collection, it created a new empty one.

---

## Solution Steps

### Step 1: Verify Python Environment

First, ensure you have the required packages installed:

```bash
# Check if you're using a virtual environment
which python3
# or
which python

# Install dependencies if not already installed
pip install -r requirements.txt
# or
pip3 install -r requirements.txt
```

If you don't have a virtual environment set up:

```bash
# Create virtual environment
python3 -m venv venv

# Activate it (macOS/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Check Database Status

Run the diagnostic script I created:

```bash
python check_db_status.py
# or
python3 check_db_status.py
```

This will tell you:
- If ChromaDB directory exists ✓
- How many collections exist
- How many documents are in each collection
- Sample content from the database

### Step 3: Rebuild the Index

The **safest and most reliable solution** is to rebuild the index from scratch:

```bash
python main.py --rebuild-index
# or
python3 main.py --rebuild-index
```

This will:
1. Delete the old collection (if it exists)
2. Extract text from `Cellular_Manufacturing.pdf`
3. Create chunks (should create ~1000 chunks based on your existing chunks.json)
4. Generate embeddings using sentence-transformers
5. Store everything in ChromaDB with the correct collection name
6. Take approximately 2-5 minutes

**Expected output:**
```
============================================================
INDEXING PHASE
============================================================

[1/4] Extracting text from PDF...
✓ Extracted 200+ pages

[2/4] Chunking text...
✓ Created ~1000 chunks

[3/4] Generating embeddings...
✓ Generated ~1000 embeddings

[4/4] Storing in vector database...
✓ Successfully added ~1000 documents

============================================================
INDEXING COMPLETE
============================================================
Total documents: 1000+
Total time: 2-5 minutes
============================================================
```

### Step 4: Verify the Fix

After rebuilding, check the stats:

```bash
python main.py --stats
```

You should see:
```
total_documents: 1000+ (not 0!)
```

### Step 5: Test Your Query

Now try your query again:

```bash
python main.py --query "Is cell scheduling effective enough such that no operator is ever without a job to work on?" --verbose
```

**Expected results:**
- Query time: **1-3 seconds** (not 49ms!)
- Retrieved documents: **3-5 chunks**
- Answer: **Properly cited response with page numbers**

---

## Alternative: Manual Database Inspection

If you want to verify the database state without Python, you can check the SQLite database:

```bash
# Install sqlite3 if not available
brew install sqlite3  # macOS

# Open the database
sqlite3 chroma_db/chroma.sqlite3

# Run SQL commands
.tables
SELECT COUNT(*) FROM collections;
SELECT * FROM collections;
.quit
```

---

## Common Issues & Solutions

### Issue 1: "ModuleNotFoundError: No module named 'chromadb'"

**Solution**: Install dependencies
```bash
pip install -r requirements.txt
```

### Issue 2: "PDF file not found"

**Solution**: Verify PDF path in `.env` file matches actual location
```bash
# Your .env should have:
PDF_PATH=./Cellular_Manufacturing.pdf
```

### Issue 3: "OpenAI API key not set"

**Solution**: Already fixed - `.env` file now exists with your API key

⚠️ **Security Note**: Your API key in `.env.example` is exposed. You should:
1. Rotate your OpenAI API key at https://platform.openai.com/api-keys
2. Update the new key in `.env`
3. Never commit `.env` to git (already in `.gitignore`)

### Issue 4: Workplace restrictions preventing file access

If you genuinely cannot access ChromaDB files due to workplace restrictions:

**Option A**: Run the rebuild index command - this will create fresh files
```bash
python main.py --rebuild-index
```

**Option B**: Check if antivirus/security software is blocking ChromaDB
- Add `chroma_db/` directory to exclusions
- Or run the script with appropriate permissions

**Option C**: Use an alternative vector database (requires code changes)
- Could switch to FAISS, Pinecone, or Weaviate
- But ChromaDB should work fine for local development

---

## Files Modified (Already Done)

I've already made these improvements to your code:

### 1. `src/indexing/vector_store.py` (lines 44-55)
- ✓ Replaced bare `except:` with specific `ValueError`
- ✓ Added document count logging
- ✓ Better error messages

### 2. `src/rag_pipeline.py` (lines 51-55)
- ✓ Added validation check after vector store init
- ✓ Warns if collection is empty
- ✓ Shows clear action needed

### 3. `config.py` (line 42)
- ✓ Lowered similarity threshold from 0.7 to 0.5
- ✓ Better recall for queries

### 4. `.env` (line 21)
- ✓ Updated threshold to match config

---

## Next Action Required

**YOU MUST RUN THIS COMMAND:**

```bash
python main.py --rebuild-index
```

Or if using Python 3 explicitly:

```bash
python3 main.py --rebuild-index
```

This is **not optional** - your database is currently empty or misconfigured, and this will fix it.

After running this, your RAG pipeline will work correctly and you'll get proper answers with citations.

---

## Questions?

If you encounter any errors while running the rebuild command, please share:
1. The complete error message
2. The output from `python --version` or `python3 --version`
3. Whether you're using a virtual environment
4. Any antivirus/security software that might be blocking file access

I'm here to help debug any issues that come up!
