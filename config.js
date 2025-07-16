class EnvConfig {
    constructor() {
        this.envVars = {
            GEMINI_EMBEDDING_API_KEY: process.env.NEXT_PUBLIC_GEMINI_EMBEDDING_API_KEY,
            GEMINI_GENERATION_API_KEY: process.env.NEXT_PUBLIC_GEMINI_GENERATION_API_KEY
        };
        this.isInitialized = true;
    }

    async loadEnv() {
        try {
            // Environment variables are already loaded in Vercel
            return true;
        } catch (error) {
            console.error('Error accessing environment variables:', error);
            return false;
        }
    }

    get(key) {
        return this.envVars[key];
    }

    isLoaded() {
        return this.isInitialized;
    }

    hasRequiredKeys() {
        const required = ['GEMINI_EMBEDDING_API_KEY', 'GEMINI_GENERATION_API_KEY'];
        return required.every(key => Boolean(this.envVars[key]));
    }

    getMissingKeys() {
        const required = ['GEMINI_EMBEDDING_API_KEY', 'GEMINI_GENERATION_API_KEY'];
        return required.filter(key => !this.envVars[key]);
    }
}

export default EnvConfig;
