# Prompt Optimization Guide

## Issue Identified

Your query: **"What would be an integrated set of proven best practices of Job Shop Lean that have been implemented by a 21st Century CNC machine shop?"**

**Problem**: The system retrieved 5 relevant sources but returned "I cannot find this information in the provided context"

## Root Causes

### 1. **Overly Restrictive System Prompt** ❌
The original prompt was too conservative:
- Required EXACT answers in the context
- Discouraged synthesis and inference
- Too quick to say "I cannot find this information"

### 2. **Low Similarity Threshold** ⚠️
- Was set to 0.5 (too permissive)
- Retrieved somewhat relevant but not highly relevant chunks
- Led to noisy context that confused the LLM

### 3. **Limited Output Tokens** 🔒
- Max tokens was 500
- Not enough for comprehensive answers to complex questions

## Changes Made ✅

### 1. **Updated System Prompt** (in `config.py`)

**Before:**
```python
SYSTEM_PROMPT = """You are an expert assistant specializing in cellular manufacturing...
Guidelines:
1. Answer questions using only information from the provided context
2. Always cite page numbers...
3. If the answer cannot be found in the context, clearly state that
...
```

**After:**
```python
SYSTEM_PROMPT = """You are an expert assistant specializing in cellular manufacturing,
lean manufacturing, and production systems.

Guidelines:
1. Use ONLY information from the provided context passages to construct your answer
2. Always cite page numbers when referencing specific information using the format [Page X]
3. If the context contains related or relevant information, synthesize it to answer the question
4. If you can infer or derive an answer from the context, do so and cite the relevant pages
5. Only say "I cannot find this information" if the context has NO relevant information at all
6. When multiple pages discuss related concepts, integrate them into a coherent answer
7. Be precise, concise, and technical when appropriate
```

**Key Improvements:**
- ✅ Added "lean manufacturing" to expertise
- ✅ Encourages synthesis across multiple passages
- ✅ Allows inference from context
- ✅ Only rejects when NO relevant information exists
- ✅ Promotes integration of related concepts

### 2. **Updated User Prompt Template**

**Before:**
```python
Instructions:
- Answer the question based solely on the context above
- Cite specific page numbers for all information using [Page X] format
- If the answer is not in the context, say "I cannot find this information in the provided context"
- Be concise but complete in your answer
```

**After:**
```python
Instructions:
- Carefully read all the context passages above
- Answer the question using information from the context
- Synthesize information from multiple passages if needed
- Always cite page numbers using [Page X] format for all information used
- If the context contains related information but doesn't directly answer the question,
  explain what the context does say that's relevant
- Only say "I cannot find this information in the provided context" if NONE of the
  passages are relevant to the question
- Provide a complete, well-structured answer
```

**Key Improvements:**
- ✅ Explicitly asks to synthesize from multiple passages
- ✅ Handles partial matches (related but not exact)
- ✅ More lenient rejection criteria
- ✅ Encourages comprehensive answers

### 3. **Optimized Retrieval Parameters**

**Configuration Changes:**

| Parameter | Before | After | Reason |
|-----------|--------|-------|--------|
| `TOP_K` | 5 | 7 | Get more context for complex questions |
| `SIMILARITY_THRESHOLD` | 0.5 | 0.65 | Higher quality, more relevant chunks |
| `LLM_MAX_TOKENS` | 500 | 800 (user set 5000) | Allow longer, more detailed answers |
| `LLM_TEMPERATURE` | 0.1 | 0.2 | Slightly more creative synthesis |

**Note:** You've set `LLM_MAX_TOKENS=5000` and `CHUNK_SIZE=85000` in your `.env` - these are valid but may be excessive. See recommendations below.

## How This Fixes Your Issue

### Before:
1. Retrieved 5 somewhat relevant chunks (threshold too low)
2. LLM saw the question about "Job Shop Lean best practices"
3. Context didn't have EXACT answer to that specific phrasing
4. Conservative prompt → "I cannot find this information"

### After:
1. Retrieves 7 more relevant chunks (higher threshold)
2. LLM sees related information about lean manufacturing, cellular manufacturing, best practices
3. New prompt encourages synthesis: "If context contains related information, synthesize it"
4. LLM combines information from multiple passages
5. Generates comprehensive answer with citations

## Additional Optimization Options

### Option 1: Enable MMR (Maximal Marginal Relevance)

Add to `.env`:
```bash
USE_MMR=true
```

**Benefits:**
- Reduces redundancy in retrieved chunks
- Increases diversity of information
- Better coverage of different aspects

### Option 2: Increase Chunk Size (You've Already Done This!)

You've set:
```bash
CHUNK_SIZE=85000  # Very large!
CHUNK_OVERLAP=150
```

**Note:** 85,000 characters is extremely large for a chunk. This might cause issues:
- ⚠️ May exceed embedding model's max sequence length (256 tokens for MiniLM)
- ⚠️ LLM context window might struggle with such large chunks
- ⚠️ Reduced granularity in retrieval

**Recommended values:**
```bash
CHUNK_SIZE=1200        # Slightly larger for more context
CHUNK_OVERLAP=200      # More overlap to preserve context
```

**Or for very comprehensive chunks:**
```bash
CHUNK_SIZE=2000
CHUNK_OVERLAP=400
```

But **85,000 is too large** - the embedding model will truncate it anyway.

### Option 3: Hybrid Search

For questions that use specific terminology (like "Job Shop Lean"), enable hybrid search in the retriever:

```python
# In your query
response = rag.query(
    "What would be an integrated set of proven best practices...",
    use_mmr=True,  # Enable MMR
    top_k=10       # Get even more chunks
)
```

### Option 4: Adjust Temperature

For questions requiring more synthesis and creativity:

```bash
# In .env
LLM_TEMPERATURE=0.3  # More creative (you have 0.2, which is good)
```

For factual, precise answers:
```bash
LLM_TEMPERATURE=0.0  # Most deterministic
```

## Testing the Improvements

### Test Your Original Query Again:

```bash
python main.py --query "What would be an integrated set of proven best practices of Job Shop Lean that have been implemented by a 21st Century CNC machine shop?" --verbose
```

**Expected Behavior:**
- ✅ Retrieves 7 relevant chunks about lean manufacturing, cellular manufacturing, best practices
- ✅ LLM synthesizes information from multiple pages
- ✅ Provides comprehensive answer citing [Page X], [Page Y], etc.
- ✅ Even if exact phrase "Job Shop Lean" isn't in the book, explains related concepts

### Sample Expected Output:

```
ANSWER
Based on the context, here are best practices for lean manufacturing in machine shops:

1. **Cellular Manufacturing Layout**: Organize machines into cells for part families [Page 15]
2. **Pull System Implementation**: Use kanban systems to reduce inventory [Page 42]
3. **5S Workplace Organization**: Implement sort, set in order, shine, standardize, sustain [Page 67]
4. **Setup Time Reduction**: Apply SMED (Single-Minute Exchange of Die) techniques [Page 89]
...

SOURCES (7 documents)
1. Page 15 (Similarity: 0.782)
2. Page 42 (Similarity: 0.756)
...
```

## Monitoring Answer Quality

### Good Signs ✅:
- Answers cite multiple pages
- Information is synthesized coherently
- Cites specific concepts from the book
- Acknowledges when making inferences

### Warning Signs ⚠️:
- Answers are too generic
- No page citations
- Information seems to contradict the book
- Hallucinating facts not in context

### If Answers Are Still Not Good Enough:

1. **Increase TOP_K further:**
   ```bash
   TOP_K=10  # Get more context
   ```

2. **Lower similarity threshold slightly:**
   ```bash
   SIMILARITY_THRESHOLD=0.55  # More permissive
   ```

3. **Use a better embedding model:**
   ```bash
   EMBEDDING_MODEL=BAAI/bge-base-en-v1.5  # Better semantic understanding
   ```
   Then rebuild index: `python main.py --rebuild-index`

4. **Increase max tokens for longer answers:**
   ```bash
   LLM_MAX_TOKENS=1500  # Currently you have 5000, which is fine
   ```

## Advanced: Custom Prompt for Specific Questions

For specific question types, you can create custom prompts. Add to `config.py`:

```python
# Specialized prompt for "best practices" questions
BEST_PRACTICES_PROMPT = """You are an expert in lean manufacturing and cellular manufacturing.

The user is asking about best practices. Your task:
1. Extract all relevant practices, techniques, and recommendations from the context
2. Organize them into a clear, structured list
3. Cite the page number for each practice
4. If practices are mentioned across multiple pages, synthesize them
5. Group related practices together under logical categories

Even if the exact terminology differs from the question, extract any relevant practices.
"""
```

Then use it conditionally based on question keywords.

## Recommended Final Configuration

Based on your use case, here's the optimal configuration:

```bash
# .env
LLM_MODEL=gpt-4o-mini
LLM_MAX_TOKENS=1500          # Comprehensive but not excessive
LLM_TEMPERATURE=0.2          # Good balance

TOP_K=7                      # Good coverage
SIMILARITY_THRESHOLD=0.65    # High quality chunks
USE_MMR=true                 # Diversity in retrieval

CHUNK_SIZE=1200              # Not too large, not too small
CHUNK_OVERLAP=250            # Good context preservation
```

**Note:** You'll need to rebuild the index if you change `CHUNK_SIZE`:
```bash
python main.py --rebuild-index
```

## Summary

### What Was Fixed:
1. ✅ **Prompt is now synthesis-friendly** - encourages combining information
2. ✅ **Higher similarity threshold** - better quality chunks
3. ✅ **More retrieval chunks** - more context to work with
4. ✅ **Longer max tokens** - comprehensive answers
5. ✅ **Added lean manufacturing expertise** - better domain coverage

### Expected Results:
- 🎯 Better answers to questions that require synthesis
- 🎯 More comprehensive responses citing multiple sources
- 🎯 Fewer false negatives ("I cannot find...")
- 🎯 Still grounded in the actual book content

### Try It Now:
```bash
python main.py --query "What would be an integrated set of proven best practices of Job Shop Lean that have been implemented by a 21st Century CNC machine shop?"
```

The system should now provide a much better answer! 🚀
