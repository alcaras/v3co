#!/usr/bin/env node

const { solve } = require('yalps');
const fs = require('fs');

console.log('🔧 FIXING YALPS: Special companies constraint bug\n');

// Load all 185 companies
const rawData = JSON.parse(fs.readFileSync('company_data_v6.json', 'utf8'));
const companyData = {};
Object.entries(rawData).forEach(([name, data]) => {
    companyData[name] = {
        building_types: data.building_types || [],
        extension_building_types: data.extension_building_types || []
    };
});

// Generate all candidates
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
    
    // Charter variants
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

// Get all buildings
const allBuildings = new Set();
candidates.forEach(c => c.buildings.forEach(b => allBuildings.add(b)));
const buildingList = Array.from(allBuildings).sort();

console.log(`Generated ${candidates.length} candidates from ${Object.keys(companyData).length} companies`);
console.log(`Total buildings: ${buildingList.length}`);

// Check special companies are in candidates
const specialCandidates = candidates.filter(c => c.special);
console.log(`Special company candidates: ${specialCandidates.length}`);
specialCandidates.forEach(c => {
    console.log(`  ${c.name} ${c.variant}: ${c.buildings.join(', ')}`);
});

console.log('\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
console.log('FIXED YALPS: Proper special company constraints');
console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');

// FIXED MODEL: Special companies don't count against limit
const model = {
    direction: 'maximize',
    objective: 'buildings_covered',
    constraints: {
        max_regular_companies: { max: 7 }  // Only regular companies count
    },
    variables: {},
    integers: []
};

// Building indicator variables
buildingList.forEach(building => {
    const buildingVar = `covered_${building}`;
    model.variables[buildingVar] = {
        buildings_covered: 1
    };
    model.integers.push(buildingVar);
});

// Company selection variables
candidates.forEach(candidate => {
    const companyVar = `select_${candidate.id}`;
    model.variables[companyVar] = {};
    
    // CRITICAL FIX: Only regular companies count against the limit
    if (!candidate.special) {
        model.variables[companyVar].max_regular_companies = 1;
    }
    // Special companies have NO constraint contribution!
    
    model.integers.push(companyVar);
});

// Coverage constraints
buildingList.forEach(building => {
    const constraint = `limit_${building}`;
    model.constraints[constraint] = { max: 0 };
    
    model.variables[`covered_${building}`][constraint] = 1;
    
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

console.log('FIXED MODEL:');
console.log(`- Variables: ${Object.keys(model.variables).length}`);
console.log(`- Constraints: ${Object.keys(model.constraints).length}`);
console.log('- Special companies: Do NOT count against 7-company limit');
console.log('- Regular companies: Count against limit\n');

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
    
    // Calculate actual unique buildings
    const actualBuildings = new Set();
    selectedCompanies.forEach(c => c.buildings.forEach(b => actualBuildings.add(b)));
    
    const regularSelected = selectedCompanies.filter(c => !c.special);
    const specialSelected = selectedCompanies.filter(c => c.special);
    
    console.log(`\n🏆 FIXED YALPS RESULTS:`);
    console.log(`YALPS Objective: ${result.result}`);
    console.log(`ACTUAL unique buildings: ${actualBuildings.size}/${buildingList.length}`);
    console.log(`Companies: ${regularSelected.length} regular + ${specialSelected.length} special\n`);
    
    console.log('Selected companies:');
    [...regularSelected, ...specialSelected].forEach((c, i) => {
        const variant = c.variant === 'base' ? '(base)' : `+${c.variant}`;
        const special = c.special ? ' ✨ FREE' : '';
        console.log(`${i+1}. ${c.name} ${variant}${special}`);
        console.log(`   → ${c.buildings.join(', ')}`);
    });
    
    // Check for overlaps
    const buildingCoverage = {};
    selectedCompanies.forEach(c => {
        c.buildings.forEach(b => {
            if (!buildingCoverage[b]) buildingCoverage[b] = [];
            buildingCoverage[b].push(c.name);
        });
    });
    
    const overlaps = Object.entries(buildingCoverage).filter(([b, companies]) => companies.length > 1);
    
    console.log('\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    console.log('FINAL COMPARISON');
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');
    
    console.log(`FIXED YALPS: ${actualBuildings.size} buildings, ${overlaps.length} overlaps`);
    console.log(`Simple greedy: 29 buildings, 0 overlaps`);
    console.log(`Your manual: 24 buildings`);
    console.log(`Broken YALPS (before fix): 18 buildings, 7 overlaps`);
    
    if (overlaps.length > 0 && overlaps.length <= 5) {
        console.log('\nOverlapping buildings:');
        overlaps.forEach(([building, companies]) => {
            console.log(`  ${building}: ${companies.join(', ')}`);
        });
    }
    
    // Check special companies
    const includesPanama = selectedCompanies.some(c => c.name.includes('panama'));
    const includesSuez = selectedCompanies.some(c => c.name.includes('suez'));
    
    console.log(`\nSpecial companies: Panama=${includesPanama ? '✅' : '❌'}, Suez=${includesSuez ? '✅' : '❌'}`);
    
    if (actualBuildings.size >= 29 && overlaps.length === 0) {
        console.log('\n🎉 PERFECT! Fixed YALPS matches greedy!');
    } else if (actualBuildings.size >= 29) {
        console.log('\n🎯 EXCELLENT! Fixed YALPS finds 29+ buildings!');
    } else if (actualBuildings.size >= 25 && includesPanama && includesSuez) {
        console.log('\n✅ GOOD! Fixed YALPS includes special companies and finds high coverage!');
    } else {
        console.log('\n❌ Still issues with YALPS formulation');
    }
    
    if (includesPanama && includesSuez) {
        console.log('\n✅ CONSTRAINT FIX WORKED: Special companies are now selected!');
    } else {
        console.log('\n❌ Special companies still missing - constraint still broken');
    }
    
} else {
    console.log(`❌ YALPS failed: ${result.status}`);
}