// Configuration for EvacuAIDi presentation
window.EVACUAIDI_CONFIG = {
    author: "Amir Rafe",
    university: "Utah State University",
    year: "2025",
    advisor: "Dr. Patrick Singleton",
    department: "Civil & Environmental Engineering"
};

window.APP_CONFIG = {
    // API keys configuration for GitHub Pages
    // Note: For security, consider using a backend service for production
    GEMINI_EMBEDDING_API_KEY: 'AIzaSyA72CsBj8MS9_KoG6ibXdBpv_Y5YMLpn3w',
    GEMINI_GENERATION_API_KEY: 'AIzaSyAlUCTBXfBKz2GTAd_CGhkm00Oh7UXBsrQ',
    
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
    }
};
