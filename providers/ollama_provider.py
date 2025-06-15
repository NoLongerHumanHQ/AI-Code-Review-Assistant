import requests
import json
import os
from utils.config import OLLAMA_BASE_URL

# Function to check if Ollama is running locally
def is_ollama_running():
    """Check if Ollama is running locally"""
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=2)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

# Function to get available Ollama models
def get_available_models():
    """Get a list of available models in Ollama"""
    if not is_ollama_running():
        return []
    
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags")
        if response.status_code == 200:
            models = response.json().get("models", [])
            return [model["name"] for model in models]
        return []
    except requests.exceptions.RequestException:
        return []

# Function to analyze code with Ollama
def analyze_with_ollama(code, language, model, prompt):
    """Analyze code using Ollama API"""
    if not is_ollama_running():
        return {
            "error": "Ollama is not running",
            "setup_instructions": """To use Ollama:
1. Download and install Ollama from https://ollama.ai/
2. Run Ollama on your machine
3. Pull models using: ollama pull codellama (or other models)
4. Ensure Ollama is running on http://localhost:11434 (default)"""
        }
    
    # Check if the model is available
    available_models = get_available_models()
    if model not in available_models:
        return {
            "error": f"Model '{model}' is not available in Ollama",
            "setup_instructions": f"""To use the {model} model:
1. Make sure Ollama is running
2. Pull the model using: ollama pull {model}
3. Try again after the model is downloaded"""
        }
    
    # Prepare the request payload
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.2,
            "num_predict": 4096  # Increase token limit for longer responses
        }
    }
    
    try:
        response = requests.post(f"{OLLAMA_BASE_URL}/api/generate", json=payload)
        
        if response.status_code == 200:
            result = response.json().get("response", "")
            
            # Try to extract JSON from the response
            try:
                # First, try to parse the entire response as JSON
                return json.loads(result)
            except json.JSONDecodeError:
                # If that fails, try to extract JSON from the text
                json_match = None
                # Look for JSON pattern with curly braces
                start_idx = result.find('{')
                end_idx = result.rfind('}')
                
                if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                    json_str = result[start_idx:end_idx+1]
                    try:
                        return json.loads(json_str)
                    except json.JSONDecodeError:
                        pass
                
                # If we couldn't extract valid JSON, return an error
                return {
                    "error": "Failed to parse Ollama response as JSON",
                    "raw_response": result[:1000]  # Include part of the raw response for debugging
                }
        else:
            return {
                "error": f"Ollama API Error: {response.status_code}",
                "details": response.text
            }
    except requests.exceptions.RequestException as e:
        return {
            "error": f"Failed to call Ollama API: {str(e)}",
            "setup_instructions": """Make sure Ollama is running properly. If you're having issues:
1. Restart the Ollama application
2. Check if the URL is correct (default: http://localhost:11434)
3. Ensure your firewall isn't blocking the connection"""
        }

# Function to get setup instructions
def get_setup_instructions():
    """Get setup instructions for Ollama"""
    return """To use Ollama (completely free, local):
1. Download and install Ollama from https://ollama.ai/
2. Run Ollama on your machine
3. Pull models using: ollama pull codellama (or other models)
4. Set OLLAMA_BASE_URL in your .env file (default: http://localhost:11434)

Recommended models for code review:
- codellama: Good general-purpose code model
- deepseek-coder: Specialized for code understanding
- starcoder: Optimized for multiple programming languages
- llama3: Good for general code review

Ollama provides completely free, offline AI capabilities running on your local machine."""