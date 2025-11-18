#!/usr/bin/env python
"""
Quick script to rebuild index and test the problematic query.
Run this after changing CHUNK_SIZE.
"""

import sys
from config import Config
from src.rag_pipeline import RAGPipeline

def main():
    print("="*60)
    print("REBUILD AND TEST SCRIPT")
    print("="*60)

    # Validate config
    try:
        Config.validate()
        print("\n✓ Configuration is valid")
    except ValueError as e:
        print(f"\n✗ Configuration error: {e}")
        sys.exit(1)

    # Show current settings
    print("\nCurrent Settings:")
    print(f"  Chunk Size: {Config.CHUNK_SIZE}")
    print(f"  Chunk Overlap: {Config.CHUNK_OVERLAP}")
    print(f"  Top-K: {Config.TOP_K}")
    print(f"  Similarity Threshold: {Config.SIMILARITY_THRESHOLD}")
    print(f"  LLM Max Tokens: {Config.LLM_MAX_TOKENS}")

    # Initialize pipeline
    print("\nInitializing RAG pipeline...")
    rag = RAGPipeline(Config)

    # Rebuild index
    print("\n" + "="*60)
    print("REBUILDING INDEX")
    print("="*60)
    print("This will take 2-5 minutes...")

    try:
        rag.build_index(force_rebuild=True)
        print("\n✓ Index rebuilt successfully!")
    except Exception as e:
        print(f"\n✗ Failed to rebuild index: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    # Test the problematic query
    print("\n" + "="*60)
    print("TESTING PROBLEMATIC QUERY")
    print("="*60)

    test_query = "What would be an integrated set of proven best practices of Job Shop Lean that have been implemented by a 21st Century CNC machine shop?"

    print(f"\nQuery: {test_query}")
    print("\nProcessing...")

    try:
        response = rag.query(test_query, top_k=7, return_sources=True)

        print("\n" + "="*60)
        print("ANSWER")
        print("="*60)
        print(response['answer'])

        if 'sources' in response and response['sources']:
            print(f"\n{'='*60}")
            print(f"SOURCES ({response['num_sources']} documents)")
            print("="*60)
            for i, src in enumerate(response['sources'], 1):
                print(f"\n{i}. Page {src['page']} (Similarity: {src['similarity_score']:.3f})")
                print(f"   Preview: {src['text_preview'][:100]}...")

        print(f"\n{'='*60}")
        print("PERFORMANCE")
        print("="*60)
        print(f"Total time: {response['total_time_ms']:.0f}ms")
        print(f"  - Retrieval: {response['retrieval_time_ms']:.0f}ms")
        print(f"  - Generation: {response['generation_time_ms']:.0f}ms")
        if 'tokens_used' in response:
            print(f"Tokens used: {response['tokens_used']}")
        print("="*60)

        # Check if answer is still "cannot find"
        if "cannot find" in response['answer'].lower():
            print("\n⚠️  WARNING: Still getting 'cannot find' response!")
            print("Try lowering SIMILARITY_THRESHOLD to 0.60 in .env")
        else:
            print("\n✓ SUCCESS: Got a real answer!")

    except Exception as e:
        print(f"\n✗ Query failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    # Test a simple query too
    print("\n" + "="*60)
    print("TESTING SIMPLE QUERY (sanity check)")
    print("="*60)

    simple_query = "What is cellular manufacturing?"
    print(f"\nQuery: {simple_query}")

    try:
        response = rag.query(simple_query, top_k=3, return_sources=True)
        print(f"\nAnswer: {response['answer'][:200]}...")

        if "cannot find" in response['answer'].lower():
            print("\n⚠️  WARNING: Even simple query failed!")
        else:
            print("\n✓ Simple query works!")

    except Exception as e:
        print(f"\n✗ Simple query failed: {e}")

    print("\n" + "="*60)
    print("DONE!")
    print("="*60)
    print("\nNext steps:")
    print("1. Review the answers above")
    print("2. If still getting 'cannot find', try:")
    print("   - Lower SIMILARITY_THRESHOLD to 0.60")
    print("   - Increase TOP_K to 10")
    print("3. Test more queries with: python main.py")
    print("="*60)

if __name__ == "__main__":
    main()
