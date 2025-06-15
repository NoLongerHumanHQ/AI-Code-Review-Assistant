import os
import json
import re
from utils.config import GEMINI_API_KEY

# Function to check if Gemini API is available
def is_gemini_available():
    """Check if Google Gemini API is available"""
    return GEMINI_API_KEY is not None

# Function to analyze code with Google Gemini
def analyze_with_gemini(code, language, model, prompt):
    """Analyze code using Google Gemini API"""
    if not is_gemini_available():
        return {
            "error": "Google Gemini API key is not available",
            "setup_instructions": """To use Google Gemini API:
1. Create an account at https://ai.google.dev/
2. Generate an API key in your Google AI Studio
3. Add the key to your .env file as GEMINI_API_KEY"""
        }
    
    try:
        # Import the library here to avoid dependency issues if not installed
        import google.generativeai as genai
        
        # Configure the API
        genai.configure(api_key=GEMINI_API_KEY)
        
        # Select the model based on the input
        if model == "gemini-1.5-flash":
            gemini_model = genai.GenerativeModel('gemini-1.5-flash')
        elif model == "gemini-1.5-pro":
            gemini_model = genai.GenerativeModel('gemini-1.5-pro')
        else:
            # Default to gemini-1.5-flash if model not recognized
            gemini_model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Set generation config
        generation_config = {
            "temperature": 0.2,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 8192,
        }
        
        # Generate the response
        response = gemini_model.generate_content(
            prompt,
            generation_config=generation_config
        )
        
        # Extract the text from the response
        result = response.text
        
        # Try to extract JSON from the response
        try:
            # First, try to parse the entire response as JSON
            return json.loads(result)
        except json.JSONDecodeError:
            # If that fails, try to extract JSON from the text
            json_match = re.search(r'```json\s*([\s\S]*?)\s*```|({[\s\S]*})', result)
            if json_match:
                json_str = json_match.group(1) or json_match.group(2)
                try:
                    return json.loads(json_str.strip())
                except json.JSONDecodeError:
                    pass
            
            # If we couldn't extract valid JSON, return an error
            return {
                "error": "Failed to parse Gemini response as JSON",
                "raw_response": result[:1000]  # Include part of the raw response for debugging
            }
    except ImportError:
        return {
            "error": "Google Generative AI library is not installed",
            "setup_instructions": "Install the required library using: pip install google-generativeai>=0.3.0"
        }
    except Exception as e:
        # Handle rate limiting errors
        if "quota" in str(e).lower() or "rate limit" in str(e).lower():
            return {
                "error": "Google Gemini API rate limit exceeded",
                "details": str(e),
                "setup_instructions": """The free tier of Google Gemini API has a limit of 15 requests per minute. Please wait and try again later."""
            }
        else:
            return {
                "error": f"Failed to call Google Gemini API: {str(e)}",
                "details": str(e)
            }

# Function to get available models
def get_available_models():
    """Get a list of available models in Google Gemini"""
    if not is_gemini_available():
        return []
    
    # Fixed list of available models
    return ["gemini-1.5-flash", "gemini-1.5-pro"]

# Function to get setup instructions
def get_setup_instructions():
    """Get setup instructions for Google Gemini"""
    return """To use Google Gemini API (free tier available):
1. Create an account at https://ai.google.dev/
2. Generate an API key in your Google AI Studio
3. Add the key to your .env file as GEMINI_API_KEY

Free tier limitations:
- 15 requests per minute
- 60 requests per day for gemini-1.5-pro
- 120 requests per day for gemini-1.5-flash

Recommended models:
- gemini-1.5-flash: Faster, more efficient for code review
- gemini-1.5-pro: More comprehensive analysis but slower

Google Gemini provides high-quality AI capabilities with a generous free tier."""