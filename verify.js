// Simple verification script to check if EnvConfig is properly loaded
(function() {
    document.addEventListener('DOMContentLoaded', function() {
        console.log('verify.js: Checking EnvConfig availability...');
        
        if (typeof window.EnvConfig === 'undefined') {
            console.error('CRITICAL ERROR: EnvConfig is not defined in global scope!');
            console.log('Available global objects:', Object.keys(window).filter(key => key.includes('Config') || key.includes('config')));
        } else {
            console.log('EnvConfig successfully loaded and available in global scope');
        }
    });
})();
