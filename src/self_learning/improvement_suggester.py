"""
Improvement Suggestion Module

This module analyzes evaluation results and suggests specific improvements
to enhance answer accuracy and quality.
"""

import json
from typing import Dict, Any, List, Optional
from openai import OpenAI
from collections import Counter, defaultdict


class ImprovementSuggester:
    """
    Suggests improvements to enhance RAG system performance.

    Features:
    - Analyzes evaluation results to identify patterns
    - Suggests parameter tuning (chunk size, top-k, etc.)
    - Recommends retrieval improvements
    - Suggests prompt engineering improvements
    - Provides actionable recommendations
    """

    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        """
        Initialize the improvement suggester.

        Args:
            api_key: OpenAI API key
            model: LLM model to use for generating suggestions
        """
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def analyze_and_suggest(
        self,
        evaluations: List[Dict[str, Any]],
        qa_results: List[Dict[str, Any]],
        current_config: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Analyze evaluation results and suggest improvements.

        Args:
            evaluations: List of evaluation results
            qa_results: List of Q&A results
            current_config: Current system configuration

        Returns:
            Dictionary with detailed improvement suggestions
        """
        print("\nAnalyzing results to generate improvement suggestions...")

        # 1. Identify patterns in weaknesses
        weakness_analysis = self._analyze_weaknesses(evaluations)

        # 2. Analyze retrieval quality
        retrieval_analysis = self._analyze_retrieval(qa_results)

        # 3. Analyze answer patterns
        answer_analysis = self._analyze_answer_patterns(evaluations, qa_results)

        # 4. Generate LLM-based recommendations
        llm_suggestions = self._generate_llm_suggestions(
            weakness_analysis=weakness_analysis,
            retrieval_analysis=retrieval_analysis,
            answer_analysis=answer_analysis,
            current_config=current_config
        )

        # 5. Generate parameter tuning suggestions
        parameter_suggestions = self._suggest_parameter_tuning(
            evaluations=evaluations,
            qa_results=qa_results,
            current_config=current_config
        )

        # Combine all suggestions
        suggestions = {
            'weakness_analysis': weakness_analysis,
            'retrieval_analysis': retrieval_analysis,
            'answer_analysis': answer_analysis,
            'llm_recommendations': llm_suggestions,
            'parameter_tuning': parameter_suggestions,
            'priority_actions': self._prioritize_actions(
                weakness_analysis,
                retrieval_analysis,
                parameter_suggestions
            )
        }

        return suggestions

    def _analyze_weaknesses(self, evaluations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze common weaknesses in answers."""
        all_weaknesses = []
        all_missing = []
        low_scores = defaultdict(list)

        for eval_result in evaluations:
            # Collect weaknesses
            all_weaknesses.extend(eval_result.get('weaknesses', []))
            all_missing.extend(eval_result.get('missing_information', []))

            # Track low scores by category
            for metric in ['accuracy_score', 'completeness_score', 'relevance_score', 'clarity_score']:
                score = eval_result.get(metric, 10)
                if score < 7:
                    low_scores[metric].append({
                        'question': eval_result.get('question', '')[:100],
                        'score': score
                    })

        weakness_freq = Counter(all_weaknesses)
        missing_freq = Counter(all_missing)

        return {
            'common_weaknesses': weakness_freq.most_common(10),
            'common_missing_info': missing_freq.most_common(10),
            'low_score_categories': {
                metric: {
                    'count': len(scores),
                    'examples': scores[:3]
                }
                for metric, scores in low_scores.items()
            }
        }

    def _analyze_retrieval(self, qa_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze retrieval quality."""
        total_queries = len(qa_results)
        num_sources = [r.get('num_sources', 0) for r in qa_results]
        avg_sources = sum(num_sources) / total_queries if total_queries > 0 else 0

        # Check for queries with no sources
        no_sources = sum(1 for n in num_sources if n == 0)

        # Analyze source diversity (different pages)
        unique_pages_per_query = []
        for result in qa_results:
            sources = result.get('sources', [])
            if sources:
                pages = set(s.get('page', 0) for s in sources)
                unique_pages_per_query.append(len(pages))

        avg_unique_pages = (
            sum(unique_pages_per_query) / len(unique_pages_per_query)
            if unique_pages_per_query else 0
        )

        return {
            'avg_sources_retrieved': avg_sources,
            'queries_with_no_sources': no_sources,
            'no_sources_percentage': (no_sources / total_queries * 100) if total_queries > 0 else 0,
            'avg_unique_pages': avg_unique_pages,
            'retrieval_diversity': avg_unique_pages / avg_sources if avg_sources > 0 else 0
        }

    def _analyze_answer_patterns(
        self,
        evaluations: List[Dict[str, Any]],
        qa_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze patterns in generated answers."""
        answer_lengths = []
        has_citations = []
        citation_counts = []

        for qa in qa_results:
            answer = qa.get('answer', '')
            answer_lengths.append(len(answer.split()))

            # Check for citations
            import re
            citations = re.findall(r'\[Page \d+\]', answer)
            has_citations.append(len(citations) > 0)
            citation_counts.append(len(citations))

        avg_length = sum(answer_lengths) / len(answer_lengths) if answer_lengths else 0
        citation_rate = sum(has_citations) / len(has_citations) if has_citations else 0
        avg_citations = sum(citation_counts) / len(citation_counts) if citation_counts else 0

        return {
            'avg_answer_length_words': avg_length,
            'citation_rate': citation_rate,
            'avg_citations_per_answer': avg_citations,
            'length_distribution': {
                'min': min(answer_lengths) if answer_lengths else 0,
                'max': max(answer_lengths) if answer_lengths else 0,
                'median': sorted(answer_lengths)[len(answer_lengths)//2] if answer_lengths else 0
            }
        }

    def _generate_llm_suggestions(
        self,
        weakness_analysis: Dict[str, Any],
        retrieval_analysis: Dict[str, Any],
        answer_analysis: Dict[str, Any],
        current_config: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Use LLM to generate improvement suggestions."""
        prompt = f"""Analyze the following QA system performance data and provide specific, actionable improvement suggestions.

**Weakness Analysis:**
Common weaknesses: {weakness_analysis.get('common_weaknesses', [])}
Common missing information: {weakness_analysis.get('common_missing_info', [])}
Low score categories: {weakness_analysis.get('low_score_categories', {})}

**Retrieval Analysis:**
{json.dumps(retrieval_analysis, indent=2)}

**Answer Pattern Analysis:**
{json.dumps(answer_analysis, indent=2)}
"""

        if current_config:
            prompt += f"\n**Current Configuration:**\n{json.dumps(current_config, indent=2)}"

        prompt += """

Based on this data, provide:

1. **Top 3 Critical Issues**: Most important problems to address
2. **Retrieval Improvements**: How to improve document retrieval
3. **Answer Generation Improvements**: How to improve answer quality
4. **Parameter Recommendations**: Specific parameter changes to try
5. **Prompt Engineering Suggestions**: How to improve system prompts

Return as JSON:
{
    "critical_issues": [
        {"issue": "description", "impact": "high/medium/low", "solution": "suggested fix"}
    ],
    "retrieval_improvements": [
        {"recommendation": "description", "expected_benefit": "description"}
    ],
    "answer_generation_improvements": [
        {"recommendation": "description", "expected_benefit": "description"}
    ],
    "parameter_recommendations": [
        {"parameter": "name", "current_value": "value", "suggested_value": "value", "rationale": "why"}
    ],
    "prompt_engineering": [
        {"area": "system/user prompt", "suggestion": "description"}
    ]
}
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert in RAG systems and information retrieval. Provide specific, actionable recommendations for improving QA system performance."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )

            content = response.choices[0].message.content
            result = json.loads(content)
            return result

        except Exception as e:
            print(f"Error generating LLM suggestions: {e}")
            return {'error': str(e)}

    def _suggest_parameter_tuning(
        self,
        evaluations: List[Dict[str, Any]],
        qa_results: List[Dict[str, Any]],
        current_config: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """Suggest specific parameter changes based on analysis."""
        suggestions = []

        # Analyze current performance
        avg_score = sum(e.get('composite_score', 0) for e in evaluations) / len(evaluations) if evaluations else 0
        avg_sources = sum(r.get('num_sources', 0) for r in qa_results) / len(qa_results) if qa_results else 0

        current_config = current_config or {}

        # TOP_K suggestions
        if avg_sources < 3:
            suggestions.append({
                'parameter': 'TOP_K',
                'current_value': current_config.get('TOP_K', 'unknown'),
                'suggested_value': min((current_config.get('TOP_K', 5) or 5) + 3, 15),
                'rationale': 'Low average source count suggests increasing retrieved documents',
                'priority': 'high'
            })

        # CHUNK_SIZE suggestions based on completeness
        avg_completeness = sum(e.get('completeness_score', 0) for e in evaluations) / len(evaluations) if evaluations else 0
        if avg_completeness < 6:
            suggestions.append({
                'parameter': 'CHUNK_SIZE',
                'current_value': current_config.get('CHUNK_SIZE', 'unknown'),
                'suggested_value': min((current_config.get('CHUNK_SIZE', 800) or 800) + 200, 1500),
                'rationale': 'Low completeness scores suggest larger chunks might provide more context',
                'priority': 'medium'
            })

        # SIMILARITY_THRESHOLD suggestions
        no_sources_count = sum(1 for r in qa_results if r.get('num_sources', 0) == 0)
        if no_sources_count > len(qa_results) * 0.1:  # More than 10% with no sources
            suggestions.append({
                'parameter': 'SIMILARITY_THRESHOLD',
                'current_value': current_config.get('SIMILARITY_THRESHOLD', 'unknown'),
                'suggested_value': max((current_config.get('SIMILARITY_THRESHOLD', 0.65) or 0.65) - 0.05, 0.5),
                'rationale': 'Many queries return no sources, suggesting threshold is too high',
                'priority': 'high'
            })

        # LLM_TEMPERATURE suggestions based on clarity
        avg_clarity = sum(e.get('clarity_score', 0) for e in evaluations) / len(evaluations) if evaluations else 0
        if avg_clarity < 7:
            suggestions.append({
                'parameter': 'LLM_TEMPERATURE',
                'current_value': current_config.get('LLM_TEMPERATURE', 'unknown'),
                'suggested_value': 0.1,
                'rationale': 'Low clarity scores suggest using lower temperature for more focused answers',
                'priority': 'medium'
            })

        return suggestions

    def _prioritize_actions(
        self,
        weakness_analysis: Dict[str, Any],
        retrieval_analysis: Dict[str, Any],
        parameter_suggestions: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Prioritize improvement actions."""
        actions = []

        # High priority: retrieval issues
        if retrieval_analysis.get('no_sources_percentage', 0) > 10:
            actions.append({
                'priority': 1,
                'action': 'Reduce SIMILARITY_THRESHOLD',
                'rationale': f"{retrieval_analysis['no_sources_percentage']:.1f}% of queries return no sources",
                'impact': 'high'
            })

        # High priority: critical weaknesses
        common_weaknesses = weakness_analysis.get('common_weaknesses', [])
        if common_weaknesses:
            top_weakness = common_weaknesses[0]
            actions.append({
                'priority': 1,
                'action': f'Address common weakness: {top_weakness[0]}',
                'rationale': f'Appears in {top_weakness[1]} evaluations',
                'impact': 'high'
            })

        # Medium priority: parameter tuning
        high_priority_params = [p for p in parameter_suggestions if p.get('priority') == 'high']
        for param in high_priority_params[:2]:
            actions.append({
                'priority': 2,
                'action': f"Tune {param['parameter']}: {param['current_value']} → {param['suggested_value']}",
                'rationale': param['rationale'],
                'impact': 'medium'
            })

        # Sort by priority
        actions.sort(key=lambda x: x['priority'])

        return actions

    def generate_improvement_report(
        self,
        suggestions: Dict[str, Any],
        output_path: str = None
    ) -> str:
        """
        Generate a human-readable improvement report.

        Args:
            suggestions: Dictionary of improvement suggestions
            output_path: Optional path to save report

        Returns:
            Report text
        """
        report = []
        report.append("=" * 80)
        report.append("IMPROVEMENT SUGGESTIONS REPORT")
        report.append("=" * 80)

        # Priority actions
        report.append("\n## PRIORITY ACTIONS\n")
        for i, action in enumerate(suggestions.get('priority_actions', [])[:5], 1):
            report.append(f"{i}. [{action['impact'].upper()}] {action['action']}")
            report.append(f"   Rationale: {action['rationale']}\n")

        # Parameter recommendations
        report.append("\n## PARAMETER TUNING RECOMMENDATIONS\n")
        for param in suggestions.get('parameter_tuning', []):
            report.append(f"- {param['parameter']}: {param['current_value']} → {param['suggested_value']}")
            report.append(f"  Rationale: {param['rationale']}\n")

        # LLM recommendations
        llm_rec = suggestions.get('llm_recommendations', {})
        if llm_rec.get('critical_issues'):
            report.append("\n## CRITICAL ISSUES\n")
            for issue in llm_rec['critical_issues']:
                report.append(f"- [{issue.get('impact', 'unknown').upper()}] {issue.get('issue', 'N/A')}")
                report.append(f"  Solution: {issue.get('solution', 'N/A')}\n")

        # Retrieval improvements
        if llm_rec.get('retrieval_improvements'):
            report.append("\n## RETRIEVAL IMPROVEMENTS\n")
            for imp in llm_rec['retrieval_improvements']:
                report.append(f"- {imp.get('recommendation', 'N/A')}")
                report.append(f"  Expected Benefit: {imp.get('expected_benefit', 'N/A')}\n")

        report.append("=" * 80)

        report_text = "\n".join(report)

        if output_path:
            with open(output_path, 'w') as f:
                f.write(report_text)
            print(f"✓ Improvement report saved to: {output_path}")

        return report_text


if __name__ == "__main__":
    # Example usage
    print("ImprovementSuggester module - use with evaluation results")
    print("See main self-learning framework for usage")
