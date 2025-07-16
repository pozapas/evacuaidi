// Simple environment configuration for EvacuAIDi presentation
// This handles API calls to Vercel serverless functions

class EnvConfig {
    constructor() {
        this.loaded = true; // Always ready since we use serverless functions
    }

    // For Vercel deployment, always use the serverless functions
    isUsingProxy() {
        return true; // Always use Vercel serverless functions
    }

    // Get the base URL for API calls
    getProxyUrl() {
        return window.location.origin;
    }

    // Always ready when using serverless functions
    isLoaded() {
        return true;
    }

    // Always has keys when using serverless functions (backend handles them)
    hasRequiredKeys() {
        return true;
    }

    // No missing keys when using serverless functions
    getMissingKeys() {
        return [];
    }

    // Dummy method for compatibility
    async loadEnv() {
        return Promise.resolve();
    }

    // Dummy method for compatibility
    get(key) {
        return null; // Not needed for serverless setup
    }
}

// Export to global scope
window.EnvConfig = EnvConfig;
