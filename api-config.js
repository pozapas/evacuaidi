// Complete Configuration for EvacuAIDi Application
// 
// SECURITY NOTE: In a production environment, these API keys should be:
// 1. Stored securely on a backend server
// 2. Accessed through secure API endpoints
// 3. Never exposed in client-side code
//
// For this demonstration/development setup, we're including them here.
// Make sure to:
// - Keep your API keys private
// - Don't commit them to public repositories
// - Consider using environment variables in a backend service

// Application Configuration Constants
const CONFIG = {
    APP_NAME: 'EvacuAIDi',
    VERSION: '1.0.0',
    AUTHOR: 'Amir Rafe',
    UNIVERSITY: 'Utah State University',
    
    // API Configuration
    GEMINI_API_BASE_URL: 'https://generativelanguage.googleapis.com/v1beta',
    
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

// API Keys Configuration
const API_KEYS = {
    // Get your Gemini API key from: https://makersuite.google.com/app/apikey
    GEMINI_EMBEDDING_API_KEY: 'AIzaSyAlUCTBXfBKz2GTAd_CGhkm00Oh7UXBsrQ',
    GEMINI_GENERATION_API_KEY: 'AIzaSyAlUCTBXfBKz2GTAd_CGhkm00Oh7UXBsrQ'
};

// Validate API keys
function validateApiKeys() {
    const requiredKeys = [
        'GEMINI_EMBEDDING_API_KEY',
        'GEMINI_GENERATION_API_KEY'
    ];
    
    const missingKeys = requiredKeys.filter(key => {
        const value = API_KEYS[key];
        return !value || value.includes('your_api_key_here') || value.length < 10;
    });
    
    if (missingKeys.length > 0) {
        console.error('Missing or invalid API keys:', missingKeys);
        return false;
    }
    
    console.log('API keys validated successfully');
    return true;
}

// Enhanced EnvConfig class that works with the API_KEYS
class EnvConfig {
    constructor() {
        this.config = { ...API_KEYS };
        this.loaded = false;
        this.requiredKeys = [
            'GEMINI_EMBEDDING_API_KEY',
            'GEMINI_GENERATION_API_KEY'
        ];
    }

    async loadEnv() {
        try {
            // Validate the API keys
            if (!validateApiKeys()) {
                throw new Error('Invalid or missing API keys in configuration');
            }
            
            this.loaded = true;
            console.log('Environment configuration loaded successfully');
            return true;
        } catch (error) {
            console.error('Failed to load environment configuration:', error);
            this.loaded = false;
            return false;
        }
    }

    get(key) {
        if (!this.loaded) {
            console.warn('Environment not loaded. Call loadEnv() first.');
            return null;
        }
        return this.config[key] || null;
    }

    isLoaded() {
        return this.loaded;
    }

    hasRequiredKeys() {
        if (!this.loaded) return false;
        
        return this.requiredKeys.every(key => {
            const value = this.config[key];
            return value && value.trim() !== '' && !value.includes('your_api_key_here') && value.length > 10;
        });
    }

    getMissingKeys() {
        if (!this.loaded) return this.requiredKeys;
        
        return this.requiredKeys.filter(key => {
            const value = this.config[key];
            return !value || value.trim() === '' || value.includes('your_api_key_here') || value.length < 10;
        });
    }

        // Gemini API client for embedding and generation
        getApiClient() {
            const embeddingKey = this.get('GEMINI_EMBEDDING_API_KEY');
            const generationKey = this.get('GEMINI_GENERATION_API_KEY');
            const baseUrl = CONFIG.GEMINI_API_BASE_URL;

            
            return {
                async generateEmbedding(text) {
                    // Gemini embedding endpoint
                    const url = `${baseUrl}/models/embedding-001:embedText?key=${embeddingKey}`;
                    try {
                        const response = await fetch(url, {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ text })
                        });
                        const data = await response.json();
                        if (data && data.embeddings && data.embeddings.length > 0) {
                            return data.embeddings[0].values;
                        }
                        throw new Error('No embedding returned');
                    } catch (err) {
                        console.error('Embedding API error:', err);
                        return null;
                    }
                },
                async generateResponse(userMessage, ragContext) {
                    // Gemini generation endpoint
                    const url = `${baseUrl}/models/gemini-pro:generateContent?key=${generationKey}`;
                    try {
                        const prompt = `${ragContext}\n\nUser: ${userMessage}`;
                        const response = await fetch(url, {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ contents: [{ parts: [{ text: prompt }] }] })
                        });
                        const data = await response.json();
                        if (data && data.candidates && data.candidates.length > 0 && data.candidates[0].content && data.candidates[0].content.parts && data.candidates[0].content.parts.length > 0) {
                            return data.candidates[0].content.parts[0].text;
                        }
                        throw new Error('No response returned');
                    } catch (err) {
                        console.error('Generation API error:', err);
                        return 'Sorry, the AI assistant could not generate a response.';
                    }
                }
            };
        }

    validate() {
        if (!this.loaded) {
            return {
                valid: false,
                error: 'Environment configuration not loaded'
            };
        }

        const missingKeys = this.getMissingKeys();
        if (missingKeys.length > 0) {
            return {
                valid: false,
                error: `Missing or invalid API keys: ${missingKeys.join(', ')}`
            };
        }

        return {
            valid: true,
            error: null
        };
    }
}

// Make all configuration available globally
if (typeof window !== 'undefined') {
    window.CONFIG = CONFIG;
    window.API_KEYS = API_KEYS;
    window.EnvConfig = EnvConfig;
    window.validateApiKeys = validateApiKeys;
}
