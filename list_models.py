"""
List available Gemini models using the new google.genai SDK
"""
import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
api_key = os.getenv("GOOGLE_GEMINI_API_KEY")

if not api_key:
    print("❌ API Key not found")
    exit(1)

try:
    client = genai.Client(api_key=api_key)
    
    # Try to list available models
    print("Attempting to list available models...")
    models = client.models.list()
    
    print("\n✅ Available Gemini models:")
    print("=" * 60)
    for model in models:
        print(f"  - {model.name}")
        if hasattr(model, 'supported_generation_methods'):
            print(f"    Methods: {model.supported_generation_methods}")
    print("=" * 60)
    
except Exception as e:
    print(f"❌ Error listing models: {e}")
    print("\nTrying alternative approach...")
    
    # Try some common model name formats
    test_formats = [
        "gemini-1.5-pro",
        "models/gemini-1.5-pro", 
        "gemini-1.5-flash-002",
        "gemini-1.5-pro-002",
        "gemini-2.0-flash-exp",
    ]
    
    for model_name in test_formats:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents="Hi"
            )
            print(f"✅ WORKS: {model_name}")
        except Exception as err:
            print(f"❌ FAILS: {model_name} - {str(err)[:80]}")
