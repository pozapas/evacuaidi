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
    }

    /**
     * Initialize the API connection
     */
    async loadEnv() {
        try {
            // Check API health
            const response = await fetch(this.apiEndpoints.health);
            if (!response.ok) {
                throw new Error(`API health check failed: ${response.status}`);
            }
            
            const healthData = await response.json();
            console.log('API Health Check:', healthData);
            
            this.loaded = true;
            console.log('API connection established successfully');
            return true;
        } catch (error) {
            console.error('Error establishing API connection:', error);
            this.loaded = false;
            return false;
        }
    }

    /**
     * Get API endpoint by name
     * @param {string} key - The API endpoint name
     * @returns {string} The API endpoint URL
     */
    get(key) {
        return this.apiEndpoints[key] || null;
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
     * Check if API is initialized
     * @returns {boolean} True if API is initialized
     */
    isLoaded() {
        return this.loaded;
    }
}

// Make the class available globally
window.EnvConfig = EnvConfig;

    /**
     * Get an environment variable by key
     * @param {string} key - The environment variable name
     * @param {*} defaultValue - Default value if key doesn't exist
     * @returns {string|null} The environment variable value or default
     */
    get(key, defaultValue = null) {
        return this.envVars[key] !== undefined ? this.envVars[key] : defaultValue;
    }

    /**
     * Check if all required keys are present
     * @returns {boolean} True if all required keys are present
     */
    hasRequiredKeys() {
        return this.requiredKeys.every(key => this.envVars[key] !== undefined);
    }

    /**
     * Get a list of missing required keys
     * @returns {string[]} Array of missing required keys
     */
    getMissingKeys() {
        return this.requiredKeys.filter(key => this.envVars[key] === undefined);
    }

    /**
     * Check if environment variables are loaded
     * @returns {boolean} True if environment is loaded
     */
    isLoaded() {
        return this.loaded;
    }
}

// Make the class available globally
window.EnvConfig = EnvConfig;
