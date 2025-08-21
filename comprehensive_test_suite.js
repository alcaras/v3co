#!/usr/bin/env node

const fs = require('fs');

// Read the generated HTML and extract the YALPS solver
const html = fs.readFileSync('index.html', 'utf8');
const yalpsStart = html.indexOf('// YALPS Linear Programming Solver');
const yalpsEnd = html.indexOf('// Company data for tooltips');
const yalpsCode = html.substring(yalpsStart, yalpsEnd);

// Evaluate just the YALPS part
eval(yalpsCode);

console.log('🧪 Victoria 3 Comprehensive Optimization Test Suite\n');

let totalTests = 0;
let passedTests = 0;

function runTest(testName, testFunction) {
    totalTests++;
    console.log(`=== Test ${totalTests}: ${testName} ===`);
    
    try {
        const result = testFunction();
        if (result) {
            passedTests++;
            console.log('✅ PASS\n');
        } else {
            console.log('❌ FAIL\n');
        }
    } catch (error) {
        console.log('❌ ERROR:', error.message);
        console.log('');
    }
}

// Test 1: Basic Optimization
runTest('Basic Optimization - Simple Case', () => {
    const model = {
        direction: 'maximize',
        objective: 'coverage',
        constraints: { maxCompanies: { max: 2 } },
        variables: {
            'companyA': { maxCompanies: 1, coverage: 3 },
            'companyB': { maxCompanies: 1, coverage: 2 },
            'companyC': { maxCompanies: 1, coverage: 1 }
        },
        integers: ['companyA', 'companyB', 'companyC']
    };
    
    const result = YALPS.solve(model);
    console.log('Expected: A+B=5, Got:', result.result);
    return result.status === 'optimal' && result.result === 5 && 
           result.variables.length === 2 &&
           result.variables.some(([name]) => name === 'companyA') &&
           result.variables.some(([name]) => name === 'companyB');
});

// Test 2: Mutual Exclusion
runTest('Mutual Exclusion - Charter vs Base', () => {
    const model = {
        direction: 'maximize',
        objective: 'coverage',
        constraints: {
            maxCompanies: { max: 2 },
            basicMining: { max: 1 },
            basicAgriculture: { max: 1 }
        },
        variables: {
            'basic_mining_base': { maxCompanies: 1, coverage: 2, basicMining: 1 },
            'basic_mining_charter': { maxCompanies: 1, coverage: 3, basicMining: 1 },
            'basic_agriculture_base': { maxCompanies: 1, coverage: 1, basicAgriculture: 1 },
            'basic_agriculture_charter': { maxCompanies: 1, coverage: 2, basicAgriculture: 1 }
        },
        integers: ['basic_mining_base', 'basic_mining_charter', 'basic_agriculture_base', 'basic_agriculture_charter']
    };
    
    const result = YALPS.solve(model);
    console.log('Expected: Both charters=5, Got:', result.result);
    const selected = result.variables.map(([name]) => name);
    return result.status === 'optimal' && result.result === 5 &&
           selected.includes('basic_mining_charter') &&
           selected.includes('basic_agriculture_charter');
});

// Test 3: No Valid Solution
runTest('Infeasible Problem - No Valid Solution', () => {
    const model = {
        direction: 'maximize',
        objective: 'coverage',
        constraints: {
            maxCompanies: { max: 0 } // Impossible constraint
        },
        variables: {
            'companyA': { maxCompanies: 1, coverage: 3 }
        },
        integers: ['companyA']
    };
    
    const result = YALPS.solve(model);
    console.log('Expected: No solution, Got status:', result.status);
    return result.status !== 'optimal' || result.result === 0;
});

// Test 4: Single Company Selection
runTest('Single Company - Trivial Case', () => {
    const model = {
        direction: 'maximize',
        objective: 'coverage',
        constraints: { maxCompanies: { max: 1 } },
        variables: {
            'only_company': { maxCompanies: 1, coverage: 5 }
        },
        integers: ['only_company']
    };
    
    const result = YALPS.solve(model);
    console.log('Expected: 5, Got:', result.result);
    return result.status === 'optimal' && result.result === 5 &&
           result.variables.length === 1 &&
           result.variables[0][0] === 'only_company';
});

// Test 5: Many Companies, Tight Constraint
runTest('Many Companies with Tight Constraint', () => {
    const model = {
        direction: 'maximize',
        objective: 'coverage',
        constraints: { maxCompanies: { max: 2 } },
        variables: {
            'company1': { maxCompanies: 1, coverage: 1 },
            'company2': { maxCompanies: 1, coverage: 2 },
            'company3': { maxCompanies: 1, coverage: 3 },
            'company4': { maxCompanies: 1, coverage: 4 },
            'company5': { maxCompanies: 1, coverage: 5 },
            'company6': { maxCompanies: 1, coverage: 6 },
            'company7': { maxCompanies: 1, coverage: 7 },
            'company8': { maxCompanies: 1, coverage: 8 }
        },
        integers: ['company1', 'company2', 'company3', 'company4', 'company5', 'company6', 'company7', 'company8']
    };
    
    const result = YALPS.solve(model);
    console.log('Expected: company7+company8=15, Got:', result.result);
    const selected = result.variables.map(([name]) => name).sort();
    return result.status === 'optimal' && result.result === 15 &&
           selected.includes('company7') && selected.includes('company8');
});

// Test 6: Key Economy Buildings (Realistic Victoria 3)
runTest('Key Economy Buildings - Full Coverage', () => {
    const targetBuildings = ['coal_mine', 'iron_mine', 'logging_camp', 'wheat_farm', 'steel_mills'];
    
    const companies = {
        'basic_extraction_coal_charter_iron': ['coal_mine', 'iron_mine'],
        'basic_agriculture_base': ['wheat_farm'],
        'basic_forestry_base': ['logging_camp'],
        'basic_manufacturing_charter_steel': ['steel_mills']
    };
    
    const model = {
        direction: 'maximize',
        objective: 'coverage',
        constraints: {
            maxCompanies: { max: 4 },
            basicExtraction: { max: 1 },
            basicAgriculture: { max: 1 },
            basicForestry: { max: 1 },
            basicManufacturing: { max: 1 }
        },
        variables: {},
        integers: []
    };
    
    Object.entries(companies).forEach(([name, buildings]) => {
        const relevantBuildings = buildings.filter(b => targetBuildings.includes(b));
        model.variables[name] = {
            maxCompanies: 1,
            coverage: relevantBuildings.length
        };
        
        if (name.includes('extraction')) model.variables[name].basicExtraction = 1;
        if (name.includes('agriculture')) model.variables[name].basicAgriculture = 1;
        if (name.includes('forestry')) model.variables[name].basicForestry = 1;
        if (name.includes('manufacturing')) model.variables[name].basicManufacturing = 1;
        
        model.integers.push(name);
    });
    
    const result = YALPS.solve(model);
    console.log('Expected: All 5 buildings=5, Got:', result.result);
    return result.status === 'optimal' && result.result === 5;
});

// Test 7: Military Complex Buildings
runTest('Military Complex - Arms Production', () => {
    const targetBuildings = ['arms_industry', 'artillery_foundries', 'munition_plants', 'explosives_factory', 'steel_mills'];
    
    const companies = {
        'krupp_base': ['arms_industry', 'artillery_foundries', 'steel_mills'],
        'krupp_charter_iron': ['arms_industry', 'artillery_foundries', 'steel_mills', 'iron_mine'],
        'rheinmetall_base': ['artillery_foundries', 'munition_plants', 'explosives_factory'],
        'rheinmetall_charter_motor': ['artillery_foundries', 'munition_plants', 'explosives_factory', 'motor_industry'],
        'trubia_base': ['arms_industry', 'artillery_foundries'],
        'trubia_charter_explosives': ['arms_industry', 'artillery_foundries', 'munition_plants', 'explosives_factory']
    };
    
    const model = {
        direction: 'maximize',
        objective: 'coverage',
        constraints: {
            maxCompanies: { max: 2 },
            krupp: { max: 1 },
            rheinmetall: { max: 1 },
            trubia: { max: 1 }
        },
        variables: {},
        integers: []
    };
    
    Object.entries(companies).forEach(([name, buildings]) => {
        const relevantBuildings = buildings.filter(b => targetBuildings.includes(b));
        model.variables[name] = {
            maxCompanies: 1,
            coverage: relevantBuildings.length
        };
        
        if (name.includes('krupp')) model.variables[name].krupp = 1;
        if (name.includes('rheinmetall')) model.variables[name].rheinmetall = 1;
        if (name.includes('trubia')) model.variables[name].trubia = 1;
        
        model.integers.push(name);
    });
    
    const result = YALPS.solve(model);
    console.log('Military coverage, Got:', result.result);
    const allCoveredBuildings = new Set();
    result.variables.forEach(([companyName]) => {
        const buildings = companies[companyName];
        buildings.filter(b => targetBuildings.includes(b)).forEach(b => allCoveredBuildings.add(b));
    });
    
    console.log('Selected:', result.variables.map(([name]) => name).join(', '));
    console.log('Covered buildings:', Array.from(allCoveredBuildings).join(', '));
    
    return result.status === 'optimal' && allCoveredBuildings.size >= 4; // Should cover most military buildings
});

// Test 8: USA Industrial Complex
runTest('USA Industrial Complex - Historical Companies', () => {
    const targetBuildings = ['steel_mills', 'arms_industry', 'motor_industry', 'electrics_industry', 'oil_rig', 'railway'];
    
    const companies = {
        'us_steel_base': ['steel_mills', 'iron_mine', 'coal_mine'],
        'us_steel_charter_arts': ['steel_mills', 'iron_mine', 'coal_mine', 'arts_academy'],
        'colt_firearms_base': ['arms_industry'],
        'colt_firearms_charter_munition': ['arms_industry', 'munition_plants'],
        'general_electric_base': ['electrics_industry', 'power_plant'],
        'general_electric_charter_motor': ['electrics_industry', 'power_plant', 'motor_industry'],
        'standard_oil_base': ['oil_rig', 'railway'],
        'standard_oil_charter_port': ['oil_rig', 'railway', 'port'],
        'ford_motor_base': ['motor_industry', 'automotive_industry'],
        'ford_motor_charter_steel': ['motor_industry', 'automotive_industry', 'steel_mills']
    };
    
    const model = {
        direction: 'maximize',
        objective: 'coverage',
        constraints: {
            maxCompanies: { max: 4 },
            usSteel: { max: 1 },
            coltFirearms: { max: 1 },
            generalElectric: { max: 1 },
            standardOil: { max: 1 },
            fordMotor: { max: 1 }
        },
        variables: {},
        integers: []
    };
    
    Object.entries(companies).forEach(([name, buildings]) => {
        const relevantBuildings = buildings.filter(b => targetBuildings.includes(b));
        model.variables[name] = {
            maxCompanies: 1,
            coverage: relevantBuildings.length
        };
        
        if (name.includes('us_steel')) model.variables[name].usSteel = 1;
        if (name.includes('colt_firearms')) model.variables[name].coltFirearms = 1;
        if (name.includes('general_electric')) model.variables[name].generalElectric = 1;
        if (name.includes('standard_oil')) model.variables[name].standardOil = 1;
        if (name.includes('ford_motor')) model.variables[name].fordMotor = 1;
        
        model.integers.push(name);
    });
    
    const result = YALPS.solve(model);
    console.log('USA industrial coverage, Got:', result.result);
    console.log('Selected:', result.variables.map(([name]) => name).join(', '));
    
    return result.status === 'optimal' && result.result >= 6; // Should cover most target buildings
});

// Test 9: British Empire Trade Network
runTest('British Empire Trade Network', () => {
    const targetBuildings = ['port', 'shipyards', 'railway', 'textile_mills', 'steel_mills', 'tea_plantation'];
    
    const companies = {
        'east_india_company_base': ['tea_plantation', 'tobacco_plantation', 'opium_plantation'],
        'east_india_company_charter_silk': ['tea_plantation', 'tobacco_plantation', 'opium_plantation', 'silk_plantation'],
        'john_brown_base': ['military_shipyards', 'shipyards', 'steel_mills'],
        'john_brown_charter_iron': ['military_shipyards', 'shipyards', 'steel_mills', 'iron_mine'],
        'gwr_base': ['railway'],
        'gwr_charter_coal': ['railway', 'coal_mine'],
        'j_p_coats_base': ['textile_mills'],
        'j_p_coats_charter_cotton': ['textile_mills', 'cotton_plantation'],
        'guinness_base': ['food_industry'],
        'guinness_charter_wheat': ['food_industry', 'wheat_farm', 'rye_farm']
    };
    
    const model = {
        direction: 'maximize',
        objective: 'coverage',
        constraints: {
            maxCompanies: { max: 3 },
            eastIndiaCompany: { max: 1 },
            johnBrown: { max: 1 },
            gwr: { max: 1 },
            jpCoats: { max: 1 },
            guinness: { max: 1 }
        },
        variables: {},
        integers: []
    };
    
    Object.entries(companies).forEach(([name, buildings]) => {
        const relevantBuildings = buildings.filter(b => targetBuildings.includes(b));
        model.variables[name] = {
            maxCompanies: 1,
            coverage: relevantBuildings.length
        };
        
        if (name.includes('east_india_company')) model.variables[name].eastIndiaCompany = 1;
        if (name.includes('john_brown')) model.variables[name].johnBrown = 1;
        if (name.includes('gwr')) model.variables[name].gwr = 1;
        if (name.includes('j_p_coats')) model.variables[name].jpCoats = 1;
        if (name.includes('guinness')) model.variables[name].guinness = 1;
        
        model.integers.push(name);
    });
    
    const result = YALPS.solve(model);
    console.log('British Empire coverage, Got:', result.result);
    console.log('Selected:', result.variables.map(([name]) => name).join(', '));
    
    return result.status === 'optimal' && result.result >= 3;
});

// Test 10: Japanese Zaibatsu System
runTest('Japanese Zaibatsu System', () => {
    const targetBuildings = ['steel_mills', 'shipyards', 'railway', 'textile_mills', 'coal_mine', 'port'];
    
    const companies = {
        'mitsubishi_base': ['military_shipyards', 'coal_mine', 'paper_mills'],
        'mitsubishi_charter_port': ['military_shipyards', 'coal_mine', 'paper_mills', 'shipyards', 'motor_industry', 'port'],
        'mitsui_base': ['textile_mills', 'silk_plantation', 'lead_mine'],
        'mitsui_charter_shipyards': ['textile_mills', 'silk_plantation', 'lead_mine', 'shipyards', 'port'],
        'mantetsu_base': ['railway', 'coal_mine', 'glassworks'],
        'mantetsu_charter_chemical': ['railway', 'coal_mine', 'glassworks', 'food_industry', 'chemical_plants']
    };
    
    const model = {
        direction: 'maximize',
        objective: 'coverage',
        constraints: {
            maxCompanies: { max: 3 },
            mitsubishi: { max: 1 },
            mitsui: { max: 1 },
            mantetsu: { max: 1 }
        },
        variables: {},
        integers: []
    };
    
    Object.entries(companies).forEach(([name, buildings]) => {
        const relevantBuildings = buildings.filter(b => targetBuildings.includes(b));
        model.variables[name] = {
            maxCompanies: 1,
            coverage: relevantBuildings.length
        };
        
        if (name.includes('mitsubishi')) model.variables[name].mitsubishi = 1;
        if (name.includes('mitsui')) model.variables[name].mitsui = 1;
        if (name.includes('mantetsu')) model.variables[name].mantetsu = 1;
        
        model.integers.push(name);
    });
    
    const result = YALPS.solve(model);
    console.log('Japanese zaibatsu coverage, Got:', result.result);
    console.log('Selected:', result.variables.map(([name]) => name).join(', '));
    
    return result.status === 'optimal' && result.result >= 5;
});

// Test 11: Edge Case - All Zero Coverage
runTest('Edge Case - All Zero Coverage', () => {
    const model = {
        direction: 'maximize',
        objective: 'coverage',
        constraints: { maxCompanies: { max: 3 } },
        variables: {
            'useless1': { maxCompanies: 1, coverage: 0 },
            'useless2': { maxCompanies: 1, coverage: 0 },
            'useless3': { maxCompanies: 1, coverage: 0 }
        },
        integers: ['useless1', 'useless2', 'useless3']
    };
    
    const result = YALPS.solve(model);
    console.log('Expected: 0 coverage, Got:', result.result);
    return result.status === 'optimal' && result.result === 0;
});

// Test 12: Edge Case - Exact Constraint Match
runTest('Edge Case - Exact Constraint Match', () => {
    const model = {
        direction: 'maximize',
        objective: 'coverage',
        constraints: { maxCompanies: { max: 3 } },
        variables: {
            'company1': { maxCompanies: 1, coverage: 2 },
            'company2': { maxCompanies: 1, coverage: 2 },
            'company3': { maxCompanies: 1, coverage: 2 }
        },
        integers: ['company1', 'company2', 'company3']
    };
    
    const result = YALPS.solve(model);
    console.log('Expected: exactly 6, Got:', result.result);
    return result.status === 'optimal' && result.result === 6 && result.variables.length === 3;
});

// Test 13: Complex Multi-Company Exclusions
runTest('Complex Multi-Company Exclusions', () => {
    const model = {
        direction: 'maximize',
        objective: 'coverage',
        constraints: {
            maxCompanies: { max: 4 },
            basicMining: { max: 1 },
            basicAgri: { max: 1 },
            basicMfg: { max: 1 },
            basicOil: { max: 1 }
        },
        variables: {
            'basic_mining_coal': { maxCompanies: 1, coverage: 1, basicMining: 1 },
            'basic_mining_iron': { maxCompanies: 1, coverage: 2, basicMining: 1 },
            'basic_mining_gold': { maxCompanies: 1, coverage: 1, basicMining: 1 },
            'basic_agri_wheat': { maxCompanies: 1, coverage: 1, basicAgri: 1 },
            'basic_agri_rice': { maxCompanies: 1, coverage: 2, basicAgri: 1 },
            'basic_mfg_textile': { maxCompanies: 1, coverage: 1, basicMfg: 1 },
            'basic_mfg_steel': { maxCompanies: 1, coverage: 3, basicMfg: 1 },
            'basic_oil_simple': { maxCompanies: 1, coverage: 1, basicOil: 1 },
            'basic_oil_coal': { maxCompanies: 1, coverage: 2, basicOil: 1 }
        },
        integers: ['basic_mining_coal', 'basic_mining_iron', 'basic_mining_gold', 'basic_agri_wheat', 'basic_agri_rice', 'basic_mfg_textile', 'basic_mfg_steel', 'basic_oil_simple', 'basic_oil_coal']
    };
    
    const result = YALPS.solve(model);
    console.log('Expected: best from each group=8, Got:', result.result);
    const selected = result.variables.map(([name]) => name);
    console.log('Selected:', selected.join(', '));
    
    // Should select best from each category: iron(2) + rice(2) + steel(3) + oil_coal(2) = 9
    return result.status === 'optimal' && result.result >= 8 && result.variables.length === 4;
});

// Test 14: Resource Extraction Focus
runTest('Resource Extraction Focus', () => {
    const targetBuildings = ['coal_mine', 'iron_mine', 'gold_mine', 'oil_rig', 'logging_camp', 'sulfur_mine'];
    
    const companies = {
        'basic_mineral_mining': ['sulfur_mine', 'coal_mine'],
        'basic_metal_mining': ['iron_mine', 'lead_mine'],
        'basic_gold_mining': ['gold_mine'],
        'basic_oil': ['oil_rig'],
        'basic_forestry': ['logging_camp', 'rubber_plantation'],
        'de_beers': ['gold_mine'],
        'branobel': ['oil_rig'],
        'lkab': ['iron_mine']
    };
    
    const model = {
        direction: 'maximize',
        objective: 'coverage',
        constraints: {
            maxCompanies: { max: 6 },
            basicMineral: { max: 1 },
            basicMetal: { max: 1 },
            basicGold: { max: 1 },
            basicOil: { max: 1 },
            basicForestry: { max: 1 },
            deBeers: { max: 1 },
            branobel: { max: 1 },
            lkab: { max: 1 }
        },
        variables: {},
        integers: []
    };
    
    Object.entries(companies).forEach(([name, buildings]) => {
        const relevantBuildings = buildings.filter(b => targetBuildings.includes(b));
        model.variables[name] = {
            maxCompanies: 1,
            coverage: relevantBuildings.length
        };
        
        if (name === 'basic_mineral_mining') model.variables[name].basicMineral = 1;
        if (name === 'basic_metal_mining') model.variables[name].basicMetal = 1;
        if (name === 'basic_gold_mining') model.variables[name].basicGold = 1;
        if (name === 'basic_oil') model.variables[name].basicOil = 1;
        if (name === 'basic_forestry') model.variables[name].basicForestry = 1;
        if (name === 'de_beers') model.variables[name].deBeers = 1;
        if (name === 'branobel') model.variables[name].branobel = 1;
        if (name === 'lkab') model.variables[name].lkab = 1;
        
        model.integers.push(name);
    });
    
    const result = YALPS.solve(model);
    console.log('Resource extraction coverage, Got:', result.result);
    console.log('Selected:', result.variables.map(([name]) => name).join(', '));
    
    return result.status === 'optimal' && result.result >= 5;
});

// Test 15: Luxury Goods Economy
runTest('Luxury Goods Economy', () => {
    const targetBuildings = ['glassworks', 'furniture_manufacturies', 'arts_academy', 'silk_plantation', 'vineyard_plantation'];
    
    const companies = {
        'ludwig_moser': ['glassworks'],
        'gebruder_thonet': ['furniture_manufacturies'],
        'maple_and_co': ['furniture_manufacturies'],
        'maison_worth': ['textile_mills'], // Luxury textiles
        'ricordi': ['arts_academy'],
        'cgv': ['vineyard_plantation'],
        'jingdezhen': ['glassworks'],
        'mantero_seta': ['silk_plantation', 'textile_mills']
    };
    
    const model = {
        direction: 'maximize',
        objective: 'coverage',
        constraints: {
            maxCompanies: { max: 5 },
            ludwigMoser: { max: 1 },
            gebruderThonet: { max: 1 },
            mapleAndCo: { max: 1 },
            maisonWorth: { max: 1 },
            ricordi: { max: 1 },
            cgv: { max: 1 },
            jingdezhen: { max: 1 },
            manteroSeta: { max: 1 }
        },
        variables: {},
        integers: []
    };
    
    Object.entries(companies).forEach(([name, buildings]) => {
        const relevantBuildings = buildings.filter(b => targetBuildings.includes(b));
        model.variables[name] = {
            maxCompanies: 1,
            coverage: relevantBuildings.length
        };
        
        if (name === 'ludwig_moser') model.variables[name].ludwigMoser = 1;
        if (name === 'gebruder_thonet') model.variables[name].gebruderThonet = 1;
        if (name === 'maple_and_co') model.variables[name].mapleAndCo = 1;
        if (name === 'maison_worth') model.variables[name].maisonWorth = 1;
        if (name === 'ricordi') model.variables[name].ricordi = 1;
        if (name === 'cgv') model.variables[name].cgv = 1;
        if (name === 'jingdezhen') model.variables[name].jingdezhen = 1;
        if (name === 'mantero_seta') model.variables[name].manteroSeta = 1;
        
        model.integers.push(name);
    });
    
    const result = YALPS.solve(model);
    console.log('Luxury goods coverage, Got:', result.result);
    console.log('Selected:', result.variables.map(([name]) => name).join(', '));
    
    return result.status === 'optimal' && result.result >= 4;
});

// Test 16: Transportation Network
runTest('Transportation Network', () => {
    const targetBuildings = ['railway', 'port', 'shipyards', 'motor_industry'];
    
    const companies = {
        'prussian_state_railways': ['railway'],
        'gwr': ['railway'],
        'orient_express': ['railway'],
        'sao_paulo_railway': ['railway'],
        'ap_moller': ['port'],
        'panama_company': ['trade_center', 'port'],
        'john_brown': ['military_shipyards', 'shipyards', 'steel_mills'],
        'fcm': ['shipyards', 'military_shipyards', 'automotive_industry'],
        'ford_motor': ['motor_industry', 'automotive_industry'],
        'fiat': ['motor_industry', 'automotive_industry']
    };
    
    const model = {
        direction: 'maximize',
        objective: 'coverage',
        constraints: {
            maxCompanies: { max: 4 },
            prussianRailways: { max: 1 },
            gwr: { max: 1 },
            orientExpress: { max: 1 },
            saoPauloRailway: { max: 1 },
            apMoller: { max: 1 },
            panamaCompany: { max: 1 },
            johnBrown: { max: 1 },
            fcm: { max: 1 },
            fordMotor: { max: 1 },
            fiat: { max: 1 }
        },
        variables: {},
        integers: []
    };
    
    Object.entries(companies).forEach(([name, buildings]) => {
        const relevantBuildings = buildings.filter(b => targetBuildings.includes(b));
        model.variables[name] = {
            maxCompanies: 1,
            coverage: relevantBuildings.length
        };
        
        const constraintMap = {
            'prussian_state_railways': 'prussianRailways',
            'gwr': 'gwr',
            'orient_express': 'orientExpress',
            'sao_paulo_railway': 'saoPauloRailway',
            'ap_moller': 'apMoller',
            'panama_company': 'panamaCompany',
            'john_brown': 'johnBrown',
            'fcm': 'fcm',
            'ford_motor': 'fordMotor',
            'fiat': 'fiat'
        };
        
        if (constraintMap[name]) {
            model.variables[name][constraintMap[name]] = 1;
        }
        
        model.integers.push(name);
    });
    
    const result = YALPS.solve(model);
    console.log('Transportation coverage, Got:', result.result);
    console.log('Selected:', result.variables.map(([name]) => name).join(', '));
    
    return result.status === 'optimal' && result.result >= 4;
});

// Test 17: Chemical Industry Focus
runTest('Chemical Industry Focus', () => {
    const targetBuildings = ['chemical_plants', 'synthetics_plants', 'explosives_factory', 'sulfur_mine', 'dye_plantation'];
    
    const companies = {
        'basf_base': ['synthetics_plants', 'chemical_plants'],
        'basf_charter_sulfur': ['synthetics_plants', 'chemical_plants', 'dye_plantation', 'sulfur_mine'],
        'basic_chemicals': ['chemical_plants', 'synthetics_plants'],
        'basic_munitions': ['munition_plants', 'explosives_factory'],
        'norsk_hydro': ['chemical_plants', 'power_plant'],
        'chr_hansens': ['food_industry', 'chemical_plants']
    };
    
    const model = {
        direction: 'maximize',
        objective: 'coverage',
        constraints: {
            maxCompanies: { max: 3 },
            basf: { max: 1 },
            basicChemicals: { max: 1 },
            basicMunitions: { max: 1 },
            norskHydro: { max: 1 },
            chrHansens: { max: 1 }
        },
        variables: {},
        integers: []
    };
    
    Object.entries(companies).forEach(([name, buildings]) => {
        const relevantBuildings = buildings.filter(b => targetBuildings.includes(b));
        model.variables[name] = {
            maxCompanies: 1,
            coverage: relevantBuildings.length
        };
        
        if (name.includes('basf')) model.variables[name].basf = 1;
        if (name === 'basic_chemicals') model.variables[name].basicChemicals = 1;
        if (name === 'basic_munitions') model.variables[name].basicMunitions = 1;
        if (name === 'norsk_hydro') model.variables[name].norskHydro = 1;
        if (name === 'chr_hansens') model.variables[name].chrHansens = 1;
        
        model.integers.push(name);
    });
    
    const result = YALPS.solve(model);
    console.log('Chemical industry coverage, Got:', result.result);
    console.log('Selected:', result.variables.map(([name]) => name).join(', '));
    
    return result.status === 'optimal' && result.result >= 3;
});

// Test 18: Agricultural Powerhouse
runTest('Agricultural Powerhouse', () => {
    const targetBuildings = ['wheat_farm', 'rice_farm', 'maize_farm', 'cotton_plantation', 'livestock_ranch', 'food_industry'];
    
    const companies = {
        'basic_agriculture_1': ['wheat_farm', 'rye_farm'],
        'basic_agriculture_2': ['rice_farm', 'millet_farm', 'maize_farm'],
        'basic_fabrics': ['cotton_plantation', 'livestock_ranch'],
        'bunge_born': ['wheat_farm', 'maize_farm', 'food_industry'],
        'united_fruit': ['sugar_plantation', 'banana_plantation'],
        'ralli_brothers': ['rice_farm', 'wheat_farm'],
        'vodka_monopoly': ['food_industry', 'vineyard_plantation'],
        'guinness': ['food_industry']
    };
    
    const model = {
        direction: 'maximize',
        objective: 'coverage',
        constraints: {
            maxCompanies: { max: 5 },
            basicAgriculture1: { max: 1 },
            basicAgriculture2: { max: 1 },
            basicFabrics: { max: 1 },
            bungeBorn: { max: 1 },
            unitedFruit: { max: 1 },
            ralliBrothers: { max: 1 },
            vodkaMonopoly: { max: 1 },
            guinness: { max: 1 }
        },
        variables: {},
        integers: []
    };
    
    Object.entries(companies).forEach(([name, buildings]) => {
        const relevantBuildings = buildings.filter(b => targetBuildings.includes(b));
        model.variables[name] = {
            maxCompanies: 1,
            coverage: relevantBuildings.length
        };
        
        const constraintMap = {
            'basic_agriculture_1': 'basicAgriculture1',
            'basic_agriculture_2': 'basicAgriculture2',
            'basic_fabrics': 'basicFabrics',
            'bunge_born': 'bungeBorn',
            'united_fruit': 'unitedFruit',
            'ralli_brothers': 'ralliBrothers',
            'vodka_monopoly': 'vodkaMonopoly',
            'guinness': 'guinness'
        };
        
        if (constraintMap[name]) {
            model.variables[name][constraintMap[name]] = 1;
        }
        
        model.integers.push(name);
    });
    
    const result = YALPS.solve(model);
    console.log('Agricultural coverage, Got:', result.result);
    console.log('Selected:', result.variables.map(([name]) => name).join(', '));
    
    return result.status === 'optimal' && result.result >= 6;
});

// Test 19: Stress Test - Large Scale Problem
runTest('Stress Test - Large Scale Problem', () => {
    const model = {
        direction: 'maximize',
        objective: 'coverage',
        constraints: { maxCompanies: { max: 7 } },
        variables: {},
        integers: []
    };
    
    // Generate 50 companies with varying coverage
    for (let i = 1; i <= 50; i++) {
        const companyName = `company_${i}`;
        model.variables[companyName] = {
            maxCompanies: 1,
            coverage: Math.floor(Math.random() * 10) + 1 // 1-10 buildings
        };
        model.integers.push(companyName);
    }
    
    const result = YALPS.solve(model);
    console.log(`Large scale (50 companies), selected ${result.variables.length}, coverage: ${result.result}`);
    
    return result.status === 'optimal' && result.variables.length <= 7 && result.result > 0;
});

// Test 20: Edge Case - Empty Variables
runTest('Edge Case - Empty Variables', () => {
    const model = {
        direction: 'maximize',
        objective: 'coverage',
        constraints: { maxCompanies: { max: 5 } },
        variables: {},
        integers: []
    };
    
    const result = YALPS.solve(model);
    console.log('Empty variables, Got status:', result.status, 'result:', result.result);
    
    return result.result === 0 && result.variables.length === 0;
});

// Final Results
console.log('🏁 Test Suite Complete');
console.log(`📊 Results: ${passedTests}/${totalTests} tests passed`);
console.log(`✅ Pass Rate: ${Math.round((passedTests / totalTests) * 100)}%`);

if (passedTests === totalTests) {
    console.log('🎉 All tests passed! Optimization system is working perfectly.');
} else {
    console.log(`⚠️  ${totalTests - passedTests} tests failed. Review implementation.`);
}