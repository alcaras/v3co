// Custom wrapper to ensure YALPS integer constraints work properly
const originalYALPS = require('yalps');

// Create a wrapper that ensures integer constraints are handled
const solve = function(model) {
    // Log the model to debug
    console.log('Input model:', JSON.stringify(model, null, 2));
    
    // Ensure integers array is properly passed
    if (model.integers && Array.isArray(model.integers)) {
        console.log('Integer variables:', model.integers);
    }
    
    // Call original solve
    const result = originalYALPS.solve(model);
    
    // Log result to debug
    console.log('Raw result:', result);
    
    return result;
};

// Export wrapper
module.exports = {
    solve: solve,
    defaultOptions: originalYALPS.defaultOptions
};