// Configuration for EvacuAIDi presentation
window.EVACUAIDI_CONFIG = {
    author: "Amir Rafe",
    university: "Utah State University",
    year: "2025",
    advisor: "Dr. Patrick Singleton",
    department: "Civil & Environmental Engineering"
};

// Simplified configuration - API keys are handled by Vercel serverless functions
window.APP_CONFIG = {
    // Environment detection
    isDevelopment: window.location.protocol === 'file:' || 
                   window.location.hostname === 'localhost' || 
                   window.location.hostname === '127.0.0.1',
    
    isProduction: window.location.hostname.includes('vercel.app') || 
                  window.location.hostname === 'pozapas.github.io',
    
    // API endpoints
    getApiUrl(endpoint) {
        const baseUrl = window.location.origin;
        return `${baseUrl}/api/${endpoint}`;
    }
};
