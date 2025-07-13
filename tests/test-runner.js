#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// Test runner for Victoria 3 Company Optimizer
console.log('🚀 Victoria 3 Company Optimizer Test Suite');
console.log('==========================================\n');

// Change to parent directory so tests can access companies_extracted.json
process.chdir(path.join(__dirname, '..'));

// Load test files
const testFiles = fs.readdirSync(__dirname)
    .filter(file => file.startsWith('test_') && file.endsWith('.js'))
    .sort();

const debugFiles = fs.readdirSync(__dirname)
    .filter(file => file.startsWith('debug_') && file.endsWith('.js'))
    .sort();

let totalTests = 0;
let passedTests = 0;
let failedTests = 0;

// Run test files
console.log('📋 Running Test Files...');
console.log('=' .repeat(50));

for (const testFile of testFiles) {
    console.log(`\n🔍 Running ${testFile}...`);
    console.log('-'.repeat(30));
    
    try {
        // Run the test file and capture output
        const output = execSync(`node tests/${testFile}`, { encoding: 'utf8', stdio: 'pipe' });
        console.log(output);
        passedTests++;
        totalTests++;
        
    } catch (error) {
        console.error(`❌ Error in ${testFile}:`);
        console.error(error.stdout || error.message);
        failedTests++;
        totalTests++;
    }
}

// Run debug files
console.log('\n📋 Running Debug Files...');
console.log('='.repeat(50));

for (const debugFile of debugFiles) {
    console.log(`\n🔍 Running ${debugFile}...`);
    console.log('-'.repeat(30));
    
    try {
        // Run the debug file and capture output
        const output = execSync(`node tests/${debugFile}`, { encoding: 'utf8', stdio: 'pipe' });
        console.log(output);
        passedTests++;
        totalTests++;
        
    } catch (error) {
        console.error(`❌ Error in ${debugFile}:`);
        console.error(error.stdout || error.message);
        failedTests++;
        totalTests++;
    }
}

// Summary
console.log('\n==========================================');
console.log('📊 Test Summary:');
console.log(`   Total tests: ${totalTests}`);
console.log(`   ✅ Passed: ${passedTests}`);
console.log(`   ❌ Failed: ${failedTests}`);
console.log(`   Success rate: ${totalTests > 0 ? ((passedTests / totalTests) * 100).toFixed(1) : 0}%`);

if (failedTests > 0) {
    process.exit(1);
}