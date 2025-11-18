"""
Query and Answer Module

This module handles querying a RAG system or LLM with generated questions
and records the answers for evaluation.
"""

import json
import time
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime


class QueryAnswerer:
    """
    Handles querying and answer recording for the self-learning framework.

    Features:
    - Queries RAG pipeline or direct LLM
    - Records Q&A pairs with metadata
    - Tracks response times and quality metrics
    - Supports batch processing
    """

    def __init__(self, rag_pipeline=None, use_rag: bool = True):
        """
        Initialize the query answerer.

        Args:
            rag_pipeline: RAGPipeline instance (optional, for RAG mode)
            use_rag: Whether to use RAG pipeline or direct LLM
        """
        self.rag_pipeline = rag_pipeline
        self.use_rag = use_rag
        self.qa_history = []

    def query_single(
        self,
        question: str,
        question_metadata: Dict[str, Any] = None,
        return_sources: bool = True,
        top_k: int = None
    ) -> Dict[str, Any]:
        """
        Query the system with a single question.

        Args:
            question: The question to ask
            question_metadata: Metadata about the question
            return_sources: Whether to return source documents
            top_k: Number of documents to retrieve (for RAG mode)

        Returns:
            Dictionary containing answer and metadata
        """
        start_time = time.time()

        try:
            if self.use_rag and self.rag_pipeline:
                # Query RAG pipeline
                response = self.rag_pipeline.query(
                    query=question,
                    top_k=top_k,
                    return_sources=return_sources
                )

                result = {
                    'question': question,
                    'answer': response.get('answer', ''),
                    'sources': response.get('sources', []),
                    'num_sources': response.get('num_sources', 0),
                    'retrieval_time_ms': response.get('retrieval_time_ms', 0),
                    'generation_time_ms': response.get('generation_time_ms', 0),
                    'total_time_ms': response.get('total_time_ms', 0),
                }
            else:
                # Direct LLM query (no RAG)
                # This would need an LLM client implementation
                raise NotImplementedError("Direct LLM mode not implemented yet")

            # Add metadata
            result['timestamp'] = datetime.now().isoformat()
            result['query_time_seconds'] = time.time() - start_time

            if question_metadata:
                result['question_metadata'] = question_metadata

            # Record in history
            self.qa_history.append(result)

            return result

        except Exception as e:
            error_result = {
                'question': question,
                'answer': '',
                'error': str(e),
                'timestamp': datetime.now().isoformat(),
                'query_time_seconds': time.time() - start_time
            }

            if question_metadata:
                error_result['question_metadata'] = question_metadata

            self.qa_history.append(error_result)
            return error_result

    def query_batch(
        self,
        questions: List[Dict[str, Any]],
        return_sources: bool = True,
        top_k: int = None,
        save_intermediate: bool = True,
        output_path: str = None
    ) -> List[Dict[str, Any]]:
        """
        Query the system with multiple questions.

        Args:
            questions: List of question dictionaries
            return_sources: Whether to return source documents
            top_k: Number of documents to retrieve (for RAG mode)
            save_intermediate: Save results after each question
            output_path: Path to save results

        Returns:
            List of Q&A results
        """
        results = []
        total_questions = len(questions)

        print(f"\nQuerying {total_questions} questions...")

        for i, q_data in enumerate(questions, 1):
            question_text = q_data.get('question', q_data.get('text', ''))

            if not question_text:
                print(f"  [{i}/{total_questions}] Skipping empty question")
                continue

            print(f"  [{i}/{total_questions}] {question_text[:60]}...", end=" ")

            result = self.query_single(
                question=question_text,
                question_metadata=q_data,
                return_sources=return_sources,
                top_k=top_k
            )

            results.append(result)

            # Print status
            if 'error' in result:
                print(f"ERROR: {result['error']}")
            else:
                print(f"✓ ({result.get('total_time_ms', 0):.0f}ms)")

            # Save intermediate results
            if save_intermediate and output_path and i % 10 == 0:
                self.save_qa_results(results, output_path)

        print(f"\n✓ Completed {len(results)} queries")

        # Final save
        if output_path:
            self.save_qa_results(results, output_path)

        return results

    def save_qa_results(
        self,
        results: List[Dict[str, Any]],
        output_path: str
    ):
        """
        Save Q&A results to JSON file.

        Args:
            results: List of Q&A results
            output_path: Path to save results
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        data = {
            'qa_pairs': results,
            'metadata': {
                'total_pairs': len(results),
                'timestamp': datetime.now().isoformat(),
                'use_rag': self.use_rag
            }
        }

        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)

        print(f"✓ Q&A results saved to: {output_path}")

    def load_qa_results(self, results_path: str) -> List[Dict[str, Any]]:
        """
        Load Q&A results from JSON file.

        Args:
            results_path: Path to results file

        Returns:
            List of Q&A results
        """
        with open(results_path, 'r') as f:
            data = json.load(f)
            return data.get('qa_pairs', data)

    def get_statistics(self, results: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Get statistics about Q&A performance.

        Args:
            results: Optional list of results (uses history if not provided)

        Returns:
            Dictionary of statistics
        """
        if results is None:
            results = self.qa_history

        if not results:
            return {'total_queries': 0}

        total = len(results)
        successful = sum(1 for r in results if 'error' not in r)
        failed = total - successful

        avg_time = sum(r.get('query_time_seconds', 0) for r in results) / total
        avg_sources = sum(r.get('num_sources', 0) for r in results) / total if successful > 0 else 0

        return {
            'total_queries': total,
            'successful': successful,
            'failed': failed,
            'success_rate': successful / total if total > 0 else 0,
            'avg_query_time_seconds': avg_time,
            'avg_sources_per_query': avg_sources,
            'total_time_seconds': sum(r.get('query_time_seconds', 0) for r in results)
        }

    def clear_history(self):
        """Clear the Q&A history."""
        self.qa_history = []


if __name__ == "__main__":
    # Example usage
    print("QueryAnswerer module - use with RAG pipeline")
    print("Example:")
    print("""
    from config import Config
    from src.rag_pipeline import RAGPipeline
    from src.self_learning.query_answerer import QueryAnswerer

    # Initialize
    rag = RAGPipeline(Config)
    rag.build_index()

    answerer = QueryAnswerer(rag_pipeline=rag)

    # Query
    result = answerer.query_single("What is cellular manufacturing?")
    print(result['answer'])
    """)
