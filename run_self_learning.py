#!/usr/bin/env python3
"""
Self-Learning QA Framework - Main Entry Point

This script runs the complete self-learning cycle:
1. Generate questions from a PDF document
2. Query the RAG system with those questions
3. Evaluate the accuracy of answers
4. Suggest improvements
5. Repeat until the system learns the entire document

Usage:
    python run_self_learning.py --pdf <path> --iterations 3
    python run_self_learning.py --pdf <path> --questions-per-page 5 --max-pages 10
    python run_self_learning.py --use-existing-questions questions.json
"""

import argparse
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from config import Config
from src.rag_pipeline import RAGPipeline
from src.self_learning.learning_loop import SelfLearningLoop


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Self-Learning QA Framework - Autonomous question generation, answering, and improvement",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run with default settings (3 questions per page, 3 iterations)
  python run_self_learning.py

  # Custom PDF and more questions
  python run_self_learning.py --pdf my_book.pdf --questions-per-page 5

  # Process first 10 pages only
  python run_self_learning.py --max-pages 10

  # Run 5 iterations with improvement application
  python run_self_learning.py --iterations 5 --apply-improvements

  # Use existing questions file
  python run_self_learning.py --use-existing-questions data/questions.json

  # Custom output directory
  python run_self_learning.py --output-dir experiments/my_run

Full Workflow:
  1. Generates diverse questions from PDF content
  2. Queries the RAG system with each question
  3. Evaluates answer quality (accuracy, completeness, relevance)
  4. Identifies weaknesses and suggests improvements
  5. Optionally applies improvements and repeats
  6. Generates comprehensive learning report
        """
    )

    # PDF and question generation
    parser.add_argument(
        '--pdf',
        type=str,
        default=None,
        help='Path to PDF document (default: from config.py)'
    )

    parser.add_argument(
        '--questions-per-page',
        type=int,
        default=3,
        help='Number of questions to generate per page (default: 3)'
    )

    parser.add_argument(
        '--max-pages',
        type=int,
        default=None,
        help='Maximum number of pages to process (default: all)'
    )

    parser.add_argument(
        '--use-existing-questions',
        type=str,
        default=None,
        help='Path to existing questions JSON file (skips question generation)'
    )

    # Learning loop settings
    parser.add_argument(
        '--iterations',
        type=int,
        default=3,
        help='Number of learning iterations (default: 3)'
    )

    parser.add_argument(
        '--apply-improvements',
        action='store_true',
        help='Apply suggested improvements between iterations'
    )

    # Output settings
    parser.add_argument(
        '--output-dir',
        type=str,
        default='experiments/self_learning',
        help='Output directory for results (default: experiments/self_learning)'
    )

    # Model settings
    parser.add_argument(
        '--model',
        type=str,
        default='gpt-4o-mini',
        help='LLM model to use (default: gpt-4o-mini)'
    )

    # Advanced options
    parser.add_argument(
        '--rebuild-index',
        action='store_true',
        help='Force rebuild of vector index before running'
    )

    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Show detailed output'
    )

    return parser.parse_args()


def main():
    """Main execution function."""
    args = parse_args()

    # Banner
    print("\n" + "=" * 80)
    print(" SELF-LEARNING QA FRAMEWORK")
    print(" Autonomous Question Generation, Answering, and Improvement")
    print("=" * 80)

    # Validate configuration
    try:
        Config.validate()
        print("\n✓ Configuration validated")
    except ValueError as e:
        print(f"\n✗ Configuration error: {e}")
        print("\nPlease check your .env file and config.py")
        return 1

    # Determine PDF path
    pdf_path = args.pdf if args.pdf else Config.PDF_PATH

    if not Path(pdf_path).exists():
        print(f"\n✗ Error: PDF not found at {pdf_path}")
        print("Please specify a valid PDF path with --pdf")
        return 1

    print(f"\nSource Document: {pdf_path}")
    print(f"Output Directory: {args.output_dir}")
    print(f"Model: {args.model}")
    print(f"Iterations: {args.iterations}")

    if args.use_existing_questions:
        print(f"Using Existing Questions: {args.use_existing_questions}")
    else:
        print(f"Questions Per Page: {args.questions_per_page}")
        if args.max_pages:
            print(f"Max Pages: {args.max_pages}")

    # Initialize RAG pipeline
    print("\n" + "-" * 80)
    print("Initializing RAG Pipeline...")
    print("-" * 80)

    try:
        rag = RAGPipeline(Config)

        # Build or load index
        if args.rebuild_index:
            print("Rebuilding vector index (forced)...")
            rag.build_index(force_rebuild=True)
        else:
            rag.build_index(force_rebuild=False)

        print("✓ RAG pipeline ready")

    except Exception as e:
        print(f"\n✗ Failed to initialize RAG pipeline: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1

    # Initialize self-learning framework
    print("\n" + "-" * 80)
    print("Initializing Self-Learning Framework...")
    print("-" * 80)

    try:
        learning_loop = SelfLearningLoop(
            rag_pipeline=rag,
            api_key=Config.OPENAI_API_KEY,
            pdf_path=pdf_path,
            output_dir=args.output_dir,
            model=args.model
        )

        print("✓ Framework initialized")

    except Exception as e:
        print(f"\n✗ Failed to initialize framework: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1

    # Run the learning cycle
    print("\n" + "=" * 80)
    print(" STARTING LEARNING CYCLE")
    print("=" * 80)

    try:
        results = learning_loop.run_full_cycle(
            questions_per_page=args.questions_per_page,
            max_pages=args.max_pages,
            use_existing_questions=args.use_existing_questions,
            num_iterations=args.iterations,
            apply_improvements=args.apply_improvements
        )

        # Display summary
        print("\n" + "=" * 80)
        print(" FINAL SUMMARY")
        print("=" * 80)
        print(f"\nTotal Questions: {results['questions_used']}")
        print(f"Total Iterations: {len(results['iterations'])}")
        print(f"Total Time: {results['total_time_seconds'] / 60:.1f} minutes")

        if results['iterations']:
            first_iter = results['iterations'][0]
            last_iter = results['iterations'][-1]

            first_score = first_iter['evaluations']['statistics']['avg_composite']
            last_score = last_iter['evaluations']['statistics']['avg_composite']
            improvement = last_score - first_score
            improvement_pct = (improvement / first_score * 100) if first_score > 0 else 0

            print(f"\nPerformance:")
            print(f"  Initial Score: {first_score:.2f}/10")
            print(f"  Final Score:   {last_score:.2f}/10")
            print(f"  Improvement:   {improvement:+.2f} ({improvement_pct:+.1f}%)")

        print(f"\n📊 Full Report: {results['final_report']['report_path']}")
        print("\n" + "=" * 80)
        print(" SUCCESS - Learning cycle complete!")
        print("=" * 80 + "\n")

        return 0

    except KeyboardInterrupt:
        print("\n\n⚠ Learning cycle interrupted by user")
        print("Partial results may be available in:", args.output_dir)
        return 1

    except Exception as e:
        print(f"\n\n✗ Error during learning cycle: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
