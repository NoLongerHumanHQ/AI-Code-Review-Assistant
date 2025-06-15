import requests
import json
import re
from utils.config import HUGGINGFACE_API_KEY

# Function to check if Hugging Face API is available
def is_huggingface_available():
    """Check if Hugging Face API is available"""
    return HUGGINGFACE_API_KEY is not None

# Function to analyze code with Hugging Face
def analyze_with_huggingface(code, language, model, prompt):
    """Analyze code using Hugging Face Inference API"""
    if not is_huggingface_available():
        return {
            "error": "Hugging Face API key is not available",
            "setup_instructions": """To use Hugging Face Inference API:
1. Create an account at https://huggingface.co/
2. Generate an API key in your account settings
3. Add the key to your .env file as HUGGINGFACE_API_KEY"""
        }
    
    # Prepare the request payload
    headers = {
        "Authorization": f"Bearer {HUGGINGFACE_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Different payload structure based on model
    if "codeparrot" in model:
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 1024,
                "temperature": 0.2,
                "return_full_text": False
            }
        }
    else:  # Default for most models like DialoGPT
        payload = {
            "inputs": {
                "text": prompt
            },
            "parameters": {
                "max_new_tokens": 1024,
                "temperature": 0.2,
                "return_full_text": False
            }
        }
    
    try:
        # API endpoint based on the model
        api_url = f"https://api-inference.huggingface.co/models/{model}"
        
        response = requests.post(
            api_url,
            headers=headers,
            json=payload
        )
        
        if response.status_code == 200:
            # Extract result based on model response format
            try:
                response_data = response.json()
                
                # Handle different response formats
                if isinstance(response_data, list) and len(response_data) > 0:
                    if isinstance(response_data[0], dict) and "generated_text" in response_data[0]:
                        result = response_data[0]["generated_text"]
                    else:
                        result = str(response_data[0])
                elif isinstance(response_data, dict) and "generated_text" in response_data:
                    result = response_data["generated_text"]
                else:
                    result = str(response_data)
                
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
                        "error": "Failed to parse Hugging Face response as JSON",
                        "raw_response": result[:1000]  # Include part of the raw response for debugging
                    }
            except json.JSONDecodeError:
                return {
                    "error": "Failed to parse Hugging Face response",
                    "raw_response": response.text[:1000]
                }
        elif response.status_code == 429:
            return {
                "error": "Hugging Face API rate limit exceeded",
                "setup_instructions": """The free tier of Hugging Face Inference API has rate limits. Please wait and try again later."""
            }
        else:
            return {
                "error": f"Hugging Face API Error: {response.status_code}",
                "details": response.text
            }
    except Exception as e:
        return {
            "error": f"Failed to call Hugging Face API: {str(e)}",
            "details": str(e)
        }

# Function to get available models
def get_available_models():
    """Get a list of available models in Hugging Face"""
    if not is_huggingface_available():
        return []
    
    # Fixed list of recommended models for code review
    return ["microsoft/DialoGPT-medium", "codeparrot/codeparrot"]

# Function to get setup instructions
def get_setup_instructions():
    """Get setup instructions for Hugging Face"""
    return """To use Hugging Face Inference API (free tier available):
1. Create an account at https://huggingface.co/
2. Generate an API key in your account settings
3. Add the key to your .env file as HUGGINGFACE_API_KEY

Free tier limitations:
- Rate limits apply
- Limited compute resources

Recommended models:
- microsoft/DialoGPT-medium: Good for general code review
- codeparrot/codeparrot: Specialized for code understanding

Hugging Face provides access to thousands of open-source models with a free tier for experimentation."""