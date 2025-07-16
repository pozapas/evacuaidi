// Vercel Serverless Function for EvacuAIDi AI Chat
// This API endpoint securely handles Gemini API calls without exposing keys

export default async function handler(req, res) {
    // Enable CORS for GitHub Pages
    // Allow all origins (GitHub Pages, Vercel, local)
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
    
    // Handle preflight requests
    if (req.method === 'OPTIONS') {
        return res.status(200).end();
    }
    
    // Only allow POST requests
    if (req.method !== 'POST') {
        return res.status(405).json({ error: 'Method not allowed' });
    }
    
    try {
        const { message, context } = req.body;
        
        // Validate input
        if (!message || typeof message !== 'string' || message.trim().length === 0) {
            return res.status(400).json({ error: 'Message is required' });
        }
        
        if (message.length > 500) {
            return res.status(400).json({ error: 'Message too long (max 500 characters)' });
        }
        
        // Get API key from environment variables
        const apiKey = process.env.GEMINI_GENERATION_API_KEY;
        if (!apiKey) {
            console.error('GEMINI_GENERATION_API_KEY not found in environment variables');
            return res.status(500).json({ error: 'Server configuration error' });
        }
        
        // Prepare the enhanced prompt with RAG context
        const enhancedPrompt = `You are an AI research assistant answering questions about Amir Rafe's PhD dissertation "EvacuAIDi: An AI-Driven, Causal-Informed Framework for Probabilistic and Disability-Inclusive Evacuation Guidance" from Utah State University (2025).

${context ? `Based on the following relevant dissertation content:\n\n${context}\n\n` : ''}

User Question: ${message}

Instructions:
- Provide specific details from the research including exact numbers, percentages, and findings
- Explain technical concepts clearly and accurately
- If the question is outside the scope of the provided context, clearly state that and suggest the user contact Amir Rafe at amir.rafe@usu.edu for more detailed information
- Be concise but comprehensive
- Focus on the EvacuAIDi research findings and methodology

Answer:`;

        const payload = {
            contents: [
                {
                    role: "user",
                    parts: [{ text: enhancedPrompt }]
                }
            ]
        };

        const apiUrl = `https://generativelanguage.googleapis.com/v1beta/models/gemma-3-27b-it:generateContent?key=${apiKey}`;

        const response = await fetch(apiUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const result = await response.json();

        if (!response.ok) {
            console.error('Gemini API Error:', result);
            return res.status(500).json({ 
                error: 'AI service unavailable',
                details: result.error?.message || 'Unknown error'
            });
        }

        // Extract the response
        if (result.candidates && result.candidates.length > 0 && 
            result.candidates[0].content && result.candidates[0].content.parts && 
            result.candidates[0].content.parts.length > 0) {
            
            const botMessage = result.candidates[0].content.parts[0].text;
            return res.status(200).json({ message: botMessage });
        } else {
            return res.status(500).json({ 
                error: 'Invalid response from AI service',
                fallback: `I apologize, but I encountered an issue. However, here are key findings from the EvacuAIDi research:

**Main Research Contributions:**
• **22.5% reduction** in evacuation time through AI guidance
• **15.9% stronger benefits** for individuals with disabilities  
• **92%+ accuracy** in automated parameter extraction from safety codes
• **57% of risk variance** attributed to occupant load, **29%** to AI compliance

For more detailed information, please contact **Amir Rafe** at **amir.rafe@usu.edu**`
            });
        }

    } catch (error) {
        console.error('API Error:', error);
        return res.status(500).json({ 
            error: 'Server error',
            message: 'Please try again later or contact amir.rafe@usu.edu for support'
        });
    }
}
