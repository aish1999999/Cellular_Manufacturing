# RAG Pipeline Tuning Cheatsheet

## Quick Reference for Common Issues

### Issue: "I cannot find this information" (False Negatives)

**Cause:** Prompt too restrictive or poor chunk retrieval

**Fix:**
```bash
# In .env - Lower threshold, more chunks
SIMILARITY_THRESHOLD=0.60
TOP_K=10
LLM_TEMPERATURE=0.3
```

Already fixed in your system! ✅

---

### Issue: Answers Not Comprehensive Enough

**Fix:**
```bash
# In .env
LLM_MAX_TOKENS=1500      # Longer answers
TOP_K=10                 # More context
```

---

### Issue: Irrelevant Information in Answers (Hallucinations)

**Cause:** Threshold too low or temperature too high

**Fix:**
```bash
# In .env - Stricter retrieval
SIMILARITY_THRESHOLD=0.75
LLM_TEMPERATURE=0.0
TOP_K=5
```

---

### Issue: Slow Queries

**Fix:**
```bash
# In .env
TOP_K=3                  # Fewer chunks
USE_GPU=true            # If available
```

---

### Issue: Missing Relevant Information

**Cause:** Chunks too small or poor semantic search

**Fix:**
```bash
# In .env
CHUNK_SIZE=1500         # Larger chunks
CHUNK_OVERLAP=300       # More overlap
USE_MMR=true           # Diversity

# Then rebuild
python main.py --rebuild-index
```

---

### Issue: Redundant Information

**Fix:**
```bash
# In .env
USE_MMR=true           # Enables diversity
```

---

## Parameter Quick Reference

### SIMILARITY_THRESHOLD

| Value | Use Case | Result |
|-------|----------|--------|
| 0.50-0.60 | Broad questions | Many results, may be noisy |
| 0.65-0.70 | **General use** ✅ | Balanced |
| 0.75-0.85 | Precise questions | High quality, may miss some |

**Current:** 0.65 ✅

---

### TOP_K

| Value | Use Case |
|-------|----------|
| 3-5 | Simple, direct questions |
| 5-7 | **General use** ✅ |
| 10-15 | Complex, multi-faceted questions |

**Current:** 7 ✅

---

### LLM_TEMPERATURE

| Value | Behavior |
|-------|----------|
| 0.0 | Deterministic, factual |
| 0.1-0.3 | **Balanced** ✅ |
| 0.5-0.7 | Creative, exploratory |

**Current:** 0.2 ✅

---

### CHUNK_SIZE

| Value | Use Case | Note |
|-------|----------|------|
| 500-800 | Precise retrieval | More chunks, slower indexing |
| 800-1200 | **General use** ✅ | Balanced |
| 1500-2000 | Comprehensive context | Fewer chunks, faster indexing |
| >10000 | ❌ **DON'T USE** | Exceeds model limits |

**Your setting:** 85000 ⚠️ **TOO LARGE - Please change to 1200**

---

## Common Configurations

### Configuration 1: Precise & Factual ⚙️
```bash
SIMILARITY_THRESHOLD=0.75
TOP_K=5
LLM_TEMPERATURE=0.0
LLM_MAX_TOKENS=500
```

**Best for:** Direct factual questions, definitions

---

### Configuration 2: Balanced (Recommended) ⭐
```bash
SIMILARITY_THRESHOLD=0.65
TOP_K=7
LLM_TEMPERATURE=0.2
LLM_MAX_TOKENS=800
```

**Best for:** Most questions, general use
**Status:** ✅ Currently active

---

### Configuration 3: Comprehensive & Exploratory 🔍
```bash
SIMILARITY_THRESHOLD=0.60
TOP_K=10
LLM_TEMPERATURE=0.3
LLM_MAX_TOKENS=1500
USE_MMR=true
```

**Best for:** Complex questions requiring synthesis, "what if" questions

---

### Configuration 4: Fast & Efficient ⚡
```bash
SIMILARITY_THRESHOLD=0.70
TOP_K=3
LLM_TEMPERATURE=0.1
LLM_MAX_TOKENS=500
```

**Best for:** Quick lookups, high-volume querying

---

## Quick Commands

### Test Current Settings
```bash
python main.py --query "Your question" --verbose
```

### View Configuration
```bash
python main.py --config
```

### View Statistics
```bash
python main.py --stats
```

### Rebuild After Changing CHUNK_SIZE
```bash
python main.py --rebuild-index
```

---

## Recommended Fixes for Your Setup

### 1. Fix Chunk Size ⚠️ IMPORTANT

**Current:** `CHUNK_SIZE=85000` (way too large!)

**Change to:**
```bash
# In .env
CHUNK_SIZE=1200
CHUNK_OVERLAP=250
```

**Why:** 85,000 chars exceeds embedding model's capacity (256 tokens ≈ 1024 chars)

**Then:**
```bash
python main.py --rebuild-index
```

### 2. Optimize Max Tokens (Optional)

**Current:** `LLM_MAX_TOKENS=5000` (works but expensive)

**Consider:**
```bash
# In .env
LLM_MAX_TOKENS=1200
```

**Why:** Most answers don't need 5000 tokens, saves cost

---

## Troubleshooting Decision Tree

```
Is answer quality poor?
│
├─ Answer says "cannot find"?
│  ├─ Lower SIMILARITY_THRESHOLD (0.60)
│  ├─ Increase TOP_K (10)
│  └─ Check prompt (should encourage synthesis) ✅ Already fixed!
│
├─ Answer has hallucinations?
│  ├─ Raise SIMILARITY_THRESHOLD (0.75)
│  ├─ Lower LLM_TEMPERATURE (0.0)
│  └─ Decrease TOP_K (5)
│
├─ Answer too short?
│  └─ Increase LLM_MAX_TOKENS (1500)
│
├─ Answer too verbose?
│  └─ Decrease LLM_MAX_TOKENS (500)
│
├─ Missing relevant info?
│  ├─ Increase CHUNK_SIZE (1500)
│  ├─ Increase CHUNK_OVERLAP (300)
│  ├─ Enable USE_MMR (true)
│  └─ Rebuild index
│
└─ Too slow?
   ├─ Decrease TOP_K (3)
   ├─ Enable USE_GPU (true)
   └─ Decrease LLM_MAX_TOKENS (500)
```

---

## Embedding Model Comparison

| Model | Dimension | Speed | Quality | When to Use |
|-------|-----------|-------|---------|-------------|
| **all-MiniLM-L6-v2** ✅ | 384 | ⚡⚡⚡ | ⭐⭐⭐ | Current, good balance |
| BAAI/bge-base-en-v1.5 | 768 | ⚡⚡ | ⭐⭐⭐⭐ | Better quality |
| intfloat/e5-base-v2 | 768 | ⚡⚡ | ⭐⭐⭐⭐ | Q&A tasks |
| BAAI/bge-m3 | 1024 | ⚡ | ⭐⭐⭐⭐⭐ | Best quality |

**To change:**
```bash
# In .env
EMBEDDING_MODEL=BAAI/bge-base-en-v1.5

# Rebuild index
python main.py --rebuild-index
```

---

## Cost Optimization

### Per Query Cost (GPT-4o-mini)

| MAX_TOKENS | Cost/Query | Use Case |
|------------|------------|----------|
| 500 | ~$0.001 | Quick answers |
| 800 | ~$0.0015 | **General** ✅ |
| 1500 | ~$0.003 | Comprehensive |
| 5000 | ~$0.01 | ⚠️ Expensive |

**Your current:** 5000 tokens = ~$0.01 per query

**Recommended:** 1200 tokens = ~$0.002 per query (5x cheaper!)

---

## Testing Checklist

After any configuration change:

- [ ] Test simple question: "What is cellular manufacturing?"
- [ ] Test complex question: "What are best practices for..."
- [ ] Test synthesis question: "How do X and Y work together?"
- [ ] Check page citations are accurate
- [ ] Verify no hallucinations
- [ ] Monitor query speed
- [ ] Check answer comprehensiveness

---

## Emergency Reset

If everything breaks:

```bash
# Reset to known-good configuration
cat > .env << 'EOF'
OPENAI_API_KEY=your-key-here
LLM_MODEL=gpt-4o-mini
LLM_MAX_TOKENS=800
LLM_TEMPERATURE=0.2
TOP_K=7
SIMILARITY_THRESHOLD=0.65
CHUNK_SIZE=1200
CHUNK_OVERLAP=250
USE_MMR=false
EOF

# Rebuild
python main.py --rebuild-index

# Test
python main.py --query "What is cellular manufacturing?"
```

---

## Pro Tips 💡

1. **Start conservative, then relax**
   - High threshold (0.75) → Lower gradually (0.65, 0.60)
   - Small TOP_K (3) → Increase gradually (5, 7, 10)

2. **Enable verbose mode for debugging**
   ```bash
   python main.py --query "..." --verbose
   ```

3. **Monitor similarity scores**
   - >0.8: Excellent match
   - 0.65-0.8: Good match
   - 0.5-0.65: Marginal
   - <0.5: Poor match

4. **Chunk size rule of thumb**
   - Embedding model max tokens × 4 = max chunk size
   - MiniLM: 256 tokens × 4 = ~1024 chars ≈ **1200 is good** ✅

5. **When in doubt, use defaults**
   - The optimized settings (0.65 threshold, 7 chunks, etc.) work for most cases

---

**Quick Start:** Your system is already optimized! Just fix `CHUNK_SIZE=1200` and rebuild. 🚀
