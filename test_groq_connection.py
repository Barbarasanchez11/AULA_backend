"""
Simple test script to verify Groq API connection.

Run this to test that:
1. GROQ_API_KEY is correctly configured
2. Groq API is accessible
3. Basic LLM call works
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.config import settings
from langchain_groq import ChatGroq

def test_groq_connection():
    """Test basic connection to Groq API"""
    print("=" * 60)
    print("Testing Groq API Connection")
    print("=" * 60)
    
    # Check API key
    if not settings.groq_api_key:
        print("❌ ERROR: GROQ_API_KEY not found in .env")
        print("   Make sure you have GROQ_API_KEY=... in your .env file")
        return False
    
    print(f"✅ GROQ_API_KEY found: {settings.groq_api_key[:10]}...")
    print(f"✅ Model configured: {settings.groq_model}")
    print(f"✅ Temperature: {settings.groq_temperature}")
    print(f"✅ Max tokens: {settings.groq_max_tokens}")
    
    # Try to create ChatGroq instance
    try:
        print("\n📡 Creating ChatGroq client...")
        llm = ChatGroq(
            api_key=settings.groq_api_key,
            model_name=settings.groq_model,
            temperature=settings.groq_temperature,
            max_tokens=settings.groq_max_tokens
        )
        print("✅ ChatGroq client created successfully")
    except Exception as e:
        print(f"❌ ERROR creating ChatGroq client: {e}")
        return False
    
    # Try a simple test call
    try:
        print("\n🤖 Testing LLM call...")
        print("   Sending test message: 'Say hello in one word'")
        response = llm.invoke("Say hello in one word")
        print(f"✅ LLM Response: {response.content}")
        print(f"✅ Response type: {type(response)}")
        return True
    except Exception as e:
        print(f"❌ ERROR calling LLM: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_groq_connection()
    print("\n" + "=" * 60)
    if success:
        print("✅ All tests passed! Groq is configured correctly.")
    else:
        print("❌ Tests failed. Check the errors above.")
    print("=" * 60)
    sys.exit(0 if success else 1)

