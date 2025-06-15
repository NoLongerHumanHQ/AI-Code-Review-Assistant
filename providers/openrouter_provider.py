import requests
import json
import re
from utils.config import OPENROUTER_API_KEY

# Function to check if OpenRouter API is available
def is_openrouter_available():
    """Check if OpenRouter API is available"""
    return OPENROUTER_API_KEY is not None

# Function to analyze code with OpenRouter
def analyze_with_openrouter(code, language, model, prompt):
    """Analyze code using OpenRouter API"""
    if not is_openrouter_available():
        return {
            "error": "OpenRouter API key is not available",
            "setup_instructions": """To use OpenRouter API:
1. Create an account at https://openrouter.ai/
2. Generate an API key in your account settings
3. Add the key to your .env file as OPENROUTER_API_KEY"""
        }
    
    # Prepare the request payload
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "HTTP-Referer": "https://github.com/NoLongerHumanHQ/AI-Code-Review-Assistant",  # Required by OpenRouter
        "X-Title": "AI Code Review Assistant"  # Optional but recommended
    }
    
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are an expert code reviewer."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2,
        "max_tokens": 4000
    }
    
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload
        )
        
        if response.status_code == 200:
            response_data = response.json()
            result = response_data["choices"][0]["message"]["content"]
            
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
                    "error": "Failed to parse OpenRouter response as JSON",
                    "raw_response": result[:1000]  # Include part of the raw response for debugging
                }
        else:
            return {
                "error": f"OpenRouter API Error: {response.status_code}",
                "details": response.text
            }
    except Exception as e:
        return {
            "error": f"Failed to call OpenRouter API: {str(e)}",
            "details": str(e)
        }

# Function to get available models
def get_available_models():
    """Get a list of available models in OpenRouter"""
    if not is_openrouter_available():
        return []
    
    try:
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "HTTP-Referer": "https://github.com/NoLongerHumanHQ/AI-Code-Review-Assistant"
        }
        
        response = requests.get(
            "https://openrouter.ai/api/v1/models",
            headers=headers
        )
        
        if response.status_code == 200:
            models_data = response.json()["data"]
            # Filter for models that are good for code review
            recommended_models = [
                "anthropic/claude-3-haiku",
                "meta-llama/llama-3-8b",
                "google/gemini-pro",
                "anthropic/claude-3-sonnet",
                "mistralai/mistral-7b"
            ]
            
            # Return models that are in both the recommended list and available from API
            available_models = [model["id"] for model in models_data]
            return [model for model in recommended_models if model in available_models]
        else:
            # Return a default list if API call fails
            return ["anthropic/claude-3-haiku", "meta-llama/llama-3-8b", "google/gemini-pro"]
    except Exception:
        # Return a default list if API call fails
        return ["anthropic/claude-3-haiku", "meta-llama/llama-3-8b", "google/gemini-pro"]

# Function to get model pricing
def get_model_pricing(model):
    """Get pricing information for a specific model"""
    if not is_openrouter_available():
        return "Pricing information not available"
    
    try:
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "HTTP-Referer": "https://github.com/NoLongerHumanHQ/AI-Code-Review-Assistant"
        }
        
        response = requests.get(
            "https://openrouter.ai/api/v1/models",
            headers=headers
        )
        
        if response.status_code == 200:
            models_data = response.json()["data"]
            for model_data in models_data:
                if model_data["id"] == model:
                    pricing = model_data.get("pricing", {})
                    input_price = pricing.get("input", 0)
                    output_price = pricing.get("output", 0)
                    return f"Input: ${input_price}/1M tokens, Output: ${output_price}/1M tokens"
            
            return "Pricing information not available for this model"
        else:
            return "Pricing information not available"
    except Exception:
        return "Pricing information not available"

# Function to get setup instructions
def get_setup_instructions():
    """Get setup instructions for OpenRouter"""
    return """To use OpenRouter API (cost-effective):
1. Create an account at https://openrouter.ai/
2. Generate an API key in your account settings
3. Add the key to your .env file as OPENROUTER_API_KEY

Benefits of OpenRouter:
- Access to multiple AI models through a single API
- Competitive pricing compared to direct provider access
- Simplified integration for multiple models

Recommended models:
- anthropic/claude-3-haiku: Fast and cost-effective
- meta-llama/llama-3-8b: Open-source model with good performance
- google/gemini-pro: Google's powerful model

OpenRouter provides access to multiple AI providers with transparent pricing."""