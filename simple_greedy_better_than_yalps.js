#!/usr/bin/env node

const fs = require('fs');

console.log('🎯 SIMPLE GREEDY vs BROKEN YALPS: Can greedy beat YALPS?\n');

// Since YALPS is maximizing total points instead of unique buildings,
// let's implement a simple greedy algorithm that maximizes unique buildings
// and see if it can beat the "sophisticated" YALPS

const rawData = JSON.parse(fs.readFileSync('company_data_v6.json', 'utf8'));
const companyData = {};
Object.entries(rawData).forEach(([name, data]) => {
    companyData[name] = {
        building_types: data.building_types || [],
        extension_building_types: data.extension_building_types || []
    };
});

// Generate candidates with building coverage
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
            buildings: new Set(baseBuildings),
            special: isSpecial,
            originalScore: baseBuildings.length
        });
    }
    
    // Charter variants  
    charterOptions.forEach(charter => {
        const withCharter = [...baseBuildings, charter];
        candidates.push({
            id: cleanName + '_' + charter,
            company: cleanName,
            variant: charter,
            buildings: new Set(withCharter),
            special: isSpecial,
            originalScore: withCharter.length
        });
    });
});

console.log(`Generated ${candidates.length} candidates from ${Object.keys(companyData).length} companies\n`);

// ═══════════════════════════════════════════════════════════════════
// SIMPLE GREEDY: Select companies that add the most NEW buildings
// ═══════════════════════════════════════════════════════════════════

function simpleGreedySelection(candidates, maxRegular = 7) {
    const selected = [];
    const coveredBuildings = new Set();
    const companyGroups = {};
    
    // Group candidates by company for mutual exclusion
    candidates.forEach(candidate => {
        if (!companyGroups[candidate.company]) companyGroups[candidate.company] = [];
        companyGroups[candidate.company].push(candidate);
    });
    
    const availableGroups = Object.keys(companyGroups);
    let regularCount = 0;
    
    // Always add special companies first if available
    ['panama_company', 'suez_company'].forEach(specialName => {
        if (companyGroups[specialName]) {
            // Pick best variant for special company
            let bestSpecial = null;
            let bestNewBuildings = 0;
            
            companyGroups[specialName].forEach(candidate => {
                const newBuildings = Array.from(candidate.buildings).filter(b => !coveredBuildings.has(b));
                if (newBuildings.length > bestNewBuildings) {
                    bestNewBuildings = newBuildings.length;
                    bestSpecial = candidate;
                }
            });
            
            if (bestSpecial) {
                selected.push(bestSpecial);
                bestSpecial.buildings.forEach(b => coveredBuildings.add(b));
                delete companyGroups[specialName];
            }
        }
    });
    
    // Greedily select regular companies
    while (regularCount < maxRegular && Object.keys(companyGroups).length > 0) {
        let bestGroup = null;
        let bestCandidate = null;
        let bestNewCount = 0;
        
        Object.entries(companyGroups).forEach(([groupName, groupCandidates]) => {
            // Skip special companies
            if (['panama_company', 'suez_company'].includes(groupName)) return;
            
            // Find best candidate in this group
            groupCandidates.forEach(candidate => {
                const newBuildings = Array.from(candidate.buildings).filter(b => !coveredBuildings.has(b));
                if (newBuildings.length > bestNewCount) {
                    bestNewCount = newBuildings.length;
                    bestCandidate = candidate;
                    bestGroup = groupName;
                }
            });
        });
        
        if (bestCandidate) {
            selected.push(bestCandidate);
            bestCandidate.buildings.forEach(b => coveredBuildings.add(b));
            delete companyGroups[bestGroup];
            if (!bestCandidate.special) regularCount++;
        } else {
            break; // No more improvements
        }
    }
    
    return {
        selected,
        totalBuildings: coveredBuildings.size,
        coveredBuildings
    };
}

console.log('SIMPLE GREEDY: Maximizing NEW buildings at each step');
const greedyResult = simpleGreedySelection(candidates);

console.log(`Selected: ${greedyResult.selected.length} companies`);
console.log(`Unique buildings: ${greedyResult.totalBuildings}`);
console.log(`Regular companies: ${greedyResult.selected.filter(c => !c.special).length}/7\n`);

console.log('Greedy selected companies:');
greedyResult.selected.forEach((c, i) => {
    const variant = c.variant === 'base' ? '(base)' : `+${c.variant}`;
    const special = c.special ? ' FREE' : '';
    const newBuildings = Array.from(c.buildings);
    console.log(`${i+1}. ${c.company} ${variant}${special}: ${newBuildings.length} buildings`);
    console.log(`   → ${newBuildings.join(', ')}`);
});

// ═══════════════════════════════════════════════════════════════════
// Compare to your manual selection
// ═══════════════════════════════════════════════════════════════════

const yourManual = [
    'company_duro_y_compania',
    'company_basic_home_goods',
    'company_nokia', 
    'company_bombay_burmah_trading_corporation',
    'company_kouppas',
    'company_bunge_born',
    'company_basic_fabrics'
];

let manualBuildings = new Set();
yourManual.forEach(companyName => {
    const company = companyData[companyName];
    if (company) {
        company.building_types.forEach(b => manualBuildings.add(b.replace('building_', '')));
        // Add first charter for simplicity
        if (company.extension_building_types.length > 0) {
            manualBuildings.add(company.extension_building_types[0].replace('building_', ''));
        }
    }
});

// Add special companies to manual
['company_panama_company', 'company_suez_company'].forEach(companyName => {
    const company = companyData[companyName];
    if (company) {
        company.building_types.forEach(b => manualBuildings.add(b.replace('building_', '')));
        if (company.extension_building_types.length > 0) {
            manualBuildings.add(company.extension_building_types[0].replace('building_', ''));
        }
    }
});

console.log('\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
console.log('COMPARISON');  
console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');

console.log(`Your manual selection: ${manualBuildings.size} buildings`);
console.log(`Simple greedy algorithm: ${greedyResult.totalBuildings} buildings`);
console.log(`Broken YALPS (from earlier): 19 buildings\n`);

if (greedyResult.totalBuildings >= manualBuildings.size) {
    console.log('✅ SUCCESS: Simple greedy matches or beats manual selection!');
} else if (greedyResult.totalBuildings >= 19) {
    console.log('✅ GOOD: Simple greedy beats broken YALPS');
} else {
    console.log('❌ Simple greedy also suboptimal');
}

console.log('\n🔍 ANALYSIS:');
console.log('- Simple greedy maximizes NEW buildings at each step');  
console.log('- Broken YALPS maximizes total points (allows overlaps)');
console.log('- Your manual selection is carefully optimized');

if (greedyResult.totalBuildings < manualBuildings.size) {
    console.log('\n💡 This suggests your manual selection has domain-specific optimizations');
    console.log('   that simple algorithms cannot discover automatically.');
} else {
    console.log('\n🎉 Simple greedy can find optimal or near-optimal solutions!');
    console.log('   This could replace the broken YALPS formulation.');
}