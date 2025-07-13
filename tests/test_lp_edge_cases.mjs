// LP Solver Edge Cases Test Suite
// Tests edge cases, error conditions, and complex constraint scenarios
import { readFileSync } from 'fs';
import { dirname, join } from 'path';
import { fileURLToPath } from 'url';
import { solveIntegerLP } from '../lp-solver.mjs';
import { expandCompaniesWithCharters } from '../company-data.mjs';

const __dirname = dirname(fileURLToPath(import.meta.url));
const projectRoot = join(__dirname, '..');

// Load company data
const data = JSON.parse(readFileSync(join(projectRoot, 'companies_extracted.json'), 'utf8'));

console.log('=== LP SOLVER EDGE CASES TEST SUITE ===');

// Set up company data
let companies = {
    basic: data.basicCompanies || [],
    flavored: data.flavoredCompanies || [],
    canal: []
};

const allRaw = [...companies.basic, ...companies.flavored];
companies.canal = allRaw.filter(c => c.special === 'canal');
companies.flavored = companies.flavored.filter(c => c.special !== 'canal');

let allCompanies = [...companies.basic, ...companies.flavored, ...companies.canal];

const edgeCaseTests = [
    {
        name: "Empty Selection Test",
        description: "Test behavior with no buildings selected",
        selectedBuildings: [],
        priorityBuildings: [],
        requiredPrestigeGoods: [],
        requiredCompanies: [],
        maxSlots: 7,
        expectFailure: false,
        expectedBehavior: "Should still find optimal solution based on prestige goods"
    },
    {
        name: "Impossible Prestige Requirement",
        description: "Test with prestige good that doesn't exist", 
        selectedBuildings: ['Coal Mine', 'Iron Mine'],
        priorityBuildings: [],
        requiredPrestigeGoods: ['NonexistentPrestigeGood'],
        requiredCompanies: [],
        maxSlots: 7,
        expectFailure: true,
        expectedError: "infeasible"
    },
    {
        name: "Too Many Required Companies",
        description: "Require more companies than available slots",
        selectedBuildings: ['Coal Mine', 'Iron Mine', 'Steel Mills'],
        priorityBuildings: [],
        requiredPrestigeGoods: [],
        requiredCompanies: ['Carnegie Steel Co.', 'Basic Metal Mining', 'Basic Coal Mining', 'Basic Iron', 'Basic Steel', 'Basic Motors', 'Basic Paper', 'Basic Munitions'],
        maxSlots: 7,
        expectFailure: true,
        expectedError: "infeasible"
    },
    {
        name: "Prestige Good Conflict",
        description: "Require companies that provide same prestige good",
        selectedBuildings: ['Steel Mills', 'Iron Mine'],
        priorityBuildings: [],
        requiredPrestigeGoods: [],
        requiredCompanies: ['Carnegie Steel Co.', 'Duro y Compañía'], // Both provide Refined Steel
        maxSlots: 7,
        expectFailure: true,
        expectedError: "infeasible"
    },
    {
        name: "Single Slot Test",
        description: "Test optimization with only one company slot",
        selectedBuildings: ['Coal Mine', 'Iron Mine', 'Steel Mills', 'Paper Mill'],
        priorityBuildings: ['Steel Mills'],
        requiredPrestigeGoods: [],
        requiredCompanies: [],
        maxSlots: 1,
        expectFailure: false,
        expectedBehavior: "Should select single best company"
    },
    {
        name: "Zero Slots Test",
        description: "Test with zero company slots (only canal companies)",
        selectedBuildings: ['Port', 'Trade Center'],
        priorityBuildings: [],
        requiredPrestigeGoods: [],
        requiredCompanies: [],
        maxSlots: 0,
        expectFailure: false,
        expectedBehavior: "Should only select canal companies"
    },
    {
        name: "All Canal Companies Test",
        description: "Test selecting only canal companies with normal slots",
        selectedBuildings: ['Port', 'Trade Center'],
        priorityBuildings: [],
        requiredPrestigeGoods: [],
        requiredCompanies: [],
        maxSlots: 7,
        expectFailure: false,
        expectedBehavior: "Should select both canal companies without using slots"
    },
    {
        name: "Complex Charter Conflicts",
        description: "Test scenario where multiple companies want same charter",
        selectedBuildings: ['Shipyards', 'Steel Mills', 'Iron Mine'],
        priorityBuildings: [],
        requiredPrestigeGoods: [],
        requiredCompanies: [],
        maxSlots: 7,
        expectFailure: false,
        expectedBehavior: "Should resolve charter conflicts optimally"
    }
];

async function runEdgeCaseTest(test) {
    console.log(`\n=== ${test.name.toUpperCase()} ===`);
    console.log(`Description: ${test.description}`);
    console.log(`Expected: ${test.expectFailure ? 'FAILURE' : 'SUCCESS'} - ${test.expectedBehavior || test.expectedError}`);
    
    try {
        // Generate company variants 
        const variants = expandCompaniesWithCharters(allCompanies, test.selectedBuildings);
        
        // Run LP solver
        const selectedVariants = await solveIntegerLP(
            variants,
            test.maxSlots,
            test.selectedBuildings,
            test.priorityBuildings,
            test.requiredPrestigeGoods,
            test.requiredCompanies
        );
        
        if (test.expectFailure) {
            console.log(`❌ ${test.name} FAILED: Expected failure but got solution with ${selectedVariants.length} companies`);
            return false;
        } else {
            console.log(`✅ ${test.name} PASSED: Found solution with ${selectedVariants.length} companies`);
            
            // Validate specific expectations
            if (test.maxSlots === 0) {
                const regularCompanies = selectedVariants.filter(c => c.special !== 'canal');
                if (regularCompanies.length > 0) {
                    console.log(`  ❌ With 0 slots, expected only canal companies, but got ${regularCompanies.length} regular companies`);
                    return false;
                } else {
                    console.log(`  ✅ Correctly selected only canal companies with 0 slots`);
                }
            }
            
            if (test.maxSlots === 1) {
                const regularCompanies = selectedVariants.filter(c => c.special !== 'canal');
                if (regularCompanies.length > 1) {
                    console.log(`  ❌ With 1 slot, expected at most 1 regular company, got ${regularCompanies.length}`);
                    return false;
                } else {
                    console.log(`  ✅ Correctly used at most 1 slot`);
                }
            }
            
            return true;
        }
        
    } catch (error) {
        if (test.expectFailure) {
            if (test.expectedError && error.message.includes(test.expectedError)) {
                console.log(`✅ ${test.name} PASSED: Correctly failed with expected error`);
                console.log(`  Error: ${error.message}`);
                return true;
            } else {
                console.log(`❌ ${test.name} FAILED: Failed with unexpected error`);
                console.log(`  Expected error containing: ${test.expectedError}`);
                console.log(`  Actual error: ${error.message}`);
                return false;
            }
        } else {
            console.log(`❌ ${test.name} FAILED: Unexpected error - ${error.message}`);
            return false;
        }
    }
}

// Performance test
async function runPerformanceTest() {
    console.log(`\n=== PERFORMANCE TEST ===`);
    console.log(`Testing LP solver performance with large problem size`);
    
    // Use all buildings and all companies for maximum complexity
    const allBuildings = new Set();
    allCompanies.forEach(company => {
        company.buildings.forEach(building => allBuildings.add(building));
        if (company.industryCharters) {
            company.industryCharters.forEach(charter => allBuildings.add(charter));
        }
    });
    
    const selectedBuildings = Array.from(allBuildings);
    console.log(`Problem size: ${allCompanies.length} companies, ${selectedBuildings.length} buildings`);
    
    const startTime = performance.now();
    
    try {
        const variants = expandCompaniesWithCharters(allCompanies, selectedBuildings);
        console.log(`Generated ${variants.length} company variants`);
        
        const selectedVariants = await solveIntegerLP(
            variants,
            7,
            selectedBuildings,
            [],
            [],
            []
        );
        
        const endTime = performance.now();
        const duration = endTime - startTime;
        
        console.log(`✅ Performance test completed in ${duration.toFixed(0)}ms`);
        console.log(`Selected ${selectedVariants.length} companies`);
        
        if (duration > 10000) { // 10 seconds
            console.log(`⚠️  Performance warning: Optimization took ${(duration/1000).toFixed(1)} seconds`);
        }
        
        return true;
        
    } catch (error) {
        const endTime = performance.now();
        const duration = endTime - startTime;
        console.log(`❌ Performance test failed after ${duration.toFixed(0)}ms: ${error.message}`);
        return false;
    }
}

// Run all edge case tests
async function runAllEdgeCaseTests() {
    console.log(`\nRunning ${edgeCaseTests.length} edge case tests...\n`);
    
    const results = [];
    for (const test of edgeCaseTests) {
        const passed = await runEdgeCaseTest(test);
        results.push({ name: test.name, passed });
    }
    
    // Run performance test
    const perfPassed = await runPerformanceTest();
    results.push({ name: 'Performance Test', passed: perfPassed });
    
    // Summary
    console.log('\n=== EDGE CASE TEST SUMMARY ===');
    const passedCount = results.filter(r => r.passed).length;
    results.forEach(result => {
        console.log(`${result.passed ? '✅' : '❌'} ${result.name}`);
    });
    
    console.log(`\nOverall: ${passedCount}/${results.length} edge case tests passed`);
    
    if (passedCount === results.length) {
        console.log('🎉 ALL EDGE CASE TESTS PASSED! LP solver handles edge cases correctly.');
        process.exit(0);
    } else {
        console.log('❌ Some edge case tests failed. LP solver needs investigation.');
        process.exit(1);
    }
}

// Run the edge case test suite
runAllEdgeCaseTests().catch(error => {
    console.error('❌ EDGE CASE TEST SUITE FAILED:', error.message);
    process.exit(1);
});