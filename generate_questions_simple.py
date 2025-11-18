"""Generate 100 training questions from the PDF - Standalone version"""

import json
import os
import time
import fitz  # PyMuPDF

# Configuration
PDF_PATH = "Cellular_Manufacturing.pdf"
OUTPUT_FILE = "training_questions.txt"
OUTPUT_JSON = "training_questions.json"
OPENAI_API_KEY = "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"


def extract_pdf_text(pdf_path):
    """Extract text from PDF"""
    print(f"Extracting content from {pdf_path}...")
    doc = fitz.open(pdf_path)

    pages_text = []
    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text()
        pages_text.append(f"[Page {page_num + 1}]\n{text}")

    print(f"✓ Extracted {len(doc)} pages")
    doc.close()

    return "\n\n".join(pages_text)


def call_openai(prompt, system_msg="You are a helpful assistant."):
    """Call OpenAI API"""
    import urllib.request
    import json

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }

    data = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.8
    }

    req = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=json.dumps(data).encode('utf-8'),
        headers=headers
    )

    with urllib.request.urlopen(req) as response:
        result = json.loads(response.read().decode('utf-8'))
        return result['choices'][0]['message']['content']


def generate_questions_batch(content_sample, batch_num, num_questions):
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

    response = call_openai(
        prompt,
        "You are an expert at creating training questions. Generate ONLY the questions, nothing else."
    )

    # Parse questions
    questions = [q.strip() for q in response.split('\n') if q.strip() and '?' in q]

    # Clean up
    cleaned = []
    for q in questions:
        q = q.lstrip('0123456789.-) ')
        if q and not q.startswith('Question'):
            cleaned.append(q)

    print(f"✓ Generated {len(cleaned)} questions")
    return cleaned


def main():
    """Main execution"""
    print("="*60)
    print("TRAINING QUESTION GENERATION")
    print("="*60)
    print(f"Target: 100 questions")
    print("="*60)

    # Extract PDF
    pdf_text = extract_pdf_text(PDF_PATH)

    # Generate questions in batches
    all_questions = []
    questions_per_batch = 10
    num_batches = 10

    text_length = len(pdf_text)
    section_size = text_length // num_batches

    for batch_num in range(1, num_batches + 1):
        start = (batch_num - 1) * section_size
        end = min(start + section_size + 2000, text_length)
        content_sample = pdf_text[start:end]

        batch_questions = generate_questions_batch(
            content_sample, batch_num, questions_per_batch
        )

        all_questions.extend(batch_questions)

        if batch_num < num_batches:
            time.sleep(1)  # Rate limiting

    # Save to text file
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        for question in all_questions[:100]:
            f.write(question + '\n')

    print(f"\n{'='*60}")
    print(f"✓ Saved {min(len(all_questions), 100)} questions to {OUTPUT_FILE}")

    # Save to JSON
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(all_questions[:100], f, indent=2, ensure_ascii=False)

    print(f"✓ Saved {min(len(all_questions), 100)} questions to {OUTPUT_JSON}")
    print(f"{'='*60}")
    print(f"\n✓ Complete!")


if __name__ == "__main__":
    main()
