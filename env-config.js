// Environment Configuration Loader

class EnvConfig {
    constructor() {
        this.config = {};
        this.loaded = false;
    }

    // Load environment configuration
    async loadEnv() {
        try {
            // For GitHub Pages, always use APP_CONFIG fallback
            if (window.location.hostname === 'pozapas.github.io' || 
                window.location.hostname.includes('github.io')) {
                console.log('GitHub Pages detected - using config.js settings');
                this.loadFromAppConfig();
                return;
            }
            
            // Try to fetch the .env file (for local development)
            const response = await fetch('./.env');
            
            // Check if the response is successful
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: .env file not found or not accessible`);
            }
            
            const envText = await response.text();
            
            // Check if the content looks like an env file
            if (!envText.trim()) {
                throw new Error('.env file is empty');
            }
            
            const lines = envText.split('\n');
            let keyCount = 0;
            
            for (const line of lines) {
                const trimmedLine = line.trim();
                
                // Skip comments and empty lines
                if (trimmedLine === '' || trimmedLine.startsWith('#')) {
                    continue;
                }
                
                // Parse key=value pairs
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
        return this.loaded && Object.keys(this.config).length > 0;
    }

    // Get all API keys for debugging (remove in production)
    getApiKeys() {
        return {
            embedding: this.get('GEMINI_EMBEDDING_API_KEY'),
            generation: this.get('GEMINI_GENERATION_API_KEY')
        };
    }
    
    // Check if required API keys are present
    hasRequiredKeys() {
        const embedding = this.get('GEMINI_EMBEDDING_API_KEY');
        const generation = this.get('GEMINI_GENERATION_API_KEY');
        return !!(embedding && generation);
    }
    
    // Get missing keys for debugging
    getMissingKeys() {
        const missing = [];
        if (!this.get('GEMINI_EMBEDDING_API_KEY')) missing.push('GEMINI_EMBEDDING_API_KEY');
        if (!this.get('GEMINI_GENERATION_API_KEY')) missing.push('GEMINI_GENERATION_API_KEY');
        return missing;
    }
}

// Export for use in main application
window.EnvConfig = EnvConfig;
