// Configuration for EvacuAIDi presentation
window.EVACUAIDI_CONFIG = {
    author: "Amir Rafe",
    university: "Utah State University",
    year: "2025",
    advisor: "Dr. Patrick Singleton",
    department: "Civil & Environmental Engineering"
};

window.APP_CONFIG = {
    // API keys are loaded dynamically for security
    // Actual keys are not stored in this public repository
    GEMINI_EMBEDDING_API_KEY: '',
    GEMINI_GENERATION_API_KEY: '',
    
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
        return !!(this.GEMINI_EMBEDDING_API_KEY && this.GEMINI_GENERATION_API_KEY);
    },
    
    // Load API keys securely (called from external source)
    loadKeys(embeddingKey, generationKey) {
        this.GEMINI_EMBEDDING_API_KEY = embeddingKey;
        this.GEMINI_GENERATION_API_KEY = generationKey;
    }
};
