# Quick Start Guide - Self-Learning QA Framework

Get started with the self-learning framework in 5 minutes!

## What Does This Do?

This framework automatically:
1. ✅ Generates questions from your PDF
2. ✅ Answers those questions using AI
3. ✅ Evaluates how good the answers are
4. ✅ Suggests improvements to make answers better
5. ✅ Repeats until the system "learns" your entire document

## Prerequisites

- Python 3.8 or higher
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))
- A PDF document to learn from

## Setup (2 minutes)

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure API Key

Create a `.env` file:

```bash
# Create .env file
echo "OPENAI_API_KEY=your_api_key_here" > .env
```

Replace `your_api_key_here` with your actual OpenAI API key.

### 3. Verify Setup

```bash
python -c "from config import Config; Config.validate(); print('✓ Setup complete!')"
```

## Run Your First Learning Cycle (3 minutes)

### Option 1: Quick Test (Recommended for First Time)

Test with just the first 5 pages:

```bash
python run_self_learning.py --max-pages 5 --questions-per-page 2 --iterations 1
```

**What happens:**
- Processes first 5 pages of your PDF
- Generates 2 questions per page (10 total)
- Runs 1 learning iteration
- Takes ~2-3 minutes
- Costs ~$0.50

### Option 2: Full Run

Run on the entire document:

```bash
python run_self_learning.py --iterations 3
```

**What happens:**
- Processes entire PDF
- Generates 3 questions per page
- Runs 3 learning iterations
- Takes ~10-30 minutes (depends on PDF size)
- Costs ~$5-10 for a 50-page document

### Option 3: Custom PDF

Use your own PDF:

```bash
python run_self_learning.py --pdf /path/to/your/document.pdf --max-pages 10
```

## Understanding the Output

The framework creates an output directory with results:

```
experiments/self_learning/
├── generated_questions.json      # All questions generated
├── qa_results_iter1.json         # Answers from iteration 1
├── improvements_iter1.txt        # Suggested improvements
└── final_learning_report.txt     # Comprehensive final report
```

### Key Files to Check

**1. Final Report** (`final_learning_report.txt`)
- Overall performance progression
- Improvement metrics
- Final recommendations

**2. Improvement Suggestions** (`improvements_iter1.txt`)
- Specific parameter changes to try
- Actionable recommendations
- Priority rankings

**3. Generated Questions** (`generated_questions.json`)
- All questions created
- Question types (factual, conceptual, analytical)
- Coverage information

## Reading the Results

### Performance Scores

Each answer gets a **composite score** out of 10:

- **8-10**: Excellent answer
- **6-8**: Good answer with minor issues
- **4-6**: Acceptable but needs improvement
- **0-4**: Poor answer, needs significant work

### Example Output

```
ITERATION 1 SUMMARY
=========================================
Performance Scores:
  Composite Score: 7.2/10
  Accuracy:        7.8/10
  Completeness:    6.9/10
  Relevance:       8.1/10

Top Priority Actions:
  1. Increase TOP_K from 5 to 8
  2. Address common weakness: incomplete context
  3. Reduce SIMILARITY_THRESHOLD to 0.60
```

## Common Use Cases

### 1. Learn a Technical Manual

```bash
python run_self_learning.py \
  --pdf technical_manual.pdf \
  --questions-per-page 4 \
  --iterations 3
```

### 2. Study a Textbook Chapter

```bash
python run_self_learning.py \
  --pdf textbook.pdf \
  --max-pages 20 \
  --questions-per-page 5
```

### 3. Quick Quality Check

```bash
python run_self_learning.py \
  --max-pages 3 \
  --questions-per-page 1 \
  --iterations 1
```

## Next Steps

After your first run:

1. **Review the final report** to understand performance
2. **Check improvement suggestions** for optimization ideas
3. **Run with more iterations** to see improvement over time
4. **Try `--apply-improvements`** to automatically apply suggestions

## Troubleshooting

### "OPENAI_API_KEY is not set"
→ Create `.env` file with your API key

### "PDF file not found"
→ Use `--pdf path/to/file.pdf` to specify correct path

### "Out of memory"
→ Use `--max-pages 10` to limit processing

### Taking too long?
→ Reduce `--questions-per-page` or use `--max-pages`

## Cost Management

To keep costs low while learning:

1. **Start small**: Use `--max-pages 5` first
2. **Fewer questions**: Use `--questions-per-page 2`
3. **Single iteration**: Use `--iterations 1` for testing

## Advanced Options

Once comfortable, explore these options:

```bash
# Apply improvements automatically between iterations
python run_self_learning.py --iterations 5 --apply-improvements

# Use a different model
python run_self_learning.py --model gpt-4

# Custom output directory
python run_self_learning.py --output-dir my_experiment

# Verbose output for debugging
python run_self_learning.py --verbose
```

## Getting Help

```bash
# See all available options
python run_self_learning.py --help

# Check configuration
python -c "from config import Config; Config.display()"
```

## Full Documentation

For detailed information, see:
- [SELF_LEARNING_README.md](SELF_LEARNING_README.md) - Complete documentation
- [README.md](README.md) - RAG Pipeline documentation

## Example Workflow

Here's a complete example workflow:

```bash
# 1. Quick test (5 pages)
python run_self_learning.py --max-pages 5 --iterations 1

# 2. Review results
cat experiments/self_learning/final_learning_report.txt

# 3. If satisfied, run full learning
python run_self_learning.py --iterations 3

# 4. Check improvement suggestions
cat experiments/self_learning/improvements_iter3.txt

# 5. Apply suggestions and run again
python run_self_learning.py --iterations 3 --apply-improvements
```

## Success Indicators

You'll know it's working when you see:
- ✓ Questions being generated from PDF
- ✓ Each question being answered
- ✓ Evaluation scores for each answer
- ✓ Improvement suggestions at the end
- ✓ Final report with performance metrics

## What's Next?

The framework provides detailed suggestions for improving performance. Common improvements include:
- Adjusting retrieval parameters (TOP_K, SIMILARITY_THRESHOLD)
- Tuning chunking parameters (CHUNK_SIZE)
- Modifying LLM parameters (TEMPERATURE)

These suggestions are automatically generated based on your specific results!

---

**Ready to start learning? Run the quick test command above!** 🚀
