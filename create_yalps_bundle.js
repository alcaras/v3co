#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

// Read all YALPS module files and combine them into a browser bundle
const yalpsDir = 'node_modules/yalps/lib/main';

console.log('Creating YALPS browser bundle...');

// Read the files in dependency order
const files = [
    'util.js',
    'types.js', 
    'constraint.js',
    'tableau.js',
    'simplex.js',
    'branchAndCut.js',
    'YALPS.js'
];

let bundleCode = `// YALPS Browser Bundle - Auto-generated from Node.js modules
(function(global) {
    'use strict';
    
    // Create YALPS namespace
    const YALPS = {};
    const exports = {};
    const module = { exports: exports };
    
    // Internal modules store
    const modules = {};
    
    // Require function for internal modules
    function require(moduleName) {
        if (moduleName.startsWith('./')) {
            const cleanName = moduleName.replace('./', '').replace('.js', '');
            return modules[cleanName] || {};
        }
        return {};
    }
    
`;

// Process each file
files.forEach(fileName => {
    const filePath = path.join(yalpsDir, fileName);
    if (fs.existsSync(filePath)) {
        const content = fs.readFileSync(filePath, 'utf8');
        const moduleName = fileName.replace('.js', '');
        
        console.log(`Adding ${fileName}...`);
        
        bundleCode += `
    // === ${fileName} ===
    (function() {
        const exports = {};
        const module = { exports: exports };
        
        ${content}
        
        modules['${moduleName}'] = module.exports;
    })();
`;
    }
});

bundleCode += `
    // Export the main solve function
    YALPS.solve = modules.YALPS.solve;
    YALPS.defaultOptions = modules.YALPS.defaultOptions;
    
    // Make available globally
    if (typeof window !== 'undefined') {
        window.YALPS = YALPS;
    } else {
        global.YALPS = YALPS;
    }
    
})(typeof window !== 'undefined' ? window : global);
`;

// Write the bundle
fs.writeFileSync('yalps_browser_bundle.js', bundleCode);
console.log('✅ Created yalps_browser_bundle.js');

// Test the bundle
console.log('🧪 Testing the bundle...');
eval(bundleCode);

const testModel = {
    direction: "maximize", 
    objective: "coverage",
    constraints: {
        maxCompanies: { max: 2 }
    },
    variables: {
        companyA: { maxCompanies: 1, coverage: 4 }, 
        companyB: { maxCompanies: 1, coverage: 3 }, 
        companyC: { maxCompanies: 1, coverage: 2 }
    },
    integers: ["companyA", "companyB", "companyC"]
};

const result = YALPS.solve(testModel);
console.log('Test result:', result);

if (result.status === 'optimal') {
    console.log('✅ Bundle works correctly!');
} else {
    console.log('❌ Bundle has issues');
}