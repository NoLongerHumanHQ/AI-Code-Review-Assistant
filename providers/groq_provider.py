import os
import json
import re
from utils.config import GROQ_API_KEY

# Function to check if Groq API is available
def is_groq_available():
    """Check if Groq API is available"""
    return GROQ_API_KEY is not None

# Function to analyze code with Groq
def analyze_with_groq(code, language, model, prompt):
    """Analyze code using Groq API"""
    if not is_groq_available():
        return {
            "error": "Groq API key is not available",
            "setup_instructions": """To use Groq API:
1. Create an account at https://console.groq.com/
2. Generate an API key in your account settings
3. Add the key to your .env file as GROQ_API_KEY"""
        }
    
    try:
        # Import the library here to avoid dependency issues if not installed
        from groq import Groq
        
        # Initialize the client
        client = Groq(api_key=GROQ_API_KEY)
        
        # Create the chat completion
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are an expert code reviewer."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=4096
        )
        
        # Extract the result
        result = response.choices[0].message.content
        
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
                "error": "Failed to parse Groq response as JSON",
                "raw_response": result[:1000]  # Include part of the raw response for debugging
            }
    except ImportError:
        return {
            "error": "Groq library is not installed",
            "setup_instructions": "Install the required library using: pip install groq>=0.4.0"
        }
    except Exception as e:
        return {
            "error": f"Failed to call Groq API: {str(e)}",
            "details": str(e)
        }

# Function to get available models
def get_available_models():
    """Get a list of available models in Groq"""
    if not is_groq_available():
        return []
    
    # Fixed list of available models
    return ["llama3-70b-8192", "mixtral-8x7b-32768"]

# Function to get setup instructions
def get_setup_instructions():
    """Get setup instructions for Groq"""
    return """To use Groq API (free tier available):
1. Create an account at https://console.groq.com/
2. Generate an API key in your account settings
3. Add the key to your .env file as GROQ_API_KEY

Free tier includes:
- Limited number of requests per day
- Access to high-quality models

Recommended models:
- llama3-70b-8192: High-quality model for code review
- mixtral-8x7b-32768: Fast and efficient for code analysis

Groq is known for its extremely fast inference speeds, making it ideal for quick code reviews."""