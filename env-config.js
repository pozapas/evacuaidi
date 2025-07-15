// Environment Configuration Loader

class EnvConfig {
    constructor() {
        this.config = {};
        this.loaded = false;
    }

    // Simple .env file parser (for client-side use)
    async loadEnv() {
        try {
            // Try to fetch the .env file
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
            
            console.log(`Successfully loaded ${keyCount} environment variables`);
            this.loaded = true;
        } catch (error) {
            console.error('Error loading environment configuration:', error);
            console.warn('Falling back to default configuration...');
            console.warn('Please ensure .env file exists and is properly formatted.');
            console.warn('See .env.example for the expected format.');
            console.warn('Or configure API keys in config.js for local development.');
            this.loaded = false;
            
            // Try fallback to APP_CONFIG if available
            if (window.APP_CONFIG && window.APP_CONFIG.hasKeys()) {
                console.log('Using fallback configuration from config.js');
                this.config['GEMINI_EMBEDDING_API_KEY'] = window.APP_CONFIG.get('GEMINI_EMBEDDING_API_KEY');
                this.config['GEMINI_GENERATION_API_KEY'] = window.APP_CONFIG.get('GEMINI_GENERATION_API_KEY');
                this.loaded = true;
            }
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
