"""
Question Generation Module

This module generates questions from PDF content to enable self-supervised learning.
It extracts text chunks and generates diverse, comprehensive questions.
"""

import os
import json
from typing import List, Dict, Any
from pathlib import Path
import PyPDF2
from openai import OpenAI


class QuestionGenerator:
    """
    Generates questions from PDF content for self-supervised learning.

    Features:
    - Extracts text from PDF files
    - Generates diverse question types (factual, conceptual, analytical)
    - Ensures comprehensive coverage of document content
    - Tracks which sections have been covered
    """

    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        """
        Initialize the question generator.

        Args:
            api_key: OpenAI API key
            model: LLM model to use for question generation
        """
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.coverage_tracker = {}  # Tracks which pages/sections have been covered

    def extract_text_from_pdf(self, pdf_path: str) -> Dict[int, str]:
        """
        Extract text from PDF, organized by page.

        Args:
            pdf_path: Path to PDF file

        Returns:
            Dictionary mapping page numbers to text content
        """
        page_texts = {}

        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            total_pages = len(pdf_reader.pages)

            for page_num in range(total_pages):
                page = pdf_reader.pages[page_num]
                text = page.extract_text()
                if text.strip():  # Only store non-empty pages
                    page_texts[page_num + 1] = text  # 1-indexed pages

        return page_texts

    def generate_questions_from_text(
        self,
        text: str,
        page_num: int,
        num_questions: int = 5,
        question_types: List[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate questions from a text chunk.

        Args:
            text: Text content to generate questions from
            page_num: Page number for tracking
            num_questions: Number of questions to generate
            question_types: Types of questions (factual, conceptual, analytical)

        Returns:
            List of question dictionaries with metadata
        """
        if question_types is None:
            question_types = ["factual", "conceptual", "analytical"]

        prompt = f"""Generate {num_questions} diverse questions from the following text.

Create a mix of question types:
- Factual: Questions about specific facts, definitions, or details
- Conceptual: Questions about concepts, relationships, or principles
- Analytical: Questions requiring analysis, comparison, or evaluation

Text:
{text}

For each question, provide:
1. The question itself
2. The type (factual, conceptual, analytical)
3. The expected answer (brief, 2-3 sentences)
4. Key concepts covered

Return as JSON array with format:
[
    {{
        "question": "...",
        "type": "...",
        "expected_answer": "...",
        "concepts": ["concept1", "concept2"]
    }}
]
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert at generating educational questions from technical documents. Generate diverse, high-quality questions that test understanding at multiple levels."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                response_format={"type": "json_object"}
            )

            content = response.choices[0].message.content
            result = json.loads(content)

            # Handle different response formats
            questions = result.get('questions', result.get('data', []))

            # Add metadata
            for q in questions:
                q['page'] = page_num
                q['source_text_preview'] = text[:200] + "..."

            return questions

        except Exception as e:
            print(f"Error generating questions: {e}")
            return []

    def generate_questions_from_pdf(
        self,
        pdf_path: str,
        questions_per_page: int = 3,
        max_pages: int = None,
        output_path: str = None
    ) -> List[Dict[str, Any]]:
        """
        Generate questions from entire PDF.

        Args:
            pdf_path: Path to PDF file
            questions_per_page: Number of questions to generate per page
            max_pages: Maximum number of pages to process (None for all)
            output_path: Optional path to save questions

        Returns:
            List of all generated questions
        """
        print(f"\nExtracting text from PDF: {pdf_path}")
        page_texts = self.extract_text_from_pdf(pdf_path)

        total_pages = len(page_texts)
        if max_pages:
            total_pages = min(total_pages, max_pages)

        print(f"Processing {total_pages} pages...")

        all_questions = []

        for page_num, text in list(page_texts.items())[:total_pages]:
            print(f"  Page {page_num}/{total_pages}...", end=" ")

            # Skip if text is too short
            if len(text.strip()) < 100:
                print("(skipped - too short)")
                continue

            questions = self.generate_questions_from_text(
                text=text,
                page_num=page_num,
                num_questions=questions_per_page
            )

            all_questions.extend(questions)
            print(f"generated {len(questions)} questions")

            # Update coverage tracker
            self.coverage_tracker[page_num] = {
                'covered': True,
                'num_questions': len(questions),
                'concepts': list(set(
                    concept
                    for q in questions
                    for concept in q.get('concepts', [])
                ))
            }

        print(f"\n✓ Generated {len(all_questions)} questions from {total_pages} pages")

        # Save if output path provided
        if output_path:
            self.save_questions(all_questions, output_path)

        return all_questions

    def save_questions(self, questions: List[Dict[str, Any]], output_path: str):
        """Save questions to JSON file."""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w') as f:
            json.dump({
                'questions': questions,
                'metadata': {
                    'total_questions': len(questions),
                    'coverage': self.coverage_tracker
                }
            }, f, indent=2)

        print(f"✓ Questions saved to: {output_path}")

    def load_questions(self, questions_path: str) -> List[Dict[str, Any]]:
        """Load questions from JSON file."""
        with open(questions_path, 'r') as f:
            data = json.loads(f.read())
            return data.get('questions', data)

    def get_coverage_report(self) -> Dict[str, Any]:
        """
        Get a report on content coverage.

        Returns:
            Dictionary with coverage statistics
        """
        total_pages = len(self.coverage_tracker)
        covered_pages = sum(1 for p in self.coverage_tracker.values() if p['covered'])
        total_concepts = len(set(
            concept
            for page_data in self.coverage_tracker.values()
            for concept in page_data.get('concepts', [])
        ))

        return {
            'total_pages_processed': total_pages,
            'pages_covered': covered_pages,
            'coverage_percentage': (covered_pages / total_pages * 100) if total_pages > 0 else 0,
            'unique_concepts': total_concepts,
            'pages_detail': self.coverage_tracker
        }


if __name__ == "__main__":
    # Example usage
    import sys

    if len(sys.argv) < 2:
        print("Usage: python question_generator.py <pdf_path> [api_key]")
        sys.exit(1)

    pdf_path = sys.argv[1]
    api_key = sys.argv[2] if len(sys.argv) > 2 else os.getenv("OPENAI_API_KEY")

    if not api_key:
        print("Error: OPENAI_API_KEY not set")
        sys.exit(1)

    generator = QuestionGenerator(api_key=api_key)
    questions = generator.generate_questions_from_pdf(
        pdf_path=pdf_path,
        questions_per_page=3,
        max_pages=5,  # Test with first 5 pages
        output_path="data/evaluation/generated_questions.json"
    )

    print(f"\nCoverage Report:")
    report = generator.get_coverage_report()
    print(json.dumps(report, indent=2))
