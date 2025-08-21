#!/usr/bin/env node

const { solve } = require('yalps');
const fs = require('fs');

console.log('🎯 SIMPLE YALPS: Weighted formulation to discourage overlaps\n');

// Load real data
const rawData = JSON.parse(fs.readFileSync('company_data_v6.json', 'utf8'));
const companyData = {};
Object.entries(rawData).forEach(([name, data]) => {
    companyData[name] = {
        building_types: data.building_types || [],
        extension_building_types: data.extension_building_types || []
    };
});

// Use all companies to match the 29-building greedy result
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
            company: cleanName,
            variant: 'base',
            buildings: baseBuildings,
            special: isSpecial
        });
    }
    
    // Charter variants (first charter only for simplicity)
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

console.log(`Generated ${candidates.length} candidates\n`);

// Get all unique buildings and calculate rarity weights
const allBuildings = new Set();
candidates.forEach(c => c.buildings.forEach(b => allBuildings.add(b)));
const buildingList = Array.from(allBuildings).sort();

// Calculate building rarity (fewer companies = higher weight)
const buildingRarity = {};
buildingList.forEach(building => {
    const count = candidates.filter(c => c.buildings.includes(building)).length;
    buildingRarity[building] = 1.0 / Math.sqrt(count); // Rare buildings get higher weight
});

console.log(`Total buildings: ${buildingList.length}`);
console.log('Building rarity weights (sample):');
Object.entries(buildingRarity).sort((a, b) => b[1] - a[1]).slice(0, 10).forEach(([building, weight]) => {
    const count = candidates.filter(c => c.buildings.includes(building)).length;
    console.log(`  ${building}: weight=${weight.toFixed(3)} (${count} companies)`);
});

// ═══════════════════════════════════════════════════════════════════
// WEIGHTED YALPS: Each building contributes based on rarity
// ═══════════════════════════════════════════════════════════════════

const model = {
    direction: 'maximize',
    objective: 'weighted_coverage',
    constraints: {
        max_regular_companies: { max: 7 }
    },
    variables: {},
    integers: []
};

// Company selection variables with weighted scores
candidates.forEach(candidate => {
    const varName = 'select_' + candidate.id;
    
    // Calculate weighted score for this candidate
    const weightedScore = candidate.buildings.reduce((sum, building) => {
        return sum + buildingRarity[building];
    }, 0);
    
    model.variables[varName] = {
        weighted_coverage: weightedScore
    };
    
    // Regular companies count against limit
    if (!candidate.special) {
        model.variables[varName].max_regular_companies = 1;
    }
    
    model.integers.push(varName);
});

// Mutual exclusion constraints
const companyGroups = {};
candidates.forEach(candidate => {
    if (!companyGroups[candidate.company]) companyGroups[candidate.company] = [];
    companyGroups[candidate.company].push(candidate.id);
});

Object.entries(companyGroups).forEach(([company, variants]) => {
    if (variants.length > 1) {
        const constraint = 'exclusive_' + company;
        model.constraints[constraint] = { max: 1 };
        variants.forEach(variantId => {
            model.variables['select_' + variantId][constraint] = 1;
        });
    }
});

console.log('\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
console.log('WEIGHTED YALPS: Rare buildings get higher weights');
console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');

console.log(`Model: ${Object.keys(model.variables).length} variables, ${Object.keys(model.constraints).length} constraints`);
console.log('Solving...\n');

const result = solve(model);

console.log(`Status: ${result.status}`);

if (result.status === 'optimal') {
    const selected = result.variables
        .filter(([name, value]) => value >= 0.5 && name.startsWith('select_'))
        .map(([name]) => {
            const id = name.replace('select_', '');
            return candidates.find(c => c.id === id);
        })
        .filter(c => c);
    
    // Calculate actual unique buildings
    const actualBuildings = new Set();
    selected.forEach(c => c.buildings.forEach(b => actualBuildings.add(b)));
    
    const regularSelected = selected.filter(c => !c.special);
    const specialSelected = selected.filter(c => c.special);
    
    console.log(`\n🏆 WEIGHTED YALPS RESULTS:`);
    console.log(`Objective: ${result.result.toFixed(2)} weighted score`);
    console.log(`Companies: ${regularSelected.length} regular + ${specialSelected.length} special`);
    console.log(`Unique buildings: ${actualBuildings.size}/${buildingList.length}\n`);
    
    console.log('Selected companies:');
    [...regularSelected, ...specialSelected].forEach((c, i) => {
        const variant = c.variant === 'base' ? '(base)' : `+${c.variant}`;
        const special = c.special ? ' FREE' : '';
        const weightedScore = c.buildings.reduce((sum, b) => sum + buildingRarity[b], 0);
        console.log(`${i+1}. ${c.company} ${variant}${special} [${weightedScore.toFixed(2)} pts]`);
        console.log(`   → ${c.buildings.join(', ')}`);
    });
    
    // Check for overlaps
    const buildingCoverage = {};
    selected.forEach(c => {
        c.buildings.forEach(b => {
            if (!buildingCoverage[b]) buildingCoverage[b] = [];
            buildingCoverage[b].push(c.company);
        });
    });
    
    const overlaps = Object.entries(buildingCoverage).filter(([b, companies]) => companies.length > 1);
    
    console.log('\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    console.log('COMPARISON WITH GREEDY');
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');
    
    console.log(`Weighted YALPS: ${actualBuildings.size} buildings, ${overlaps.length} overlaps`);
    console.log(`Simple greedy: 29 buildings, 0 overlaps`);
    
    if (overlaps.length > 0) {
        console.log('\nOverlapping buildings:');
        overlaps.forEach(([building, companies]) => {
            console.log(`  ${building}: ${companies.join(', ')}`);
        });
    }
    
    if (actualBuildings.size >= 29 && overlaps.length === 0) {
        console.log('\n🎉 SUCCESS! Weighted YALPS beats greedy!');
    } else if (actualBuildings.size >= 25) {
        console.log('\n✅ GOOD: Weighted YALPS finds high-quality solution');
        if (overlaps.length > 0) {
            console.log('   But still has overlaps - weighting may need adjustment');
        }
    } else {
        console.log('\n❌ Weighted YALPS underperforms - need better formulation');
    }
    
} else {
    console.log(`❌ YALPS failed: ${result.status}`);
}