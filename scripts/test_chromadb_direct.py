"""
Direct test of ChromaDB to diagnose search issues
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.vector_store import VectorStore
from app.services.embeddingService import EmbeddingService
from uuid import UUID

print("="*70)
print("Direct ChromaDB Search Test")
print("="*70)

# Initialize
vector_store = VectorStore()
embedding_service = EmbeddingService.get_instance()
classroom_id = UUID('d74559d9-1b3b-41ef-bbae-17f136484901')

# Get collection
print("\n1. Getting collection...")
collection = vector_store.get_or_create_collection(classroom_id, 'quality')
print(f"   Collection name: {collection.name}")
print(f"   Collection count: {collection.count()}")

# Get a sample embedding
print("\n2. Getting sample embedding from collection...")
sample = collection.get(limit=1)
if not sample['ids']:
    print("   ❌ No embeddings in collection!")
    sys.exit(1)

sample_id = sample['ids'][0]
sample_embedding = sample['embeddings'][0] if sample.get('embeddings') else None
print(f"   Sample ID: {sample_id}")
print(f"   Sample embedding dimension: {len(sample_embedding) if sample_embedding else 'None'}")

# Test 1: Search with sample embedding itself
print("\n3. Test 1: Search using sample embedding as query...")
try:
    results1 = collection.query(
        query_embeddings=[sample_embedding],
        n_results=3
    )
    print(f"   Results keys: {results1.keys()}")
    print(f"   IDs returned: {len(results1.get('ids', [[]])[0]) if results1.get('ids') else 0}")
    if results1.get('ids') and len(results1['ids'][0]) > 0:
        print(f"   ✅ Test 1 PASSED - Found {len(results1['ids'][0])} results")
        for i, rid in enumerate(results1['ids'][0]):
            dist = results1['distances'][0][i] if results1.get('distances') else None
            print(f"      Result {i+1}: {rid}, distance={dist}")
    else:
        print(f"   ❌ Test 1 FAILED - No results")
        print(f"   Full results: {results1}")
except Exception as e:
    print(f"   ❌ Test 1 ERROR: {e}")
    import traceback
    traceback.print_exc()

# Test 2: Generate query embedding and search
print("\n4. Test 2: Generate query embedding and search...")
query_text = "sobrecarga sensorial"
print(f"   Query text: '{query_text}'")
query_embedding = embedding_service.generate_quality_embedding(query_text)
query_embedding_list = query_embedding.tolist()
print(f"   Query embedding dimension: {len(query_embedding_list)}")

# Check dimension match
if sample_embedding and len(sample_embedding) != len(query_embedding_list):
    print(f"   ❌ DIMENSION MISMATCH!")
    print(f"      Sample: {len(sample_embedding)}, Query: {len(query_embedding_list)}")
    sys.exit(1)
else:
    print(f"   ✅ Dimensions match: {len(query_embedding_list)}")

try:
    results2 = collection.query(
        query_embeddings=[query_embedding_list],
        n_results=3,
        include=['metadatas', 'distances']
    )
    print(f"   Results type: {type(results2)}")
    print(f"   Results keys: {results2.keys()}")
    
    if results2.get('ids'):
        ids = results2['ids']
        print(f"   IDs type: {type(ids)}")
        print(f"   IDs: {ids}")
        if ids and len(ids) > 0:
            print(f"   IDs[0] type: {type(ids[0])}")
            print(f"   IDs[0]: {ids[0]}")
            print(f"   IDs[0] length: {len(ids[0])}")
            
            if len(ids[0]) > 0:
                print(f"   ✅ Test 2 PASSED - Found {len(ids[0])} results")
                for i, rid in enumerate(ids[0]):
                    dist = results2['distances'][0][i] if results2.get('distances') else None
                    similarity = 1.0 - (dist / 2.0) if dist is not None else None
                    print(f"      Result {i+1}: {rid}, distance={dist}, similarity={similarity}")
            else:
                print(f"   ❌ Test 2 FAILED - IDs[0] is empty")
        else:
            print(f"   ❌ Test 2 FAILED - IDs list is empty")
    else:
        print(f"   ❌ Test 2 FAILED - No 'ids' key in results")
        print(f"   Full results: {results2}")
        
except Exception as e:
    print(f"   ❌ Test 2 ERROR: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*70)




