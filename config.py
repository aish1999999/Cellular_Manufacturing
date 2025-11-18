"""Configuration Management for RAG Pipeline

This module provides centralized configuration for all components.
Settings can be overridden via environment variables.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Centralized configuration for RAG pipeline"""

    # Project paths
    BASE_DIR = Path(__file__).parent
    DATA_DIR = BASE_DIR / "data"
    RAW_DATA_DIR = DATA_DIR / "raw"
    PROCESSED_DATA_DIR = DATA_DIR / "processed"

    # PDF Configuration
    PDF_PATH = os.getenv("PDF_PATH", str(BASE_DIR / "Cellular_Manufacturing.pdf"))

    # Embedding Model Configuration
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    EMBEDDING_DIM = 384  # MiniLM-L6-v2 output dimension
    EMBEDDING_DEVICE = "cuda" if os.getenv("USE_GPU", "false").lower() == "true" else "cpu"

    # Text Chunking Configuration
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "800"))
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "150"))

    # Vector Database Configuration
    CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", str(BASE_DIR / "chroma_db"))
    CHROMA_COLLECTION_NAME = "cellular_manufacturing"

    # Retrieval Configuration
    TOP_K = int(os.getenv("TOP_K", "7"))
    SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", "0.65"))  # Balance between precision and recall
    USE_MMR = os.getenv("USE_MMR", "false").lower() == "true"
    MMR_LAMBDA = 0.5  # Balance between relevance and diversity (0-1)

    # LLM Configuration
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_ORG_ID = os.getenv("OPENAI_ORG_ID", None)
    LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")
    LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.2"))
    LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "800"))

    # System Prompts
    SYSTEM_PROMPT = """You are an expert assistant specializing in cellular manufacturing, lean manufacturing, and production systems.
Your role is to answer questions based on the provided context from the book.

Guidelines:
1. Use ONLY information from the provided context passages to construct your answer
2. Always cite page numbers when referencing specific information using the format [Page X]
3. If the context contains related or relevant information, synthesize it to answer the question
4. If you can infer or derive an answer from the context, do so and cite the relevant pages
5. Only say "I cannot find this information" if the context has NO relevant information at all
6. When multiple pages discuss related concepts, integrate them into a coherent answer
7. Be precise, concise, and technical when appropriate
"""

    USER_PROMPT_TEMPLATE = """Context passages from the book:
{context}

Question: {question}

Instructions:
- Carefully read all the context passages above
- Answer the question using information from the context
- Synthesize information from multiple passages if needed
- Always cite page numbers using [Page X] format for all information used
- If the context contains related information but doesn't directly answer the question, explain what the context does say that's relevant
- Only say "I cannot find this information in the provided context" if NONE of the passages are relevant to the question
- Provide a complete, well-structured answer

Answer:"""

    # Logging Configuration
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = BASE_DIR / "rag_pipeline.log"

    # Performance Configuration
    BATCH_SIZE = int(os.getenv("BATCH_SIZE", "32"))  # For batch embedding
    MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))  # API retry attempts
    TIMEOUT = int(os.getenv("TIMEOUT", "30"))  # API timeout in seconds

    @classmethod
    def validate(cls):
        """Validate critical configuration settings"""
        errors = []

        # Check for required API key
        if not cls.OPENAI_API_KEY:
            errors.append("OPENAI_API_KEY is not set. Please add it to your .env file.")

        # Check if PDF exists
        if not Path(cls.PDF_PATH).exists():
            errors.append(f"PDF file not found at: {cls.PDF_PATH}")

        # Validate numeric ranges
        if cls.CHUNK_SIZE <= 0:
            errors.append("CHUNK_SIZE must be positive")

        if cls.CHUNK_OVERLAP >= cls.CHUNK_SIZE:
            errors.append("CHUNK_OVERLAP must be less than CHUNK_SIZE")

        if not 0 <= cls.SIMILARITY_THRESHOLD <= 1:
            errors.append("SIMILARITY_THRESHOLD must be between 0 and 1")

        if cls.TOP_K <= 0:
            errors.append("TOP_K must be positive")

        if not 0 <= cls.LLM_TEMPERATURE <= 2:
            errors.append("LLM_TEMPERATURE must be between 0 and 2")

        if errors:
            raise ValueError("Configuration validation failed:\n" + "\n".join(f"  - {e}" for e in errors))

        return True

    @classmethod
    def display(cls):
        """Display current configuration (excluding sensitive data)"""
        print("=" * 60)
        print("RAG Pipeline Configuration")
        print("=" * 60)
        print(f"Embedding Model: {cls.EMBEDDING_MODEL}")
        print(f"Embedding Device: {cls.EMBEDDING_DEVICE}")
        print(f"Chunk Size: {cls.CHUNK_SIZE}")
        print(f"Chunk Overlap: {cls.CHUNK_OVERLAP}")
        print(f"Vector DB: {cls.CHROMA_PERSIST_DIR}")
        print(f"Collection: {cls.CHROMA_COLLECTION_NAME}")
        print(f"Top-K Retrieval: {cls.TOP_K}")
        print(f"Similarity Threshold: {cls.SIMILARITY_THRESHOLD}")
        print(f"LLM Model: {cls.LLM_MODEL}")
        print(f"LLM Temperature: {cls.LLM_TEMPERATURE}")
        print(f"Max Tokens: {cls.LLM_MAX_TOKENS}")
        print(f"PDF Path: {cls.PDF_PATH}")
        print(f"API Key Set: {'Yes' if cls.OPENAI_API_KEY else 'No'}")
        print("=" * 60)

    @classmethod
    def multi_k_summary_and_answer(cls, query, retriever):
        """
        Retrieve top passages for multiple K values, summarize, and answer.
        Args:
            query (str): The question to answer
            retriever (callable): Function to retrieve top-K passages (query, k) -> List[passages]
        Returns:
            dict: { 'summary': str, 'answers': dict }
        """
        k_values = [3, 5, 7, 10, 15]
        all_passages = []
        answers = {}
        for k in k_values:
            passages = retriever(query, k)
            answers[k] = passages
            all_passages.extend(passages)
        # Deduplicate passages
        unique_passages = {p['text']: p for p in all_passages}.values()
        # Form summary (simple concatenation, can be improved with LLM)
        summary = '\n'.join([p['text'] for p in unique_passages])
        return {
            'summary': summary,
            'answers': answers
        }


# Alternative embedding models from todo.md
ALTERNATIVE_EMBEDDINGS = {
    "minilm": "sentence-transformers/all-MiniLM-L6-v2",  # Current (384 dim)
    "bge-base": "BAAI/bge-base-en-v1.5",  # Better quality (768 dim)
    "e5-base": "intfloat/e5-base-v2",  # Good for QA (768 dim)
    "nv-embed": "nvidia/NV-Embed-v2",  # Advanced (1024 dim)
    "bge-m3": "BAAI/bge-m3",  # Multilingual (1024 dim)
}


if __name__ == "__main__":
    # Test configuration
    try:
        Config.validate()
        Config.display()
        print("\n✓ Configuration is valid!")
    except ValueError as e:
        print(f"\n✗ Configuration error:\n{e}")
