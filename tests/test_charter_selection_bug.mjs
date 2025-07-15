// Test case to reproduce the charter selection bug
// This test replicates the exact scenario from victoria3_selections_2025-07-15.json
// where no charters are picked despite companies having charter options

import { readFileSync } from 'fs';
import { dirname, join } from 'path';
import { fileURLToPath } from 'url';
import { solveIntegerLP } from '../lp-solver.mjs';
import { expandCompaniesWithCharters } from '../company-data.mjs';

const __dirname = dirname(fileURLToPath(import.meta.url));
const projectRoot = join(__dirname, '..');

// Load company data
const data = JSON.parse(readFileSync(join(projectRoot, 'companies_extracted.json'), 'utf8'));

console.log('=== CHARTER SELECTION BUG TEST ===');

// Set up company data structure matching the main app
const companies = {
    basic: data.basicCompanies || [],
    flavored: data.flavoredCompanies || [],
    canal: data.flavoredCompanies.filter(c => c.special === 'canal') || [],
    mandate: []
};

// Remove canal companies from flavored list
companies.flavored = companies.flavored.filter(c => c.special !== 'canal');

// Find United Construction Conglomerate
companies.mandate = companies.basic.filter(c => c.name === 'United Construction Conglomerate');
companies.basic = companies.basic.filter(c => c.name !== 'United Construction Conglomerate');

// All companies for optimization
const allCompanies = [...companies.basic, ...companies.flavored, ...companies.canal, ...companies.mandate];

// Test configuration matching the JSON file
const selectedBuildings = [
    "Coal Mine", "Iron Mine", "Logging Camp", "Oil Rig", "Rubber Plantation",
    "Automotive Industries", "Explosives Factory", "Glassworks", "Motor Industries", "Paper Mill", "Steel Mills", "Tooling Workshops",
    "Port", "Railway", "Trade Center", "Power Plant"
];

const priorityBuildings = [
    "Coal Mine", "Iron Mine", "Steel Mills", "Paper Mill", "Tooling Workshops", "Logging Camp",
    "Motor Industries", "Glassworks", "Rubber Plantation", "Oil Rig", "Explosives Factory"
];

const requiredPrestigeGoods = ["Tools"];

const maxSlots = 7;

// Test charter expansion first
console.log('\n=== TESTING CHARTER EXPANSION ===');

// Find companies with charters
const companiesWithCharters = allCompanies.filter(c => c.industryCharters && c.industryCharters.length > 0);
console.log(`Companies with charters: ${companiesWithCharters.length}`);

// Test charter expansion
const variants = expandCompaniesWithCharters(allCompanies, selectedBuildings);
console.log(`Total variants generated: ${variants.length}`);

// Count charter variants
const charterVariants = variants.filter(v => v.variantType === 'charter');
console.log(`Charter variants generated: ${charterVariants.length}`);

// Show some examples of charter variants
console.log('\n=== CHARTER VARIANTS EXAMPLES ===');
charterVariants.slice(0, 5).forEach(variant => {
    console.log(`${variant.name} (charter: ${variant.selectedCharter})`);
});

// Show which charters are being filtered out
console.log('\n=== CHARTER FILTERING ANALYSIS ===');
companiesWithCharters.forEach(company => {
    console.log(`Company: ${company.name}`);
    console.log(`  Available charters: ${company.industryCharters.join(', ')}`);
    const filteredCharters = company.industryCharters.filter(charter => selectedBuildings.includes(charter));
    console.log(`  Charters in selectedBuildings: ${filteredCharters.join(', ') || 'NONE'}`);
    const excludedCharters = company.industryCharters.filter(charter => !selectedBuildings.includes(charter));
    console.log(`  Excluded charters: ${excludedCharters.join(', ') || 'NONE'}`);
});

// Run the LP solver test
async function testCharterSelectionBug() {
    console.log('\n=== RUNNING LP SOLVER TEST ===');
    
    try {
        const selectedVariants = await solveIntegerLP(
            variants,
            maxSlots,
            selectedBuildings,
            priorityBuildings,
            requiredPrestigeGoods,
            []
        );
        
        console.log(`\nSelected variants: ${selectedVariants.length}`);
        
        // Check if any charter variants were selected
        const selectedCharterVariants = selectedVariants.filter(v => v.variantType === 'charter');
        console.log(`Selected charter variants: ${selectedCharterVariants.length}`);
        
        if (selectedCharterVariants.length === 0) {
            console.log('❌ BUG REPRODUCED: No charter variants selected');
            console.log('This confirms the charter selection bug');
        } else {
            console.log('✅ Charter variants were selected:');
            selectedCharterVariants.forEach(variant => {
                console.log(`  ${variant.name} (charter: ${variant.selectedCharter})`);
            });
        }
        
        // Show all selected variants
        console.log('\n=== ALL SELECTED VARIANTS ===');
        selectedVariants.forEach(variant => {
            console.log(`${variant.name} (type: ${variant.variantType}, charter: ${variant.selectedCharter || 'none'})`);
        });
        
    } catch (error) {
        console.error('Error running LP solver:', error);
    }
}

// Run the test
testCharterSelectionBug();