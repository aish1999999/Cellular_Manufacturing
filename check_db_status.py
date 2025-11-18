"""Diagnostic script to check ChromaDB status"""
import chromadb
from pathlib import Path
import json

def check_database_status():
    """Check if ChromaDB has indexed documents"""

    chroma_path = "./chroma_db"
    chunks_path = "./data/processed/chunks.json"

    print("="*60)
    print("CHROMADB DATABASE STATUS CHECK")
    print("="*60)

    # Check chunks.json
    if Path(chunks_path).exists():
        try:
            with open(chunks_path, 'r') as f:
                chunks = json.load(f)
            print(f"✓ chunks.json exists with {len(chunks)} chunks")
        except Exception as e:
            print(f"⚠ chunks.json exists but could not be read: {e}")
    else:
        print(f"✗ chunks.json does not exist: {chunks_path}")

    # Check if directory exists
    if not Path(chroma_path).exists():
        print(f"✗ ChromaDB directory does not exist: {chroma_path}")
        print("\n" + "="*60)
        print("DIAGNOSIS: Database not initialized")
        print("="*60)
        print("Action needed: Run 'python3 main.py --rebuild-index'")
        return

    print(f"✓ ChromaDB directory exists: {chroma_path}")

    try:
        # Connect to ChromaDB
        client = chromadb.PersistentClient(path=chroma_path)
        print(f"✓ Successfully connected to ChromaDB")

        # List all collections
        collections = client.list_collections()
        print(f"\nFound {len(collections)} collection(s):")

        if not collections:
            print("  ✗ No collections found!")
            print("\n" + "="*60)
            print("DIAGNOSIS: ChromaDB exists but has no collections")
            print("="*60)
            print("Action needed: Run 'python3 main.py --rebuild-index'")
            return

        # Check each collection
        for collection in collections:
            print(f"\n  Collection: {collection.name}")
            print(f"  ID: {collection.id}")
            print(f"  Metadata: {collection.metadata}")

            # Get document count
            count = collection.count()
            print(f"  Document count: {count}")

            if count == 0:
                print(f"  ✗ Collection is EMPTY!")
                print("\n" + "="*60)
                print("DIAGNOSIS: Collection exists but contains NO documents")
                print("="*60)
                print("This means indexing was started but never completed.")
                print("\nSolution:")
                print("  1. Delete the chroma_db folder: python3 cleanup_db.py")
                print("  2. Rebuild index: python3 main.py --rebuild-index")
            else:
                print(f"  ✓ Collection has {count} documents")

                # Sample a document to verify content
                try:
                    sample = collection.peek(limit=3)
                    if sample and sample['ids']:
                        print(f"\n  Sample chunk IDs: {sample['ids'][:3]}")
                        if sample['documents']:
                            preview = sample['documents'][0][:100]
                            print(f"  Sample text preview: {preview}...")
                        if sample['metadatas']:
                            print(f"  Sample metadata: {sample['metadatas'][0]}")
                except Exception as e:
                    print(f"  Warning: Could not peek collection: {e}")

        print("\n" + "="*60)
        print("SUMMARY")
        print("="*60)

        total_docs = sum(c.count() for c in collections)
        if total_docs > 0:
            print(f"✓ Database is properly indexed with {total_docs} documents")
            print("\n✓ READY TO USE!")
            print("  You can now run queries:")
            print("  python3 main.py --query 'What is cellular manufacturing?'")
        else:
            print("✗ Database has NO documents")
            print("\n✗ PROBLEM: Empty database")
            print("  Solution:")
            print("  1. python3 cleanup_db.py")
            print("  2. python3 main.py --rebuild-index")

        # Check for target collection specifically
        print("\n" + "="*60)
        print("TARGET COLLECTION CHECK")
        print("="*60)
        try:
            target = client.get_collection(name='cellular_manufacturing')
            count = target.count()
            print(f"Collection 'cellular_manufacturing': {count} documents")

            if count == 0:
                print("✗ Target collection is EMPTY - rebuild needed!")
            else:
                print(f"✓ Target collection ready with {count} documents")
        except Exception as e:
            print(f"✗ Target collection 'cellular_manufacturing' not found: {e}")

    except Exception as e:
        print(f"\n✗ Error connecting to ChromaDB: {e}")
        print(f"\n  This might indicate a corrupted database")
        print(f"  Solution:")
        print(f"  1. python3 cleanup_db.py")
        print(f"  2. python3 main.py --rebuild-index")

if __name__ == "__main__":
    check_database_status()
