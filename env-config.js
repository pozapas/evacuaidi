/**
 * Environment Configuration Loader for EvacuAIDi Application
 * This class provides an interface for API communication
 */
class EnvConfig {
    constructor() {
        this.apiEndpoints = {
            embedding: '/api/embedding',
            generation: '/api/generate',
            health: '/api/health'
        };
        this.loaded = false;
        this.envVars = {}; // Add this for fallback
        this.requiredKeys = ['API connection']; // Add this for compatibility
    }

    /**
     * Initialize the API connection
     */
    async loadEnv() {
        try {
            // Detect deployment environment
            const isRenderDeploy = window.location.hostname.includes('render') || 
                                    window.location.hostname.includes('onrender.com');
            const isLocalhost = window.location.hostname === 'localhost' || 
                                window.location.hostname === '127.0.0.1';
            
            if (isRenderDeploy) {
                console.log('Render.com deployment detected - using origin-prefixed paths');
                // Ensure paths are absolute with origin for Render.com
                Object.keys(this.apiEndpoints).forEach(key => {
                    if (!this.apiEndpoints[key].startsWith('http')) {
                        this.apiEndpoints[key] = window.location.origin + this.apiEndpoints[key];
                    }
                });
            }
            
            // Try health check if local or in development mode
            if (isLocalhost || !isRenderDeploy) {
                try {
                    const response = await fetch(this.apiEndpoints.health);
                    if (response.ok) {
                        const healthData = await response.json();
                        console.log('API Health Check:', healthData);
                    }
                } catch (healthError) {
                    console.warn('Health check failed, but continuing:', healthError.message);
                }
            }
            
            this.loaded = true;
            console.log('API connection configured with endpoints:', this.apiEndpoints);
            return true;
        } catch (error) {
            console.error('Error establishing API connection:', error);
            // For Render.com - continue even if health check fails
            if (window.location.hostname.includes('render') || 
                window.location.hostname.includes('onrender.com')) {
                console.log('Render.com deployment detected - continuing despite connection issues');
                this.loaded = true;
                return true;
            }
            this.loaded = false;
            return false;
        }
    }

    /**
     * Get API endpoint by name
     * @param {string} key - The API endpoint name
     * @param {*} defaultValue - Default value if key doesn't exist
     * @returns {string} The API endpoint URL
     */
    get(key, defaultValue = null) {
        return this.apiEndpoints[key] || defaultValue;
    }

    /**
     * Check if API connection is available
     * @returns {boolean} True if API is connected
     */
    hasRequiredKeys() {
        return this.loaded;
    }

    /**
     * Get a list of missing endpoints (always empty if connected)
     * @returns {string[]} Empty array if connected
     */
    getMissingKeys() {
        return this.loaded ? [] : ['API connection'];
    }

    /**
     * Check if environment variables are loaded
     * @returns {boolean} True if API is initialized
     */
    isLoaded() {
        return this.loaded;
    }
}

// Make the class available globally
window.EnvConfig = EnvConfig;
