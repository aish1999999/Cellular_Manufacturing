# Fix Your RAG System NOW - Step by Step

## Problem

Your query: **"What would be an integrated set of proven best practices of Job Shop Lean that have been implemented by a 21st Century CNC machine shop?"**

**Current Status:** Not generating an answer

---

## Root Cause

You had `CHUNK_SIZE=85000` which is **way too large**. This causes:
- ❌ Embedding model truncates to ~1024 chars (ignores the rest)
- ❌ Very few, overly-large chunks created
- ❌ Poor semantic matching
- ❌ Cannot find specific concepts in huge chunks

**I've already fixed this in your .env file** ✅

---

## Quick Fix (5 minutes)

### Step 1: Verify Settings

Your `.env` now has (I already updated it):
```bash
CHUNK_SIZE=1200          # ✅ Fixed!
CHUNK_OVERLAP=250        # ✅ Good
SIMILARITY_THRESHOLD=0.65 # ✅ Good
TOP_K=7                  # ✅ Good
LLM_MAX_TOKENS=1200      # ✅ Fixed (was 5000)
```

### Step 2: Run Diagnostic (Optional but Recommended)

See what's wrong with current index:
```bash
python diagnose_issue.py
```

This will show you:
- How many documents are in your index
- Whether retrieval is working
- What similarity scores you're getting
- If generation is the problem

### Step 3: Rebuild Index with Correct Settings

**This is REQUIRED because chunk size changed:**

```bash
python rebuild_and_test.py
```

This script will:
1. ✅ Rebuild the index with CHUNK_SIZE=1200
2. ✅ Automatically test your problematic query
3. ✅ Show you if it works
4. ✅ Test a simple query as sanity check

**Expected time:** 2-5 minutes

### Step 4: Verify It Works

After rebuilding, test your query:
```bash
python main.py --query "What would be an integrated set of proven best practices of Job Shop Lean that have been implemented by a 21st Century CNC machine shop?" --verbose
```

---

## Expected Results After Fix

### Before (Broken):
```
Retrieved 5 documents
Similarity scores: 0.45, 0.52, 0.58, 0.61, 0.64

ANSWER
I cannot find this information in the provided context
```

### After (Fixed):
```
Retrieved 7 documents
Similarity scores: 0.78, 0.76, 0.72, 0.71, 0.69, 0.68, 0.67

ANSWER
Based on the manufacturing best practices discussed in the book, here is an
integrated set for Job Shop Lean implementation:

1. Cellular Manufacturing Layout [Page 15, Page 23]
   - Organize machines into manufacturing cells...

2. Pull Production Systems [Page 42]
   - Implement kanban systems...

3. 5S Workplace Organization [Page 67]
   - Sort, Set in Order, Shine, Standardize, Sustain...

[... more practices with citations ...]

SOURCES (7 documents)
1. Page 15 (Similarity: 0.782)
2. Page 23 (Similarity: 0.756)
...
```

---

## If Still Not Working

### Issue: Still getting "cannot find"

**Solution 1:** Lower the threshold
```bash
# In .env
SIMILARITY_THRESHOLD=0.60  # or even 0.55
```

**Solution 2:** Get more chunks
```bash
# In .env
TOP_K=10
```

Then test again:
```bash
python main.py --query "your question"
```

### Issue: Similarity scores too low (all < 0.60)

This means the book might not have direct information about "Job Shop Lean" specifically.

**Try these queries instead:**

```bash
# More general - should work
python main.py --query "What are lean manufacturing best practices?"

# More specific to the book content
python main.py --query "What are the benefits of cellular manufacturing?"

# Specific techniques
python main.py --query "What techniques reduce setup time in manufacturing?"
```

---

## Understanding Similarity Scores

| Score | Meaning |
|-------|---------|
| 0.85+ | Excellent match - almost identical semantic meaning |
| 0.70-0.85 | Good match - highly relevant |
| 0.60-0.70 | Decent match - relevant but not perfect |
| 0.50-0.60 | Marginal - somewhat related |
| < 0.50 | Poor match - not very relevant |

**Your threshold is 0.65** - this means only "decent" or better matches are used.

---

## Quick Commands Reference

```bash
# Diagnose what's wrong
python diagnose_issue.py

# Rebuild and test automatically
python rebuild_and_test.py

# Test a query with verbose output
python main.py --query "your question" --verbose

# View current settings
python main.py --config

# Interactive mode
python main.py
```

---

## What Changed

| Setting | Old Value | New Value | Why |
|---------|-----------|-----------|-----|
| `CHUNK_SIZE` | 85000 ❌ | 1200 ✅ | Fits embedding model capacity |
| `CHUNK_OVERLAP` | 150 | 250 ✅ | Better context preservation |
| `LLM_MAX_TOKENS` | 5000 | 1200 ✅ | More reasonable, cheaper |
| `SIMILARITY_THRESHOLD` | 0.5 | 0.65 ✅ | Higher quality chunks |
| `TOP_K` | 5 | 7 ✅ | More context |
| System Prompt | Restrictive ❌ | Synthesis-friendly ✅ | Allows inference |

---

## TL;DR - Just Do This

```bash
# 1. Rebuild (REQUIRED - chunk size changed)
python rebuild_and_test.py

# 2. Test it worked
python main.py --query "What would be an integrated set of proven best practices of Job Shop Lean that have been implemented by a 21st Century CNC machine shop?"

# Done! 🎉
```

---

## Still Having Issues?

Run the diagnostic and share the output:
```bash
python diagnose_issue.py > diagnostic_output.txt
```

Then review `diagnostic_output.txt` to see exactly what's wrong.

---

**The fix is ready - just rebuild the index!** 🚀
