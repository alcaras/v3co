// LP Solver Test Runner
// Runs all LP solver tests in sequence and provides comprehensive reporting
import { spawn } from 'child_process';
import { dirname, join } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));

console.log('=== LP SOLVER TEST RUNNER ===');
console.log('Running comprehensive test suite for YALPS-based LP solver\n');

const testFiles = [
    {
        name: 'Steel Requirement Test',
        file: 'test_lp_solver_steel_requirement.mjs',
        description: 'Tests Steel prestige good OR constraint logic'
    },
    {
        name: 'Canal Companies Bug Test', 
        file: 'test_canal_companies_bug.mjs',
        description: 'Tests that both canal companies can be selected simultaneously'
    },
    {
        name: 'Comprehensive Test Suite',
        file: 'test_lp_comprehensive.mjs',
        description: 'Tests various optimization scenarios and constraints'
    },
    {
        name: 'Edge Cases Test Suite',
        file: 'test_lp_edge_cases.mjs',
        description: 'Tests edge cases, error conditions, and performance'
    }
];

function runTest(testFile) {
    return new Promise((resolve, reject) => {
        console.log(`🧪 Running ${testFile.name}...`);
        console.log(`   ${testFile.description}`);
        
        const startTime = Date.now();
        const testProcess = spawn('node', [testFile.file], {
            cwd: __dirname,
            stdio: 'pipe'
        });
        
        let output = '';
        let errorOutput = '';
        
        testProcess.stdout.on('data', (data) => {
            output += data.toString();
        });
        
        testProcess.stderr.on('data', (data) => {
            errorOutput += data.toString();
        });
        
        testProcess.on('close', (code) => {
            const duration = Date.now() - startTime;
            const result = {
                name: testFile.name,
                file: testFile.file,
                passed: code === 0,
                duration,
                output,
                errorOutput
            };
            
            if (code === 0) {
                console.log(`   ✅ PASSED (${duration}ms)`);
            } else {
                console.log(`   ❌ FAILED (${duration}ms)`);
            }
            
            resolve(result);
        });
        
        testProcess.on('error', (error) => {
            console.log(`   ❌ ERROR: ${error.message}`);
            reject(error);
        });
    });
}

async function runAllTests() {
    const results = [];
    const startTime = Date.now();
    
    console.log(`Running ${testFiles.length} test suites...\n`);
    
    for (const testFile of testFiles) {
        try {
            const result = await runTest(testFile);
            results.push(result);
        } catch (error) {
            console.error(`Failed to run ${testFile.name}: ${error.message}`);
            results.push({
                name: testFile.name,
                file: testFile.file,
                passed: false,
                duration: 0,
                output: '',
                errorOutput: error.message
            });
        }
        console.log(''); // Add spacing between tests
    }
    
    const totalDuration = Date.now() - startTime;
    
    // Generate summary report
    console.log('='.repeat(60));
    console.log('                    TEST RESULTS SUMMARY');
    console.log('='.repeat(60));
    
    const passedTests = results.filter(r => r.passed);
    const failedTests = results.filter(r => !r.passed);
    
    console.log(`\\nOverall Results: ${passedTests.length}/${results.length} tests passed`);
    console.log(`Total Duration: ${totalDuration}ms\\n`);
    
    // Detailed results
    results.forEach(result => {
        const status = result.passed ? '✅ PASS' : '❌ FAIL';
        const duration = result.duration.toString().padStart(6);
        console.log(`${status} ${duration}ms  ${result.name}`);
    });
    
    // Show failed test details
    if (failedTests.length > 0) {
        console.log('\\n' + '='.repeat(60));
        console.log('                     FAILURE DETAILS');
        console.log('='.repeat(60));
        
        failedTests.forEach(result => {
            console.log(`\\n❌ ${result.name} (${result.file})`);
            console.log('-'.repeat(40));
            
            if (result.errorOutput) {
                console.log('STDERR:');
                console.log(result.errorOutput);
            }
            
            if (result.output) {
                // Show last 20 lines of output for failed tests
                const lines = result.output.split('\\n');
                const relevantLines = lines.slice(-20);
                console.log('STDOUT (last 20 lines):');
                relevantLines.forEach(line => console.log(line));
            }
        });
    }
    
    // Performance summary
    console.log('\\n' + '='.repeat(60));
    console.log('                   PERFORMANCE SUMMARY');
    console.log('='.repeat(60));
    
    const totalTestDuration = results.reduce((sum, r) => sum + r.duration, 0);
    const avgDuration = totalTestDuration / results.length;
    
    console.log(`\\nAverage test duration: ${avgDuration.toFixed(0)}ms`);
    console.log('Test durations:');
    results.forEach(result => {
        const bar = '█'.repeat(Math.floor(result.duration / 100));
        console.log(`  ${result.name.padEnd(30)} ${result.duration.toString().padStart(6)}ms ${bar}`);
    });
    
    // Final verdict
    console.log('\\n' + '='.repeat(60));
    if (passedTests.length === results.length) {
        console.log('🎉 ALL LP SOLVER TESTS PASSED!');
        console.log('The YALPS-based Integer Linear Programming solver is working correctly.');
        console.log('✅ Ready for production use');
    } else {
        console.log('❌ SOME LP SOLVER TESTS FAILED');
        console.log(`${failedTests.length} out of ${results.length} test suites failed.`);
        console.log('⚠️  LP solver needs investigation before production use');
    }
    console.log('='.repeat(60));
    
    // Exit with appropriate code
    process.exit(failedTests.length === 0 ? 0 : 1);
}

// Run all tests
runAllTests().catch(error => {
    console.error('❌ TEST RUNNER FAILED:', error.message);
    process.exit(1);
});