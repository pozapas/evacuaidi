// API Endpoint Checker Tool
// This file helps diagnose API connectivity issues

// Function to check a specific API endpoint
async function checkEndpoint(endpoint) {
    const baseUrl = window.location.origin;
    const url = new URL(endpoint, baseUrl).toString();
    const resultElem = document.getElementById('endpoint-results');
    
    try {
        console.log(`Testing endpoint: ${url}`);
        resultElem.innerHTML += `<p>Testing endpoint: ${url}</p>`;
        
        // Make the request
        const response = await fetch(url, {
            method: 'GET',
            headers: {
                'Accept': 'application/json',
                'Cache-Control': 'no-cache'
            }
        });
        
        // Get response as text first (works even if not valid JSON)
        const responseText = await response.text();
        
        // Try to parse as JSON
        let responseJson = null;
        try {
            responseJson = JSON.parse(responseText);
        } catch (e) {
            console.log('Response is not valid JSON');
        }
        
        const status = response.ok ? 
            '<span style="color: green">✓ SUCCESS</span>' : 
            '<span style="color: red">✗ FAILED</span>';
        
        resultElem.innerHTML += `<p>${status} Status: ${response.status} ${response.statusText}</p>`;
        
        if (responseJson) {
            resultElem.innerHTML += `<pre style="background: #f5f5f5; padding: 10px; overflow: auto;">${JSON.stringify(responseJson, null, 2)}</pre>`;
            
            // Check for API keys if this is the test endpoint
            if (endpoint === '/api/test' && responseJson) {
                if (responseJson.hasEmbeddingKey && responseJson.hasGenerationKey) {
                    resultElem.innerHTML += '<p style="color: green">✓ Both API keys found on server</p>';
                } else {
                    resultElem.innerHTML += '<p style="color: red">✗ API keys missing: ' + 
                        (!responseJson.hasEmbeddingKey ? 'GEMINI_EMBEDDING_API_KEY ' : '') +
                        (!responseJson.hasGenerationKey ? 'GEMINI_GENERATION_API_KEY' : '') + '</p>';
                }
            }
        } else {
            resultElem.innerHTML += `<p>Response body (not JSON):</p>`;
            resultElem.innerHTML += `<pre style="background: #f5f5f5; padding: 10px; overflow: auto;">${responseText}</pre>`;
        }
    } catch (error) {
        console.error(`Error testing endpoint ${url}:`, error);
        resultElem.innerHTML += `<p style="color: red">Error: ${error.message}</p>`;
    }
    
    resultElem.innerHTML += '<hr>';
}

// Function to check all API endpoints
async function checkAllEndpoints() {
    const resultElem = document.getElementById('endpoint-results');
    resultElem.innerHTML = '<h3>API Endpoint Test Results</h3>';
    
    // Add environment info
    resultElem.innerHTML += `<p>Testing from: ${window.location.origin}</p>`;
    resultElem.innerHTML += `<p>Browser: ${navigator.userAgent}</p>`;
    resultElem.innerHTML += '<hr>';
    
    // Test endpoints
    await checkEndpoint('/api/test');
    await checkEndpoint('/api/embeddings');
    
    resultElem.innerHTML += '<p>Testing complete! See results above.</p>';
}
