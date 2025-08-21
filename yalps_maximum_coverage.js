#!/usr/bin/env node

const { solve } = require('yalps');
const fs = require('fs');

console.log('🎯 YALPS MAXIMUM COVERAGE: Binary building indicators\n');

// Use the same companies that greedy selected for a fair comparison
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
    // Add your manual companies
    'company_duro_y_compania',
    'company_basic_home_goods', 
    'company_nokia',
    'company_kouppas',
    'company_bunge_born',
    // Add alternatives
    'company_russian_american_company',
    'company_john_holt',
    'company_krupp'
];

const rawData = JSON.parse(fs.readFileSync('company_data_v6.json', 'utf8'));
const companyData = {};
Object.entries(rawData).forEach(([name, data]) => {
    companyData[name] = {
        building_types: data.building_types || [],
        extension_building_types: data.extension_building_types || []
    };
});

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
    
    // First charter variant
    if (charterOptions.length > 0) {
        const charter = charterOptions[0];
        const withCharter = [...baseBuildings, charter];
        candidates.push({
            id: cleanName + '_' + charter,
            company: cleanName,
            variant: charter,
            buildings: withCharter,
            special: isSpecial
        });
    }
});

// Get all buildings
const allBuildings = new Set();
candidates.forEach(c => c.buildings.forEach(b => allBuildings.add(b)));
const buildingList = Array.from(allBuildings).sort();

console.log(`Testing with ${candidates.length} candidates covering ${buildingList.length} buildings\n`);

// ═══════════════════════════════════════════════════════════════════
// MAXIMUM COVERAGE FORMULATION
// Each building has a binary indicator variable
// Objective: maximize sum of building indicators
// Constraint: building indicator ≤ sum of companies covering it
// ═══════════════════════════════════════════════════════════════════

const model = {
    direction: 'maximize',
    objective: 'total_buildings_covered',
    constraints: {
        max_regular_companies: { max: 7 }
    },
    variables: {},
    integers: []
};

// Building indicator variables (1 if building is covered, 0 otherwise)
buildingList.forEach(building => {
    const buildingVar = `covered_${building}`;
    model.variables[buildingVar] = {
        total_buildings_covered: 1  // Each covered building contributes 1 to objective
    };
    model.integers.push(buildingVar);
});

// Company selection variables
candidates.forEach(candidate => {
    const companyVar = `select_${candidate.id}`;
    model.variables[companyVar] = {};
    
    if (!candidate.special) {
        model.variables[companyVar].max_regular_companies = 1;
    }
    
    model.integers.push(companyVar);
});

// Coverage constraints: building can only be covered if at least one company covering it is selected
buildingList.forEach(building => {
    const constraint = `limit_${building}`;
    model.constraints[constraint] = { max: 0 };
    
    // Building indicator contributes positively to its constraint
    model.variables[`covered_${building}`][constraint] = 1;
    
    // Each company that covers this building reduces the constraint bound
    candidates.forEach(candidate => {
        if (candidate.buildings.includes(building)) {
            const companyVar = `select_${candidate.id}`;
            if (!model.variables[companyVar][constraint]) {
                model.variables[companyVar][constraint] = 0;
            }
            model.variables[companyVar][constraint] -= 1;
        }
    });
});

// Mutual exclusion
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

console.log('MAXIMUM COVERAGE MODEL:');
console.log(`- Building indicators: ${buildingList.length} variables`);
console.log(`- Company selectors: ${candidates.length} variables`);
console.log(`- Total variables: ${Object.keys(model.variables).length}`);
console.log(`- Constraints: ${Object.keys(model.constraints).length}\n`);

console.log('Solving with YALPS...\n');

const result = solve(model);

console.log(`Status: ${result.status}`);

if (result.status === 'optimal') {
    const selectedCompanies = result.variables
        .filter(([name, value]) => value >= 0.5 && name.startsWith('select_'))
        .map(([name]) => {
            const id = name.replace('select_', '');
            return candidates.find(c => c.id === id);
        })
        .filter(c => c);
    
    const coveredBuildings = result.variables
        .filter(([name, value]) => value >= 0.5 && name.startsWith('covered_'))
        .map(([name]) => name.replace('covered_', ''));
    
    // Verify actual coverage
    const actualBuildings = new Set();
    selectedCompanies.forEach(c => c.buildings.forEach(b => actualBuildings.add(b)));
    
    const regularSelected = selectedCompanies.filter(c => !c.special);
    const specialSelected = selectedCompanies.filter(c => c.special);
    
    console.log(`\n🏆 MAXIMUM COVERAGE YALPS RESULTS:`);
    console.log(`Objective: ${result.result} buildings (YALPS)`);
    console.log(`Actually covered: ${actualBuildings.size} buildings (verification)`);
    console.log(`Companies: ${regularSelected.length} regular + ${specialSelected.length} special\n`);
    
    console.log('Selected companies:');
    [...regularSelected, ...specialSelected].forEach((c, i) => {
        const variant = c.variant === 'base' ? '(base)' : `+${c.variant}`;
        const special = c.special ? ' FREE' : '';
        console.log(`${i+1}. ${c.company} ${variant}${special}`);
        console.log(`   → ${c.buildings.join(', ')}`);
    });
    
    console.log(`\nBuildings YALPS says are covered: ${coveredBuildings.sort().join(', ')}`);
    console.log(`Buildings actually covered: ${Array.from(actualBuildings).sort().join(', ')}\n`);
    
    // Check for overlaps
    const buildingCoverage = {};
    selectedCompanies.forEach(c => {
        c.buildings.forEach(b => {
            if (!buildingCoverage[b]) buildingCoverage[b] = [];
            buildingCoverage[b].push(c.company);
        });
    });
    
    const overlaps = Object.entries(buildingCoverage).filter(([b, companies]) => companies.length > 1);
    
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    console.log('FINAL COMPARISON');
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');
    
    console.log(`YALPS Maximum Coverage: ${actualBuildings.size} buildings, ${overlaps.length} overlaps`);
    console.log(`Simple Greedy: 29 buildings, 0 overlaps`);
    console.log(`Your Manual Selection: 24 buildings`);
    
    if (overlaps.length > 0) {
        console.log('\nOverlaps detected:');
        overlaps.forEach(([building, companies]) => {
            console.log(`  ${building}: ${companies.join(', ')}`);
        });
    }
    
    if (result.result === actualBuildings.size) {
        console.log('\n✅ YALPS objective matches reality - formulation is mathematically correct!');
        
        if (actualBuildings.size >= 29 && overlaps.length === 0) {
            console.log('🎉 PERFECT! YALPS beats greedy with no overlaps!');
        } else if (actualBuildings.size >= 25) {
            console.log('🎯 EXCELLENT! YALPS finds high-quality solution!');
        } else {
            console.log('✅ YALPS works but may need larger candidate pool');
        }
    } else {
        console.log('\n❌ Objective mismatch - constraint formulation still has bugs');
    }
    
} else {
    console.log(`❌ YALPS failed: ${result.status}`);
}