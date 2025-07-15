# EvacuAIDi: AI-Driven Evacuation Framework

An AI-driven, causal-informed framework for probabilistic and disability-inclusive evacuation guidance.

## 📖 About

This is the presentation website for the PhD dissertation "EvacuAIDi: An AI-Driven, Causal-Informed Framework for Probabilistic and Disability-Inclusive Evacuation Guidance" by Amir Rafe at Utah State University (2025).

## 🚀 Live Demo

Visit the live presentation: [https://pozapas.github.io/evacuaidi-presentation/](https://pozapas.github.io/evacuaidi-presentation/)

## 🔬 Research Overview

This dissertation addresses critical gaps in evacuation science through four interconnected research contributions:

1. **AI Knowledge Extraction**: Automated parameter extraction from fire safety codes
2. **Disability-Inclusive Modeling**: Enhanced agent-based models for heterogeneous populations
3. **Causal Evaluation**: Quantifying the impact of AI guidance on evacuation performance
4. **Probabilistic Risk Assessment**: Bayesian framework for uncertainty quantification

## 📊 Key Findings

- **22.5%** reduction in evacuation time with AI guidance
- **15.9%** greater benefits for individuals with disabilities
- **92%+** accuracy in automated parameter extraction
- **57%** of risk variance attributed to occupant load

## 🛠 Technology Stack

- HTML5/CSS3 with Tailwind CSS
- Vanilla JavaScript with RAG-based AI chat
- Google Gemini API for dissertation Q&A
- Responsive design with interactive plot modals

## ⚙️ Setup & Configuration

### For GitHub Pages Deployment (Current Setup)

The site is configured to work automatically on GitHub Pages with API keys in `config.js`. No additional setup required for the live demo.

### For Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/pozapas/evacuaidi-presentation.git
   cd evacuaidi-presentation
   ```

2. **Configure API Keys** (Choose one method):

   **Method A: Environment File (Recommended)**
   ```bash
   # Copy the example environment file
   cp .env.example .env
   
   # Edit .env and add your Google Gemini API keys
   GEMINI_EMBEDDING_API_KEY=your_embedding_api_key_here
   GEMINI_GENERATION_API_KEY=your_generation_api_key_here
   ```

   **Method B: Config File**
   ```javascript
   // Edit config.js and update the API keys
   window.APP_CONFIG = {
       GEMINI_EMBEDDING_API_KEY: 'your_embedding_api_key_here',
       GEMINI_GENERATION_API_KEY: 'your_generation_api_key_here'
   };
   ```

3. **Get Google Gemini API Keys**
   - Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create a new API key
   - You need both embedding and generation capabilities

4. **Serve the site locally**
   ```bash
   # Using Python
   python -m http.server 8000
   
   # Using Node.js
   npx serve .
   
   # Using PHP
   php -S localhost:8000
   ```

5. **Open in browser**: `http://localhost:8000`

## 🤖 AI Chat Feature

The site includes an AI research assistant that can answer questions about the dissertation:

- **RAG-based search**: Uses semantic embeddings to find relevant dissertation content
- **Context-aware responses**: Provides specific data and findings from the research
- **Interactive Q&A**: Ask about methodology, findings, implications, and technical details

### Sample Questions
- "What are the main research contributions of EvacuAIDi?"
- "How much does AI guidance improve evacuation times?"
- "What are the benefits for people with disabilities?"
- "Explain the DiSFM-GS model and its validation"

## 🔒 Security Considerations

- **API Keys**: For production use, consider implementing a backend proxy to hide API keys
- **Rate Limiting**: Google Gemini API has usage limits
- **CORS**: Current setup works for client-side only applications

## 📧 Contact

**Amir Rafe**  
PhD Candidate, Civil & Environmental Engineering  
Utah State University  
Email: amir.rafe@usu.edu  
Advisor: Dr. Patrick Singleton

## 📄 License

This research presentation is part of academic work conducted at Utah State University.
