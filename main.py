"""Main Application Entry Point

Command-line interface for the RAG pipeline.
Supports interactive mode and direct query mode.
"""

import argparse
import sys
from pathlib import Path

from config import Config
from src.rag_pipeline import RAGPipeline


def print_banner():
    """Print application banner"""
    print("\n" + "="*60)
    print("  RAG PIPELINE - Cellular Manufacturing Q&A System")
    print("="*60)


def print_response(response: dict, verbose: bool = False):
    """
    Print query response in a formatted way

    Args:
        response: Response dictionary from RAG pipeline
        verbose: Whether to show detailed information
    """
    print("\n" + "="*60)
    print("ANSWER")
    print("="*60)
    print(response["answer"])

    if "sources" in response and response["sources"]:
        print(f"\n{'='*60}")
        print(f"SOURCES ({response['num_sources']} documents)")
        print("="*60)
        for i, src in enumerate(response["sources"], 1):
            print(f"\n{i}. Page {src['page']} (Similarity: {src['similarity_score']:.3f})")
            if verbose:
                print(f"   Chunk ID: {src['chunk_id']}")
                print(f"   Preview: {src['text_preview']}")

    if verbose and "total_time_ms" in response:
        print(f"\n{'='*60}")
        print("PERFORMANCE")
        print("="*60)
        print(f"Total time: {response['total_time_ms']:.0f}ms")
        print(f"  - Retrieval: {response['retrieval_time_ms']:.0f}ms")
        print(f"  - Generation: {response['generation_time_ms']:.0f}ms")
        if "tokens_used" in response:
            print(f"Tokens used: {response['tokens_used']}")

    print("="*60 + "\n")


def interactive_mode(rag: RAGPipeline, verbose: bool = False):
    """
    Run interactive query mode

    Args:
        rag: RAGPipeline instance
        verbose: Whether to show detailed information
    """
    print("\n" + "="*60)
    print("INTERACTIVE MODE")
    print("="*60)
    print("Ask questions about cellular manufacturing.")
    print("Commands:")
    print("  - Type 'quit' or 'exit' to exit")
    print("  - Type 'stats' to show pipeline statistics")
    print("  - Type 'help' for more options")
    print("="*60 + "\n")

    while True:
        try:
            # Get user input
            question = input("\nYour question: ").strip()

            if not question:
                continue

            # Handle commands
            if question.lower() in ['quit', 'exit', 'q']:
                print("\nGoodbye!")
                break

            elif question.lower() == 'stats':
                stats = rag.get_stats()
                print("\n" + "="*60)
                print("PIPELINE STATISTICS")
                print("="*60)
                print(f"Indexed: {stats['indexed']}")
                print(f"Total documents: {stats['vector_store_stats']['total_documents']}")
                print(f"Embedding model: {stats['config']['embedding_model']}")
                print(f"LLM model: {stats['config']['llm_model']}")
                print(f"Chunk size: {stats['config']['chunk_size']}")
                print(f"Top-K retrieval: {stats['config']['top_k']}")
                print("="*60)
                continue

            elif question.lower() == 'help':
                print("\n" + "="*60)
                print("HELP")
                print("="*60)
                print("Available commands:")
                print("  quit/exit/q - Exit the application")
                print("  stats       - Show pipeline statistics")
                print("  help        - Show this help message")
                print("\nJust type your question to get an answer.")
                print("="*60)
                continue

            # Process query
            response = rag.query(question, return_sources=True)
            print_response(response, verbose=verbose)

        except KeyboardInterrupt:
            print("\n\nInterrupted by user. Goodbye!")
            break
        except Exception as e:
            print(f"\nError: {e}")
            if verbose:
                import traceback
                traceback.print_exc()


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="RAG Pipeline for Cellular Manufacturing Q&A",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode
  python main.py

  # Direct query
  python main.py --query "What is cellular manufacturing?"

  # Rebuild index
  python main.py --rebuild-index

  # Show statistics
  python main.py --stats

  # Verbose output
  python main.py --query "What are the benefits?" --verbose
        """
    )

    parser.add_argument(
        '--query', '-q',
        type=str,
        help='Direct query (non-interactive mode)'
    )

    parser.add_argument(
        '--rebuild-index',
        action='store_true',
        help='Force rebuild of the vector index'
    )

    parser.add_argument(
        '--stats',
        action='store_true',
        help='Show pipeline statistics and exit'
    )

    parser.add_argument(
        '--top-k',
        type=int,
        default=None,
        help=f'Number of documents to retrieve (default: {Config.TOP_K})'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Show detailed output including timing and sources'
    )

    parser.add_argument(
        '--config',
        action='store_true',
        help='Display current configuration'
    )

    args = parser.parse_args()

    # Print banner
    print_banner()

    # Display configuration if requested
    if args.config:
        Config.display()
        return

    # Validate configuration
    try:
        Config.validate()
    except ValueError as e:
        print(f"\n✗ Configuration Error:")
        print(f"{e}\n")
        print("Please check your .env file and ensure all required settings are correct.")
        sys.exit(1)

    # Initialize pipeline
    try:
        print("\nInitializing RAG pipeline...")
        rag = RAGPipeline(Config)
    except Exception as e:
        print(f"\n✗ Failed to initialize pipeline: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

    # Handle rebuild index
    if args.rebuild_index:
        print("\nRebuilding index...")
        try:
            rag.build_index(force_rebuild=True)
            print("\n✓ Index rebuilt successfully")
        except Exception as e:
            print(f"\n✗ Failed to rebuild index: {e}")
            if args.verbose:
                import traceback
                traceback.print_exc()
            sys.exit(1)
        return

    # Build index if needed
    try:
        rag.build_index(force_rebuild=False)
    except Exception as e:
        print(f"\n✗ Failed to build index: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

    # Handle stats display
    if args.stats:
        stats = rag.get_stats()
        print("\n" + "="*60)
        print("PIPELINE STATISTICS")
        print("="*60)
        print(f"Indexed: {stats['indexed']}")
        print(f"\nVector Store:")
        for key, value in stats['vector_store_stats'].items():
            print(f"  {key}: {value}")
        print(f"\nEmbedder:")
        for key, value in stats['embedder_info'].items():
            print(f"  {key}: {value}")
        print(f"\nConfiguration:")
        for key, value in stats['config'].items():
            print(f"  {key}: {value}")
        if 'index_stats' in stats:
            print(f"\nIndexing:")
            print(f"  Time: {stats['index_stats'].get('indexing_time_seconds', 0):.2f}s")
        print("="*60)
        return

    # Handle direct query
    if args.query:
        try:
            response = rag.query(args.query, top_k=args.top_k, return_sources=True)
            print_response(response, verbose=args.verbose)
        except Exception as e:
            print(f"\n✗ Query failed: {e}")
            if args.verbose:
                import traceback
                traceback.print_exc()
            sys.exit(1)
        return

    # Interactive mode (default)
    interactive_mode(rag, verbose=args.verbose)


if __name__ == "__main__":
    main()
