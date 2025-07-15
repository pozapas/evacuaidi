// Configuration for EvacuAIDi presentation
window.EVACUAIDI_CONFIG = {
    author: "Amir Rafe",
    university: "Utah State University",
    year: "2025",
    advisor: "Dr. Patrick Singleton",
    department: "Civil & Environmental Engineering"
};

window.APP_CONFIG = {
    // API keys will be injected during build process for security
    // Do not commit actual API keys to this file
    GEMINI_EMBEDDING_API_KEY: '{{GEMINI_EMBEDDING_API_KEY}}',
    GEMINI_GENERATION_API_KEY: '{{GEMINI_GENERATION_API_KEY}}',
    
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
                  !embeddingKey.includes('{{') && 
                  !generationKey.includes('{{'));
    }
};
