import streamlit as st
import requests
import os
import tempfile
import json
from dotenv import load_dotenv
import time
import re

# Import utility modules
from utils.config import (
    get_available_providers, 
    get_models_for_provider, 
    has_free_tier, 
    get_setup_instructions,
    validate_api_key
)
from utils.prompts import create_review_prompt

# Import provider modules
from providers.ollama_provider import analyze_with_ollama, is_ollama_running
from providers.gemini_provider import analyze_with_gemini, is_gemini_available
from providers.groq_provider import analyze_with_groq, is_groq_available
from providers.huggingface_provider import analyze_with_huggingface, is_huggingface_available
from providers.openrouter_provider import analyze_with_openrouter, is_openrouter_available, get_model_pricing

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="AI Code Review Assistant",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
    }
    .severity-critical {
        color: #ff4b4b;
        font-weight: bold;
    }
    .severity-high {
        color: #ffa500;
        font-weight: bold;
    }
    .severity-medium {
        color: #ffce5c;
        font-weight: bold;
    }
    .severity-low {
        color: #5cb85c;
        font-weight: bold;
    }
    .code-block {
        background-color: #f0f0f0;
        border-radius: 3px;
        padding: 8px;
        font-family: monospace;
        white-space: pre-wrap;
        margin-bottom: 10px;
    }
    .feedback-section {
        margin: 10px 0;
        padding: 10px;
        border-left: 3px solid #ccc;
    }
    .free-tier-badge {
        background-color: #5cb85c;
        color: white;
        padding: 2px 6px;
        border-radius: 3px;
        font-size: 0.8em;
        margin-left: 5px;
    }
    .provider-status {
        font-size: 0.9em;
        margin-top: 5px;
    }
    .status-available {
        color: #5cb85c;
    }
    .status-unavailable {
        color: #ff4b4b;
    }
</style>
""", unsafe_allow_html=True)

# App title and description
st.title("AI Code Review Assistant")
st.markdown("Upload or paste your code to get professional feedback, best practices, and improvement suggestions.")

# Sidebar for settings
with st.sidebar:
    st.header("Settings")
    
    # API Provider selection
    available_providers = ["OpenAI", "Anthropic", "Ollama", "Google Gemini", "Groq", "Hugging Face", "OpenRouter"]
    
    # Check provider availability
    provider_status = {
        "OpenAI": validate_api_key("OpenAI"),
        "Anthropic": validate_api_key("Anthropic"),
        "Ollama": is_ollama_running(),
        "Google Gemini": is_gemini_available(),
        "Groq": is_groq_available(),
        "Hugging Face": is_huggingface_available(),
        "OpenRouter": is_openrouter_available()
    }
    
    # Add free tier indicators to provider names
    provider_display_names = []
    for provider in available_providers:
        if has_free_tier(provider):
            provider_display_names.append(f"{provider} 🆓")
        else:
            provider_display_names.append(provider)
    
    # Provider selection with free tier indicators
    selected_provider_index = st.selectbox(
        "Select API Provider",
        range(len(provider_display_names)),
        format_func=lambda i: provider_display_names[i]
    )
    
    api_provider = available_providers[selected_provider_index]
    
    # Show provider status
    if provider_status[api_provider]:
        st.markdown(f"<div class='provider-status status-available'>✅ {api_provider} is available</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='provider-status status-unavailable'>❌ {api_provider} is not available</div>", unsafe_allow_html=True)
        with st.expander("Setup Instructions"):
            st.markdown(get_setup_instructions(api_provider))
    
    # API Key input (not needed for Ollama)
    if api_provider != "Ollama":
        api_key_env_var = f"{api_provider.upper().replace(' ', '_')}_API_KEY"
        if api_provider == "Google Gemini":
            api_key_env_var = "GEMINI_API_KEY"
            
        api_key = st.text_input(
            "API Key",
            type="password",
            value=os.getenv(api_key_env_var, ""),
            help=f"Enter your API key for {api_provider}"
        )
    else:
        api_key = None  # No API key needed for Ollama
        # Show Ollama status
        if is_ollama_running():
            st.success("Ollama is running locally")
        else:
            st.error("Ollama is not running")
            with st.expander("Ollama Setup Instructions"):
                st.markdown(get_setup_instructions("Ollama"))
    
    # Model selection based on provider
    models = get_models_for_provider(api_provider)
    model = st.selectbox(
        "Select Model",
        models
    )
    
    # Show pricing for OpenRouter models
    if api_provider == "OpenRouter" and is_openrouter_available():
        pricing_info = get_model_pricing(model)
        st.info(f"Pricing: {pricing_info}")
    
    # Review depth
    review_depth = st.select_slider(
        "Review Depth",
        options=["Basic", "Standard", "Comprehensive"],
        value="Standard"
    )
    
    st.divider()
    
    # About section
    st.markdown("### About")
    st.markdown("""
    This tool uses AI to analyze your code and provide helpful suggestions for improvement.
    
    **Features:**
    - Code quality assessment
    - Bug detection
    - Security vulnerability checks
    - Performance optimization tips
    - Style and best practice recommendations
    - Multiple AI providers (free & paid options)
    """)


# Function to detect programming language from code or filename
def detect_language(code, filename=None):
    # Check filename extension first if available
    if filename:
        extension_map = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.ts': 'TypeScript',
            '.html': 'HTML',
            '.css': 'CSS',
            '.java': 'Java',
            '.cpp': 'C++',
            '.c': 'C',
            '.go': 'Go',
            '.rs': 'Rust',
            '.php': 'PHP',
            '.rb': 'Ruby',
            '.swift': 'Swift',
            '.kt': 'Kotlin',
            '.scala': 'Scala',
            '.sh': 'Shell',
            '.pl': 'Perl',
            '.cs': 'C#'
        }
        ext = os.path.splitext(filename)[1].lower()
        if ext in extension_map:
            return extension_map[ext]
    
    # Basic detection based on code patterns
    language_patterns = {
        'Python': [r'import\s+[a-zA-Z0-9_]+', r'def\s+[a-zA-Z0-9_]+\s*\(', r'class\s+[a-zA-Z0-9_]+\s*:'],
        'JavaScript': [r'const\s+[a-zA-Z0-9_]+\s*=', r'function\s+[a-zA-Z0-9_]+\s*\(', r'let\s+[a-zA-Z0-9_]+\s*='],
        'Java': [r'public\s+class\s+[a-zA-Z0-9_]+', r'public\s+static\s+void\s+main'],
        'C++': [r'#include\s+<[a-zA-Z0-9_]+>', r'int\s+main\s*\('],
        'HTML': [r'<!DOCTYPE\s+html>', r'<html.*>.*</html>'],
        'CSS': [r'[a-zA-Z0-9_]+\s*{[^}]*}', r'\.[a-zA-Z0-9_-]+\s*{']
    }
    
    for lang, patterns in language_patterns.items():
        for pattern in patterns:
            if re.search(pattern, code):
                return lang
    
    return "Unknown"


# Function to call OpenAI API for code review
def analyze_with_openai(code, language, api_key, model, depth):
    if not api_key:
        st.error("Please provide an OpenAI API key in the sidebar.")
        return None
    
    prompt = create_review_prompt(code, language, depth, "OpenAI")
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are an expert code reviewer."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2
    }
    
    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=payload
        )
        
        if response.status_code == 200:
            response_data = response.json()
            result = response_data["choices"][0]["message"]["content"]
            # Extract JSON from the response if it's wrapped in text
            json_match = re.search(r'```json\s*([\s\S]*?)\s*```|({[\s\S]*})', result)
            if json_match:
                json_str = json_match.group(1) or json_match.group(2)
                return json.loads(json_str.strip())
            else:
                try:
                    return json.loads(result)
                except:
                    st.error("Failed to parse API response as JSON")
                    return None
        else:
            st.error(f"API Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        st.error(f"Failed to call OpenAI API: {str(e)}")
        return None


# Function to call Anthropic API for code review
def analyze_with_anthropic(code, language, api_key, model, depth):
    if not api_key:
        st.error("Please provide an Anthropic API key in the sidebar.")
        return None
    
    prompt = create_review_prompt(code, language, depth, "Anthropic")
    
    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01"
    }
    
    payload = {
        "model": model,
        "max_tokens": 4000,
        "temperature": 0.2,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }
    
    try:
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers=headers,
            json=payload
        )
        
        if response.status_code == 200:
            response_data = response.json()
            result = response_data["content"][0]["text"]
            # Extract JSON from the response if it's wrapped in text
            json_match = re.search(r'```json\s*([\s\S]*?)\s*```|({[\s\S]*})', result)
            if json_match:
                json_str = json_match.group(1) or json_match.group(2)
                return json.loads(json_str.strip())
            else:
                try:
                    return json.loads(result)
                except:
                    st.error("Failed to parse API response as JSON")
                    return None
        else:
            st.error(f"API Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        st.error(f"Failed to call Anthropic API: {str(e)}")
        return None


# Function to analyze code based on selected provider
def analyze_code(code, language, api_key, provider, model, depth):
    if provider == "OpenAI":
        return analyze_with_openai(code, language, api_key, model, depth)
    elif provider == "Anthropic":
        return analyze_with_anthropic(code, language, api_key, model, depth)
    elif provider == "Ollama":
        prompt = create_review_prompt(code, language, depth, "Ollama")
        return analyze_with_ollama(code, language, model, prompt)
    elif provider == "Google Gemini":
        prompt = create_review_prompt(code, language, depth, "Google Gemini")
        return analyze_with_gemini(code, language, model, prompt)
    elif provider == "Groq":
        prompt = create_review_prompt(code, language, depth, "Groq")
        return analyze_with_groq(code, language, model, prompt)
    elif provider == "Hugging Face":
        prompt = create_review_prompt(code, language, depth, "Hugging Face")
        return analyze_with_huggingface(code, language, model, prompt)
    elif provider == "OpenRouter":
        prompt = create_review_prompt(code, language, depth, "OpenRouter", model)
        return analyze_with_openrouter(code, language, model, prompt)
    else:
        st.error(f"Unsupported provider: {provider}")
        return None


# Function to format and display review output
def display_review_output(review_data):
    if not review_data:
        return
    
    # Check if there's an error in the response
    if "error" in review_data:
        st.error(f"Error: {review_data['error']}")
        if "setup_instructions" in review_data:
            with st.expander("Setup Instructions"):
                st.markdown(review_data["setup_instructions"])
        if "details" in review_data:
            with st.expander("Error Details"):
                st.markdown(review_data["details"])
        if "raw_response" in review_data:
            with st.expander("Raw Response"):
                st.code(review_data["raw_response"])
        return
    
    # Display overall rating
    st.subheader("Overall Code Quality")
    rating = review_data.get("overall_rating", 0)
    st.progress(rating / 10.0)
    st.write(f"**Rating:** {rating}/10")
    
    # Display summary
    st.subheader("Summary")
    summary = review_data.get("summary", {})
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("##### Strengths")
        strengths = summary.get("strengths", [])
        if strengths:
            for strength in strengths:
                st.markdown(f"- {strength}")
        else:
            st.write("No specific strengths highlighted.")
    
    with col2:
        st.markdown("##### Areas for Improvement")
        weaknesses = summary.get("weaknesses", [])
        if weaknesses:
            for weakness in weaknesses:
                st.markdown(f"- {weakness}")
        else:
            st.write("No specific weaknesses highlighted.")
    
    # Display key recommendations
    st.subheader("Key Recommendations")
    recommendations = review_data.get("key_recommendations", [])
    if recommendations:
        for i, rec in enumerate(recommendations, 1):
            st.markdown(f"**{i}. {rec}**")
    else:
        st.write("No specific recommendations provided.")
    
    # Display detailed issues
    st.subheader("Detailed Feedback")
    issues = review_data.get("issues", [])
    
    if not issues:
        st.write("No specific issues found.")
        return
    
    # Count issues by severity
    severity_counts = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0}
    for issue in issues:
        severity = issue.get("severity", "Low")
        severity_counts[severity] += 1
    
    # Display severity counts
    st.write("##### Issue Summary")
    cols = st.columns(4)
    with cols[0]:
        st.markdown(f"<div class='severity-critical'>Critical: {severity_counts['Critical']}</div>", unsafe_allow_html=True)
    with cols[1]:
        st.markdown(f"<div class='severity-high'>High: {severity_counts['High']}</div>", unsafe_allow_html=True)
    with cols[2]:
        st.markdown(f"<div class='severity-medium'>Medium: {severity_counts['Medium']}</div>", unsafe_allow_html=True)
    with cols[3]:
        st.markdown(f"<div class='severity-low'>Low: {severity_counts['Low']}</div>", unsafe_allow_html=True)
    
    # Display each issue
    for i, issue in enumerate(issues, 1):
        severity = issue.get("severity", "Low")
        severity_class = f"severity-{severity.lower()}"
        
        with st.expander(f"Issue #{i}: {issue.get('description', 'Unnamed Issue')} (Line {issue.get('line', 'N/A')})"): 
            st.markdown(f"<span class='{severity_class}'>Severity: {severity}</span>", unsafe_allow_html=True)
            st.markdown(f"**Line(s):** {issue.get('line', 'N/A')}")
            st.markdown(f"**Description:** {issue.get('description', 'No description provided.')}")
            
            st.markdown("**Recommendation:**")
            st.markdown(issue.get("recommendation", "No specific recommendation provided."))
            
            if "improved_code" in issue and issue["improved_code"].strip():
                st.markdown("**Suggested Improvement:**")
                st.markdown(f"```{issue.get('improved_code', '')}```")


# Create tabs for different input methods
tab1, tab2 = st.tabs(["Paste Code", "Upload File"])

with tab1:
    # Code input
    input_language = st.selectbox(
        "Select Programming Language",
        ["Auto-detect", "Python", "JavaScript", "TypeScript", "Java", "C++", "C", "Go", "Rust", "PHP", "Ruby", "HTML", "CSS", "C#", "Kotlin", "Swift"]
    )
    
    code_input = st.text_area("Paste your code here:", height=300)
    
    # Process input
    if st.button("Analyze Code", key="analyze_pasted", disabled=not code_input.strip()):
        if not code_input.strip():
            st.error("Please paste some code to analyze.")
        else:
            with st.spinner("Analyzing your code..."):
                # Detect language if auto-detect is selected
                detected_language = "Unknown"
                if input_language == "Auto-detect":
                    detected_language = detect_language(code_input)
                    st.info(f"Detected language: {detected_language}")
                else:
                    detected_language = input_language
                
                # Analyze code
                review_result = analyze_code(
                    code_input,
                    detected_language,
                    api_key,
                    api_provider,
                    model,
                    review_depth
                )
                
                if review_result:
                    st.success("Analysis complete!")
                    st.divider()
                    display_review_output(review_result)

with tab2:
    # File upload
    uploaded_file = st.file_uploader(
        "Upload your code file:",
        type=["py", "js", "ts", "java", "cpp", "c", "go", "rs", "php", "rb", "html", "css", "cs", "kt", "swift"]
    )
    
    if uploaded_file is not None:
        # Read and display the file
        file_contents = uploaded_file.getvalue().decode("utf-8")
        st.code(file_contents[:1000] + ("..." if len(file_contents) > 1000 else ""))
        
        # Process uploaded file
        if st.button("Analyze Code", key="analyze_uploaded"):
            with st.spinner("Analyzing your code..."):
                # Detect language from file extension
                detected_language = detect_language(file_contents, uploaded_file.name)
                st.info(f"Detected language: {detected_language}")
                
                # Analyze code
                review_result = analyze_code(
                    file_contents,
                    detected_language,
                    api_key,
                    api_provider,
                    model,
                    review_depth
                )
                
                if review_result:
                    st.success("Analysis complete!")
                    st.divider()
                    display_review_output(review_result)
                    
                    # Download report option
                    if "error" not in review_result:
                        report_json = json.dumps(review_result, indent=2)
                        st.download_button(
                            label="Download Report (JSON)",
                            data=report_json,
                            file_name=f"code_review_{uploaded_file.name}.json",
                            mime="application/json"
                        )

# Footer
st.divider()
st.markdown("""
<div style="text-align: center; color: #888;">
    AI Code Review Assistant | Built with Streamlit | Supports multiple AI providers
</div>
""", unsafe_allow_html=True)
