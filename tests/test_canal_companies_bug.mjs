// Test: Canal Companies Bug - Should select both canal companies when all companies/buildings selected
// This test should FAIL initially to demonstrate the bug, then PASS after we fix it
import { readFileSync } from 'fs';
import { dirname, join } from 'path';
import { fileURLToPath } from 'url';
import { solveIntegerLP } from '../lp-solver.mjs';
import { expandCompaniesWithCharters } from '../company-data.mjs';

const __dirname = dirname(fileURLToPath(import.meta.url));
const projectRoot = join(__dirname, '..');

// Load company data
const data = JSON.parse(readFileSync(join(projectRoot, 'companies_extracted.json'), 'utf8'));

console.log('=== CANAL COMPANIES BUG TEST ===');

// Set up test configuration: ALL companies and ALL buildings selected
let companies = {
    basic: data.basicCompanies || [],
    flavored: data.flavoredCompanies || [],
    canal: []
};

// Find canal companies and separate them
const allRaw = [...companies.basic, ...companies.flavored];
companies.canal = allRaw.filter(c => c.special === 'canal');
companies.flavored = companies.flavored.filter(c => c.special !== 'canal');

// ALL companies for this test (no filtering)
let allCompanies = [...companies.basic, ...companies.flavored, ...companies.canal];

console.log(`Total companies: ${allCompanies.length}`);
console.log(`Canal companies: ${companies.canal.length}`);

// Find the specific canal companies
const panamaCanal = companies.canal.find(c => c.name === 'Panama Canal Company');
const suezCanal = companies.canal.find(c => c.name === 'Suez Canal Company');

if (!panamaCanal || !suezCanal) {
    console.error('❌ Canal companies not found in data!');
    console.log('Available canal companies:', companies.canal.map(c => c.name));
    process.exit(1);
}

console.log(`Found canal companies:`);
console.log(`  Panama Canal Company: ${panamaCanal.name}`);
console.log(`  Suez Canal Company: ${suezCanal.name}`);

// Get ALL unique building types from all companies
const allBuildings = new Set();
allCompanies.forEach(company => {
    company.buildings.forEach(building => allBuildings.add(building));
    if (company.industryCharters) {
        company.industryCharters.forEach(charter => allBuildings.add(charter));
    }
});

// Test configuration: ALL buildings selected, no specific prestige goods required
let selectedBuildings = Array.from(allBuildings);
let priorityBuildings = [];
let requiredPrestigeGoods = []; // No prestige goods requirements for this test
let requiredCompanies = [];

console.log(`Configuration:`);
console.log(`  Total companies: ${allCompanies.length}`);
console.log(`  Selected buildings: ${selectedBuildings.length} (ALL buildings)`);
console.log(`  Required prestige goods: ${requiredPrestigeGoods.length} (none)`);
console.log(`  Canal companies available: ${companies.canal.length}`);

// Run the test
async function testCanalCompaniesBug() {
    console.log('\\n=== RUNNING CANAL COMPANIES TEST ===');
    
    // Generate company variants with all buildings selected
    const variants = expandCompaniesWithCharters(allCompanies, selectedBuildings);
    console.log(`Generated ${variants.length} company variants`);
    
    // Filter to just canal company variants for debugging
    const canalVariants = variants.filter(v => companies.canal.some(c => c.name === v.baseCompanyName));
    console.log(`Canal company variants: ${canalVariants.length}`);
    canalVariants.forEach(variant => {
        console.log(`  ${variant.name} (special: ${variant.special})`);
    });
    
    // Test with 7 regular slots (canal companies don't use slots)
    const maxSlots = 7;
    
    try {
        const selectedVariants = await solveIntegerLP(
            variants, 
            maxSlots, 
            selectedBuildings, 
            priorityBuildings, 
            requiredPrestigeGoods, 
            requiredCompanies
        );
        
        console.log(`\\n✅ LP SOLVER SUCCESS: Found solution with ${selectedVariants.length} companies`);
        
        // Check which canal companies were selected
        const selectedCanals = selectedVariants.filter(company => company.special === 'canal');
        const selectedCanalNames = selectedCanals.map(c => c.baseCompanyName || c.name);
        
        console.log(`\\nCanal companies in solution: ${selectedCanals.length}`);
        selectedCanals.forEach(canal => {
            console.log(`  ${canal.name} (base: ${canal.baseCompanyName})`);
        });
        
        // Check for both specific canal companies
        const hasPanama = selectedCanalNames.includes('Panama Canal Company');
        const hasSuez = selectedCanalNames.includes('Suez Canal Company');
        
        console.log(`\\nCanal company analysis:`);
        console.log(`  Panama Canal Company selected: ${hasPanama ? '✅ YES' : '❌ NO'}`);
        console.log(`  Suez Canal Company selected: ${hasSuez ? '✅ YES' : '❌ NO'}`);
        
        // Show regular companies count (should be 7, using all slots)
        const regularCompanies = selectedVariants.filter(company => company.special !== 'canal');
        console.log(`  Regular companies: ${regularCompanies.length}/${maxSlots} slots used`);
        
        // TEST EXPECTATION: Both canal companies should be selected
        if (hasPanama && hasSuez) {
            console.log(`\\n✅ TEST PASSED: Both canal companies selected as expected!`);
            console.log(`Total companies: ${selectedVariants.length} (${regularCompanies.length} regular + ${selectedCanals.length} canal)`);
        } else {
            console.log(`\\n❌ TEST FAILED: Expected both canal companies to be selected`);
            console.log(`Expected: Panama Canal Company AND Suez Canal Company`);
            console.log(`Actual: Panama=${hasPanama}, Suez=${hasSuez}`);
            console.log(`\\nThis demonstrates the canal companies bug!`);
            
            // Show why this is wrong
            console.log(`\\n🐛 BUG ANALYSIS:`);
            console.log(`  - Canal companies don't use company slots (special: 'canal')`);
            console.log(`  - Both should be selectable simultaneously`);
            console.log(`  - Expected total: ${maxSlots} regular + 2 canal = ${maxSlots + 2} companies`);
            console.log(`  - Actual total: ${selectedVariants.length} companies`);
            
            process.exit(1);
        }
        
    } catch (error) {
        console.log(`❌ LP SOLVER ERROR: ${error.message}`);
        console.log(`\\n❌ TEST FAILED: Unexpected error in LP solver`);
        process.exit(1);
    }
}

// Run the test
testCanalCompaniesBug().catch(error => {
    console.error('❌ TEST FAILED:', error.message);
    process.exit(1);
});