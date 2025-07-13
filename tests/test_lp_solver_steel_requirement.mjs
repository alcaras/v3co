// Test: LP solver with Steel requirement (mirrors index.html exactly)
import { readFileSync } from 'fs';
import { dirname, join } from 'path';
import { fileURLToPath } from 'url';
import { solveIntegerLP, calculateIndividualScore } from '../lp-solver.mjs';

const __dirname = dirname(fileURLToPath(import.meta.url));
const projectRoot = join(__dirname, '..');

// Load company data
const data = JSON.parse(readFileSync(join(projectRoot, 'companies_extracted.json'), 'utf8'));

console.log('=== LP SOLVER STEEL REQUIREMENT TEST ===');

// Set up test configuration (mirrors index.html)
let companies = {
    basic: data.basicCompanies || [],
    flavored: data.flavoredCompanies || [],
    canal: []
};

// Find canal companies and separate them
const allRaw = [...companies.basic, ...companies.flavored];
companies.canal = allRaw.filter(c => c.special === 'canal');
companies.flavored = companies.flavored.filter(c => c.special !== 'canal');

let allCompanies = [...companies.basic, ...companies.flavored];

// Get all unique building types from all companies
const allBuildings = new Set();
allCompanies.forEach(company => {
    company.buildings.forEach(building => allBuildings.add(building));
    if (company.industryCharters) {
        company.industryCharters.forEach(charter => allBuildings.add(charter));
    }
});

// Test configuration: all buildings selected, Steel required, Bolckow disabled
let selectedBuildings = Array.from(allBuildings);
let priorityBuildings = [];
let requiredPrestigeGoods = ['Steel'];
let requiredCompanies = [];

// Remove Bolckow, Vaughan & Co. to test the OR constraint logic
const bolckowCompany = allCompanies.find(c => c.name === 'Bolckow, Vaughan & Co.');
if (bolckowCompany) {
    allCompanies = allCompanies.filter(c => c.name !== 'Bolckow, Vaughan & Co.');
    console.log(`Disabled Bolckow, Vaughan & Co. (provides Sheffield Steel)`);
}

console.log(`Configuration:`);
console.log(`  Total companies: ${allCompanies.length}`);
console.log(`  Selected buildings: ${selectedBuildings.length}`);
console.log(`  Required prestige goods: ${requiredPrestigeGoods.join(', ')}`);

// Generate company variants (mirrors index.html logic)
function expandCompaniesWithCharters(companies) {
    const expandedCompanies = [];
    
    companies.forEach(company => {
        // Always add the base company (no charter)
        const baseCompany = {
            ...company,
            buildings: [...company.buildings],
            variantType: 'base',
            selectedCharter: null,
            baseCompanyName: company.name
        };
        expandedCompanies.push(baseCompany);
        
        // Add variant for each charter
        if (company.industryCharters && company.industryCharters.length > 0) {
            company.industryCharters.forEach(charter => {
                // Only add charter variants for selected buildings
                if (selectedBuildings.includes(charter)) {
                    const charterVariant = {
                        ...company,
                        name: `${company.name} + ${charter}`,
                        buildings: [...company.buildings, charter],
                        variantType: 'charter',
                        selectedCharter: charter,
                        baseCompanyName: company.name
                    };
                    expandedCompanies.push(charterVariant);
                }
            });
        }
    });
    
    return expandedCompanies;
}

// Run the LP solver test
async function testLPSolver() {
    console.log('\\n=== RUNNING LP SOLVER TEST ===');
    
    // Generate company variants
    const variants = expandCompaniesWithCharters(allCompanies);
    console.log(`Generated ${variants.length} company variants`);
    
    // Test with 7 slots
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
        
        console.log(`✅ LP SOLVER SUCCESS: Found optimal solution with ${selectedVariants.length} companies`);
        console.log(`Selected companies:`);
        
        selectedVariants.forEach((company, i) => {
            const steelGoods = company.prestigeGoods?.filter(pg => {
                // Check if this prestige good maps to Steel
                const prestigeGoodsMapping = {
                    'Refined Steel': 'Steel',
                    'Sheffield Steel': 'Steel'
                };
                return prestigeGoodsMapping[pg] === 'Steel';
            }) || [];
            
            console.log(`  ${i + 1}. ${company.name}${steelGoods.length > 0 ? ` (provides: ${steelGoods.join(', ')})` : ''}`);
        });
        
        // Verify Steel requirement is satisfied
        const providedBaseTypes = new Set();
        selectedVariants.forEach(company => {
            if (company.prestigeGoods) {
                company.prestigeGoods.forEach(pg => {
                    const prestigeGoodsMapping = {
                        'Refined Steel': 'Steel',
                        'Sheffield Steel': 'Steel'
                    };
                    const baseType = prestigeGoodsMapping[pg];
                    if (baseType) {
                        providedBaseTypes.add(baseType);
                    }
                });
            }
        });
        
        if (providedBaseTypes.has('Steel')) {
            console.log(`✅ Steel requirement satisfied!`);
            console.log(`\\n✅ TEST PASSED: LP solver correctly handles Steel prestige goods OR constraint`);
        } else {
            console.log(`❌ Steel requirement NOT satisfied!`);
            console.log(`\\n❌ TEST FAILED: LP solver did not satisfy Steel requirement`);
            process.exit(1);
        }
        
    } catch (error) {
        if (error.message.includes('LP infeasible')) {
            console.log(`❌ LP SOLVER FAILED: LP is infeasible - this should not happen with Steel requirement`);
            console.log(`\\n❌ TEST FAILED: LP solver incorrectly reports infeasibility`);
            
            // Show diagnostic information
            console.log('\\n=== DIAGNOSTIC INFO ===');
            console.log(`Available Steel providers: ${allCompanies.filter(c => 
                c.prestigeGoods?.some(pg => pg === 'Refined Steel' || pg === 'Sheffield Steel')
            ).length}`);
            
            process.exit(1);
        } else {
            console.log(`❌ LP SOLVER ERROR: ${error.message}`);
            console.log(`\\n❌ TEST FAILED: Unexpected error`);
            process.exit(1);
        }
    }
}

// Run the test
testLPSolver().catch(error => {
    console.error('❌ TEST FAILED:', error.message);
    process.exit(1);
});