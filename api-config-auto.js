// Auto-Configuration Switcher for EvacuAIDi
// Automatically detects environment and uses appropriate configuration

// Detect if running on GitHub Pages or localhost
const isGitHubPages = window.location.hostname.includes('github.io');
const isLocalhost = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' || window.location.protocol === 'file:';

console.log(`Detected environment: ${isGitHubPages ? 'GitHub Pages' : isLocalhost ? 'Local Development' : 'Unknown'}`);

// Configuration based on environment
const CONFIG = {
    APP_NAME: 'EvacuAIDi',
    VERSION: '1.0.0',
    AUTHOR: 'Amir Rafe',
    UNIVERSITY: 'Utah State University',
    
    // Dynamic API configuration
    // This will be your Vercel deployment URL - update after deploying to Vercel
    API_BASE_URL: isGitHubPages ? 'https://evacuaidi-presentation.vercel.app' : null,
    USE_SECURE_BACKEND: isGitHubPages,
    
    // Chat Configuration
    MAX_MESSAGE_LENGTH: 500,
    MAX_CHUNKS_FOR_RAG: 5,
    CHUNK_SIZE: 800,
    CHUNK_OVERLAP: 200,
    
    // Rate limiting
    API_RATE_LIMIT_MS: 100,
    
    // UI Configuration
    TYPING_ANIMATION_DELAY: 100,
    SCROLL_BEHAVIOR: 'smooth'
};

// API Keys for local development only
const LOCAL_API_KEYS = {
    // Only used in local development - UPDATE THESE WITH YOUR ACTUAL KEYS
    GEMINI_EMBEDDING_API_KEY: 'AIzaSyAlUCTBXfBKz2GTAd_CGhkm00Oh7UXBsrQ',
    GEMINI_GENERATION_API_KEY: 'AIzaSyAlUCTBXfBKz2GTAd_CGhkm00Oh7UXBsrQ'
};

// Secure API client for GitHub Pages
class SecureApiClient {
    constructor(baseUrl) {
        this.baseUrl = baseUrl;
    }

    async generateEmbedding(text) {
        try {
            const response = await fetch(`${this.baseUrl}/api/embed`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const result = await response.json();
            return result.embedding;
        } catch (error) {
            console.error('Error generating embedding via secure backend:', error);
            return null;
        }
    }

    async generateResponse(message, context = '') {
        try {
            const response = await fetch(`${this.baseUrl}/api/chat`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message, context })
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || `HTTP ${response.status}: ${response.statusText}`);
            }
            
            const result = await response.json();
            return result.message || result.fallback;
        } catch (error) {
            console.error('Error generating response via secure backend:', error);
            throw error;
        }
    }
}

// Local API client for development
class LocalApiClient {
    constructor(apiKeys) {
        this.apiKeys = apiKeys;
    }

    async generateEmbedding(text) {
        try {
            const response = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-embedding-001:embedContent?key=${this.apiKeys.GEMINI_EMBEDDING_API_KEY}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    model: "models/gemini-embedding-001",
                    content: {
                        parts: [{ text: text }]
                    }
                })
            });
            
            const result = await response.json();
            return result.embedding?.values || null;
        } catch (error) {
            console.error('Error generating embedding via local API:', error);
            return null;
        }
    }

    async generateResponse(message, context = '') {
        try {
            const enhancedPrompt = `You are an AI research assistant answering questions about Amir Rafe's PhD dissertation "EvacuAIDi: An AI-Driven, Causal-Informed Framework for Probabilistic and Disability-Inclusive Evacuation Guidance" from Utah State University (2025).

${context ? `Based on the following relevant dissertation content:\n\n${context}\n\n` : ''}

User Question: ${message}

Instructions:
- Provide specific details from the research including exact numbers, percentages, and findings
- Explain technical concepts clearly and accurately
- If the question is outside the scope of the provided context, clearly state that and suggest the user contact Amir Rafe at amir.rafe@usu.edu for more detailed information
- Be concise but comprehensive

Answer:`;

            const payload = {
                contents: [
                    {
                        role: "user",
                        parts: [{ text: enhancedPrompt }]
                    }
                ]
            };

            const apiUrl = `https://generativelanguage.googleapis.com/v1beta/models/gemma-3-27b-it:generateContent?key=${this.apiKeys.GEMINI_GENERATION_API_KEY}`;

            const response = await fetch(apiUrl, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            const result = await response.json();
            
            if (result.candidates && result.candidates.length > 0 && 
                result.candidates[0].content && result.candidates[0].content.parts && 
                result.candidates[0].content.parts.length > 0) {
                return result.candidates[0].content.parts[0].text;
            } else {
                throw new Error('Invalid response format from Gemini API');
            }
        } catch (error) {
            console.error('Error generating response via local API:', error);
            throw error;
        }
    }
}

// Unified EnvConfig class that works in both environments
class EnvConfig {
    constructor() {
        this.loaded = false;
        this.apiClient = null;
        this.requiredKeys = [
            'GEMINI_EMBEDDING_API_KEY',
            'GEMINI_GENERATION_API_KEY'
        ];
    }

    async loadEnv() {
        try {
            if (CONFIG.USE_SECURE_BACKEND) {
                // GitHub Pages: Use secure backend
                console.log('Initializing secure backend client...');
                this.apiClient = new SecureApiClient(CONFIG.API_BASE_URL);
                
                // Test backend connectivity
                const testResponse = await fetch(`${CONFIG.API_BASE_URL}/api/chat`, {
                    method: 'OPTIONS'
                });
                
                if (testResponse.status === 200 || testResponse.status === 204) {
                    this.loaded = true;
                    console.log('✅ Secure backend connection established');
                    return true;
                } else {
                    throw new Error('Backend not accessible');
                }
            } else {
                // Local development: Use direct API
                console.log('Initializing local API client...');
                
                // Validate local API keys
                if (!LOCAL_API_KEYS.GEMINI_EMBEDDING_API_KEY || 
                    !LOCAL_API_KEYS.GEMINI_GENERATION_API_KEY ||
                    LOCAL_API_KEYS.GEMINI_EMBEDDING_API_KEY.includes('your_api_key_here')) {
                    throw new Error('Please update LOCAL_API_KEYS in the configuration with your actual Gemini API keys');
                }
                
                this.apiClient = new LocalApiClient(LOCAL_API_KEYS);
                this.loaded = true;
                console.log('✅ Local API client initialized');
                return true;
            }
        } catch (error) {
            console.error('Failed to initialize API client:', error);
            this.loaded = false;
            return false;
        }
    }

    get(key) {
        if (!this.loaded) {
            console.warn('Environment not loaded. Call loadEnv() first.');
            return null;
        }
        
        if (CONFIG.USE_SECURE_BACKEND) {
            // For secure backend, return placeholder
            return 'SECURE_BACKEND_HANDLED';
        } else {
            // For local development, return actual keys
            return LOCAL_API_KEYS[key] || null;
        }
    }

    getApiClient() {
        return this.apiClient;
    }

    isLoaded() {
        return this.loaded;
    }

    hasRequiredKeys() {
        return this.loaded;
    }

    getMissingKeys() {
        return this.loaded ? [] : this.requiredKeys;
    }

    validate() {
        if (!this.loaded) {
            return {
                valid: false,
                error: CONFIG.USE_SECURE_BACKEND ? 
                    'Backend connection not established' : 
                    'Local API keys not configured'
            };
        }

        return {
            valid: true,
            error: null
        };
    }
}

// Unified embedding function
async function generateEmbedding(text, apiClient) {
    if (apiClient) {
        return await apiClient.generateEmbedding(text);
    } else {
        console.error('API client not available');
        return null;
    }
}

// Validation function
async function validateApiKeys() {
    try {
        const envConfig = new EnvConfig();
        return await envConfig.loadEnv();
    } catch (error) {
        console.error('API validation error:', error);
        return false;
    }
}

// Make all configuration available globally
if (typeof window !== 'undefined') {
    window.CONFIG = CONFIG;
    window.LOCAL_API_KEYS = LOCAL_API_KEYS;
    window.SecureApiClient = SecureApiClient;
    window.LocalApiClient = LocalApiClient;
    window.EnvConfig = EnvConfig;
    window.generateEmbedding = generateEmbedding;
    window.validateApiKeys = validateApiKeys;
    
    // Show configuration info
    console.log('🚀 EvacuAIDi Configuration Loaded');
    console.log(`📍 Environment: ${CONFIG.USE_SECURE_BACKEND ? 'GitHub Pages (Secure)' : 'Local Development'}`);
    console.log(`🔗 API Endpoint: ${CONFIG.API_BASE_URL || 'Direct Gemini API'}`);
}
