#!/usr/bin/env python
"""
Diagnostic script to understand why queries aren't working.
Run this BEFORE rebuilding to see what's wrong.
"""

import sys
from config import Config
from src.rag_pipeline import RAGPipeline

def main():
    print("="*60)
    print("RAG PIPELINE DIAGNOSTIC")
    print("="*60)

    # Check config
    print("\n[1/5] Checking Configuration...")
    try:
        Config.validate()
        print("✓ Configuration is valid")
    except ValueError as e:
        print(f"✗ Configuration error: {e}")
        return

    print(f"\nCurrent Settings:")
    print(f"  Chunk Size: {Config.CHUNK_SIZE}")
    print(f"  Chunk Overlap: {Config.CHUNK_OVERLAP}")
    print(f"  Top-K: {Config.TOP_K}")
    print(f"  Similarity Threshold: {Config.SIMILARITY_THRESHOLD}")
    print(f"  LLM Max Tokens: {Config.LLM_MAX_TOKENS}")
    print(f"  Embedding Model: {Config.EMBEDDING_MODEL}")

    # Initialize
    print("\n[2/5] Initializing Pipeline...")
    try:
        rag = RAGPipeline(Config)
        print("✓ Pipeline initialized")
    except Exception as e:
        print(f"✗ Failed to initialize: {e}")
        import traceback
        traceback.print_exc()
        return

    # Check index stats
    print("\n[3/5] Checking Vector Store...")
    stats = rag.get_stats()
    print(f"Total documents in index: {stats['vector_store_stats']['total_documents']}")

    if stats['vector_store_stats']['total_documents'] == 0:
        print("✗ Vector store is EMPTY! You need to build the index first.")
        print("  Run: python rebuild_and_test.py")
        return
    else:
        print(f"✓ Index exists with {stats['vector_store_stats']['total_documents']} documents")

    # Test retrieval
    print("\n[4/5] Testing Retrieval...")
    test_query = "What would be an integrated set of proven best practices of Job Shop Lean"

    print(f"Query: {test_query}")

    try:
        # Get query embedding
        query_embedding = rag.embedder.embed_text(test_query)
        print(f"✓ Generated query embedding: shape {query_embedding.shape}")

        # Retrieve documents
        retrieved = rag.retriever.retrieve(
            test_query,
            top_k=10,  # Get more to see what we're getting
            similarity_threshold=0.0  # No threshold to see all results
        )

        print(f"\n✓ Retrieved {len(retrieved)} documents (no threshold)")

        if len(retrieved) == 0:
            print("✗ NO documents retrieved at all! Index might be broken.")
            print("  Try rebuilding: python rebuild_and_test.py")
            return

        # Show top results
        print("\nTop 10 Results:")
        for i, doc in enumerate(retrieved[:10], 1):
            print(f"\n{i}. Page {doc['page_num']} - Similarity: {doc['similarity_score']:.4f}")
            print(f"   Text: {doc['text'][:150]}...")

        # Check how many pass threshold
        threshold = Config.SIMILARITY_THRESHOLD
        passed = [d for d in retrieved if d['similarity_score'] >= threshold]
        print(f"\n✓ {len(passed)} documents pass threshold of {threshold}")

        if len(passed) == 0:
            print(f"⚠️  WARNING: No documents pass similarity threshold {threshold}!")
            print(f"   Highest score: {retrieved[0]['similarity_score']:.4f}")
            print(f"   Consider lowering threshold to: {retrieved[0]['similarity_score'] - 0.05:.2f}")

    except Exception as e:
        print(f"✗ Retrieval failed: {e}")
        import traceback
        traceback.print_exc()
        return

    # Test generation with retrieved context
    print("\n[5/5] Testing Generation...")

    if len(passed) > 0:
        context = rag.retriever.get_context_for_generation(passed[:7])
        print(f"✓ Formatted context from {len(passed[:7])} documents")
        print(f"\nContext length: {len(context)} characters")
        print(f"Context preview:\n{context[:500]}...\n")

        try:
            result = rag.generator.generate(test_query, context)
            print("✓ Generation successful")
            print(f"\nGenerated Answer:\n{result['answer']}")

            if "cannot find" in result['answer'].lower():
                print("\n⚠️  ISSUE FOUND: LLM says 'cannot find' despite having context!")
                print("   This is a PROMPT issue, not a retrieval issue.")
                print("   The prompt has been updated to be less restrictive.")
            else:
                print("\n✓ Got a real answer!")

        except Exception as e:
            print(f"✗ Generation failed: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("✗ Cannot test generation - no documents passed threshold")

    # Summary
    print("\n" + "="*60)
    print("DIAGNOSTIC SUMMARY")
    print("="*60)

    issues = []

    if stats['vector_store_stats']['total_documents'] < 100:
        issues.append(f"Very few documents in index ({stats['vector_store_stats']['total_documents']})")

    if Config.CHUNK_SIZE > 10000:
        issues.append(f"CHUNK_SIZE is too large ({Config.CHUNK_SIZE})")

    if len(retrieved) > 0 and retrieved[0]['similarity_score'] < Config.SIMILARITY_THRESHOLD:
        issues.append(f"Best similarity ({retrieved[0]['similarity_score']:.3f}) is below threshold ({Config.SIMILARITY_THRESHOLD})")

    if len(passed) == 0:
        issues.append("No documents pass similarity threshold")

    if issues:
        print("\n⚠️  Issues Found:")
        for i, issue in enumerate(issues, 1):
            print(f"{i}. {issue}")

        print("\n📋 Recommended Actions:")
        if Config.CHUNK_SIZE > 10000:
            print("1. Fix CHUNK_SIZE in .env (set to 1200)")
        if len(passed) == 0:
            print("2. Lower SIMILARITY_THRESHOLD (try 0.60 or 0.55)")
        if stats['vector_store_stats']['total_documents'] < 100 or Config.CHUNK_SIZE > 10000:
            print("3. Rebuild index: python rebuild_and_test.py")
    else:
        print("\n✓ No major issues detected!")
        print("The system should be working correctly.")

    print("="*60)

if __name__ == "__main__":
    main()
