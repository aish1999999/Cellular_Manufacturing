"""
Run Self-Supervised Learning Loop

This script executes the complete autonomous learning framework:
1. Generate questions from the book
2. Run baseline evaluation
3. Optimize parameters
4. Generate final report
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from config import Config
from src.rag_pipeline import RAGPipeline
from src.evaluation.learning_loop import SelfSupervisedLearningLoop


def main():
    """Main execution function."""

    print("\n" + "="*80)
    print(" SELF-SUPERVISED RAG LEARNING FRAMEWORK")
    print("="*80)
    print("\nThis framework will:")
    print("  1. Generate diverse questions from your document")
    print("  2. Evaluate baseline RAG performance")
    print("  3. Optimize parameters through adaptive search")
    print("  4. Generate comprehensive improvement report")
    print("\n" + "="*80 + "\n")

    # Validate configuration
    try:
        Config.validate()
        print("✓ Configuration validated")
    except ValueError as e:
        print(f"✗ Configuration error: {e}")
        return

    # Initialize RAG pipeline
    print("\nInitializing RAG pipeline...")
    rag_pipeline = RAGPipeline(Config)

    # Check if index exists
    stats = rag_pipeline.vector_store.get_collection_stats()
    if stats["total_documents"] == 0:
        print("\n⚠ Vector store is empty. Building index first...")
        rag_pipeline.build_index()
    else:
        print(f"✓ Found existing index with {stats['total_documents']} documents")

    # Prepare base configuration for optimization
    base_config = {
        'EMBEDDING_MODEL': Config.EMBEDDING_MODEL,
        'CHUNK_SIZE': Config.CHUNK_SIZE,
        'CHUNK_OVERLAP': Config.CHUNK_OVERLAP,
        'TOP_K': Config.TOP_K,
        'SIMILARITY_THRESHOLD': Config.SIMILARITY_THRESHOLD,
        'LLM_MODEL': Config.LLM_MODEL,
        'LLM_TEMPERATURE': Config.LLM_TEMPERATURE,
        'LLM_MAX_TOKENS': Config.LLM_MAX_TOKENS,
        'USE_MMR': Config.USE_MMR
    }

    # Initialize learning loop
    print("\nInitializing learning loop...")
    learning_loop = SelfSupervisedLearningLoop(
        rag_pipeline=rag_pipeline,
        api_key=Config.OPENAI_API_KEY,
        base_config=base_config,
        questions_path="data/evaluation/questions.json",
        experiments_dir="experiments"
    )

    # Define parameter grid for optimization
    # These are runtime parameters that don't require re-indexing
    param_grid = {
        'TOP_K': [3, 5, 7, 10, 15],
        'SIMILARITY_THRESHOLD': [0.5, 0.6, 0.65, 0.7, 0.75],
        'LLM_TEMPERATURE': [0.0, 0.1, 0.2, 0.3],
    }

    # Run learning loop
    print("\nStarting autonomous learning loop...")
    print("This may take 30-60 minutes depending on the number of questions and iterations.")
    print("Progress will be logged throughout the process.\n")

    try:
        results = learning_loop.run(
            num_questions=50,  # Start with 50 questions for faster iteration
            max_iterations=10,  # Adaptive search iterations
            convergence_threshold=0.01,  # Stop if improvement < 1%
            search_strategy='adaptive',  # 'adaptive', 'random', or 'grid'
            param_grid=param_grid,
            verbose=True
        )

        # Display final summary
        print("\n" + "="*80)
        print(" FINAL RESULTS")
        print("="*80)
        print(f"\n✓ Learning loop completed successfully!")
        print(f"\nBaseline Score: {results['baseline_results']['aggregate_metrics']['avg_composite_score']:.3f}")
        print(f"Final Score: {results['final_results']['aggregate_metrics']['avg_composite_score']:.3f}")
        improvement = (
            results['final_results']['aggregate_metrics']['avg_composite_score'] -
            results['baseline_results']['aggregate_metrics']['avg_composite_score']
        )
        print(f"Improvement: +{improvement:.3f} ({improvement/results['baseline_results']['aggregate_metrics']['avg_composite_score']*100:.1f}%)")

        print(f"\n📊 Report saved to: {results['report_path']}")

        print("\n🎯 Best Configuration:")
        best_config = results['best_config']
        for key, value in best_config.items():
            if key not in base_config or base_config[key] != value:
                print(f"  • {key}: {base_config.get(key, 'N/A')} → {value}")

        print("\n" + "="*80 + "\n")

    except KeyboardInterrupt:
        print("\n\n⚠ Learning loop interrupted by user")
        print("Partial results may be available in the experiments directory")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n✗ Error during learning loop: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
