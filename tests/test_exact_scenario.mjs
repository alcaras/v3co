// Test case to exactly replicate the scenario from victoria3_selections_2025-07-15.json
// This test matches the exact UI state shown in the screenshot

import { readFileSync } from 'fs';
import { dirname, join } from 'path';
import { fileURLToPath } from 'url';
import { solveIntegerLP } from '../lp-solver.mjs';
import { expandCompaniesWithCharters } from '../company-data.mjs';

const __dirname = dirname(fileURLToPath(import.meta.url));
const projectRoot = join(__dirname, '..');

// Load the exact exported scenario
const scenarioData = JSON.parse(readFileSync(join(projectRoot, 'victoria3_selections_2025-07-15.json'), 'utf8'));

// Load company data
const data = JSON.parse(readFileSync(join(projectRoot, 'companies_extracted.json'), 'utf8'));

console.log('=== EXACT SCENARIO REPLICATION TEST ===');
console.log('Replicating the exact scenario from victoria3_selections_2025-07-15.json');

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

// Extract exact settings from the JSON
const selectedBuildings = scenarioData.selectedBuildings;
const priorityBuildings = scenarioData.priorityBuildings;
const requiredPrestigeGoods = scenarioData.requiredPrestigeGoods;
const requiredCompanies = scenarioData.requiredCompanies;
const maxSlots = scenarioData.settings.companySlots;

console.log('\n=== EXACT SCENARIO SETTINGS ===');
console.log(`Company slots: ${maxSlots}`);
console.log(`Selected buildings: ${selectedBuildings.length}`);
console.log(`Priority buildings: ${priorityBuildings.length}`);
console.log(`Required prestige goods: ${requiredPrestigeGoods.join(', ')}`);
console.log(`Required companies: ${requiredCompanies.length}`);

// Create a filtered list of companies that match the selectedCompanies from JSON
const selectedCompanyNames = scenarioData.selectedCompanies.map(c => c.name);
console.log(`\nSelected companies from JSON: ${selectedCompanyNames.length}`);
selectedCompanyNames.forEach(name => console.log(`  - ${name}`));

// Filter to only the companies that were selected in the UI
const filteredCompanies = allCompanies.filter(company => 
    selectedCompanyNames.includes(company.name)
);

console.log(`\nFiltered companies: ${filteredCompanies.length}`);
console.log('Companies with charters:');
filteredCompanies.forEach(company => {
    if (company.industryCharters && company.industryCharters.length > 0) {
        console.log(`  ${company.name}: ${company.industryCharters.join(', ')}`);
    }
});

// Generate company variants
const variants = expandCompaniesWithCharters(filteredCompanies, selectedBuildings);
console.log(`\nGenerated ${variants.length} variants from ${filteredCompanies.length} companies`);

// Count charter variants
const charterVariants = variants.filter(v => v.variantType === 'charter');
console.log(`Charter variants: ${charterVariants.length}`);

// Show charter variants
console.log('\n=== CHARTER VARIANTS ===');
charterVariants.forEach(variant => {
    console.log(`${variant.name} (charter: ${variant.selectedCharter})`);
});

// Run the LP solver test
async function testExactScenario() {
    console.log('\n=== RUNNING LP SOLVER WITH EXACT SCENARIO ===');
    
    try {
        const selectedVariants = await solveIntegerLP(
            variants,
            maxSlots,
            selectedBuildings,
            priorityBuildings,
            requiredPrestigeGoods,
            requiredCompanies
        );
        
        console.log(`\nSelected variants: ${selectedVariants.length}`);
        
        // Check if any charter variants were selected
        const selectedCharterVariants = selectedVariants.filter(v => v.variantType === 'charter');
        console.log(`Selected charter variants: ${selectedCharterVariants.length}`);
        
        if (selectedCharterVariants.length === 0) {
            console.log('❌ BUG CONFIRMED: No charter variants selected in exact scenario');
            console.log('This matches the screenshot showing 0 charters');
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
        
        // Check which required companies were selected
        console.log('\n=== REQUIRED COMPANIES CHECK ===');
        const selectedBaseNames = selectedVariants.map(v => v.baseCompanyName || v.name);
        requiredCompanies.forEach(reqCompany => {
            const isSelected = selectedBaseNames.includes(reqCompany);
            console.log(`${reqCompany}: ${isSelected ? '✅' : '❌'}`);
        });
        
    } catch (error) {
        console.error('Error running LP solver:', error);
    }
}

// Run the test
testExactScenario();