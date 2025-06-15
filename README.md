# AI Code Review Assistant

A lightweight Streamlit application that uses AI to review code, detect bugs, suggest improvements, and provide best practice recommendations.

## Project Architecture

```mermaid
graph TB
    A[User Interface<br/>Streamlit Frontend] --> B[Code Input Handler]
    B --> C{Input Type}
    C -->|Text Input| D[Direct Code Input]
    C -->|File Upload| E[File Reader]
    
    D --> F[Language Detector]
    E --> F
    
    F --> G[Code Preprocessor]
    G --> H{AI Provider Selection}
    
    H -->|OpenAI| I[OpenAI API<br/>GPT Models]
    H -->|Anthropic| J[Anthropic API<br/>Claude Models]
    H -->|Ollama| K[Ollama API<br/>Local Models]
    H -->|Google Gemini| L[Gemini API<br/>Gemini Models]
    H -->|Groq| M[Groq API<br/>Fast Inference]
    H -->|Hugging Face| N[Hugging Face<br/>Inference API]
    H -->|OpenRouter| O[OpenRouter API<br/>Multiple Models]
    
    I --> P[Response Parser]
    J --> P
    K --> P
    L --> P
    M --> P
    N --> P
    O --> P
    
    P --> Q[Result Formatter]
    Q --> R[Review Display]
    Q --> S[JSON Report Generator]
    
    R --> T[Code Quality Rating]
    R --> U[Issue Categorization]
    R --> V[Recommendations]
    
    S --> W[Download Report]
    
    style A fill:#e1f5fe
    style I fill:#fff3e0
    style J fill:#f3e5f5
    style K fill:#e8f5e8
    style L fill:#e0f7fa
    style M fill:#f1f8e9
    style N fill:#fff8e1
    style O fill:#fce4ec
    style T fill:#e8f5e8
    style U fill:#fff8e1
    style V fill:#fce4ec
```

### Component Description

- **User Interface**: Streamlit-based web interface for user interaction
- **Code Input Handler**: Manages both direct text input and file uploads
- **Language Detector**: Automatically identifies programming language
- **Code Preprocessor**: Prepares code for analysis and handles formatting
- **AI Provider Integration**: Supports multiple AI providers including free and paid options
  - OpenAI API (GPT models)
  - Anthropic API (Claude models)
  - Ollama API (Local, completely free)
  - Google Gemini API (Free tier available)
  - Groq API (Fast inference, free tier available)
  - Hugging Face Inference API (Free tier available)
  - OpenRouter API (Access to multiple models with competitive pricing)
- **Response Parser**: Processes AI responses into structured data
- **Result Formatter**: Organizes results into user-friendly format
- **Report Generator**: Creates downloadable JSON reports

## Features

- **Code Input Options**
  - Paste code directly into the application
  - Upload code files (.py, .js, .java, etc.)
  - Automatic language detection

- **Comprehensive Review**
  - Code quality assessment
  - Bug and security vulnerability detection
  - Performance optimization suggestions
  - Style and best practice recommendations

- **Customizable Analysis**
  - Support for multiple AI providers:
    - OpenAI (GPT models)
    - Anthropic (Claude models)
    - Ollama (Local, completely free)
    - Google Gemini (Free tier available)
    - Groq (Fast inference, free tier available)
    - Hugging Face (Free tier available)
    - OpenRouter (Multiple models, competitive pricing)
  - Multiple model options for each provider
  - Free tier indicators for applicable providers
  - Provider status monitoring
  - Adjustable review depth (Basic, Standard, Comprehensive)

- **User-Friendly Output**
  - Clear organization of review results
  - Severity-based categorization
  - Line-specific feedback
  - Downloadable JSON reports

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/NoLongerHumanHQ/AI-Code-Review-Assistant.git
   cd AI-Code-Review-Assistant
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up your environment variables:
   - Create a `.env` file based on the provided `.env.example`
   - Add your API keys for the providers you want to use:
     ```
     OPENAI_API_KEY=your_openai_key
     ANTHROPIC_API_KEY=your_anthropic_key
     GEMINI_API_KEY=your_gemini_key
     GROQ_API_KEY=your_groq_key
     HUGGINGFACE_API_KEY=your_huggingface_key
     OPENROUTER_API_KEY=your_openrouter_key
     OLLAMA_BASE_URL=http://localhost:11434
     ```

## Usage

1. Start the Streamlit app:
   ```
   streamlit run app.py
   ```

2. Open your web browser and navigate to the URL displayed in the terminal (typically http://localhost:8501)

3. Configure your settings in the sidebar:
   - Select API provider (OpenAI, Anthropic, Ollama, Google Gemini, Groq, Hugging Face, or OpenRouter)
   - Enter your API key if not already set in .env (not required for Ollama)
   - Select the AI model from the available options for your chosen provider
   - View provider status and setup instructions if needed
   - Choose review depth

4. Input your code:
   - Paste code directly into the text area, or
   - Upload a code file using the file uploader

5. Click "Analyze Code" to start the review process

6. Review the results:
   - Overall code quality rating
   - Summary of strengths and weaknesses
   - Key recommendations
   - Detailed issue breakdown with severity levels
   - Suggested improvements with code examples

7. Optionally download the report as JSON for future reference

## Supported Languages

The application supports detection and review of multiple programming languages, including:
- Python
- JavaScript
- TypeScript
- Java
- C++
- C
- Go
- Rust
- PHP
- Ruby
- HTML
- CSS
- C#
- Kotlin
- Swift
- And more...

## Configuration Options

### API Providers
- **OpenAI**: Uses GPT models for code review
  - Models: gpt-3.5-turbo, gpt-4, gpt-4-turbo
  
- **Anthropic**: Uses Claude models for code review
  - Models: claude-2, claude-instant-1, claude-3-opus, claude-3-sonnet

- **Ollama** 🆓: Uses local models for completely free code review
  - Models: codellama, deepseek-coder, starcoder, and other locally installed models
  - Requires Ollama to be installed and running locally
  
- **Google Gemini** 🆓: Uses Google's Gemini models with free tier
  - Models: gemini-1.5-flash, gemini-1.5-pro
  - Free tier with rate limits (15 requests per minute)
  
- **Groq** 🆓: Uses fast inference models with free tier
  - Models: llama3-70b-8192, mixtral-8x7b-32768
  - Optimized for speed and performance
  
- **Hugging Face** 🆓: Uses Inference API with free tier
  - Models: microsoft/DialoGPT-medium, codeparrot/codeparrot
  - Free tier with rate limits
  
- **OpenRouter**: Access to multiple models through a single API
  - Models: anthropic/claude-3-haiku, meta-llama/llama-3-8b, and many more
  - Cost-effective pricing with model selection

### Review Depth
- **Basic**: Quick review focusing on critical issues
- **Standard**: Balanced review covering bugs, style, and common best practices
- **Comprehensive**: In-depth analysis including edge cases, optimizations, and security concerns

## Author

**NoLongerHumanHQ**
- GitHub: [@NoLongerHumanHQ](https://github.com/NoLongerHumanHQ)
- Email: patel.veeru@protonmail.com

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### How to Contribute
1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Support

If you encounter any issues or have questions, please:
- Open an issue on GitHub
- Contact me at patel.veeru@protonmail.com

## Acknowledgements

- This project uses the [Streamlit](https://streamlit.io/) framework
- AI-powered code analysis provided by:
  - [OpenAI](https://openai.com/) (GPT models)
  - [Anthropic](https://www.anthropic.com/) (Claude models)
  - [Ollama](https://ollama.ai/) (Local models)
  - [Google Gemini](https://ai.google.dev/) (Gemini models)
  - [Groq](https://groq.com/) (Fast inference models)
  - [Hugging Face](https://huggingface.co/) (Inference API)
  - [OpenRouter](https://openrouter.ai/) (Multiple model access)
- Special thanks to the open-source community for their valuable contributions

## Changelog

### Version 2.0.0
- Added support for multiple free and affordable API providers:
  - Ollama (Local, completely free)
  - Google Gemini API (Free tier available)
  - Groq API (Fast inference, free tier available)
  - Hugging Face Inference API (Free tier available)
  - OpenRouter API (Multiple models, competitive pricing)
- Enhanced UI with provider status indicators
- Added free tier indicators for applicable providers
- Improved error handling and setup instructions
- Optimized prompts for each provider
- Updated documentation

### Version 1.0.0
- Initial release with basic code review functionality
- Support for OpenAI and Anthropic APIs
- Multiple programming language support
- Downloadable JSON reports
