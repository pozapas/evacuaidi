// Local development configuration
// Copy this file to config.local.js and add your API keys for local testing
// This file is ignored by git to keep your keys private

window.APP_CONFIG = {
    // Add your actual API keys here for local development
    GEMINI_EMBEDDING_API_KEY: 'your_embedding_api_key_here',
    GEMINI_GENERATION_API_KEY: 'your_generation_api_key_here',
    
    // Environment detection
    isDevelopment: window.location.protocol === 'file:' || 
                   window.location.hostname === 'localhost' || 
                   window.location.hostname === '127.0.0.1',
    
    isProduction: window.location.hostname === 'pozapas.github.io',
    
    // Get configuration value with fallback
    get(key) {
        return this[key] || '';
    },
    
    // Check if keys are configured
    hasKeys() {
        const embeddingKey = this.GEMINI_EMBEDDING_API_KEY;
        const generationKey = this.GEMINI_GENERATION_API_KEY;
        return !!(embeddingKey && generationKey && 
                  embeddingKey !== 'your_embedding_api_key_here' &&
                  generationKey !== 'your_generation_api_key_here');
    }
};
