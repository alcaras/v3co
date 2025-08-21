#!/usr/bin/env node

const { solve } = require('yalps');
const fs = require('fs');

console.log('🎯 FINAL YALPS FIX: True set cover without double-counting\n');

// The problem: Current formulation allows building indicators to be 1 
// even when multiple companies cover the same building
// Solution: Use proper set cover constraints

// Load all companies
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

Object.entries(companyData).forEach(([companyName, company]) => {
    const isSpecial = specialCompanies.includes(companyName);
    const cleanName = companyName.replace('company_', '');
    
    const baseBuildings = company.building_types.map(b => b.replace('building_', ''));
    const charterOptions = company.extension_building_types.map(b => b.replace('building_', ''));
    
    if (baseBuildings.length === 0 && charterOptions.length === 0) return;
    
    // Base variant
    if (baseBuildings.length > 0) {
        candidates.push({
            id: cleanName + '_base',
            name: cleanName,
            variant: 'base',
            buildings: baseBuildings,
            special: isSpecial
        });
    }
    
    // Charter variant (first one only)
    if (charterOptions.length > 0) {
        const charter = charterOptions[0];
        const withCharter = [...baseBuildings, charter];
        candidates.push({
            id: cleanName + '_' + charter,
            name: cleanName,
            variant: charter,
            buildings: withCharter,
            special: isSpecial
        });
    }
});

const allBuildings = new Set();
candidates.forEach(c => c.buildings.forEach(b => allBuildings.add(b)));
const buildingList = Array.from(allBuildings).sort();

console.log(`Generated ${candidates.length} candidates covering ${buildingList.length} buildings\n`);

// ═══════════════════════════════════════════════════════════════════
// CORRECT SET COVER FORMULATION
// Each building can only be covered by exactly one selected company
// ═══════════════════════════════════════════════════════════════════

const model = {
    direction: 'maximize',
    objective: 'unique_buildings',
    constraints: {
        max_regular_companies: { max: 7 }
    },
    variables: {},
    binaries: []
};

// Building coverage variables: building_company pairs
// building_X_companyY = 1 if company Y covers building X
buildingList.forEach(building => {
    candidates.forEach(candidate => {
        if (candidate.buildings.includes(building)) {
            const coverageVar = `covers_${building}_${candidate.id}`;
            model.variables[coverageVar] = {
                unique_buildings: 1  // Each building-company pair contributes 1
            };
            model.binaries.push(coverageVar);
        }
    });
});

// Company selection variables
candidates.forEach(candidate => {
    const companyVar = `select_${candidate.id}`;
    model.variables[companyVar] = {};
    
    if (!candidate.special) {
        model.variables[companyVar].max_regular_companies = 1;
    }
    
    model.binaries.push(companyVar);
});

// CRITICAL: Each building can only be covered by AT MOST ONE company
buildingList.forEach(building => {
    const constraint = `unique_cover_${building}`;
    model.constraints[constraint] = { max: 1 };
    
    candidates.forEach(candidate => {
        if (candidate.buildings.includes(building)) {
            const coverageVar = `covers_${building}_${candidate.id}`;
            model.variables[coverageVar][constraint] = 1;
        }
    });
});

// Link coverage to company selection: can only cover building if company is selected
buildingList.forEach(building => {
    candidates.forEach(candidate => {
        if (candidate.buildings.includes(building)) {
            const constraint = `link_${building}_${candidate.id}`;
            const coverageVar = `covers_${building}_${candidate.id}`;
            const companyVar = `select_${candidate.id}`;
            
            model.constraints[constraint] = { max: 0 };
            model.variables[coverageVar][constraint] = 1;
            model.variables[companyVar][constraint] = -1; // If company selected, coverage can be 1
        }
    });
});

// Mutual exclusion
const companyGroups = {};
candidates.forEach(candidate => {
    if (!companyGroups[candidate.name]) companyGroups[candidate.name] = [];
    companyGroups[candidate.name].push(candidate.id);
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

console.log('CORRECT SET COVER MODEL:');
console.log(`- Coverage variables: ${buildingList.length * candidates.length} (building-company pairs)`);
console.log(`- Company variables: ${candidates.length}`);
console.log(`- Total variables: ${Object.keys(model.variables).length}`);
console.log(`- Constraints: ${Object.keys(model.constraints).length}`);
console.log('- Key: Each building covered by AT MOST one company\n');

console.log('Solving with REAL YALPS...\n');

const startTime = Date.now();
const result = solve(model);
const solveTime = Date.now() - startTime;

console.log(`⏱️  Solved in ${solveTime}ms`);
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
    
    // Extract covered buildings (should match objective exactly)
    const coveredBuildings = result.variables
        .filter(([name, value]) => value >= 0.5 && name.startsWith('covers_'))
        .map(([name]) => {
            const parts = name.replace('covers_', '').split('_');
            return parts[0]; // Building name
        });
    
    const uniqueCoveredBuildings = [...new Set(coveredBuildings)];
    
    // Verify no overlaps
    const actualBuildings = new Set();
    selectedCompanies.forEach(c => c.buildings.forEach(b => actualBuildings.add(b)));
    
    const regularSelected = selectedCompanies.filter(c => !c.special);
    const specialSelected = selectedCompanies.filter(c => c.special);
    
    console.log(`\n🏆 CORRECT SET COVER RESULTS:`);
    console.log(`YALPS Objective: ${result.result} (should match unique buildings)`);
    console.log(`Unique buildings covered: ${uniqueCoveredBuildings.length}/${buildingList.length}`);
    console.log(`Verification count: ${actualBuildings.size} (should match objective)`);
    console.log(`Companies: ${regularSelected.length} regular + ${specialSelected.length} special\n`);
    
    console.log('Selected companies:');
    [...regularSelected, ...specialSelected].forEach((c, i) => {
        const variant = c.variant === 'base' ? '(base)' : `+${c.variant}`;
        const special = c.special ? ' ✨ FREE' : '';
        console.log(`${i+1}. ${c.name} ${variant}${special}`);
        console.log(`   → ${c.buildings.join(', ')}`);
    });
    
    // Verify no overlaps (should be impossible with correct formulation)
    const buildingCoverage = {};
    selectedCompanies.forEach(c => {
        c.buildings.forEach(b => {
            if (!buildingCoverage[b]) buildingCoverage[b] = [];
            buildingCoverage[b].push(c.name);
        });
    });
    
    const overlaps = Object.entries(buildingCoverage).filter(([b, companies]) => companies.length > 1);
    
    console.log('\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    console.log('FINAL VERIFICATION');
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');
    
    console.log(`Correct Set Cover YALPS: ${uniqueCoveredBuildings.length} buildings, ${overlaps.length} overlaps`);
    console.log(`Simple greedy: 29 buildings, 0 overlaps`);
    console.log(`Your manual: 24 buildings`);
    console.log(`Previous YALPS: 19 buildings, 8 overlaps`);
    
    if (overlaps.length > 0) {
        console.log('\n❌ STILL HAS OVERLAPS (formulation bug):');
        overlaps.forEach(([building, companies]) => {
            console.log(`  ${building}: ${companies.join(', ')}`);
        });
    } else {
        console.log('\n✅ NO OVERLAPS - Set cover constraint worked!');
    }
    
    if (result.result === uniqueCoveredBuildings.length && result.result === actualBuildings.size) {
        console.log('✅ OBJECTIVE MATCHES - No double counting!');
    } else {
        console.log('❌ Objective mismatch - still has issues');
    }
    
    const includesPanama = selectedCompanies.some(c => c.name.includes('panama'));
    const includesSuez = selectedCompanies.some(c => c.name.includes('suez'));
    console.log(`Special companies: Panama=${includesPanama ? '✅' : '❌'}, Suez=${includesSuez ? '✅' : '❌'}`);
    
    if (uniqueCoveredBuildings.length >= 29 && overlaps.length === 0) {
        console.log('\n🎉 PERFECT! Set cover YALPS matches greedy!');
    } else if (uniqueCoveredBuildings.length >= 25 && overlaps.length === 0) {
        console.log('\n✅ EXCELLENT! Set cover YALPS works correctly!');
    } else if (overlaps.length === 0) {
        console.log('\n✅ GOOD! No overlaps, but may need larger search space');
    } else {
        console.log('\n❌ Set cover formulation still needs work');
    }
    
} else {
    console.log(`❌ YALPS failed: ${result.status}`);
    if (result.status === 'infeasible') {
        console.log('Constraints are too restrictive - no feasible solution exists');
    }
}