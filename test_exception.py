"""Test to identify ChromaDB exception type"""
import chromadb

client = chromadb.PersistentClient(path="./chroma_db")

try:
    collection = client.get_collection(name="nonexistent_collection")
except Exception as e:
    print(f"Exception type: {type(e)}")
    print(f"Exception name: {type(e).__name__}")
    print(f"Exception message: {e}")
    print(f"Exception module: {type(e).__module__}")
