# Self-Learning QA Framework

A comprehensive framework for autonomous question generation, answering, evaluation, and continuous improvement. The system learns from a PDF document by generating questions, answering them, evaluating its own performance, and suggesting improvements.

## Overview

This framework implements a complete self-supervised learning cycle:

1. **Question Generation**: Automatically generates diverse questions from PDF content
2. **Query & Answer**: Uses a RAG (Retrieval-Augmented Generation) pipeline to answer questions
3. **Accuracy Evaluation**: Evaluates answer quality across multiple dimensions
4. **Improvement Suggestions**: Analyzes results and suggests specific improvements
5. **Iterative Learning**: Repeats the cycle, optionally applying improvements

## Features

### Question Generation
- Extracts text from PDF documents
- Generates diverse question types (factual, conceptual, analytical)
- Tracks content coverage across pages
- Ensures comprehensive document understanding

### Query & Answer
- Integrates with RAG pipeline for semantic search
- Records Q&A pairs with metadata
- Supports batch processing
- Tracks performance metrics

### Accuracy Evaluation
- Multi-dimensional scoring (accuracy, completeness, relevance, clarity)
- LLM-based evaluation with detailed feedback
- Citation quality assessment
- Identifies weak areas and common issues

### Improvement Suggestions
- Analyzes patterns in weaknesses
- Suggests parameter tuning (chunk size, top-k, temperature, etc.)
- Provides actionable recommendations
- Prioritizes improvements by impact

### Learning Loop
- Orchestrates complete cycle
- Tracks progress across iterations
- Generates comprehensive reports
- Supports adaptive parameter tuning

## Quick Start

### Prerequisites

- Python 3.8+
- OpenAI API key
- PDF document to learn from

### Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment:
```bash
# Copy example env file
cp .env.example .env

# Edit .env and add your OpenAI API key
OPENAI_API_KEY=your_key_here
```

3. Place your PDF in the project directory or specify path

### Basic Usage

Run with default settings (uses PDF from config.py):
```bash
python run_self_learning.py
```

Specify a PDF and number of iterations:
```bash
python run_self_learning.py --pdf my_book.pdf --iterations 5
```

Process first 10 pages with 5 questions per page:
```bash
python run_self_learning.py --max-pages 10 --questions-per-page 5
```

## Command Line Options

```
Usage: python run_self_learning.py [options]

PDF and Question Generation:
  --pdf PATH                    Path to PDF document
  --questions-per-page N        Questions to generate per page (default: 3)
  --max-pages N                 Maximum pages to process (default: all)
  --use-existing-questions PATH Use existing questions file

Learning Loop:
  --iterations N                Number of learning iterations (default: 3)
  --apply-improvements          Apply suggested improvements between iterations

Output:
  --output-dir PATH            Output directory (default: experiments/self_learning)

Model:
  --model NAME                 LLM model to use (default: gpt-4o-mini)

Advanced:
  --rebuild-index              Force rebuild of vector index
  --verbose                    Show detailed output
```

## Usage Examples

### Example 1: Learn from a Technical Manual

```bash
python run_self_learning.py \
  --pdf technical_manual.pdf \
  --questions-per-page 4 \
  --iterations 3 \
  --output-dir experiments/manual_learning
```

### Example 2: Quick Test on First Few Pages

```bash
python run_self_learning.py \
  --pdf my_book.pdf \
  --max-pages 5 \
  --questions-per-page 2 \
  --iterations 1
```

### Example 3: Full Learning with Improvements

```bash
python run_self_learning.py \
  --pdf textbook.pdf \
  --questions-per-page 5 \
  --iterations 5 \
  --apply-improvements \
  --verbose
```

### Example 4: Use Pre-Generated Questions

```bash
# First, generate questions
python -m src.self_learning.question_generator my_book.pdf

# Then run learning with those questions
python run_self_learning.py \
  --use-existing-questions data/evaluation/generated_questions.json \
  --iterations 3
```

## Architecture

### Module Structure

```
src/
├── self_learning/
│   ├── question_generator.py      # Generates questions from PDF
│   ├── query_answerer.py          # Queries RAG system
│   ├── accuracy_evaluator.py      # Evaluates answer quality
│   ├── improvement_suggester.py   # Suggests improvements
│   └── learning_loop.py            # Orchestrates the cycle
├── rag_pipeline.py                 # RAG pipeline implementation
└── ...
```

### Data Flow

```
PDF Document
    ↓
[Question Generator] → Questions (JSON)
    ↓
[Query Answerer] → Q&A Pairs (JSON)
    ↓
[Accuracy Evaluator] → Evaluation Results (JSON)
    ↓
[Improvement Suggester] → Improvement Suggestions (JSON)
    ↓
[Learning Loop] → Final Report (TXT)
```

## Output Files

The framework generates several output files in the output directory:

```
experiments/self_learning/
├── generated_questions.json           # Generated questions
├── qa_results_iter1.json             # Q&A results for iteration 1
├── qa_results_iter2.json             # Q&A results for iteration 2
├── iteration_1_summary.json          # Summary of iteration 1
├── iteration_2_summary.json          # Summary of iteration 2
├── improvements_iter1.txt            # Improvement suggestions (iteration 1)
├── improvements_iter2.txt            # Improvement suggestions (iteration 2)
└── final_learning_report.txt         # Comprehensive final report
```

## Understanding the Results

### Evaluation Scores

Each answer is scored on four dimensions (0-10):

- **Accuracy**: Factual correctness of the answer
- **Completeness**: How fully the question is answered
- **Relevance**: How relevant the answer is to the question
- **Clarity**: How clear and well-structured the answer is

A **composite score** combines these dimensions with weights:
- Accuracy: 35%
- Completeness: 25%
- Relevance: 20%
- Clarity: 15%
- Citation Quality: 5%

### Final Report

The final report includes:
- Performance progression across iterations
- Overall improvement metrics
- Priority recommendations for further improvement
- Detailed statistics for each iteration

## Interpreting Suggestions

The framework provides three types of suggestions:

### 1. Parameter Tuning
Specific parameter changes (e.g., "Increase TOP_K from 5 to 8")

### 2. Retrieval Improvements
Ways to improve document retrieval quality

### 3. Answer Generation Improvements
Ways to improve answer generation

Each suggestion includes:
- Current value
- Suggested value
- Rationale
- Expected impact (high/medium/low)

## Advanced Usage

### Programmatic Usage

```python
from config import Config
from src.rag_pipeline import RAGPipeline
from src.self_learning.learning_loop import SelfLearningLoop

# Initialize
Config.validate()
rag = RAGPipeline(Config)
rag.build_index()

# Create learning loop
learning_loop = SelfLearningLoop(
    rag_pipeline=rag,
    api_key=Config.OPENAI_API_KEY,
    pdf_path="my_book.pdf",
    output_dir="experiments/my_run"
)

# Run
results = learning_loop.run_full_cycle(
    questions_per_page=3,
    max_pages=None,
    num_iterations=3,
    apply_improvements=True
)

print(f"Final score: {results['iterations'][-1]['evaluations']['statistics']['avg_composite']}")
```

### Using Individual Components

#### Question Generator

```python
from src.self_learning.question_generator import QuestionGenerator

generator = QuestionGenerator(api_key="your_key")
questions = generator.generate_questions_from_pdf(
    pdf_path="book.pdf",
    questions_per_page=3,
    output_path="questions.json"
)
```

#### Accuracy Evaluator

```python
from src.self_learning.accuracy_evaluator import AccuracyEvaluator

evaluator = AccuracyEvaluator(api_key="your_key")
result = evaluator.evaluate_single_answer(
    question="What is X?",
    generated_answer="X is...",
    expected_answer="X is defined as..."
)
print(f"Composite score: {result['composite_score']}/10")
```

#### Improvement Suggester

```python
from src.self_learning.improvement_suggester import ImprovementSuggester

suggester = ImprovementSuggester(api_key="your_key")
suggestions = suggester.analyze_and_suggest(
    evaluations=eval_results,
    qa_results=qa_results,
    current_config=config_dict
)
```

## Configuration

Key settings in `config.py`:

```python
# LLM Model
LLM_MODEL = "gpt-4o-mini"
LLM_TEMPERATURE = 0.2
LLM_MAX_TOKENS = 800

# Retrieval
TOP_K = 7
SIMILARITY_THRESHOLD = 0.65

# Chunking
CHUNK_SIZE = 800
CHUNK_OVERLAP = 150

# Embedding
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
```

## Cost Estimates

Using GPT-4o-mini:

- **Question Generation**: ~$0.01-0.02 per page
- **Answer Evaluation**: ~$0.01-0.02 per Q&A pair
- **Improvement Suggestions**: ~$0.05-0.10 per iteration

**Example**: 50-page document, 3 questions/page, 3 iterations
- Question generation: ~$1.00
- Q&A evaluation: ~$4.50
- Improvement suggestions: ~$0.30
- **Total: ~$5-6**

## Troubleshooting

### Issue: "OPENAI_API_KEY is not set"
**Solution**: Add your API key to `.env` file

### Issue: "PDF file not found"
**Solution**: Check PDF path or use `--pdf` to specify correct path

### Issue: Low scores on all questions
**Solutions**:
- Check if RAG pipeline is properly indexed
- Verify PDF content is being extracted correctly
- Review generated questions quality
- Adjust evaluation criteria if too strict

### Issue: Out of memory
**Solutions**:
- Use `--max-pages` to limit processing
- Reduce `--questions-per-page`
- Process document in chunks

## Extending the Framework

### Add Custom Question Types

Edit `question_generator.py`:
```python
question_types = ["factual", "conceptual", "analytical", "application"]
```

### Custom Evaluation Metrics

Edit `accuracy_evaluator.py` to add new scoring dimensions

### Custom Improvement Logic

Edit `improvement_suggester.py` to add domain-specific suggestions

## Best Practices

1. **Start Small**: Test with `--max-pages 5` first
2. **Review Questions**: Check generated questions quality before full run
3. **Multiple Iterations**: Use 3-5 iterations for best results
4. **Save Results**: Use descriptive `--output-dir` names
5. **Monitor Costs**: Track API usage with `--verbose`

## Limitations

- Requires OpenAI API (cost per question)
- PDF extraction quality depends on PDF structure
- Evaluation is LLM-based (may be subjective)
- Large documents may take significant time
- Mock RAG pipeline needs full implementation for production use

## Future Enhancements

- [ ] Support for multiple documents
- [ ] Human-in-the-loop evaluation
- [ ] Automatic parameter optimization
- [ ] Support for other LLM providers
- [ ] Web-based dashboard
- [ ] Export results to various formats

## Contributing

To contribute improvements:
1. Add tests for new features
2. Update documentation
3. Follow existing code style
4. Submit PR with clear description

## License

[Your License Here]

## Support

For issues or questions:
1. Check this documentation
2. Review output files in experiments directory
3. Use `--verbose` for detailed error messages
4. Check OpenAI API status if API errors occur

---

**Built for autonomous learning and continuous improvement**
