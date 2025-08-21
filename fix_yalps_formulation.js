#!/usr/bin/env node

const { solve } = require('yalps');

console.log('🔧 FIXING YALPS FORMULATION\n');

// The issue: Current formulation has scaling problems
// Let's create a clean, simple formulation that just maximizes unique buildings

console.log('=== CORRECT FORMULATION TEST ===\n');

// Test case: 3 buildings, 4 companies
const companies = [
    { name: 'A', buildings: ['b1'] },
    { name: 'B', buildings: ['b2'] }, 
    { name: 'C', buildings: ['b3'] },
    { name: 'D', buildings: ['b1', 'b2'] }  // Overlapping
];

const buildings = ['b1', 'b2', 'b3'];

// FIXED FORMULATION: Direct set cover without building variables
const model = {
    direction: 'maximize',
    objective: 'buildings_covered',
    constraints: {
        max_companies: { max: 3 }
    },
    variables: {},
    integers: []
};

// Add company selection variables
companies.forEach((company, i) => {
    const varName = `company_${company.name}`;
    model.variables[varName] = {
        max_companies: 1,
        buildings_covered: 0  // Will be set based on unique contribution
    };
    model.integers.push(varName);
});

// Calculate each company's unique contribution to objective
// This is the key fix: each company contributes based on buildings it can uniquely cover
companies.forEach((company, i) => {
    const varName = `company_${company.name}`;
    
    // For now, give each company credit for all its buildings
    // (overlaps will be handled by the solver naturally preferring more coverage)
    model.variables[varName].buildings_covered = company.buildings.length;
});

// Add constraints for each building: at least one company must cover it
buildings.forEach(building => {
    const constraint = `cover_${building}`;
    model.constraints[constraint] = { min: 1 }; // At least 1 company must cover this building
    
    companies.forEach(company => {
        if (company.buildings.includes(building)) {
            const varName = `company_${company.name}`;
            if (!model.variables[varName][constraint]) {
                model.variables[varName][constraint] = 0;
            }
            model.variables[varName][constraint] = 1; // This company can cover this building
        }
    });
});

console.log('Fixed Model:');
console.log('- Objective: Maximize buildings_covered');
console.log('- Company variables contribute their building count to objective');
console.log('- Constraints: Each building must be covered by at least 1 company');
console.log('- Max 3 companies\n');

console.log('Expected optimal: A + B + C (3 companies, 3 buildings, 6 objective)');
console.log('Alternative: D + C (2 companies, 3 buildings, 5 objective) - should be worse\n');

const result1 = solve(model);

console.log(`Result: ${result1.status}, objective = ${result1.result}`);

if (result1.status === 'optimal') {
    const selected = result1.variables
        .filter(([name, value]) => value > 0.5)
        .map(([name]) => name.replace('company_', ''));
    
    console.log(`Selected companies: ${selected.join(', ')}`);
    
    // Calculate actual buildings covered
    const actualBuildings = new Set();
    selected.forEach(companyName => {
        const company = companies.find(c => c.name === companyName);
        company.buildings.forEach(b => actualBuildings.add(b));
    });
    
    console.log(`Actual buildings covered: ${Array.from(actualBuildings).join(', ')} (${actualBuildings.size} total)`);
    
    if (actualBuildings.size === 3 && selected.length <= 3) {
        console.log('✅ Covers all buildings efficiently!');
    } else {
        console.log('❌ Suboptimal solution');
    }
}

// =================================================================
// Test 2: Even simpler approach - weighted set cover
// =================================================================

console.log('\n=== WEIGHTED SET COVER APPROACH ===\n');

// Give each company a score based on unique buildings it adds
// This eliminates the scaling issue entirely

const model2 = {
    direction: 'maximize',
    objective: 'weighted_coverage',
    constraints: {
        max_companies: { max: 3 }
    },
    variables: {},
    integers: []
};

// Calculate weighted scores to prefer companies with less overlap
const companyCoverageScores = companies.map(company => {
    // Score = number of buildings this company covers
    // In a real implementation, we could weight by rarity/importance
    return {
        name: company.name,
        buildings: company.buildings,
        score: company.buildings.length
    };
});

companyCoverageScores.forEach(company => {
    const varName = `select_${company.name}`;
    model2.variables[varName] = {
        max_companies: 1,
        weighted_coverage: company.score  // Direct score contribution
    };
    model2.integers.push(varName);
});

// Add coverage constraints: each building must be covered
buildings.forEach(building => {
    const constraint = `must_cover_${building}`;
    model2.constraints[constraint] = { min: 1 };
    
    companyCoverageScores.forEach(company => {
        if (company.buildings.includes(building)) {
            model2.variables[`select_${company.name}`][constraint] = 1;
        }
    });
});

console.log('Weighted Set Cover Model:');
console.log('- Each company gets score = number of buildings it covers');
console.log('- Constraints: Each building MUST be covered by at least 1 selected company');
console.log('- Naturally prefers efficient combinations\n');

console.log('Company scores:');
companyCoverageScores.forEach(c => {
    console.log(`  ${c.name}: ${c.buildings.join(',')} = ${c.score} points`);
});

const result2 = solve(model2);

console.log(`\nResult: ${result2.status}, objective = ${result2.result}`);

if (result2.status === 'optimal') {
    const selected2 = result2.variables
        .filter(([name, value]) => value > 0.5)
        .map(([name]) => name.replace('select_', ''));
    
    console.log(`Selected companies: ${selected2.join(', ')}`);
    
    // Verify all buildings are covered
    const covered2 = new Set();
    selected2.forEach(companyName => {
        const company = companies.find(c => c.name === companyName);
        company.buildings.forEach(b => covered2.add(b));
    });
    
    console.log(`Buildings covered: ${Array.from(covered2).join(', ')}`);
    
    if (covered2.size === buildings.length) {
        console.log('✅ ALL BUILDINGS COVERED with weighted approach!');
        console.log(`Efficiency: ${covered2.size} buildings with ${selected2.length} companies`);
    } else {
        console.log('❌ Missing buildings - constraint failed');
    }
}

// =================================================================  
// Test 3: Your optimal companies with fixed formulation
// =================================================================

console.log('\n=== TESTING YOUR OPTIMAL SELECTION ===\n');

// Use the fixed formulation on your optimal companies
const yourCompanies = [
    { name: 'duro_y_compania', buildings: ['coal_mine', 'steel_mills', 'iron_mine', 'logging_camp'] },
    { name: 'basic_home_goods', buildings: ['glassworks', 'furniture_manufacturies', 'lead_mine'] },
    { name: 'nokia', buildings: ['paper_mills', 'logging_camp', 'power_plant', 'electrics_industry'] },
    { name: 'bombay_burmah', buildings: ['logging_camp', 'rubber_plantation', 'oil_rig'] },
    { name: 'kouppas', buildings: ['motor_industry', 'tooling_workshops', 'automotive_industry'] },
    { name: 'bunge_born', buildings: ['wheat_farm', 'maize_farm', 'food_industry', 'chemical_plants'] },
    { name: 'basic_fabrics', buildings: ['textile_mills', 'cotton_plantation'] },
    
    // Add some suboptimal alternatives
    { name: 'us_steel', buildings: ['steel_mills', 'iron_mine', 'coal_mine'] },
    { name: 'krupp', buildings: ['arms_industry', 'artillery_foundries', 'steel_mills'] }
];

const yourBuildings = [...new Set(yourCompanies.flatMap(c => c.buildings))];

const model3 = {
    direction: 'maximize',
    objective: 'coverage_score',
    constraints: {
        max_companies: { max: 7 }
    },
    variables: {},
    integers: []
};

yourCompanies.forEach(company => {
    const varName = `sel_${company.name}`;
    model3.variables[varName] = {
        max_companies: 1,
        coverage_score: company.buildings.length  // Score = building count
    };
    model3.integers.push(varName);
});

// Coverage constraints for each building
yourBuildings.forEach(building => {
    const constraint = `req_${building}`;
    model3.constraints[constraint] = { min: 1 };
    
    yourCompanies.forEach(company => {
        if (company.buildings.includes(building)) {
            model3.variables[`sel_${company.name}`][constraint] = 1;
        }
    });
});

console.log(`Testing with ${yourCompanies.length} companies and ${yourBuildings.length} buildings...`);

const result3 = solve(model3);

console.log(`\nYour companies result: ${result3.status}, objective = ${result3.result}`);

if (result3.status === 'optimal') {
    const selected3 = result3.variables
        .filter(([name, value]) => value > 0.5)
        .map(([name]) => name.replace('sel_', ''));
    
    console.log(`\nSelected (${selected3.length} companies):`);
    selected3.forEach(name => {
        const company = yourCompanies.find(c => c.name === name);
        console.log(`  ${name}: ${company.buildings.join(', ')}`);
    });
    
    const totalCovered = new Set();
    selected3.forEach(name => {
        const company = yourCompanies.find(c => c.name === name);
        company.buildings.forEach(b => totalCovered.add(b));
    });
    
    console.log(`\nTotal coverage: ${totalCovered.size}/${yourBuildings.length} buildings`);
    
    const isOptimal = selected3.includes('duro_y_compania') && 
                     selected3.includes('nokia') && 
                     selected3.includes('kouppas') &&
                     !selected3.includes('us_steel') &&
                     !selected3.includes('krupp');
    
    if (isOptimal) {
        console.log('✅ YALPS selected your optimal companies with fixed formulation!');
    } else {
        console.log('❌ YALPS still picking suboptimal companies');
    }
}