# Prompt optimization for different providers

# Base prompt template for code review
def create_base_review_prompt(code, language, depth):
    """Create a base prompt template for code review"""
    depth_instructions = {
        "Basic": "Focus on critical bugs and major issues only. Keep the review brief.",
        "Standard": "Cover bugs, style issues, and common best practices. Provide a balanced review.",
        "Comprehensive": "Perform a thorough analysis including edge cases, optimizations, security concerns, and detailed best practices. Provide in-depth feedback."
    }
    
    prompt = f"""
    You are an expert code reviewer specializing in {language} programming. Please review the following code and provide detailed feedback.

    {depth_instructions[depth]}

    Analyze the code for:
    1. Bugs and logical errors
    2. Security vulnerabilities
    3. Performance issues and optimization opportunities
    4. Adherence to {language} best practices and coding standards
    5. Code readability and maintainability issues

    For each issue found:
    - Specify the line number(s) when possible
    - Categorize the severity (Critical, High, Medium, Low)
    - Explain why it's an issue
    - Provide a specific code example showing how to improve it

    Also include:
    - An overall code quality rating (1-10)
    - A summary of the main strengths and weaknesses
    - 2-3 key recommendations for improvement

    Format your response as JSON with the following structure:
    {{
        "overall_rating": number,
        "summary": {{
            "strengths": [list of strings],
            "weaknesses": [list of strings]
        }},
        "key_recommendations": [list of strings],
        "issues": [
            {{
                "line": number or range (e.g., "10" or "10-15"),
                "severity": "Critical|High|Medium|Low",
                "description": "string",
                "recommendation": "string",
                "improved_code": "string"
            }}
        ]
    }}

    Here is the code to review:
    ```{language}
    {code}
    ```
    """
    return prompt

# Provider-specific prompt optimizations

def create_ollama_prompt(code, language, depth):
    """Create an optimized prompt for Ollama (local processing)"""
    # Ollama works best with concise prompts
    depth_instructions = {
        "Basic": "Focus on critical bugs and major issues only.",
        "Standard": "Cover bugs, style issues, and common best practices.",
        "Comprehensive": "Analyze edge cases, optimizations, security concerns, and best practices."
    }
    
    prompt = f"""
    You are a code reviewer. Review this {language} code.

    {depth_instructions[depth]}

    Analyze for: bugs, security issues, performance, best practices, readability.

    For each issue: specify line number, severity (Critical/High/Medium/Low), explain why, suggest improvement.

    Include: quality rating (1-10), strengths, weaknesses, key recommendations.

    Format as JSON: {{
        "overall_rating": number,
        "summary": {{
            "strengths": [list],
            "weaknesses": [list]
        }},
        "key_recommendations": [list],
        "issues": [
            {{
                "line": number or range,
                "severity": "Critical|High|Medium|Low",
                "description": "string",
                "recommendation": "string",
                "improved_code": "string"
            }}
        ]
    }}

    Code:
    ```{language}
    {code}
    ```
    """
    return prompt

def create_gemini_prompt(code, language, depth):
    """Create an optimized prompt for Google Gemini"""
    # Gemini works well with structured prompts
    base_prompt = create_base_review_prompt(code, language, depth)
    
    # Add Gemini-specific instructions
    gemini_prompt = f"""{base_prompt}
    
    IMPORTANT: Ensure your response is valid JSON that can be parsed. Do not include any explanatory text outside the JSON structure.
    """
    return gemini_prompt

def create_groq_prompt(code, language, depth):
    """Create an optimized prompt for Groq (fast inference)"""
    # Groq works best with direct, efficient prompts
    base_prompt = create_base_review_prompt(code, language, depth)
    
    # Optimize for fast inference
    groq_prompt = f"""{base_prompt}
    
    IMPORTANT: Be concise and direct in your analysis. Focus on the most important issues first.
    """
    return groq_prompt

def create_huggingface_prompt(code, language, depth):
    """Create an optimized prompt for Hugging Face models"""
    # Hugging Face models may need more specific formatting
    depth_instructions = {
        "Basic": "Focus on critical bugs and major issues only.",
        "Standard": "Cover bugs, style issues, and common best practices.",
        "Comprehensive": "Analyze edge cases, optimizations, security concerns, and best practices."
    }
    
    # Simplified prompt for smaller models
    prompt = f"""
    Task: Review {language} code.
    Instructions: {depth_instructions[depth]}
    Find bugs, security issues, performance problems, and style issues.
    Rate code quality (1-10).
    List strengths and weaknesses.
    Give recommendations.
    Format as JSON.
    
    Code:
    ```{language}
    {code}
    ```
    """
    return prompt

def create_openrouter_prompt(code, language, depth, model):
    """Create an optimized prompt for OpenRouter (provider-specific)"""
    # OpenRouter can route to different providers, so adapt based on the model
    if "claude" in model.lower():
        # Claude-specific optimizations
        prompt = f"""{create_base_review_prompt(code, language, depth)}
        
        IMPORTANT: Be thorough in your analysis but focus on actionable improvements.
        """
    elif "llama" in model.lower():
        # Llama-specific optimizations
        prompt = f"""{create_ollama_prompt(code, language, depth)}
        
        IMPORTANT: Ensure your response is valid JSON that can be parsed.
        """
    elif "gemini" in model.lower():
        # Gemini-specific optimizations
        prompt = create_gemini_prompt(code, language, depth)
    else:
        # Default prompt
        prompt = create_base_review_prompt(code, language, depth)
    
    return prompt

# Function to select the appropriate prompt based on provider
def create_review_prompt(code, language, depth, provider, model=None):
    """Create a review prompt optimized for the selected provider"""
    if provider == "Ollama":
        return create_ollama_prompt(code, language, depth)
    elif provider == "Google Gemini":
        return create_gemini_prompt(code, language, depth)
    elif provider == "Groq":
        return create_groq_prompt(code, language, depth)
    elif provider == "Hugging Face":
        return create_huggingface_prompt(code, language, depth)
    elif provider == "OpenRouter":
        return create_openrouter_prompt(code, language, depth, model)
    elif provider == "OpenAI":
        return create_base_review_prompt(code, language, depth)
    elif provider == "Anthropic":
        return create_base_review_prompt(code, language, depth)
    else:
        # Default to base prompt
        return create_base_review_prompt(code, language, depth)