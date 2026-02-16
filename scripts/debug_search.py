"""
Debug script to investigate why ChromaDB search returns 0 results
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.vector_store import VectorStore
from app.services.embeddingService import EmbeddingService
from uuid import UUID

# Initialize services
vector_store = VectorStore()
embedding_service = EmbeddingService.get_instance()
classroom_id = UUID('d74559d9-1b3b-41ef-bbae-17f136484901')

# Get collection
collection = vector_store.get_or_create_collection(classroom_id, 'quality')
print(f"📊 Collection count: {collection.count()}")
print(f"📊 Collection name: {collection.name}")

# Get a sample embedding from the collection
print("\n🔍 Getting sample embedding from collection...")
sample_results = collection.get(limit=1)
if sample_results['ids']:
    sample_id = sample_results['ids'][0]
    sample_embedding = sample_results['embeddings'][0] if sample_results.get('embeddings') else None
    sample_metadata = sample_results['metadatas'][0] if sample_results.get('metadatas') else None
    
    print(f"   Sample ID: {sample_id}")
    print(f"   Sample embedding length: {len(sample_embedding) if sample_embedding else 'None'}")
    print(f"   Sample metadata: {sample_metadata}")
    
    # Try to search using the sample embedding itself
    print("\n🔍 Testing search with sample embedding as query...")
    search_results = collection.query(
        query_embeddings=[sample_embedding],
        n_results=3,
        include=['metadatas', 'distances']
    )
    
    print(f"   Search results keys: {search_results.keys()}")
    print(f"   Search results IDs: {search_results.get('ids', [])}")
    print(f"   Number of results: {len(search_results.get('ids', [[]])[0]) if search_results.get('ids') else 0}")
    
    if search_results.get('ids') and len(search_results['ids'][0]) > 0:
        print(f"   ✅ Search works with sample embedding!")
        for i, result_id in enumerate(search_results['ids'][0]):
            distance = search_results['distances'][0][i] if search_results.get('distances') else None
            print(f"      Result {i+1}: ID={result_id}, Distance={distance}")
    else:
        print(f"   ❌ Search failed even with sample embedding!")

# Generate query embedding
print("\n🔍 Generating query embedding...")
query_text = 'sobrecarga sensorial'
query_embedding = embedding_service.generate_quality_embedding(query_text)
query_embedding_list = query_embedding.tolist()

print(f"   Query text: '{query_text}'")
print(f"   Query embedding shape: {query_embedding.shape}")
print(f"   Query embedding length: {len(query_embedding_list)}")
print(f"   Query embedding type: {type(query_embedding)}")
print(f"   Query embedding list type: {type(query_embedding_list)}")

# Check if dimensions match
if sample_embedding:
    sample_dim = len(sample_embedding)
    query_dim = len(query_embedding_list)
    print(f"\n📏 Dimension check:")
    print(f"   Sample embedding dimension: {sample_dim}")
    print(f"   Query embedding dimension: {query_dim}")
    if sample_dim != query_dim:
        print(f"   ❌ DIMENSION MISMATCH! This is the problem!")
    else:
        print(f"   ✅ Dimensions match")

# Try the actual search
print("\n🔍 Testing actual search with query embedding...")
try:
    search_results = collection.query(
        query_embeddings=[query_embedding_list],
        n_results=3,
        include=['metadatas', 'distances']
    )
    
    print(f"   Search results type: {type(search_results)}")
    print(f"   Search results keys: {search_results.keys()}")
    print(f"   Search results: {search_results}")
    
    if search_results.get('ids'):
        ids_list = search_results['ids']
        print(f"   IDs list type: {type(ids_list)}")
        print(f"   IDs list: {ids_list}")
        if ids_list and len(ids_list) > 0:
            print(f"   IDs[0] type: {type(ids_list[0])}")
            print(f"   IDs[0]: {ids_list[0]}")
            print(f"   IDs[0] length: {len(ids_list[0])}")
        else:
            print(f"   ❌ IDs list is empty!")
    else:
        print(f"   ❌ No 'ids' key in results!")
        
except Exception as e:
    print(f"   ❌ Error during search: {e}")
    import traceback
    traceback.print_exc()


