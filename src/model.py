import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from openai import OpenAI

class Model:
    # Supported Gemini models (as of Feb 2026)
    # These are the actual available models from google.genai SDK
    SUPPORTED_MODELS = [
        "gemini-pro-latest",       # Aliased to latest pro model
        "gemini-flash-latest",     # Aliased to latest flash model  
        "gemini-2.5-pro",          # Gemini 2.5 Pro (most capable)
        "gemini-2.5-flash",        # Gemini 2.5 Flash (fast)
        "gemini-2.0-flash",        # Gemini 2.0 Flash
    ]
    
    def __init__(self):
        load_dotenv()

    @staticmethod
    def google_gemini(transcript, prompt, extra="", model_type="gemini-flash-latest"):
        """Generate content using Google Gemini API (google.genai SDK)
        
        Args:
            transcript: Video transcript text
            prompt: System prompt for the model
            extra: Additional context (e.g., video URL)
            model_type: Gemini model name (default: gemini-flash-latest)
        
        Returns:
            Generated text or tuple of (error_message, error_details)
        """
        load_dotenv()
        api_key = os.getenv("GOOGLE_GEMINI_API_KEY")
        
        if not api_key:
            return "⚠️ GOOGLE_GEMINI_API_KEY not found in environment.", "Please add your API key to the .env file"
        
        # Ensure all parameters are strings
        transcript = transcript or ""
        prompt = prompt or ""
        extra = extra or ""
        
        # Build the complete content with clear separation
        if transcript:
            full_content = f"{prompt}\n\n{extra}\n\n{transcript}"
        else:
            full_content = prompt + extra
        
        # Initialize the client with API key
        client = genai.Client(api_key=api_key)
        
        # Use supported model with fallback
        if model_type not in Model.SUPPORTED_MODELS:
            model_type = "gemini-flash-latest"  # Fallback to flash (fast and quota-friendly)
        
        try:
            # Generate content using the new SDK
            response = client.models.generate_content(
                model=model_type,
                contents=full_content
            )
            return response.text
        except Exception as e:
            # Try fallback models if the selected model fails
            fallback_models = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-flash-latest"]
            
            for fallback_model in fallback_models:
                if fallback_model != model_type:
                    try:
                        response = client.models.generate_content(
                            model=fallback_model,
                            contents=full_content
                        )
                        return response.text
                    except:
                        continue
            
            response_error = "⚠️ There is a problem with the API key or model availability."
            return response_error, f"Error: {str(e)}. Please check your API key and ensure you have access to Gemini models."
    
    @staticmethod
    def openai_chatgpt(transcript, prompt, extra=""):
        load_dotenv()
        client = OpenAI(api_key=os.getenv("OPENAI_CHATGPT_API_KEY"))
        model = "gpt-3.5-turbo"
        message = [{"role": "system", "content": prompt + extra + transcript}]
        try:
            response = client.chat.completions.create(model=model, messages=message)
            return response.choices[0].message.content
        except Exception as e:
            response_error = "⚠️ There is a problem with the API key or with python module."
            return response_error, str(e)
