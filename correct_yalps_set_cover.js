#!/usr/bin/env node

const { solve } = require('yalps');
const fs = require('fs');

console.log('🎯 CORRECT YALPS: Maximize unique building coverage using set cover\n');

// Load real company data
const rawData = JSON.parse(fs.readFileSync('company_data_v6.json', 'utf8'));
const companyData = {};
Object.entries(rawData).forEach(([name, data]) => {
    companyData[name] = {
        building_types: data.building_types || [],
        extension_building_types: data.extension_building_types || []
    };
});

// Use a smaller test set for verification (including companies from greedy result)
const testCompanies = [
    'company_panama_company',
    'company_suez_company', 
    'company_lee_wilson',
    'company_hanyang_arsenal',
    'company_john_cockerill',
    'company_east_india_company',
    'company_basic_agriculture_2',
    'company_norsk_hydro',
    'company_paradox',
    // Add your manual companies too
    'company_duro_y_compania',
    'company_basic_home_goods',
    'company_nokia',
    'company_bombay_burmah_trading_corporation',
    'company_kouppas',
    'company_bunge_born',
    'company_basic_fabrics',
    // Add some alternatives
    'company_russian_american_company',
    'company_john_holt',
    'company_krupp'
];

console.log(`Testing with ${testCompanies.length} companies\n`);

// Generate candidates
const specialCompanies = ['company_panama_company', 'company_suez_company'];
const candidates = [];

testCompanies.forEach(companyName => {
    const company = companyData[companyName];
    if (!company) return;
    
    const isSpecial = specialCompanies.includes(companyName);
    const cleanName = companyName.replace('company_', '');
    
    const baseBuildings = company.building_types.map(b => b.replace('building_', ''));
    const charterOptions = company.extension_building_types.map(b => b.replace('building_', ''));
    
    if (baseBuildings.length === 0) return;
    
    // Base variant
    candidates.push({
        id: cleanName + '_base',
        company: cleanName,
        variant: 'base',
        buildings: baseBuildings,
        special: isSpecial
    });
    
    // Charter variants
    charterOptions.forEach(charter => {
        const withCharter = [...baseBuildings, charter];
        candidates.push({
            id: cleanName + '_' + charter,
            company: cleanName,
            variant: charter,
            buildings: withCharter,
            special: isSpecial
        });
    });
});

// Get all unique buildings
const allBuildings = new Set();
candidates.forEach(c => c.buildings.forEach(b => allBuildings.add(b)));
const buildingList = Array.from(allBuildings).sort();

console.log(`Generated ${candidates.length} candidates covering ${buildingList.length} buildings\n`);

// ═══════════════════════════════════════════════════════════════════
// CORRECT YALPS FORMULATION: Set Cover - maximize unique buildings
// ═══════════════════════════════════════════════════════════════════

const model = {
    direction: 'maximize',
    objective: 'unique_buildings_covered',
    constraints: {
        max_regular_companies: { max: 7 }
    },
    variables: {},
    integers: []
};

// Create a binary variable for each building (1 if covered, 0 if not)
buildingList.forEach(building => {
    const buildingVar = `building_${building}`;
    model.variables[buildingVar] = {
        unique_buildings_covered: 1  // Each building contributes 1 to objective
    };
    model.integers.push(buildingVar);
});

// Create binary variables for company selection
candidates.forEach(candidate => {
    const companyVar = `select_${candidate.id}`;
    model.variables[companyVar] = {};
    
    // Regular companies count against limit
    if (!candidate.special) {
        model.variables[companyVar].max_regular_companies = 1;
    }
    
    model.integers.push(companyVar);
});

// CRUCIAL: Building coverage constraints
// If any company is selected that covers a building, that building MUST be marked as covered
buildingList.forEach(building => {
    const constraint = `coverage_${building}`;
    model.constraints[constraint] = { max: 0 };
    
    // The building variable contributes to its constraint
    model.variables[`building_${building}`][constraint] = 1;
    
    // Each company that can cover this building
    candidates.forEach(candidate => {
        if (candidate.buildings.includes(building)) {
            const companyVar = `select_${candidate.id}`;
            if (!model.variables[companyVar][constraint]) {
                model.variables[companyVar][constraint] = 0;
            }
            model.variables[companyVar][constraint] -= 1; // If company selected, building must be covered
        }
    });
});

// Mutual exclusion: only one variant per company
const companyGroups = {};
candidates.forEach(candidate => {
    if (!companyGroups[candidate.company]) companyGroups[candidate.company] = [];
    companyGroups[candidate.company].push(candidate.id);
});

Object.entries(companyGroups).forEach(([company, variants]) => {
    if (variants.length > 1) {
        const constraint = `exclusive_${company}`;
        model.constraints[constraint] = { max: 1 };
        variants.forEach(variantId => {
            model.variables[`select_${variantId}`][constraint] = 1;
        });
    }
});

console.log('CORRECT YALPS MODEL:');
console.log(`- Variables: ${Object.keys(model.variables).length} (${candidates.length} companies + ${buildingList.length} buildings)`);
console.log(`- Constraints: ${Object.keys(model.constraints).length}`);
console.log(`- Objective: Maximize sum of covered building indicators\n`);

console.log('Solving with YALPS...\n');

const result = solve(model);

console.log(`Status: ${result.status}`);

if (result.status === 'optimal') {
    // Extract selected companies
    const selectedCompanies = result.variables
        .filter(([name, value]) => value >= 0.5 && name.startsWith('select_'))
        .map(([name]) => {
            const id = name.replace('select_', '');
            return candidates.find(c => c.id === id);
        })
        .filter(c => c);
    
    // Extract covered buildings
    const coveredBuildings = result.variables
        .filter(([name, value]) => value >= 0.5 && name.startsWith('building_'))
        .map(([name]) => name.replace('building_', ''));
    
    const regularSelected = selectedCompanies.filter(c => !c.special);
    const specialSelected = selectedCompanies.filter(c => c.special);
    
    console.log(`\n🏆 CORRECT YALPS RESULTS:`);
    console.log(`Objective: ${result.result} unique buildings`);
    console.log(`Companies: ${regularSelected.length} regular + ${specialSelected.length} special`);
    console.log(`Buildings covered: ${coveredBuildings.length}/${buildingList.length}\n`);
    
    console.log('Selected companies:');
    [...regularSelected, ...specialSelected].forEach((c, i) => {
        const variant = c.variant === 'base' ? '(base)' : `+${c.variant}`;
        const special = c.special ? ' FREE' : '';
        console.log(`${i+1}. ${c.company} ${variant}${special}`);
        console.log(`   → ${c.buildings.join(', ')}`);
    });
    
    console.log(`\nBuildings covered: ${coveredBuildings.sort().join(', ')}\n`);
    
    // Verify no overlaps (should be impossible with this formulation)
    const actualBuildings = new Set();
    selectedCompanies.forEach(c => c.buildings.forEach(b => actualBuildings.add(b)));
    
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    console.log('VERIFICATION');
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');
    
    console.log(`YALPS objective: ${result.result} buildings`);
    console.log(`Actual unique buildings: ${actualBuildings.size} buildings`);
    console.log(`Greedy result (for comparison): 29 buildings`);
    
    if (result.result === actualBuildings.size) {
        console.log('✅ YALPS objective matches actual coverage - formulation is correct!');
    } else {
        console.log('❌ Objective mismatch - formulation still has issues');
    }
    
    if (actualBuildings.size >= 25) {
        console.log('🎉 EXCELLENT! YALPS found high-quality solution using set cover');
    } else {
        console.log('🔄 Decent result but could be optimized further');
    }
    
} else {
    console.log(`❌ YALPS failed: ${result.status}`);
    
    if (result.status === 'infeasible') {
        console.log('\nDEBUG: Checking for infeasible constraints...');
        // This suggests the constraint formulation is wrong
    }
}