"""Generate 100 training questions using existing RAG infrastructure"""

import json
import os
import time
from pathlib import Path

# Add project root to path
import sys
sys.path.insert(0, str(Path(__file__).parent))

from config import Config
from src.data_preparation.pdf_processor import PDFProcessor
from openai import OpenAI


def extract_pdf_content():
    """Extract PDF content using existing processor"""
    print("="*60)
    print("Extracting PDF content...")
    print("="*60)

    processor = PDFProcessor(Config.PDF_PATH)
    pages = processor.process_pdf(clean=True, show_progress=True)
    stats = processor.get_stats()

    print(f"✓ Extracted {stats['total_pages']} pages")

    return pages, stats


def generate_questions_from_pages(pages, num_questions=100):
    """Generate questions using OpenAI"""
    client = OpenAI(api_key=Config.OPENAI_API_KEY)

    print(f"\nGenerating {num_questions} questions...")
    print("="*60)

    all_questions = []
    questions_per_batch = 10
    num_batches = num_questions // questions_per_batch

    total_pages = len(pages)

    for batch in range(num_batches):
        print(f"\nBatch {batch + 1}/{num_batches}...")

        # Select pages for this batch
        start_idx = (batch * total_pages) // num_batches
        end_idx = ((batch + 1) * total_pages) // num_batches
        batch_pages = pages[start_idx:end_idx]

        # Create content sample
        content = "\n\n".join([
            f"[Page {p['page_num']}] {p['text'][:2000]}"
            for p in batch_pages[:5]  # Use first 5 pages of each batch
        ])

        # Generate questions
        prompt = f"""Based on this book about Cellular Manufacturing, generate exactly {questions_per_batch} diverse questions.

Content sample:
{content[:8000]}

Requirements:
- Mix of difficulty: basic, intermediate, advanced
- Different types: definitions, benefits, processes, comparisons, applications
- Specific and answerable from the book
- Clear and standalone questions

Generate ONLY the questions, one per line. No numbering or extra text."""

        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Generate ONLY questions, one per line."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8
            )

            # Extract questions
            content_text = response.choices[0].message.content.strip()
            questions = [
                q.strip().lstrip('0123456789.-) ')
                for q in content_text.split('\n')
                if q.strip() and '?' in q and not q.strip().startswith('Question')
            ]

            all_questions.extend(questions)
            print(f"  Generated {len(questions)} questions")

            # Rate limiting
            if batch < num_batches - 1:
                time.sleep(1)

        except Exception as e:
            print(f"  Error in batch {batch + 1}: {e}")
            continue

    return all_questions[:num_questions]


def save_questions(questions):
    """Save questions to files"""
    print(f"\n{'='*60}")
    print("Saving questions...")
    print("="*60)

    # Save as text file
    txt_file = "training_questions.txt"
    with open(txt_file, 'w', encoding='utf-8') as f:
        for q in questions:
            f.write(q + '\n')
    print(f"✓ Saved to {txt_file}")

    # Save as JSON
    json_file = "training_questions.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(questions, f, indent=2, ensure_ascii=False)
    print(f"✓ Saved to {json_file}")

    print(f"\nTotal questions: {len(questions)}")
    print("="*60)


def main():
    """Main execution"""
    print("\n" + "="*60)
    print("TRAINING QUESTION GENERATION")
    print("="*60)
    print(f"Source: {Config.PDF_PATH}")
    print(f"Target: 100 questions")
    print("="*60 + "\n")

    # Validate config
    try:
        Config.validate()
    except ValueError as e:
        print(f"Configuration error: {e}")
        return

    # Extract PDF
    pages, stats = extract_pdf_content()

    # Generate questions
    questions = generate_questions_from_pages(pages, num_questions=100)

    # Save results
    save_questions(questions)

    print("\n✓ Generation complete!")


if __name__ == "__main__":
    main()
