// Environment Configuration Loader - Generated during build
class EnvConfig {
    constructor() {
        this.config = {
            GEMINI_EMBEDDING_API_KEY: "AIzaSyA72CsBj8MS9_KoG6ibXdBpv_Y5YMLpn3w",
            GEMINI_GENERATION_API_KEY: "AIzaSyAlUCTBXfBKz2GTAd_CGhkm00Oh7UXBsrQ"
        };
        this.loaded = true;
    }

    // Load environment configuration (minimal in production)
    async loadEnv() {
        // In production, already loaded with environment variables
        // No additional loading required
        console.log('EnvConfig: Production environment loaded');
    }
    
    // Get environment variable
    get(key) {
        return this.config[key] || null;
    }

    // Check if environment is loaded
    isLoaded() {
        return this.loaded;
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
