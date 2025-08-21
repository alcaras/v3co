#!/usr/bin/env node

const { solve } = require('yalps');
const fs = require('fs');

console.log('🔧 FIXING YALPS: Maximize UNIQUE buildings, not total points\n');

// Load the real data
const rawData = JSON.parse(fs.readFileSync('company_data_v6.json', 'utf8'));
const companyData = {};
Object.entries(rawData).forEach(([name, data]) => {
    companyData[name] = {
        building_types: data.building_types || [],
        extension_building_types: data.extension_building_types || []
    };
});

// Your manual companies for reference
const yourManual = [
    'company_duro_y_compania',
    'company_basic_home_goods', 
    'company_nokia',
    'company_bombay_burmah_trading_corporation',
    'company_kouppas',
    'company_bunge_born',
    'company_basic_fabrics'
];

// Generate a smaller test set including your manual companies + some alternatives
const testCompanies = [
    // Your manual selection
    'company_duro_y_compania',
    'company_nokia', 
    'company_kouppas',
    'company_bunge_born',
    // Some basic companies
    'company_basic_home_goods',
    'company_basic_fabrics',
    'company_basic_steel',
    'company_basic_motors',
    'company_basic_chemicals',
    // Some high-scoring alternatives
    'company_russian_american_company',
    'company_john_holt',
    'company_hanyang_arsenal',
    'company_john_cockerill',
    // Special companies
    'company_panama_company',
    'company_suez_company'
];

console.log('Test companies:', testCompanies.length);

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
        special: isSpecial,
        score: baseBuildings.length
    });
    
    // Best charter variant (highest building count)
    if (charterOptions.length > 0) {
        const charter = charterOptions[0]; // Take first charter for simplicity
        const withCharter = [...baseBuildings, charter];
        candidates.push({
            id: cleanName + '_' + charter,
            company: cleanName,
            variant: charter,
            buildings: withCharter,
            special: isSpecial,
            score: withCharter.length
        });
    }
});

console.log(`Generated ${candidates.length} candidates\n`);

// Get all unique buildings
const allBuildings = new Set();
candidates.forEach(c => c.buildings.forEach(b => allBuildings.add(b)));
const buildingList = Array.from(allBuildings).sort();
console.log(`Total buildings: ${buildingList.length}`);

console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
console.log('TESTING: WRONG vs CORRECT YALPS FORMULATION');
console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');

// ═══════════════════════════════════════════════════════════════════
// WRONG FORMULATION: Maximize sum of building counts (what we were doing)
// ═══════════════════════════════════════════════════════════════════

const wrongModel = {
    direction: 'maximize',
    objective: 'total_points',
    constraints: {
        max_regular: { max: 7 }
    },
    variables: {},
    integers: []
};

candidates.forEach(candidate => {
    const varName = 'select_' + candidate.id;
    wrongModel.variables[varName] = {
        total_points: candidate.score // WRONG: Just sum up building counts
    };
    
    if (!candidate.special) {
        wrongModel.variables[varName].max_regular = 1;
    }
    
    wrongModel.integers.push(varName);
});

// Mutual exclusion
const companyGroups = {};
candidates.forEach(candidate => {
    if (!companyGroups[candidate.company]) companyGroups[candidate.company] = [];
    companyGroups[candidate.company].push(candidate.id);
});

Object.entries(companyGroups).forEach(([company, variants]) => {
    if (variants.length > 1) {
        const constraint = 'exclusive_' + company;
        wrongModel.constraints[constraint] = { max: 1 };
        variants.forEach(variantId => {
            wrongModel.variables['select_' + variantId][constraint] = 1;
        });
    }
});

console.log('WRONG FORMULATION: Maximizing sum of building counts (allows overlaps)');
const wrongResult = solve(wrongModel);

if (wrongResult.status === 'optimal') {
    const wrongSelected = wrongResult.variables
        .filter(([name, value]) => value >= 0.5)
        .map(([name]) => candidates.find(c => c.id === name.replace('select_', '')))
        .filter(c => c);
    
    const wrongBuildings = new Set();
    wrongSelected.forEach(c => c.buildings.forEach(b => wrongBuildings.add(b)));
    
    console.log(`Selected: ${wrongSelected.length} companies`);
    console.log(`Objective: ${wrongResult.result} points`);
    console.log(`Actual unique buildings: ${wrongBuildings.size}/${buildingList.length}\n`);
    
    wrongSelected.forEach(c => {
        const variant = c.variant === 'base' ? '(base)' : `+${c.variant}`;
        console.log(`  ${c.company} ${variant}: ${c.buildings.join(', ')}`);
    });
}

console.log('\n' + '═'.repeat(60));

// ═══════════════════════════════════════════════════════════════════
// CORRECT FORMULATION: Set Cover - each building must be covered at least once
// ═══════════════════════════════════════════════════════════════════

const correctModel = {
    direction: 'maximize',
    objective: 'unique_buildings',
    constraints: {
        max_regular: { max: 7 }
    },
    variables: {},
    integers: []
};

// Building coverage variables
buildingList.forEach(building => {
    const buildingVar = 'covers_' + building;
    correctModel.variables[buildingVar] = {
        unique_buildings: 1 // Each building contributes 1 to the objective
    };
    correctModel.integers.push(buildingVar);
});

// Company selection variables
candidates.forEach(candidate => {
    const varName = 'select_' + candidate.id;
    correctModel.variables[varName] = {};
    
    if (!candidate.special) {
        correctModel.variables[varName].max_regular = 1;
    }
    
    correctModel.integers.push(varName);
});

// Building coverage constraints: building is covered if at least one selected company covers it
buildingList.forEach(building => {
    const constraint = 'cover_' + building;
    correctModel.constraints[constraint] = { min: 0 }; // Building can be covered or not
    
    // Building variable contributes to its own constraint
    correctModel.variables['covers_' + building][constraint] = 1;
    
    // Companies that can cover this building
    candidates.forEach(candidate => {
        if (candidate.buildings.includes(building)) {
            const varName = 'select_' + candidate.id;
            if (!correctModel.variables[varName][constraint]) {
                correctModel.variables[varName][constraint] = 0;
            }
            correctModel.variables[varName][constraint] -= 999; // Big M: if company selected, building MUST be covered
        }
    });
});

// Mutual exclusion (same as before)
Object.entries(companyGroups).forEach(([company, variants]) => {
    if (variants.length > 1) {
        const constraint = 'exclusive_' + company;
        correctModel.constraints[constraint] = { max: 1 };
        variants.forEach(variantId => {
            correctModel.variables['select_' + variantId][constraint] = 1;
        });
    }
});

console.log('CORRECT FORMULATION: Set Cover - maximize unique buildings covered');
const correctResult = solve(correctModel);

if (correctResult.status === 'optimal') {
    const selectedCompanies = correctResult.variables
        .filter(([name, value]) => value >= 0.5 && name.startsWith('select_'))
        .map(([name]) => candidates.find(c => c.id === name.replace('select_', '')))
        .filter(c => c);
    
    const coveredBuildings = correctResult.variables
        .filter(([name, value]) => value >= 0.5 && name.startsWith('covers_'))
        .map(([name]) => name.replace('covers_', ''));
    
    console.log(`Selected: ${selectedCompanies.length} companies`);
    console.log(`Objective: ${correctResult.result} unique buildings`);
    console.log(`Actually covered: ${coveredBuildings.length}/${buildingList.length} buildings\n`);
    
    selectedCompanies.forEach(c => {
        const variant = c.variant === 'base' ? '(base)' : `+${c.variant}`;
        console.log(`  ${c.company} ${variant}: ${c.buildings.join(', ')}`);
    });
    
    console.log(`\nBuildings covered: ${coveredBuildings.join(', ')}`);
} else {
    console.log(`❌ Correct model failed: ${correctResult.status}`);
}

console.log('\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
console.log('CONCLUSION');
console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');

if (wrongResult.status === 'optimal' && correctResult.status === 'optimal') {
    const wrongBuildings = new Set();
    wrongResult.variables
        .filter(([name, value]) => value >= 0.5 && name.startsWith('select_'))
        .forEach(([name]) => {
            const candidate = candidates.find(c => c.id === name.replace('select_', ''));
            if (candidate) candidate.buildings.forEach(b => wrongBuildings.add(b));
        });
    
    console.log('Wrong formulation (maximize points):');
    console.log(`  ${wrongResult.result} total points`);
    console.log(`  ${wrongBuildings.size} unique buildings (with overlaps)`);
    
    console.log('\nCorrect formulation (set cover):');
    console.log(`  ${correctResult.result} unique buildings`);
    console.log(`  No overlaps by design\n`);
    
    if (correctResult.result > wrongBuildings.size) {
        console.log('✅ FIXED! Correct formulation finds more unique buildings');
    } else if (correctResult.result === wrongBuildings.size) {
        console.log('✅ EQUAL: Both find same number of buildings');
    } else {
        console.log('❌ Still broken - need different approach');
    }
}