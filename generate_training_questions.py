"""Generate 100 training questions from the PDF

This script extracts content from the PDF and uses LLM to generate
100 diverse questions for training/evaluating the RAG system.
"""

import json
import os
from pathlib import Path
from typing import List
import time
from dotenv import load_dotenv

from src.data_preparation.pdf_processor import PDFProcessor
from openai import OpenAI

load_dotenv()

PDF_PATH = "Cellular_Manufacturing.pdf"
OUTPUT_FILE = "training_questions.txt"
OUTPUT_JSON = "training_questions.json"
NUM_QUESTIONS = 100
QUESTIONS_PER_BATCH = 10


def extract_pdf_content(pdf_path: str) -> str:
    """Extract text from PDF"""
    print(f"Extracting content from {pdf_path}...")
    processor = PDFProcessor(pdf_path)
    pages = processor.process_pdf(clean=True, show_progress=True)
    full_text = "\n\n".join([f"[Page {p['page_num']}]\n{p['text']}" for p in pages])
    print(f"✓ Extracted {len(pages)} pages")
    return full_text


def generate_questions_batch(client: OpenAI, content_sample: str, batch_num: int,
                            num_questions: int) -> List[str]:
    """Generate a batch of questions"""
    print(f"Generating batch {batch_num} ({num_questions} questions)...")

    prompt = f"""Based on this book about Cellular Manufacturing, generate exactly {num_questions} diverse questions.

Sample content:
{content_sample[:10000]}

Requirements:
- Mix of difficulty levels: some basic, some intermediate, some advanced
- Different types: definitions, benefits, processes, comparisons, applications
- Cover different topics from the content
- Make questions specific and answerable from the book
- Each question should be clear and standalone

Generate ONLY the questions, one per line. No numbering, no extra text.
Just the questions."""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an expert at creating training questions. Generate ONLY the questions, nothing else."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.8
    )

    # Parse questions from response
    content = response.choices[0].message.content.strip()
    questions = [q.strip() for q in content.split('\n') if q.strip() and '?' in q]

    # Remove any numbering that might have been added
    cleaned_questions = []
    for q in questions:
        # Remove leading numbers/bullets
        q = q.lstrip('0123456789.-) ')
        if q and not q.startswith('Question'):
            cleaned_questions.append(q)

    print(f"✓ Generated {len(cleaned_questions)} questions")
    return cleaned_questions


def generate_all_questions(pdf_text: str, num_questions: int = 100) -> List[str]:
    """Generate all questions from PDF"""
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    all_questions = []
    questions_per_batch = QUESTIONS_PER_BATCH
    num_batches = (num_questions + questions_per_batch - 1) // questions_per_batch

    # Split PDF into sections
    text_length = len(pdf_text)
    section_size = text_length // num_batches

    for batch_num in range(1, num_batches + 1):
        start = (batch_num - 1) * section_size
        end = min(start + section_size + 2000, text_length)  # Overlap
        content_sample = pdf_text[start:end]

        # Generate questions
        batch_questions = generate_questions_batch(
            client, content_sample, batch_num, questions_per_batch
        )

        all_questions.extend(batch_questions)

        if batch_num < num_batches:
            time.sleep(1)  # Rate limiting

    # Return exact number requested
    return all_questions[:num_questions]


def save_questions(questions: List[str]):
    """Save questions to both text and JSON files"""

    # Save as simple text file
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        for question in questions:
            f.write(question + '\n')

    print(f"\n{'='*60}")
    print(f"✓ Saved {len(questions)} questions to {OUTPUT_FILE}")

    # Save as JSON (simple array)
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(questions, f, indent=2, ensure_ascii=False)

    print(f"✓ Saved {len(questions)} questions to {OUTPUT_JSON}")
    print(f"{'='*60}")


def main():
    """Main execution"""
    print("="*60)
    print("TRAINING QUESTION GENERATION")
    print("="*60)
    print(f"Target: {NUM_QUESTIONS} questions")
    print("="*60)

    # Extract PDF
    pdf_text = extract_pdf_content(PDF_PATH)

    # Generate questions
    print(f"\nGenerating {NUM_QUESTIONS} questions...")
    questions = generate_all_questions(pdf_text, NUM_QUESTIONS)

    # Save
    save_questions(questions)

    print(f"\n✓ Complete! Generated {len(questions)} questions")


if __name__ == "__main__":
    main()
