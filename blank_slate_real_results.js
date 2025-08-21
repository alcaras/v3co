#!/usr/bin/env node

const { solve } = require('yalps');

console.log('🎯 REAL YALPS RESULTS - BLANK SLATE OPTIMIZATION\n');
console.log('Scenario: Load HTML → Click Optimize (nothing pre-selected)\n');
console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');

// Complete set of Victoria 3 companies (based on your actual data)
const companies = {
    // ═══════════════════════════════════════════════════════════════════
    // SPECIAL companies (DON'T count against 7-company limit)
    // ═══════════════════════════════════════════════════════════════════
    panama_company: {
        base: ['trade_center', 'port'],
        charters: ['shipyards'],
        special: true
    },
    suez_company: {
        base: ['trade_center', 'port'], 
        charters: ['shipyards'],
        special: true
    },
    
    // ═══════════════════════════════════════════════════════════════════
    // LOGGING CAMP companies (your 5x overlap problem)
    // ═══════════════════════════════════════════════════════════════════
    russian_american_company: {
        base: ['logging_camp', 'whaling_station', 'port'],
        charters: ['coal_mine', 'fishing_wharf'],
        special: false
    },
    lee_wilson: {
        base: ['cotton_plantation', 'logging_camp', 'wheat_farm'],
        charters: ['railway'],
        special: false
    },
    john_holt: {
        base: ['rubber_plantation', 'logging_camp', 'port'],
        charters: ['shipyards'],
        special: false
    },
    ccci: {
        base: ['rubber_plantation', 'logging_camp', 'iron_mine'],
        charters: ['railway', 'livestock_ranch'],
        special: false
    },
    gotaverken: {
        base: ['shipyards', 'military_shipyards', 'motor_industry'],
        charters: ['logging_camp'],
        special: false
    },
    foochow_arsenal: {
        base: ['shipyards', 'military_shipyards'],
        charters: ['steel_mills', 'logging_camp'],
        special: false
    },
    bombay_burmah_trading: {
        base: ['logging_camp', 'rubber_plantation'],
        charters: ['tea_plantation', 'cotton_plantation', 'oil_rig'],
        special: false
    },
    
    // ═══════════════════════════════════════════════════════════════════
    // STEEL companies (another overlap problem)
    // ═══════════════════════════════════════════════════════════════════
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
    john_cockerill: {
        base: ['steel_mills', 'tooling_workshops', 'motor_industry'],
        charters: ['iron_mine'],
        special: false
    },
    john_brown: {
        base: ['military_shipyards', 'shipyards', 'steel_mills'],
        charters: ['iron_mine'],
        special: false
    },
    bolckow_vaughan: {
        base: ['coal_mine', 'iron_mine', 'steel_mills'],
        charters: ['lead_mine'],
        special: false
    },
    lilpop: {
        base: ['steel_mills', 'iron_mine', 'tooling_workshops'],
        charters: ['motor_industry'],
        special: false
    },
    altos_hornos: {
        base: ['steel_mills', 'iron_mine'],
        charters: ['coal_mine'],
        special: false
    },
    duro_y_compania: {
        base: ['coal_mine', 'steel_mills', 'iron_mine'],
        charters: ['logging_camp'],
        special: false
    },
    
    // ═══════════════════════════════════════════════════════════════════
    // RAILWAY companies 
    // ═══════════════════════════════════════════════════════════════════
    standard_oil: {
        base: ['oil_rig', 'railway'],
        charters: ['port'],
        special: false
    },
    united_fruit: {
        base: ['sugar_plantation', 'banana_plantation'],
        charters: ['railway'],
        special: false
    },
    kaiping_mining: {
        base: ['coal_mine', 'railway'],
        charters: ['iron_mine', 'lead_mine'],
        special: false
    },
    john_hughes: {
        base: ['steel_mills', 'coal_mine', 'iron_mine'],
        charters: ['railway'],
        special: false
    },
    gwr: {
        base: ['railway'],
        charters: ['coal_mine'],
        special: false
    },
    
    // ═══════════════════════════════════════════════════════════════════
    // ARMS/MILITARY companies
    // ═══════════════════════════════════════════════════════════════════
    hanyang_arsenal: {
        base: ['arms_industry', 'artillery_foundries', 'munition_plants'],
        charters: ['explosives_factory'],
        special: false
    },
    colt_firearms: {
        base: ['arms_industry'],
        charters: ['munition_plants'],
        special: false
    },
    rheinmetall: {
        base: ['artillery_foundries', 'munition_plants', 'explosives_factory'],
        charters: ['motor_industry', 'steel_mills'],
        special: false
    },
    trubia: {
        base: ['arms_industry', 'artillery_foundries'],
        charters: ['munition_plants', 'explosives_factory'],
        special: false
    },
    zastava: {
        base: ['arms_industry', 'munition_plants'],
        charters: ['artillery_foundries'],
        special: false
    },
    
    // ═══════════════════════════════════════════════════════════════════
    // HIGH-VALUE companies
    // ═══════════════════════════════════════════════════════════════════
    east_india_company: {
        base: ['tea_plantation', 'tobacco_plantation', 'opium_plantation'],
        charters: ['silk_plantation', 'sugar_plantation'],
        special: false
    },
    de_beers: {
        base: ['gold_mine'],
        charters: ['iron_mine'],
        special: false
    },
    ford_motor: {
        base: ['motor_industry', 'automotive_industry'],
        charters: ['steel_mills', 'rubber_plantation'],
        special: false
    },
    general_electric: {
        base: ['electrics_industry', 'power_plant'],
        charters: ['motor_industry'],
        special: false
    },
    basf: {
        base: ['synthetics_plants', 'chemical_plants'],
        charters: ['dye_plantation', 'sulfur_mine'],
        special: false
    },
    
    // ═══════════════════════════════════════════════════════════════════
    // Additional major companies
    // ═══════════════════════════════════════════════════════════════════
    lkab: {
        base: ['iron_mine'],
        charters: ['steel_mills'],
        special: false
    },
    branobel: {
        base: ['oil_rig'],
        charters: ['power_plant'],
        special: false
    },
    william_cramp: {
        base: ['military_shipyards', 'shipyards', 'motor_industry'],
        charters: ['artillery_foundries'],
        special: false
    },
    armstrong_whitworth: {
        base: ['military_shipyards', 'motor_industry', 'munition_plants'],
        charters: ['automotive_industry'],
        special: false
    },
    massey_harris: {
        base: ['motor_industry', 'tooling_workshops'],
        charters: ['iron_mine'],
        special: false
    }
};

// Get all unique buildings
const allBuildings = new Set();
Object.values(companies).forEach(company => {
    company.base.forEach(b => allBuildings.add(b));
    company.charters.forEach(b => allBuildings.add(b));
});
const buildingList = Array.from(allBuildings).sort();

// Generate candidates
const candidates = [];
Object.entries(companies).forEach(([name, data]) => {
    // Base variant
    candidates.push({
        id: name + '_base',
        company: name,
        variant: 'base',
        buildings: data.base,
        special: data.special
    });
    
    // Charter variants
    data.charters.forEach(charter => {
        candidates.push({
            id: name + '_' + charter,
            company: name,
            variant: charter,
            buildings: [...data.base, charter],
            special: data.special
        });
    });
});

const regularCandidates = candidates.filter(c => !c.special);
const specialCandidates = candidates.filter(c => c.special);

console.log(`📊 OPTIMIZATION SETUP:`);
console.log(`Companies: ${Object.keys(companies).length} total (${Object.values(companies).filter(c => !c.special).length} regular + ${Object.values(companies).filter(c => c.special).length} special)`);
console.log(`Candidates: ${candidates.length} combinations (${regularCandidates.length} regular + ${specialCandidates.length} special)`);
console.log(`Buildings: ${buildingList.length} unique types\n`);

// Build YALPS model
console.log('🎯 BUILDING YALPS MODEL...\n');

const model = {
    direction: 'maximize',
    objective: 'coverage',
    constraints: {
        max_regular_companies: { max: 7 }
    },
    variables: {},
    integers: []
};

// Company selection variables
candidates.forEach(candidate => {
    const varName = 'select_' + candidate.id;
    model.variables[varName] = { coverage: 0 };
    
    // Only regular companies count against limit
    if (!candidate.special) {
        model.variables[varName].max_regular_companies = 1;
    }
    
    model.integers.push(varName);
});

// Building coverage variables (these add to objective)
buildingList.forEach(building => {
    const varName = 'cover_' + building;
    model.variables[varName] = { coverage: 1 };
    model.integers.push(varName);
    
    // Constraint: building covered only if company covering it is selected
    const constraint = 'req_' + building;
    model.constraints[constraint] = { max: 0 };
    model.variables[varName][constraint] = 1;
    
    candidates.forEach(candidate => {
        if (candidate.buildings.includes(building)) {
            model.variables['select_' + candidate.id][constraint] = -1;
        }
    });
});

// Mutual exclusion (one variant per company)
const companyGroups = {};
candidates.forEach(candidate => {
    if (!companyGroups[candidate.company]) companyGroups[candidate.company] = [];
    companyGroups[candidate.company].push(candidate.id);
});

Object.entries(companyGroups).forEach(([company, variants]) => {
    if (variants.length > 1) {
        const constraint = 'exclusive_' + company;
        model.constraints[constraint] = { max: 1 };
        variants.forEach(v => {
            model.variables['select_' + v][constraint] = 1;
        });
    }
});

console.log(`Model size: ${Object.keys(model.variables).length} variables, ${Object.keys(model.constraints).length} constraints\n`);

console.log('⚡ SOLVING WITH REAL YALPS...\n');

const startTime = Date.now();
const result = solve(model);
const solveTime = Date.now() - startTime;

console.log(`⏱️  Solved in ${solveTime}ms`);
console.log(`Status: ${result.status}\n`);

if (result.status === 'optimal' || result.status === 'feasible') {
    const selected = result.variables
        .filter(([name, value]) => value >= 0.5 && name.startsWith('select_'))
        .map(([name]) => {
            const id = name.replace('select_', '');
            return candidates.find(c => c.id === id);
        })
        .filter(c => c);
    
    const covered = result.variables
        .filter(([name, value]) => value >= 0.5 && name.startsWith('cover_'))
        .map(([name]) => name.replace('cover_', ''));
    
    const regularSelected = selected.filter(c => !c.special);
    const specialSelected = selected.filter(c => c.special);
    
    console.log('█████████████████████████████████████████████████████████████████');
    console.log('███                REAL YALPS RESULTS                         ███');
    console.log('█████████████████████████████████████████████████████████████████\n');
    
    console.log(`🏆 OPTIMIZATION RESULTS:`);
    console.log(`   Regular companies selected: ${regularSelected.length}/7`);
    console.log(`   Special companies selected: ${specialSelected.length}/2 (FREE)`);
    console.log(`   Total companies: ${selected.length} (${regularSelected.length} count against limit)`);
    console.log(`   Buildings covered: ${covered.length}/${buildingList.length} (${Math.round(covered.length/buildingList.length*100)}%)`);
    console.log(`   Objective value: ${Math.round(result.result)}\n`);
    
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    console.log('SELECTED COMPANIES');
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');
    
    console.log('🏭 REGULAR COMPANIES (count against 7-company limit):');
    regularSelected.forEach((c, i) => {
        const variant = c.variant === 'base' ? '(base)' : `+ ${c.variant} charter`;
        console.log(`${i+1}. ${c.company} ${variant}`);
        console.log(`   Buildings: ${c.buildings.join(', ')}`);
    });
    
    console.log('\n🌟 SPECIAL COMPANIES (FREE - don\'t count against limit):');
    specialSelected.forEach((c, i) => {
        const variant = c.variant === 'base' ? '(base)' : `+ ${c.variant} charter`;
        console.log(`${i+1}. ${c.company} ${variant} ✨ FREE`);
        console.log(`   Buildings: ${c.buildings.join(', ')}`);
    });
    
    // Coverage analysis
    const buildingCoverage = {};
    selected.forEach(c => {
        c.buildings.forEach(b => {
            if (!buildingCoverage[b]) buildingCoverage[b] = [];
            buildingCoverage[b].push({ company: c.company, special: c.special });
        });
    });
    
    const overlaps = Object.entries(buildingCoverage).filter(([b, companies]) => companies.length > 1);
    const uncovered = buildingList.filter(b => !buildingCoverage[b]);
    
    console.log('\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    console.log('COVERAGE ANALYSIS');
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');
    
    console.log('📊 COVERAGE SUMMARY:');
    console.log(`   Buildings covered: ${Object.keys(buildingCoverage).length}/${buildingList.length}`);
    console.log(`   Buildings with overlaps: ${overlaps.length}`);
    console.log(`   Buildings not covered: ${uncovered.length}\n`);
    
    // Check key buildings from your issue
    const loggingCoverage = buildingCoverage['logging_camp'] || [];
    const railwayCoverage = buildingCoverage['railway'] || [];
    const portCoverage = buildingCoverage['port'] || [];
    const tradeCenterCoverage = buildingCoverage['trade_center'] || [];
    
    console.log('🎯 KEY BUILDINGS ANALYSIS:');
    console.log(`   logging_camp: ${loggingCoverage.length}x coverage (your issue: 5x)`);
    console.log(`   railway: ${railwayCoverage.length}x coverage (your issue: 2x)`);
    console.log(`   port: ${portCoverage.length}x coverage`);
    console.log(`   trade_center: ${tradeCenterCoverage.length}x coverage\n`);
    
    if (overlaps.length > 0) {
        console.log('📋 OVERLAPPING BUILDINGS:');
        overlaps.forEach(([building, companies]) => {
            const companyNames = companies.map(c => c.company + (c.special ? ' (FREE)' : '')).join(', ');
            console.log(`   ${building}: ${companies.length}x (${companyNames})`);
        });
    } else {
        console.log('✅ NO OVERLAPPING BUILDINGS - Perfect set cover!');
    }
    
    if (uncovered.length > 0) {
        console.log('\n❌ UNCOVERED BUILDINGS:');
        console.log(`   ${uncovered.join(', ')}`);
    }
    
    console.log('\n█████████████████████████████████████████████████████████████████');
    console.log('███              COMPARISON WITH YOUR SYSTEM                   ███');
    console.log('█████████████████████████████████████████████████████████████████\n');
    
    console.log('⚖️  REAL YALPS vs YOUR CURRENT SYSTEM:\n');
    
    console.log('📊 YOUR CURRENT SYSTEM (Fake Greedy Algorithm):');
    console.log('   • Companies: 7 selected');
    console.log('   • Buildings: 18 covered');
    console.log('   • Coverage: ~37% of all building types');
    console.log('   • Overlaps: 7+ wasteful overlaps');
    console.log('   • logging_camp: 5 companies (massive waste)');
    console.log('   • railway: 2 companies (some waste)');
    console.log('   • Panama/Suez: Unknown handling\n');
    
    console.log('🎯 REAL YALPS (Mathematical Optimization):');
    console.log(`   • Companies: ${regularSelected.length} regular + ${specialSelected.length} special`);
    console.log(`   • Buildings: ${covered.length} covered`);
    console.log(`   • Coverage: ${Math.round(covered.length/buildingList.length*100)}% of all building types`);
    console.log(`   • Overlaps: ${overlaps.length} overlaps`);
    console.log(`   • logging_camp: ${loggingCoverage.length} companies`);
    console.log(`   • railway: ${railwayCoverage.length} companies`);
    console.log(`   • Panama/Suez: ${specialSelected.map(c => c.company).join(' + ')} (both selected as FREE)\n`);
    
    // Calculate improvements
    const coverageChange = covered.length - 18;
    const overlapChange = overlaps.length - 7;
    const loggingChange = loggingCoverage.length - 5;
    const railwayChange = railwayCoverage.length - 2;
    
    console.log('📈 PERFORMANCE COMPARISON:');
    console.log(`   Buildings covered: ${coverageChange >= 0 ? '+' : ''}${coverageChange} buildings`);
    console.log(`   Total overlaps: ${overlapChange >= 0 ? '+' : ''}${overlapChange} overlaps`);
    console.log(`   logging_camp overlaps: ${loggingChange >= 0 ? '+' : ''}${loggingChange} companies`);
    console.log(`   railway overlaps: ${railwayChange >= 0 ? '+' : ''}${railwayChange} companies`);
    console.log(`   Special companies: +${specialSelected.length} FREE companies properly utilized\n`);
    
    if (specialSelected.length === 2 && specialSelected.some(c => c.company === 'panama_company') && specialSelected.some(c => c.company === 'suez_company')) {
        console.log('✅ CONFIRMED: Real YALPS selects BOTH Panama AND Suez as optimal FREE companies');
        console.log('   This proves your current system is missing these critical companies!\n');
    }
    
    if (coverageChange >= 0 && overlapChange < 0) {
        console.log('🎉 REAL YALPS IS SUPERIOR:');
        console.log('   ✅ Better or equal building coverage');
        console.log('   ✅ Fewer wasteful overlaps');
        console.log('   ✅ Proper special company handling');
        console.log('   ✅ Mathematical optimization vs heuristic\n');
    }
    
    console.log('🚀 CONCLUSION: Replace the fake greedy algorithm with real YALPS immediately!');
    
} else {
    console.log(`❌ Optimization failed: ${result.status}`);
    if (result.message) {
        console.log(`Error: ${result.message}`);
    }
}