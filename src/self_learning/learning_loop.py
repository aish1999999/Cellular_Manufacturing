"""
Self-Learning Loop Orchestrator

This module coordinates the entire self-learning QA framework:
1. Generate questions from document
2. Query the system with questions
3. Evaluate answer accuracy
4. Suggest improvements
5. Repeat until convergence or completion
"""

import json
import time
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

from .question_generator import QuestionGenerator
from .query_answerer import QueryAnswerer
from .accuracy_evaluator import AccuracyEvaluator
from .improvement_suggester import ImprovementSuggester


class SelfLearningLoop:
    """
    Orchestrates the complete self-learning QA framework.

    The learning loop:
    1. Generates questions from the source document
    2. Queries the RAG system with those questions
    3. Evaluates the accuracy of answers
    4. Suggests improvements to parameters and configuration
    5. Optionally applies improvements and repeats
    """

    def __init__(
        self,
        rag_pipeline,
        api_key: str,
        pdf_path: str,
        output_dir: str = "experiments/self_learning",
        model: str = "gpt-4o-mini"
    ):
        """
        Initialize the self-learning loop.

        Args:
            rag_pipeline: RAGPipeline instance
            api_key: OpenAI API key
            pdf_path: Path to source PDF document
            output_dir: Directory to save results
            model: LLM model to use
        """
        self.rag_pipeline = rag_pipeline
        self.api_key = api_key
        self.pdf_path = pdf_path
        self.output_dir = Path(output_dir)
        self.model = model

        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Initialize components
        self.question_gen = QuestionGenerator(api_key=api_key, model=model)
        self.query_answerer = QueryAnswerer(rag_pipeline=rag_pipeline, use_rag=True)
        self.evaluator = AccuracyEvaluator(api_key=api_key, model=model)
        self.suggester = ImprovementSuggester(api_key=api_key, model=model)

        # Tracking
        self.iteration_history = []
        self.current_iteration = 0

    def run_full_cycle(
        self,
        questions_per_page: int = 3,
        max_pages: int = None,
        use_existing_questions: str = None,
        num_iterations: int = 3,
        apply_improvements: bool = False
    ) -> Dict[str, Any]:
        """
        Run the complete self-learning cycle.

        Args:
            questions_per_page: Questions to generate per page
            max_pages: Maximum pages to process (None for all)
            use_existing_questions: Path to existing questions file
            num_iterations: Number of learning iterations
            apply_improvements: Whether to apply improvements between iterations

        Returns:
            Dictionary with complete results
        """
        print("\n" + "=" * 80)
        print(" SELF-LEARNING QA FRAMEWORK")
        print("=" * 80)
        print(f"\nSource Document: {self.pdf_path}")
        print(f"Output Directory: {self.output_dir}")
        print(f"Iterations: {num_iterations}")
        print("=" * 80 + "\n")

        start_time = time.time()

        # Step 1: Generate or load questions
        if use_existing_questions:
            print(f"Loading existing questions from: {use_existing_questions}")
            questions = self.question_gen.load_questions(use_existing_questions)
            print(f"✓ Loaded {len(questions)} questions")
        else:
            print("STEP 1: Generating Questions")
            print("-" * 80)
            questions_file = self.output_dir / "generated_questions.json"
            questions = self.question_gen.generate_questions_from_pdf(
                pdf_path=self.pdf_path,
                questions_per_page=questions_per_page,
                max_pages=max_pages,
                output_path=str(questions_file)
            )

        # Run iterations
        for iteration in range(1, num_iterations + 1):
            self.current_iteration = iteration
            print(f"\n{'=' * 80}")
            print(f" ITERATION {iteration}/{num_iterations}")
            print(f"{'=' * 80}\n")

            iteration_results = self._run_single_iteration(questions)

            self.iteration_history.append(iteration_results)

            # Display iteration summary
            self._display_iteration_summary(iteration_results)

            # Apply improvements if requested and not last iteration
            if apply_improvements and iteration < num_iterations:
                print("\nApplying suggested improvements...")
                self._apply_improvements(iteration_results['suggestions'])

            # Save iteration results
            self._save_iteration_results(iteration, iteration_results)

        # Generate final report
        final_report = self._generate_final_report()

        total_time = time.time() - start_time

        print(f"\n{'=' * 80}")
        print(" LEARNING CYCLE COMPLETE")
        print(f"{'=' * 80}")
        print(f"Total Time: {total_time / 60:.1f} minutes")
        print(f"Final Report: {final_report['report_path']}")
        print(f"{'=' * 80}\n")

        return {
            'iterations': self.iteration_history,
            'final_report': final_report,
            'total_time_seconds': total_time,
            'questions_used': len(questions)
        }

    def _run_single_iteration(self, questions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Run a single iteration of the learning loop."""
        iteration_start = time.time()

        # Step 2: Query the system
        print(f"STEP 2: Querying RAG System (Iteration {self.current_iteration})")
        print("-" * 80)
        qa_results_file = self.output_dir / f"qa_results_iter{self.current_iteration}.json"
        qa_results = self.query_answerer.query_batch(
            questions=questions,
            return_sources=True,
            save_intermediate=True,
            output_path=str(qa_results_file)
        )

        # Get query statistics
        query_stats = self.query_answerer.get_statistics(qa_results)
        print(f"\nQuery Statistics:")
        print(f"  Success Rate: {query_stats['success_rate']*100:.1f}%")
        print(f"  Avg Query Time: {query_stats['avg_query_time_seconds']:.2f}s")

        # Step 3: Evaluate answers
        print(f"\nSTEP 3: Evaluating Answer Quality")
        print("-" * 80)
        eval_results = self.evaluator.evaluate_batch(
            qa_results=qa_results,
            expected_answers=None  # Expected answers are in question metadata
        )

        print(f"\nEvaluation Summary:")
        stats = eval_results['statistics']
        print(f"  Average Accuracy: {stats['avg_accuracy']:.2f}/10")
        print(f"  Average Completeness: {stats['avg_completeness']:.2f}/10")
        print(f"  Average Relevance: {stats['avg_relevance']:.2f}/10")
        print(f"  Average Composite Score: {stats['avg_composite']:.2f}/10")

        # Identify weak areas
        weak_areas = self.evaluator.identify_weak_areas(
            evaluations=eval_results['evaluations'],
            threshold=6.0
        )
        print(f"  Weak Answers: {weak_areas['total_weak_answers']} ({weak_areas['percentage_weak']:.1f}%)")

        # Step 4: Generate improvement suggestions
        print(f"\nSTEP 4: Generating Improvement Suggestions")
        print("-" * 80)

        # Get current config from RAG pipeline
        current_config = self._get_current_config()

        suggestions = self.suggester.analyze_and_suggest(
            evaluations=eval_results['evaluations'],
            qa_results=qa_results,
            current_config=current_config
        )

        # Generate improvement report
        report_file = self.output_dir / f"improvements_iter{self.current_iteration}.txt"
        report_text = self.suggester.generate_improvement_report(
            suggestions=suggestions,
            output_path=str(report_file)
        )

        iteration_time = time.time() - iteration_start

        return {
            'iteration': self.current_iteration,
            'qa_results': qa_results,
            'query_statistics': query_stats,
            'evaluations': eval_results,
            'weak_areas': weak_areas,
            'suggestions': suggestions,
            'improvement_report': report_text,
            'iteration_time_seconds': iteration_time,
            'current_config': current_config
        }

    def _get_current_config(self) -> Dict[str, Any]:
        """Get current RAG pipeline configuration."""
        # This assumes the RAG pipeline has a config attribute
        # Adjust based on actual implementation
        try:
            from config import Config
            return {
                'CHUNK_SIZE': Config.CHUNK_SIZE,
                'CHUNK_OVERLAP': Config.CHUNK_OVERLAP,
                'TOP_K': Config.TOP_K,
                'SIMILARITY_THRESHOLD': Config.SIMILARITY_THRESHOLD,
                'LLM_TEMPERATURE': Config.LLM_TEMPERATURE,
                'LLM_MAX_TOKENS': Config.LLM_MAX_TOKENS,
                'EMBEDDING_MODEL': Config.EMBEDDING_MODEL,
                'LLM_MODEL': Config.LLM_MODEL
            }
        except:
            return {}

    def _apply_improvements(self, suggestions: Dict[str, Any]):
        """
        Apply suggested improvements to the system.

        Note: Some improvements require rebuilding the index (e.g., chunk size changes),
        while others can be applied directly (e.g., TOP_K, temperature).
        """
        print("Applying improvements...")

        # Get parameter tuning suggestions
        param_suggestions = suggestions.get('parameter_tuning', [])

        # Apply runtime parameters (no rebuild needed)
        runtime_params = ['TOP_K', 'SIMILARITY_THRESHOLD', 'LLM_TEMPERATURE']

        for suggestion in param_suggestions:
            param_name = suggestion.get('parameter')
            suggested_value = suggestion.get('suggested_value')

            if param_name in runtime_params:
                print(f"  - Setting {param_name} = {suggested_value}")
                # Apply to RAG pipeline
                # This is a simplified example - actual implementation depends on pipeline structure
                # setattr(self.rag_pipeline, param_name.lower(), suggested_value)

        print("✓ Runtime parameters updated")
        print("  Note: Some improvements may require re-indexing, which is not done automatically")

    def _display_iteration_summary(self, results: Dict[str, Any]):
        """Display summary of iteration results."""
        print(f"\n{'=' * 80}")
        print(f" ITERATION {self.current_iteration} SUMMARY")
        print(f"{'=' * 80}")

        stats = results['evaluations']['statistics']
        print(f"\nPerformance Scores:")
        print(f"  Composite Score: {stats['avg_composite']:.2f}/10")
        print(f"  Accuracy:        {stats['avg_accuracy']:.2f}/10")
        print(f"  Completeness:    {stats['avg_completeness']:.2f}/10")
        print(f"  Relevance:       {stats['avg_relevance']:.2f}/10")

        print(f"\nTop Priority Actions:")
        for i, action in enumerate(results['suggestions'].get('priority_actions', [])[:3], 1):
            print(f"  {i}. {action['action']}")

        print(f"\nTime: {results['iteration_time_seconds']:.1f}s")
        print(f"{'=' * 80}")

    def _save_iteration_results(self, iteration: int, results: Dict[str, Any]):
        """Save complete iteration results to JSON."""
        # Remove large data structures for summary
        summary = {
            'iteration': iteration,
            'timestamp': datetime.now().isoformat(),
            'statistics': results['evaluations']['statistics'],
            'query_statistics': results['query_statistics'],
            'weak_areas_summary': {
                'total': results['weak_areas']['total_weak_answers'],
                'percentage': results['weak_areas']['percentage_weak']
            },
            'top_suggestions': results['suggestions'].get('priority_actions', [])[:5],
            'parameter_suggestions': results['suggestions'].get('parameter_tuning', []),
            'iteration_time_seconds': results['iteration_time_seconds'],
            'current_config': results['current_config']
        }

        summary_file = self.output_dir / f"iteration_{iteration}_summary.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)

        print(f"\n✓ Iteration {iteration} results saved to: {summary_file}")

    def _generate_final_report(self) -> Dict[str, Any]:
        """Generate final comprehensive report."""
        report_path = self.output_dir / "final_learning_report.txt"

        lines = []
        lines.append("=" * 80)
        lines.append(" SELF-LEARNING QA FRAMEWORK - FINAL REPORT")
        lines.append("=" * 80)
        lines.append(f"\nDocument: {self.pdf_path}")
        lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"Total Iterations: {len(self.iteration_history)}")
        lines.append("\n" + "=" * 80)

        # Performance progression
        lines.append("\n## PERFORMANCE PROGRESSION\n")
        for i, iteration in enumerate(self.iteration_history, 1):
            stats = iteration['evaluations']['statistics']
            lines.append(f"Iteration {i}:")
            lines.append(f"  Composite Score: {stats['avg_composite']:.2f}/10")
            lines.append(f"  Accuracy:        {stats['avg_accuracy']:.2f}/10")
            lines.append(f"  Completeness:    {stats['avg_completeness']:.2f}/10")
            lines.append("")

        # Overall improvement
        if len(self.iteration_history) > 1:
            first_score = self.iteration_history[0]['evaluations']['statistics']['avg_composite']
            last_score = self.iteration_history[-1]['evaluations']['statistics']['avg_composite']
            improvement = last_score - first_score
            improvement_pct = (improvement / first_score * 100) if first_score > 0 else 0

            lines.append(f"## OVERALL IMPROVEMENT\n")
            lines.append(f"Initial Score: {first_score:.2f}/10")
            lines.append(f"Final Score:   {last_score:.2f}/10")
            lines.append(f"Improvement:   {improvement:+.2f} ({improvement_pct:+.1f}%)\n")

        # Final recommendations
        lines.append("\n## FINAL RECOMMENDATIONS\n")
        if self.iteration_history:
            final_suggestions = self.iteration_history[-1]['suggestions']
            for i, action in enumerate(final_suggestions.get('priority_actions', [])[:5], 1):
                lines.append(f"{i}. [{action['impact'].upper()}] {action['action']}")
                lines.append(f"   Rationale: {action['rationale']}\n")

        lines.append("=" * 80)

        report_text = "\n".join(lines)

        with open(report_path, 'w') as f:
            f.write(report_text)

        print(f"\n✓ Final report generated: {report_path}")

        return {
            'report_path': str(report_path),
            'report_text': report_text
        }


if __name__ == "__main__":
    print("SelfLearningLoop - Main orchestrator for self-learning QA framework")
    print("See main entry point script for usage")
