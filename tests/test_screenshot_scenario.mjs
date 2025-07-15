// Test case to exactly replicate the screenshot scenario
// This should show 0 charters selected to match the screenshot

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

console.log('=== SCREENSHOT SCENARIO BUG REPLICATION ===');
console.log('This test should show 0 charters selected to match the screenshot');

// Set up company data structure matching the main app
const companies = {
    basic: data.basicCompanies || [],
    flavored: data.flavoredCompanies || [],
    canal: data.flavoredCompanies.filter(c => c.special === 'canal') || [],
    mandate: []
};

companies.flavored = companies.flavored.filter(c => c.special !== 'canal');
companies.mandate = companies.basic.filter(c => c.name === 'United Construction Conglomerate');
companies.basic = companies.basic.filter(c => c.name !== 'United Construction Conglomerate');

const allCompanies = [...companies.basic, ...companies.flavored, ...companies.canal, ...companies.mandate];

// From the screenshot, I can see the exact building coverage:
// Priority Buildings (7/11): Coal Mine, Iron Mine, Steel Mills, Paper Mill, Tooling Workshops, Logging Camp, Motor Industries, Glassworks, Rubber Plantation, Oil Rig, Explosives Factory
// Other Selected (5/5): Automotive Industries, Port, Railway, Trade Center, Power Plant  
// Other Buildings (4): Arms Industries, Cotton Plantation, Electrics Industries, Wheat Farm

const selectedBuildings = [
    // Priority buildings that are selected (showing blue stars)
    "Coal Mine", "Iron Mine", "Steel Mills", "Paper Mill", "Tooling Workshops", "Logging Camp", 
    "Motor Industries", "Glassworks", "Rubber Plantation", "Oil Rig", "Explosives Factory",
    // Other selected buildings (5/5)
    "Automotive Industries", "Port", "Railway", "Trade Center", "Power Plant"
];

const priorityBuildings = [
    "Coal Mine", "Iron Mine", "Steel Mills", "Paper Mill", "Tooling Workshops", "Logging Camp",
    "Motor Industries", "Glassworks", "Rubber Plantation", "Oil Rig", "Explosives Factory"
];

// From the screenshot: Selected Companies (32) - these are the exact companies shown
const selectedCompanyNames = [
    "Basic Agriculture 1", "Basic Agriculture 2", "Basic Fabrics", "Basic Colonial Plantations 1", 
    "Basic Colonial Plantations 2", "Basic Silk and Dye", "Basic Wine and Fruit", "Basic Fishing", 
    "Basic Forestry", "Basic Oil", "Basic Gold Mining", "Basic Metal Mining", "Basic Mineral Mining",
    "Basic Food", "Basic Paper", "Basic Home Goods", "Basic Textiles", "Basic Steel", "Basic Metalworks",
    "Basic Shipyards", "Basic Chemicals", "Basic Motors", "Basic Munitions", "Basic Electrics", 
    "Basic Weapons", "Lee Wilson & Company", "Colt's Patent Firearms Manufacturing Company", 
    "Ford Motor Company", "General Electric", "Carnegie Steel Co.", "Standard Oil", "Panama Canal Company"
];

const requiredPrestigeGoods = ["Tools"];
const requiredCompanies = [
    "Lee Wilson & Company", "Panama Canal Company", "Colt's Patent Firearms Manufacturing Company",
    "Ford Motor Company", "General Electric", "Standard Oil", "Carnegie Steel Co."
];
const maxSlots = 7;

console.log('\n=== EXACT SCREENSHOT CONFIGURATION ===');
console.log(`Selected buildings: ${selectedBuildings.length}`);
console.log(`Priority buildings: ${priorityBuildings.length}`);
console.log(`Selected companies: ${selectedCompanyNames.length}`);
console.log(`Required companies: ${requiredCompanies.length}`);
console.log(`Max slots: ${maxSlots}`);

// Filter companies to match the screenshot
const filteredCompanies = allCompanies.filter(company => 
    selectedCompanyNames.includes(company.name)
);

console.log(`\nFiltered companies: ${filteredCompanies.length}`);

// Generate variants with the exact selectedBuildings (this is the key difference!)
const variants = expandCompaniesWithCharters(filteredCompanies, selectedBuildings);
console.log(`Generated ${variants.length} variants`);

const charterVariants = variants.filter(v => v.variantType === 'charter');
console.log(`Charter variants: ${charterVariants.length}`);

// Show which charter variants exist
console.log('\n=== AVAILABLE CHARTER VARIANTS ===');
charterVariants.forEach(variant => {
    const isCharterInSelected = selectedBuildings.includes(variant.selectedCharter);
    console.log(`${variant.name} (charter: ${variant.selectedCharter}) - in selectedBuildings: ${isCharterInSelected}`);
});

// Run the LP solver
async function testScreenshotScenario() {
    console.log('\n=== RUNNING LP SOLVER ===');
    
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
        
        const selectedCharterVariants = selectedVariants.filter(v => v.variantType === 'charter');
        console.log(`Selected charter variants: ${selectedCharterVariants.length}`);
        
        if (selectedCharterVariants.length === 0) {
            console.log('❌ BUG REPRODUCED: 0 charter variants selected (matches screenshot)');
            
            // Let's analyze why no charters were selected
            console.log('\n=== CHARTER ANALYSIS ===');
            
            // Check if the issue is that no charter variants were even created
            if (charterVariants.length === 0) {
                console.log('No charter variants were created at all!');
            } else {
                console.log(`${charterVariants.length} charter variants were created but none selected`);
                console.log('This suggests the LP solver is not finding charter variants beneficial');
            }
            
        } else {
            console.log('✅ Charter variants were selected (does NOT match screenshot):');
            selectedCharterVariants.forEach(variant => {
                console.log(`  ${variant.name} (charter: ${variant.selectedCharter})`);
            });
            console.log('This means the test case is still not accurate');
        }
        
        // Show all selected companies
        console.log('\n=== ALL SELECTED COMPANIES ===');
        selectedVariants.forEach(variant => {
            const baseCompanyName = variant.baseCompanyName || variant.name;
            console.log(`${baseCompanyName} (type: ${variant.variantType}, charter: ${variant.selectedCharter || 'none'})`);
        });
        
        // Verify required companies
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
testScreenshotScenario();