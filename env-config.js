// Environment Configuration Loader with Backend Proxy Support

class EnvConfig {
    constructor() {
        this.config = {};
        this.loaded = false;
        this.useProxy = false;
        
        // Determine if we should use backend proxy
        this.backendUrl = this.getBackendUrl();
        this.useProxy = !!this.backendUrl;
        
        if (this.useProxy) {
            console.log('Using backend proxy for API calls:', this.backendUrl);
            this.loaded = true;
        }
    }

    // Determine backend URL based on environment
    getBackendUrl() {
        // For production GitHub Pages, use Vercel serverless functions
        if (window.location.hostname === 'pozapas.github.io' || 
            window.location.hostname.includes('github.io')) {
            return 'https://evacuaidi-backend.vercel.app'; // Replace with your Vercel deployment URL
        }
        
        // For local development, try local backend first
        if (window.location.hostname === 'localhost' || 
            window.location.hostname === '127.0.0.1') {
            return 'http://localhost:3001'; // Local backend server
        }
        
        return null; // Fallback to direct API calls
    }

    // Load environment configuration
    async loadEnv() {
        if (this.useProxy) {
            // Using backend proxy, no need to load API keys client-side
            this.loaded = true;
            return;
        }
        
        try {
            // Try to fetch the .env file (for local development only)
            const response = await fetch('./.env');
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: .env file not found`);
            }
            
            const envText = await response.text();
            const lines = envText.split('\n');
            let keyCount = 0;
            
            for (const line of lines) {
                const trimmedLine = line.trim();
                
                if (trimmedLine === '' || trimmedLine.startsWith('#')) {
                    continue;
                }
                
                const [key, ...valueParts] = trimmedLine.split('=');
                if (key && valueParts.length > 0) {
                    const value = valueParts.join('=').trim();
                    this.config[key.trim()] = value;
                    keyCount++;
                }
            }
            
            if (keyCount === 0) {
                throw new Error('No valid key=value pairs found in .env file');
            }
            
            console.log(`Successfully loaded ${keyCount} environment variables from .env`);
            this.loaded = true;
        } catch (error) {
            console.warn('Could not load .env file:', error.message);
            console.log('Falling back to config.js configuration...');
            this.loadFromAppConfig();
        }
    }
    
    // Load from APP_CONFIG fallback
    loadFromAppConfig() {
        if (window.APP_CONFIG && window.APP_CONFIG.hasKeys()) {
            console.log('Using configuration from config.js');
            this.config['GEMINI_EMBEDDING_API_KEY'] = window.APP_CONFIG.get('GEMINI_EMBEDDING_API_KEY');
            this.config['GEMINI_GENERATION_API_KEY'] = window.APP_CONFIG.get('GEMINI_GENERATION_API_KEY');
            this.loaded = true;
        } else {
            console.error('No valid configuration found in config.js');
            this.loaded = false;
        }
    }

    // Get environment variable
    get(key) {
        return this.config[key] || null;
    }

    // Check if environment is loaded
    isLoaded() {
        return this.loaded;
    }

    // Check if using backend proxy
    isUsingProxy() {
        return this.useProxy;
    }

    // Get backend URL
    getProxyUrl() {
        return this.backendUrl;
    }
    
    // Check if required API keys are present (only relevant for direct API calls)
    hasRequiredKeys() {
        if (this.useProxy) {
            return true; // Backend handles API keys
        }
        
        const embedding = this.get('GEMINI_EMBEDDING_API_KEY');
        const generation = this.get('GEMINI_GENERATION_API_KEY');
        return !!(embedding && generation);
    }
    
    // Get missing keys for debugging
    getMissingKeys() {
        if (this.useProxy) {
            return []; // Backend handles API keys
        }
        
        const missing = [];
        if (!this.get('GEMINI_EMBEDDING_API_KEY')) missing.push('GEMINI_EMBEDDING_API_KEY');
        if (!this.get('GEMINI_GENERATION_API_KEY')) missing.push('GEMINI_GENERATION_API_KEY');
        return missing;
    }
}

// Export for use in main application
window.EnvConfig = EnvConfig;
