import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# Provider configurations
PROVIDER_CONFIGS = {
    "OpenAI": {
        "models": ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"],
        "api_key": OPENAI_API_KEY,
        "free_tier": False,
        "setup_instructions": """To use OpenAI's API:
1. Create an account at https://platform.openai.com/
2. Generate an API key in your account settings
3. Add the key to your .env file as OPENAI_API_KEY"""
    },
    "Anthropic": {
        "models": ["claude-2", "claude-instant-1", "claude-3-opus", "claude-3-sonnet"],
        "api_key": ANTHROPIC_API_KEY,
        "free_tier": False,
        "setup_instructions": """To use Anthropic's API:
1. Create an account at https://console.anthropic.com/
2. Generate an API key in your account settings
3. Add the key to your .env file as ANTHROPIC_API_KEY"""
    },
    "Ollama": {
        "models": ["codellama", "deepseek-coder", "starcoder", "llama3"],
        "api_key": None,  # No API key needed
        "free_tier": True,
        "setup_instructions": """To use Ollama (completely free, local):
1. Download and install Ollama from https://ollama.ai/
2. Run Ollama on your machine
3. Pull models using: ollama pull codellama (or other models)
4. Set OLLAMA_BASE_URL in your .env file (default: http://localhost:11434)"""
    },
    "Google Gemini": {
        "models": ["gemini-1.5-flash", "gemini-1.5-pro"],
        "api_key": GEMINI_API_KEY,
        "free_tier": True,
        "setup_instructions": """To use Google Gemini API (free tier available):
1. Create an account at https://ai.google.dev/
2. Generate an API key in your Google AI Studio
3. Add the key to your .env file as GEMINI_API_KEY
4. Free tier has a limit of 15 requests per minute"""
    },
    "Groq": {
        "models": ["llama3-70b-8192", "mixtral-8x7b-32768"],
        "api_key": GROQ_API_KEY,
        "free_tier": True,
        "setup_instructions": """To use Groq API (free tier available):
1. Create an account at https://console.groq.com/
2. Generate an API key in your account settings
3. Add the key to your .env file as GROQ_API_KEY"""
    },
    "Hugging Face": {
        "models": ["microsoft/DialoGPT-medium", "codeparrot/codeparrot"],
        "api_key": HUGGINGFACE_API_KEY,
        "free_tier": True,
        "setup_instructions": """To use Hugging Face Inference API (free tier available):
1. Create an account at https://huggingface.co/
2. Generate an API key in your account settings
3. Add the key to your .env file as HUGGINGFACE_API_KEY"""
    },
    "OpenRouter": {
        "models": ["anthropic/claude-3-haiku", "meta-llama/llama-3-8b", "google/gemini-pro"],
        "api_key": OPENROUTER_API_KEY,
        "free_tier": False,  # Not free but cost-effective
        "setup_instructions": """To use OpenRouter API (cost-effective):
1. Create an account at https://openrouter.ai/
2. Generate an API key in your account settings
3. Add the key to your .env file as OPENROUTER_API_KEY
4. Provides access to multiple models with competitive pricing"""
    }
}

# Function to validate API keys
def validate_api_key(provider):
    """Validate if the API key for a provider is available"""
    if provider not in PROVIDER_CONFIGS:
        return False
    
    # Ollama doesn't need an API key
    if provider == "Ollama":
        return True
    
    return PROVIDER_CONFIGS[provider]["api_key"] is not None

# Function to get available providers
def get_available_providers():
    """Get a list of available providers with valid API keys"""
    return [provider for provider in PROVIDER_CONFIGS.keys() if validate_api_key(provider)]

# Function to get models for a provider
def get_models_for_provider(provider):
    """Get a list of models for a specific provider"""
    if provider in PROVIDER_CONFIGS:
        return PROVIDER_CONFIGS[provider]["models"]
    return []

# Function to check if a provider has a free tier
def has_free_tier(provider):
    """Check if a provider has a free tier"""
    if provider in PROVIDER_CONFIGS:
        return PROVIDER_CONFIGS[provider]["free_tier"]
    return False

# Function to get setup instructions for a provider
def get_setup_instructions(provider):
    """Get setup instructions for a specific provider"""
    if provider in PROVIDER_CONFIGS:
        return PROVIDER_CONFIGS[provider]["setup_instructions"]
    return ""