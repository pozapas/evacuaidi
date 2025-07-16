// Secure Configuration for EvacuAIDi Application (GitHub Pages)
// This version uses a backend API proxy to protect API keys

// Application Configuration Constants
const CONFIG = {
    APP_NAME: 'EvacuAIDi',
    VERSION: '1.0.0',
    AUTHOR: 'Amir Rafe',
    UNIVERSITY: 'Utah State University',
    
    // Backend API Configuration (Vercel deployment)
    // Update this URL after deploying to Vercel
    API_BASE_URL: 'https://evacuaidi-presentation.vercel.app',
    
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

// Secure API client that uses backend proxy
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
            console.error('Error generating embedding:', error);
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
            console.error('Error generating response:', error);
            throw error;
        }
    }
}

// Legacy EnvConfig class for compatibility (now uses secure backend)
class EnvConfig {
    constructor() {
        this.apiClient = new SecureApiClient(CONFIG.API_BASE_URL);
        this.loaded = false;
        this.requiredKeys = [
            'GEMINI_EMBEDDING_API_KEY',
            'GEMINI_GENERATION_API_KEY'
        ];
    }

    async loadEnv() {
        try {
            // Test backend connectivity
            const testResponse = await fetch(`${CONFIG.API_BASE_URL}/api/chat`, {
                method: 'OPTIONS'
            });
            
            if (testResponse.status === 200 || testResponse.status === 204) {
                this.loaded = true;
                console.log('Secure backend connection established');
                return true;
            } else {
                throw new Error('Backend not accessible');
            }
        } catch (error) {
            console.error('Failed to connect to secure backend:', error);
            this.loaded = false;
            return false;
        }
    }

    get(key) {
        // For backward compatibility, but keys are now handled securely on backend
        if (!this.loaded) {
            console.warn('Backend not connected. Call loadEnv() first.');
            return null;
        }
        
        // Return a placeholder since real keys are on backend
        if (key === 'GEMINI_EMBEDDING_API_KEY' || key === 'GEMINI_GENERATION_API_KEY') {
            return 'SECURE_BACKEND_HANDLED';
        }
        
        return null;
    }

    isLoaded() {
        return this.loaded;
    }

    hasRequiredKeys() {
        return this.loaded; // Backend handles key validation
    }

    getMissingKeys() {
        return this.loaded ? [] : this.requiredKeys;
    }

    validate() {
        if (!this.loaded) {
            return {
                valid: false,
                error: 'Backend connection not established'
            };
        }

        return {
            valid: true,
            error: null
        };
    }
}

// Secure wrapper functions for embedding generation
async function generateEmbedding(text) {
    const apiClient = new SecureApiClient(CONFIG.API_BASE_URL);
    return await apiClient.generateEmbedding(text);
}

// Validation function (now checks backend connectivity)
async function validateApiKeys() {
    try {
        const testResponse = await fetch(`${CONFIG.API_BASE_URL}/api/chat`, {
            method: 'OPTIONS'
        });
        
        const isValid = testResponse.status === 200 || testResponse.status === 204;
        
        if (isValid) {
            console.log('Backend API connection validated successfully');
        } else {
            console.error('Backend API validation failed');
        }
        
        return isValid;
    } catch (error) {
        console.error('Backend API validation error:', error);
        return false;
    }
}

// Make all configuration available globally
if (typeof window !== 'undefined') {
    window.CONFIG = CONFIG;
    window.SecureApiClient = SecureApiClient;
    window.EnvConfig = EnvConfig;
    window.generateEmbedding = generateEmbedding;
    window.validateApiKeys = validateApiKeys;
}
