# EvacuAIDi: AI-Driven Evacuation Framework

An AI-driven, causal-informed framework for probabilistic and disability-inclusive evacuation guidance.

## 📖 About

This is the presentation website for the PhD dissertation "EvacuAIDi: An AI-Driven, Causal-Informed Framework for Probabilistic and Disability-Inclusive Evacuation Guidance" by Amir Rafe at Utah State University (2025).

## 🚀 Live Demo

Visit the live presentation: [https://pozapas.github.io/evacuaidi-presentation/](https://pozapas.github.io/evacuaidi-presentation/)

## 🔧 Deployment Guide

### Local Development

1. Clone the repository
2. Create a `.env` file in the root directory with your API keys:
   ```
   GEMINI_EMBEDDING_API_KEY=your_embedding_api_key
   GEMINI_GENERATION_API_KEY=your_generation_api_key
   ```
3. Install dependencies: `npm install`
4. Start the server: `node server.js`
5. Open `index.html` in your browser

### Deploying on Render.com

1. Create a new Web Service on Render.com
2. Connect your GitHub repository
3. Configure the build settings:
   - Build Command: `npm install`
   - Start Command: `node server.js`
4. Add environment variables:
   - `GEMINI_EMBEDDING_API_KEY`: Your Google AI Gemini embedding API key
   - `GEMINI_GENERATION_API_KEY`: Your Google AI Gemini generation API key
5. Deploy your application

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

## 📧 Contact

**Amir Rafe**  
PhD Candidate, Civil & Environmental Engineering  
Utah State University  
Email: amir.rafe@usu.edu  
Advisor: Dr. Patrick Singleton

## 📄 License

This research presentation is part of academic work conducted at Utah State University.
