"""Script to safely delete and reset ChromaDB database"""
import shutil
from pathlib import Path

def cleanup_chromadb():
    """Delete the ChromaDB directory to start fresh"""
    chroma_path = Path("./chroma_db")

    if chroma_path.exists():
        print(f"Found ChromaDB directory: {chroma_path}")
        print(f"Deleting...")

        try:
            shutil.rmtree(chroma_path)
            print(f"✓ Successfully deleted {chroma_path}")
            print("\nNext steps:")
            print("  1. Run: python3 main.py --rebuild-index")
            print("  2. Wait for indexing to complete (2-5 minutes)")
            print("  3. Verify: python3 main.py --stats")
            print("  4. Test: python3 main.py --query 'What is cellular manufacturing?'")
        except Exception as e:
            print(f"✗ Error deleting directory: {e}")
            print(f"Try manually deleting the 'chroma_db' folder")
    else:
        print(f"ChromaDB directory does not exist: {chroma_path}")
        print("This is expected. Now run: python3 main.py --rebuild-index")

if __name__ == "__main__":
    cleanup_chromadb()
