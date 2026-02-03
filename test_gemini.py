import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GOOGLE_GEMINI_API_KEY")
print(f"API Key loaded: {api_key[:20]}..." if api_key else "No API key found")

try:
    client = genai.Client(api_key=api_key)
    print("✓ Client created successfully")
    
    response = client.models.generate_content(
        model="gemini-flash-latest",
        contents="Say hello"
    )
    print(f"✓ API Response: {response.text}")
    
except Exception as e:
    print(f"✗ Error: {type(e).__name__}")
    print(f"✗ Message: {str(e)}")
