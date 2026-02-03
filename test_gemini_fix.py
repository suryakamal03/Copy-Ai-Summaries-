"""
Quick test to verify Gemini API integration works
Run this before starting the full Streamlit app
"""
import os
from dotenv import load_dotenv
from google import genai

def test_gemini_connection():
    """Test basic Gemini API connection and model availability"""
    load_dotenv()
    api_key = os.getenv("GOOGLE_GEMINI_API_KEY")
    
    if not api_key:
        print("❌ ERROR: GOOGLE_GEMINI_API_KEY not found in .env file")
        return False
    
    print(f"✅ API Key found: {api_key[:10]}...")
    
    try:
        # Initialize client
        client = genai.Client(api_key=api_key)
        print("✅ Gemini client initialized successfully")
        
        # Test with actual available model names
        test_models = ["gemini-pro-latest", "gemini-flash-latest", "gemini-2.5-pro", "gemini-2.5-flash"]
        
        for model_name in test_models:
            try:
                print(f"\n🧪 Testing model: {model_name}")
                response = client.models.generate_content(
                    model=model_name,
                    contents="Say 'Hello, I am working!' in one sentence."
                )
                print(f"✅ {model_name} works!")
                print(f"   Response: {response.text[:100]}")
                return True  # If any model works, we're good
            except Exception as e:
                print(f"⚠️  {model_name} failed: {str(e)[:100]}")
                continue
        
        print("\n❌ All models failed. Check your API key or model availability.")
        return False
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("GEMINI API CONNECTION TEST")
    print("=" * 60)
    
    success = test_gemini_connection()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ SUCCESS! Gemini API is working correctly.")
        print("You can now run: streamlit run app.py")
    else:
        print("❌ FAILED! Please check:")
        print("   1. GOOGLE_GEMINI_API_KEY in .env file")
        print("   2. API key is valid and has Gemini access")
        print("   3. Model names are correct (no -latest suffix)")
    print("=" * 60)
