"""Test script to identify import issues"""

import sys
print(f"Python version: {sys.version}")
print(f"Python executable: {sys.executable}")
print("\nTesting imports...\n")

try:
    import torch
    print(f"✓ torch {torch.__version__}")
except ImportError as e:
    print(f"✗ torch: {e}")

try:
    import sentence_transformers
    print(f"✓ sentence_transformers {sentence_transformers.__version__}")
except ImportError as e:
    print(f"✗ sentence_transformers: {e}")

try:
    import transformers
    print(f"✓ transformers {transformers.__version__}")
except ImportError as e:
    print(f"✗ transformers: {e}")

try:
    import langchain
    print(f"✓ langchain")
except ImportError as e:
    print(f"✗ langchain: {e}")

try:
    import chromadb
    print(f"✓ chromadb {chromadb.__version__}")
except ImportError as e:
    print(f"✗ chromadb: {e}")

try:
    import fitz
    print(f"✓ PyMuPDF (fitz) {fitz.__version__}")
except ImportError as e:
    print(f"✗ PyMuPDF (fitz): {e}")

try:
    import openai
    print(f"✓ openai {openai.__version__}")
except ImportError as e:
    print(f"✗ openai: {e}")

try:
    import pandas
    print(f"✓ pandas {pandas.__version__}")
except ImportError as e:
    print(f"✗ pandas: {e}")

try:
    import numpy
    print(f"✓ numpy {numpy.__version__}")
except ImportError as e:
    print(f"✗ numpy: {e}")

try:
    from dotenv import load_dotenv
    print(f"✓ python-dotenv")
except ImportError as e:
    print(f"✗ python-dotenv: {e}")

try:
    import tqdm
    print(f"✓ tqdm {tqdm.__version__}")
except ImportError as e:
    print(f"✗ tqdm: {e}")

print("\nTesting configuration...")
try:
    from config import Config
    Config.validate()
    print("✓ Configuration is valid")
except Exception as e:
    print(f"✗ Configuration error: {e}")

print("\nTesting RAG pipeline import...")
try:
    from src.rag_pipeline import RAGPipeline
    print("✓ RAGPipeline imports successfully")
except Exception as e:
    print(f"✗ RAGPipeline import error: {e}")
    import traceback
    traceback.print_exc()
