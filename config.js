/**
 * Configuration Settings for EvacuAIDi Application
 * This file contains application configuration settings
 */

// Application Settings
const appConfig = {
    appName: "EvacuAIDi",
    version: "1.0.0",
    description: "An AI-Driven, Causal-Informed Framework for Probabilistic and Disability-Inclusive Evacuation Guidance",
    author: "Amir Rafe",
    institution: "Utah State University"
};

// AI Assistant Configuration
const aiConfig = {
    // Maximum tokens to generate in responses
    maxResponseTokens: 500,
    
    // Temperature controls randomness (0.0-1.0)
    temperature: 0.7,
    
    // Models to use
    models: {
        embedding: "gemini-embedding-001",
        generation: "gemma-3-27b-it"
    },
    
    // RAG (Retrieval-Augmented Generation) Settings
    rag: {
        chunkSize: 800,
        chunkOverlap: 200,
        topK: 4
    }
};

// Export configurations
window.appConfig = appConfig;
window.aiConfig = aiConfig;
