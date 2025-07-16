# EvacuAIDi: AI-Driven Evacuation Framework

An AI-driven, causal-informed framework for probabilistic and disability-inclusive evacuation guidance.

## 📖 About

This is the presentation website for the PhD dissertation "EvacuAIDi: An AI-Driven, Causal-Informed Framework for Probabilistic and Disability-Inclusive Evacuation Guidance" by Amir Rafe at Utah State University (2025).

## 🚀 Live Demo

Visit the live presentation: [https://pozapas.github.io/evacuaidi-presentation/](https://pozapas.github.io/evacuaidi-presentation/)

## 🤖 AI Chat Feature

The website includes an interactive AI research assistant that can answer questions about the dissertation. The AI uses:

- **RAG (Retrieval-Augmented Generation)** for accurate, context-aware responses
- **Google Gemini API** for embeddings and text generation
- **Secure backend proxy** to protect API keys

### 🔧 Setup Instructions

To enable the AI chat feature:

1. **Deploy Backend Proxy** (Required for security)
   - See [BACKEND_DEPLOYMENT.md](./BACKEND_DEPLOYMENT.md) for detailed instructions
   - Recommended: Deploy to Vercel (free and easy)
   - Alternative: Deploy to Netlify Functions

2. **Configure API Keys** (In your backend deployment)
   - `GEMINI_EMBEDDING_API_KEY`: For semantic search functionality
   - `GEMINI_GENERATION_API_KEY`: For chat responses
   - Get these from [Google AI Studio](https://makersuite.google.com/app/apikey)

3. **Update Frontend Configuration**
   - Edit `env-config.js` to point to your deployed backend URL
   - The frontend will automatically use the secure backend proxy

### 🔒 Security Model

- ✅ **API Keys Protected**: Never exposed to client-side code
- ✅ **Backend Proxy**: Secure server-side API handling
- ✅ **CORS Configured**: Only authorized domains can access backend
- ✅ **No Repository Secrets**: GitHub secrets not used for client-side code

## �🔬 Research Overview

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

## 📧 Contact

**Amir Rafe**  
PhD Candidate, Civil & Environmental Engineering  
Utah State University  
Email: amir.rafe@usu.edu  
Advisor: Dr. Patrick Singleton

## 📄 License

This research presentation is part of academic work conducted at Utah State University.
