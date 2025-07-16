// Configuration for deployment environments
const CONFIG = {
    // Set to true when deploying to Vercel, false for local development
    USE_SECURE_BACKEND: true,
    
    // Vercel function endpoint (will be created)
    SECURE_ENDPOINT: '/api/chat',
    
    // Local development settings
    LOCAL_API_KEY_VAR: 'GEMINI_API_KEY',
    
    // Model configuration
    MODEL_CONFIG: {
        name: 'gemma-3-27b-it',
        embeddingModel: 'gemini-embedding-001',
        temperature: 0.7,
        maxTokens: 1000,
        topP: 0.9
    }
};

// Environment configuration class
class EnvConfig {
    constructor() {
        this.loaded = false;
        this.apiKey = null;
        this.apiClient = null;
    }
    
    async loadEnv() {
        try {
            if (CONFIG.USE_SECURE_BACKEND) {
                // For Vercel deployment - use serverless function
                this.apiClient = new SecureApiClient();
                this.loaded = true;
                console.log('Using secure backend for Vercel deployment');
            } else {
                // For local development - load from environment
                this.apiKey = await this.getLocalApiKey();
                if (this.apiKey && this.apiKey !== 'your_api_key_here') {
                    this.apiClient = new LocalApiClient(this.apiKey);
                    this.loaded = true;
                    console.log('Using local API key');
                } else {
                    throw new Error('Local API key not found or not configured');
                }
            }
        } catch (error) {
            console.error('Environment loading failed:', error);
            this.loaded = false;
        }
    }
    
    async getLocalApiKey() {
        // In a real local environment, this would read from environment variables
        // For browser-based local testing, you'd need to set this manually
        return process?.env?.GEMINI_API_KEY || 'your_api_key_here';
    }
    
    isLoaded() {
        return this.loaded && this.apiClient !== null;
    }
    
    hasRequiredKeys() {
        if (CONFIG.USE_SECURE_BACKEND) {
            return this.loaded; // Vercel handles the API key
        } else {
            return this.apiKey && this.apiKey !== 'your_api_key_here';
        }
    }
    
    getMissingKeys() {
        if (!this.hasRequiredKeys()) {
            return ['GEMINI_API_KEY'];
        }
        return [];
    }
    
    getApiClient() {
        return this.apiClient;
    }
}

// Secure API client for Vercel deployment
class SecureApiClient {
    constructor() {
        this.endpoint = CONFIG.SECURE_ENDPOINT;
    }
    
    async generateEmbedding(text) {
        try {
            console.log('Attempting to generate embedding for:', text.substring(0, 100) + '...');
            console.log('Using endpoint:', this.endpoint);
            
            const response = await fetch(this.endpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    action: 'embedding',
                    text: text
                })
            });
            
            console.log('Embedding response status:', response.status);
            
            if (!response.ok) {
                const errorText = await response.text();
                console.error('Embedding API error response:', errorText);
                throw new Error(`HTTP error! status: ${response.status}, message: ${errorText}`);
            }
            
            const data = await response.json();
            console.log('Embedding generated successfully');
            return data.embedding;
        } catch (error) {
            console.error('Error generating embedding:', error);
            return null;
        }
    }
    
    async generateResponse(userMessage, ragContext) {
        try {
            console.log('Attempting to generate response for:', userMessage);
            console.log('Using endpoint:', this.endpoint);
            console.log('RAG context length:', ragContext.length);
            
            const response = await fetch(this.endpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    action: 'chat',
                    message: userMessage,
                    context: ragContext
                })
            });
            
            console.log('Chat response status:', response.status);
            
            if (!response.ok) {
                const errorText = await response.text();
                console.error('Chat API error response:', errorText);
                throw new Error(`HTTP error! status: ${response.status}, message: ${errorText}`);
            }
            
            const data = await response.json();
            console.log('Response generated successfully');
            return data.response;
        } catch (error) {
            console.error('Error generating response:', error);
            throw error;
        }
    }
}

// Local API client for development
class LocalApiClient {
    constructor(apiKey) {
        this.apiKey = apiKey;
        this.baseUrl = 'https://generativelanguage.googleapis.com/v1beta';
    }
    
    async generateEmbedding(text) {
        try {
            const response = await fetch(`${this.baseUrl}/models/gemini-embedding-001:embedContent?key=${this.apiKey}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    model: "models/gemini-embedding-001",
                    content: {
                        parts: [{ text: text }]
                    }
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            return data.embedding.values;
        } catch (error) {
            console.error('Error generating embedding:', error);
            return null;
        }
    }
    
    async generateResponse(userMessage, ragContext) {
        try {
            const prompt = this.buildPrompt(userMessage, ragContext);
            
            const response = await fetch(`${this.baseUrl}/models/${CONFIG.MODEL_CONFIG.name}:generateContent?key=${this.apiKey}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    contents: [{
                        parts: [{ text: prompt }]
                    }],
                    generationConfig: {
                        temperature: CONFIG.MODEL_CONFIG.temperature,
                        maxOutputTokens: CONFIG.MODEL_CONFIG.maxTokens,
                        topP: CONFIG.MODEL_CONFIG.topP
                    }
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            return data.candidates[0].content.parts[0].text;
        } catch (error) {
            console.error('Error generating response:', error);
            throw error;
        }
    }
    
    buildPrompt(userMessage, ragContext) {
        return `You are an AI research assistant specializing in the EvacuAIDi dissertation research on AI-driven, causal-informed framework for probabilistic and disability-inclusive evacuation guidance.

**Context from Research:**
${ragContext}

**User Question:** ${userMessage}

**Instructions:**
- Provide accurate, detailed answers based on the research context
- Focus on quantitative findings and specific methodological details
- If the question is outside the research scope, clearly state the limitations
- Use bullet points and formatting for readability
- Keep responses informative but concise (under 300 words)

**Your Response:**`;
    }
}

// Legacy compatibility (for existing code references)
const geminiAPI = {
    async initialize() {
        try {
            const envConfig = new EnvConfig();
            await envConfig.loadEnv();
            window.envConfigInstance = envConfig;
            return envConfig.isLoaded();
        } catch (error) {
            console.error('Gemini API initialization failed:', error);
            return false;
        }
    }
};

// Make classes globally available
window.EnvConfig = EnvConfig;
window.SecureApiClient = SecureApiClient;
window.LocalApiClient = LocalApiClient;
window.geminiAPI = geminiAPI;
window.CONFIG = CONFIG;
