// Comprehensive LP Solver Test Suite
// Tests the YALPS-based Integer Linear Programming solver with various scenarios
import { readFileSync } from 'fs';
import { dirname, join } from 'path';
import { fileURLToPath } from 'url';
import { solveIntegerLP, calculateIndividualScore } from '../lp-solver.mjs';
import { expandCompaniesWithCharters } from '../company-data.mjs';

const __dirname = dirname(fileURLToPath(import.meta.url));
const projectRoot = join(__dirname, '..');

// Load company data
const data = JSON.parse(readFileSync(join(projectRoot, 'companies_extracted.json'), 'utf8'));

console.log('=== COMPREHENSIVE LP SOLVER TEST SUITE ===');

// Set up company data structure
let companies = {
    basic: data.basicCompanies || [],
    flavored: data.flavoredCompanies || [],
    canal: []
};

// Find canal companies and separate them
const allRaw = [...companies.basic, ...companies.flavored];
companies.canal = allRaw.filter(c => c.special === 'canal');
companies.flavored = companies.flavored.filter(c => c.special !== 'canal');

let allCompanies = [...companies.basic, ...companies.flavored, ...companies.canal];

// Test scenarios
const testScenarios = [
    {
        name: "Basic Coverage Test",
        description: "Select few buildings, ensure optimal coverage",
        selectedBuildings: ['Coal Mine', 'Iron Mine', 'Steel Mills', 'Paper Mill'],
        priorityBuildings: ['Steel Mills'],
        requiredPrestigeGoods: [],
        requiredCompanies: [],
        maxSlots: 7,
        expectedMinCompanies: 3
    },
    {
        name: "Steel Requirement Test", 
        description: "Test Steel prestige good OR constraint (Refined Steel OR Sheffield Steel)",
        selectedBuildings: ['Coal Mine', 'Iron Mine', 'Steel Mills', 'Motor Industries'],
        priorityBuildings: [],
        requiredPrestigeGoods: ['Steel'],
        requiredCompanies: [],
        maxSlots: 7,
        expectedSteelProvider: true
    },
    {
        name: "Required Company Test",
        description: "Test that required companies are included in solution",
        selectedBuildings: ['Coal Mine', 'Iron Mine', 'Steel Mills'],
        priorityBuildings: [],
        requiredPrestigeGoods: [],
        requiredCompanies: ['Carnegie Steel Co.'],
        maxSlots: 7,
        expectedRequiredCompany: 'Carnegie Steel Co.'
    },
    {
        name: "Canal Companies Test",
        description: "Both canal companies should be selectable without using slots",
        selectedBuildings: ['Port', 'Trade Center', 'Railway'],
        priorityBuildings: [],
        requiredPrestigeGoods: [],
        requiredCompanies: [],
        maxSlots: 7,
        expectedCanalCompanies: 2
    },
    {
        name: "Charter Selection Test",
        description: "Test charter variants are only selected when beneficial",
        selectedBuildings: ['Coal Mine', 'Iron Mine', 'Steel Mills', 'Shipyards'],
        priorityBuildings: [],
        requiredPrestigeGoods: [],
        requiredCompanies: [],
        maxSlots: 7,
        expectCharters: true
    },
    {
        name: "Slot Maximization Test",
        description: "Should use all available slots when beneficial",
        selectedBuildings: ['Coal Mine', 'Iron Mine', 'Steel Mills', 'Paper Mill', 'Motor Industries', 'Tooling Workshops', 'Railway'],
        priorityBuildings: [],
        requiredPrestigeGoods: [],
        requiredCompanies: [],
        maxSlots: 7,
        expectedSlotUsage: 7
    }
];

async function runTestScenario(scenario) {
    console.log(`\n=== ${scenario.name.toUpperCase()} ===`);
    console.log(`Description: ${scenario.description}`);
    console.log(`Selected buildings: ${scenario.selectedBuildings.length}`);
    console.log(`Required prestige goods: ${scenario.requiredPrestigeGoods.join(', ') || 'none'}`);
    console.log(`Required companies: ${scenario.requiredCompanies.join(', ') || 'none'}`);
    
    try {
        // Generate company variants
        const variants = expandCompaniesWithCharters(allCompanies, scenario.selectedBuildings);
        console.log(`Generated ${variants.length} company variants`);
        
        // Run LP solver
        const selectedVariants = await solveIntegerLP(
            variants,
            scenario.maxSlots,
            scenario.selectedBuildings,
            scenario.priorityBuildings,
            scenario.requiredPrestigeGoods,
            scenario.requiredCompanies
        );
        
        console.log(`✅ LP solver found solution with ${selectedVariants.length} companies`);
        
        // Validate test-specific expectations
        let testPassed = true;
        const results = [];
        
        // Check minimum companies
        if (scenario.expectedMinCompanies && selectedVariants.length < scenario.expectedMinCompanies) {
            results.push(`❌ Expected at least ${scenario.expectedMinCompanies} companies, got ${selectedVariants.length}`);
            testPassed = false;
        } else if (scenario.expectedMinCompanies) {
            results.push(`✅ Company count: ${selectedVariants.length} >= ${scenario.expectedMinCompanies}`);
        }
        
        // Check steel provider
        if (scenario.expectedSteelProvider) {
            const steelProviders = selectedVariants.filter(c => 
                c.prestigeGoods?.some(pg => pg === 'Refined Steel' || pg === 'Sheffield Steel')
            );
            if (steelProviders.length === 0) {
                results.push(`❌ Expected Steel provider, found none`);
                testPassed = false;
            } else {
                results.push(`✅ Steel provider found: ${steelProviders.map(c => c.baseCompanyName).join(', ')}`);
            }
        }
        
        // Check required company
        if (scenario.expectedRequiredCompany) {
            const hasRequired = selectedVariants.some(c => c.baseCompanyName === scenario.expectedRequiredCompany);
            if (!hasRequired) {
                results.push(`❌ Required company ${scenario.expectedRequiredCompany} not found`);
                testPassed = false;
            } else {
                results.push(`✅ Required company ${scenario.expectedRequiredCompany} included`);
            }
        }
        
        // Check canal companies
        if (scenario.expectedCanalCompanies) {
            const canalCompanies = selectedVariants.filter(c => c.special === 'canal');
            if (canalCompanies.length < scenario.expectedCanalCompanies) {
                results.push(`❌ Expected ${scenario.expectedCanalCompanies} canal companies, got ${canalCompanies.length}`);
                testPassed = false;
            } else {
                results.push(`✅ Canal companies: ${canalCompanies.length} (${canalCompanies.map(c => c.baseCompanyName).join(', ')})`);
            }
        }
        
        // Check charter usage
        if (scenario.expectCharters) {
            const charterVariants = selectedVariants.filter(c => c.selectedCharter);
            if (charterVariants.length === 0) {
                results.push(`❌ Expected charter variants, found none`);
                testPassed = false;
            } else {
                results.push(`✅ Charter variants: ${charterVariants.length} (${charterVariants.map(c => c.selectedCharter).join(', ')})`);
            }
        }
        
        // Check slot usage
        if (scenario.expectedSlotUsage) {
            const regularCompanies = selectedVariants.filter(c => c.special !== 'canal');
            if (regularCompanies.length !== scenario.expectedSlotUsage) {
                results.push(`❌ Expected ${scenario.expectedSlotUsage} slots used, got ${regularCompanies.length}`);
                testPassed = false;
            } else {
                results.push(`✅ Slot usage: ${regularCompanies.length}/${scenario.maxSlots}`);
            }
        }
        
        // Print results
        results.forEach(result => console.log(`  ${result}`));
        
        if (testPassed) {
            console.log(`✅ ${scenario.name} PASSED`);
            return true;
        } else {
            console.log(`❌ ${scenario.name} FAILED`);
            return false;
        }
        
    } catch (error) {
        console.log(`❌ ${scenario.name} FAILED: ${error.message}`);
        return false;
    }
}

// Run all test scenarios
async function runAllTests() {
    console.log(`\nRunning ${testScenarios.length} test scenarios...\n`);
    
    const results = [];
    for (const scenario of testScenarios) {
        const passed = await runTestScenario(scenario);
        results.push({ name: scenario.name, passed });
    }
    
    // Summary
    console.log('\n=== TEST SUMMARY ===');
    const passedCount = results.filter(r => r.passed).length;
    results.forEach(result => {
        console.log(`${result.passed ? '✅' : '❌'} ${result.name}`);
    });
    
    console.log(`\nOverall: ${passedCount}/${results.length} tests passed`);
    
    if (passedCount === results.length) {
        console.log('🎉 ALL TESTS PASSED! LP solver is working correctly.');
        process.exit(0);
    } else {
        console.log('❌ Some tests failed. LP solver needs investigation.');
        process.exit(1);
    }
}

// Run the test suite
runAllTests().catch(error => {
    console.error('❌ TEST SUITE FAILED:', error.message);
    process.exit(1);
});