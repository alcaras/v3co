#!/usr/bin/env node

const { solve } = require('yalps');

console.log('🎯 FINAL FIXED YALPS FORMULATION\n');

// Apply the working weighted set cover approach to your real optimization problem

const companies = {
    // Your optimal manual selection
    duro_y_compania: {
        base: ['coal_mine', 'steel_mills', 'iron_mine'],
        charters: ['logging_camp'],
        special: false
    },
    basic_home_goods: {
        base: ['glassworks', 'furniture_manufacturies'],
        charters: ['lead_mine'],
        special: false
    },
    nokia: {
        base: ['paper_mills', 'logging_camp', 'power_plant'],
        charters: ['electrics_industry'],
        special: false
    },
    bombay_burmah_trading: {
        base: ['logging_camp', 'rubber_plantation'],
        charters: ['oil_rig'],
        special: false
    },
    kouppas: {
        base: ['motor_industry', 'tooling_workshops'],
        charters: ['automotive_industry'],
        special: false
    },
    bunge_born: {
        base: ['wheat_farm', 'maize_farm', 'food_industry'],
        charters: ['chemical_plants'],
        special: false
    },
    basic_fabrics: {
        base: ['textile_mills'],
        charters: ['cotton_plantation', 'livestock_ranch'],
        special: false
    },
    
    // Alternative companies to test against
    us_steel: {
        base: ['steel_mills', 'iron_mine', 'coal_mine'],
        charters: ['arts_academy'],
        special: false
    },
    krupp: {
        base: ['arms_industry', 'artillery_foundries', 'steel_mills'],
        charters: ['iron_mine'],
        special: false
    },
    russian_american_company: {
        base: ['logging_camp', 'whaling_station', 'port'],
        charters: ['coal_mine'],
        special: false
    },
    john_holt: {
        base: ['rubber_plantation', 'logging_camp', 'port'],
        charters: ['shipyards'],
        special: false
    },
    
    // Special companies (FREE)
    panama_company: {
        base: ['trade_center', 'port'],
        charters: ['shipyards'],
        special: true
    },
    suez_company: {
        base: ['trade_center', 'port'],
        charters: ['shipyards'],
        special: true
    }
};

// Generate all candidates (base + charter variants)
const candidates = [];
Object.entries(companies).forEach(([name, data]) => {
    // Base variant
    candidates.push({
        id: name + '_base',
        company: name,
        variant: 'base',
        buildings: data.base,
        special: data.special,
        score: data.base.length // Score = number of buildings covered
    });
    
    // Charter variants (test with first charter only to avoid conflicts)
    if (data.charters.length > 0) {
        const charter = data.charters[0];
        const charterBuildings = [...data.base, charter];
        candidates.push({
            id: name + '_' + charter,
            company: name,
            variant: charter,
            buildings: charterBuildings,
            special: data.special,
            score: charterBuildings.length // Higher score for charter variants
        });
    }
});

// Get all unique buildings
const allBuildings = new Set();
candidates.forEach(candidate => {
    candidate.buildings.forEach(b => allBuildings.add(b));
});
const buildingList = Array.from(allBuildings).sort();

console.log(`Companies: ${Object.keys(companies).length}`);
console.log(`Candidates: ${candidates.length} (base + charter combinations)`);
console.log(`Buildings: ${buildingList.length}`);

// ═══════════════════════════════════════════════════════════════════
// FIXED WEIGHTED SET COVER MODEL
// ═══════════════════════════════════════════════════════════════════

const model = {
    direction: 'maximize',
    objective: 'weighted_coverage',
    constraints: {
        max_regular_companies: { max: 7 } // Only regular companies count
    },
    variables: {},
    integers: []
};

console.log('\nBuilding FIXED weighted set cover model...');

// Company selection variables with weighted scores
candidates.forEach(candidate => {
    const varName = 'select_' + candidate.id;
    model.variables[varName] = {
        weighted_coverage: candidate.score // Score = number of buildings
    };
    
    // Only regular companies count against limit
    if (!candidate.special) {
        model.variables[varName].max_regular_companies = 1;
    }
    
    model.integers.push(varName);
});

// Building coverage constraints: each building must be covered by at least 1 company
buildingList.forEach(building => {
    const constraint = 'must_cover_' + building;
    model.constraints[constraint] = { min: 1 };
    
    candidates.forEach(candidate => {
        if (candidate.buildings.includes(building)) {
            model.variables['select_' + candidate.id][constraint] = 1;
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
        const constraint = 'exclusive_' + company;
        model.constraints[constraint] = { max: 1 };
        variants.forEach(variantId => {
            model.variables['select_' + variantId][constraint] = 1;
        });
    }
});

console.log(`Model: ${Object.keys(model.variables).length} variables, ${Object.keys(model.constraints).length} constraints`);

console.log('\nSolving with FIXED YALPS formulation...');

const result = solve(model);

console.log(`\nStatus: ${result.status}`);

if (result.status === 'optimal') {
    const selected = result.variables
        .filter(([name, value]) => value >= 0.5 && name.startsWith('select_'))
        .map(([name]) => {
            const id = name.replace('select_', '');
            return candidates.find(c => c.id === id);
        })
        .filter(c => c);
    
    const regularSelected = selected.filter(c => !c.special);
    const specialSelected = selected.filter(c => c.special);
    
    console.log(`Objective: ${result.result}`);
    console.log(`Regular companies: ${regularSelected.length}/7`);
    console.log(`Special companies: ${specialSelected.length}/2 (FREE)`);
    
    // Calculate actual building coverage
    const actualCoverage = new Set();
    selected.forEach(candidate => {
        candidate.buildings.forEach(b => actualCoverage.add(b));
    });
    
    console.log(`Buildings covered: ${actualCoverage.size}/${buildingList.length} (${Math.round(actualCoverage.size/buildingList.length*100)}%)`);
    
    console.log('\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    console.log('SELECTED COMPANIES (FIXED FORMULATION)');
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');
    
    console.log('Regular companies:');
    regularSelected.forEach(c => {
        const variant = c.variant === 'base' ? '(base)' : `+${c.variant}`;
        console.log(`  ${c.company} ${variant}: ${c.buildings.join(', ')} [${c.score} pts]`);
    });
    
    console.log('\nSpecial companies (FREE):');
    specialSelected.forEach(c => {
        const variant = c.variant === 'base' ? '(base)' : `+${c.variant}`;
        console.log(`  ${c.company} ${variant}: ${c.buildings.join(', ')} [${c.score} pts]`);
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
    
    console.log(`\n🔍 OVERLAP ANALYSIS: ${overlaps.length} overlapping buildings`);
    if (overlaps.length > 0) {
        overlaps.forEach(([building, companies]) => {
            console.log(`  ${building}: ${companies.join(', ')}`);
        });
    } else {
        console.log('✅ NO OVERLAPS - Perfect efficiency!');
    }
    
    // Compare to your manual selection
    const yourOptimalCompanies = ['duro_y_compania', 'basic_home_goods', 'nokia', 'bombay_burmah_trading', 'kouppas', 'bunge_born', 'basic_fabrics'];
    const selectedCompanies = selected.map(c => c.company);
    const matchesOptimal = yourOptimalCompanies.every(name => selectedCompanies.includes(name)) && 
                          selectedCompanies.includes('panama_company') && 
                          selectedCompanies.includes('suez_company');
    
    console.log('\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    console.log('COMPARISON WITH YOUR MANUAL SELECTION');
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');
    
    console.log('Your manual selection covers ~22 buildings');
    console.log(`Fixed YALPS covers ${actualCoverage.size} buildings`);
    
    if (matchesOptimal) {
        console.log('✅ FIXED YALPS matches your optimal selection!');
    } else if (actualCoverage.size >= 20 && overlaps.length <= 2) {
        console.log('✅ FIXED YALPS found equivalent or better solution!');
    } else {
        console.log('🔄 FIXED YALPS improved but may not be fully optimal yet');
    }
    
    if (actualCoverage.size > 18 && overlaps.length < 7) {
        console.log('\n🎉 MAJOR IMPROVEMENT over original broken YALPS:');
        console.log(`  📈 Coverage: ${actualCoverage.size} vs 18 buildings`);
        console.log(`  📉 Overlaps: ${overlaps.length} vs 7+ overlaps`);
        console.log('  🧮 Proper linear programming formulation');
    }
    
} else if (result.status === 'infeasible') {
    console.log('\n❌ INFEASIBLE - Some buildings cannot be covered');
    console.log('This suggests missing companies or conflicting constraints');
    
    // Find uncovered buildings
    console.log('\nDebugging infeasibility...');
    buildingList.forEach(building => {
        const coveringCandidates = candidates.filter(c => c.buildings.includes(building));
        if (coveringCandidates.length === 0) {
            console.log(`❌ No company can cover: ${building}`);
        }
    });
    
} else {
    console.log(`❌ Optimization failed: ${result.status}`);
}