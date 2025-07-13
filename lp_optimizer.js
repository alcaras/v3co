// Linear Programming Optimizer for Victoria 3 Company Selection
// Uses javascript-lp-solver to find optimal company combinations

function solveCompanyOptimization(companies, maxSlots, canalCompanies = [], requiredPrestigeGoods = [], selectedBuildings = [], priorityBuildings = []) {
    console.log('Setting up LP problem...');
    
    // Filter out canal companies for slot constraints
    const regularCompanies = companies.filter(c => c.special !== 'canal');
    
    // Create LP model
    const model = {
        optimize: "score",
        opType: "max",
        constraints: {},
        variables: {},
        ints: {}
    };
    
    // Decision variables: x_i for each company
    regularCompanies.forEach((company, i) => {
        const varName = `x_${i}`;
        model.variables[varName] = {};
        model.ints[varName] = 1; // Integer variable (0 or 1)
        
        // Objective coefficient: calculate individual company value
        const companyValue = calculateIndividualCompanyValue(company, selectedBuildings, priorityBuildings);
        model.variables[varName].score = companyValue;
    });
    
    // Charter decision variables: c_i_j for company i charter j
    regularCompanies.forEach((company, i) => {
        if (company.industryCharters && company.industryCharters.length > 0) {
            company.industryCharters.forEach((charter, j) => {
                const charterVar = `c_${i}_${j}`;
                model.variables[charterVar] = {};
                model.ints[charterVar] = 1;
                
                // Charter value: +1 if it covers a selected building not already covered
                const charterValue = selectedBuildings.includes(charter) ? 1 : 0;
                model.variables[charterVar].score = charterValue;
                
                // Charter can only be taken if company is selected
                const companyVar = `x_${i}`;
                if (!model.constraints[`charter_requires_company_${i}_${j}`]) {
                    model.constraints[`charter_requires_company_${i}_${j}`] = { max: 0 };
                }
                model.constraints[`charter_requires_company_${i}_${j}`][charterVar] = 1;
                model.constraints[`charter_requires_company_${i}_${j}`][companyVar] = -1;
            });
            
            // At most one charter per company
            const charterConstraint = `max_one_charter_${i}`;
            model.constraints[charterConstraint] = { max: 1 };
            company.industryCharters.forEach((charter, j) => {
                model.constraints[charterConstraint][`c_${i}_${j}`] = 1;
            });
        }
    });
    
    // Slot constraint: sum of selected companies <= maxSlots
    model.constraints.slot_limit = { max: maxSlots };
    regularCompanies.forEach((company, i) => {
        model.constraints.slot_limit[`x_${i}`] = 1;
    });
    
    // Building coverage constraints: each selected building must be covered
    selectedBuildings.forEach((building, buildingIdx) => {
        const constraintName = `cover_building_${buildingIdx}`;
        model.constraints[constraintName] = { min: 1 };
        
        // Companies that provide this building
        regularCompanies.forEach((company, i) => {
            if (company.buildings.includes(building)) {
                model.constraints[constraintName][`x_${i}`] = 1;
            }
        });
        
        // Charters that provide this building
        regularCompanies.forEach((company, i) => {
            if (company.industryCharters && company.industryCharters.includes(building)) {
                const charterIdx = company.industryCharters.indexOf(building);
                model.constraints[constraintName][`c_${i}_${charterIdx}`] = 1;
            }
        });
    });
    
    // Prestige goods constraints: each required prestige good must be provided
    requiredPrestigeGoods.forEach((requiredGood, goodIdx) => {
        const constraintName = `prestige_${goodIdx}`;
        model.constraints[constraintName] = { min: 1 };
        
        // Companies that provide this prestige good base type
        regularCompanies.forEach((company, i) => {
            const providesGood = company.prestigeGoods.some(pg => prestigeGoodsMapping[pg] === requiredGood);
            if (providesGood) {
                model.constraints[constraintName][`x_${i}`] = 1;
            }
        });
        
        // Canal companies also count for prestige goods
        canalCompanies.forEach(canalCompany => {
            const providesGood = canalCompany.prestigeGoods.some(pg => prestigeGoodsMapping[pg] === requiredGood);
            if (providesGood) {
                // Add canal company as a fixed variable (always selected)
                model.constraints[constraintName][`canal_${canalCompany.name}`] = 1;
                model.variables[`canal_${canalCompany.name}`] = { score: 0 }; // No score impact, just for constraint
                model.ints[`canal_${canalCompany.name}`] = 1;
                // Fix canal company to 1
                if (!model.constraints[`fix_canal_${canalCompany.name}`]) {
                    model.constraints[`fix_canal_${canalCompany.name}`] = { equal: 1 };
                    model.constraints[`fix_canal_${canalCompany.name}`][`canal_${canalCompany.name}`] = 1;
                }
            }
        });
    });
    
    console.log('LP model created, solving...');
    console.log('Variables:', Object.keys(model.variables).length);
    console.log('Constraints:', Object.keys(model.constraints).length);
    
    // Solve the LP
    const solution = solver.Solve(model);
    
    if (!solution || solution.feasible === false) {
        console.log('No feasible solution found');
        return [];
    }
    
    console.log('LP solution found:', solution);
    
    // Extract selected companies and charters
    const selectedCompanies = [];
    const selectedCharters = [];
    
    regularCompanies.forEach((company, i) => {
        if (solution[`x_${i}`] && solution[`x_${i}`] > 0.5) {
            selectedCompanies.push(company);
            
            // Check which charter was selected for this company
            if (company.industryCharters) {
                company.industryCharters.forEach((charter, j) => {
                    if (solution[`c_${i}_${j}`] && solution[`c_${i}_${j}`] > 0.5) {
                        selectedCharters.push({ company: company.name, charter });
                    }
                });
            }
        }
    });
    
    // Add canal companies (always included)
    const allCompanies = [...selectedCompanies, ...canalCompanies];
    
    console.log('Selected companies:', selectedCompanies.map(c => c.name));
    console.log('Selected charters:', selectedCharters);
    console.log('Objective value:', solution.result);
    
    // Calculate actual score using the original scoring function for verification
    const actualScore = calculateScore(allCompanies);
    console.log('Verification score:', actualScore);
    
    return [{
        companies: selectedCompanies,
        totalScore: actualScore,
        slotsUsed: selectedCompanies.length,
        charters: selectedCharters
    }];
}

function calculateIndividualCompanyValue(company, selectedBuildings, priorityBuildings) {
    let value = 0;
    
    // +1 for each selected building covered
    const selectedCovered = company.buildings.filter(b => selectedBuildings.includes(b)).length;
    value += selectedCovered;
    
    // +2 for each priority building covered  
    const priorityCovered = company.buildings.filter(b => priorityBuildings.includes(b)).length;
    value += priorityCovered * 2;
    
    // +0.1 for each prestige good
    value += company.prestigeGoods.length * 0.1;
    
    // +0.01 for each non-selected building (tiebreaker)
    const nonSelectedCovered = company.buildings.filter(b => !selectedBuildings.includes(b)).length;
    value += nonSelectedCovered * 0.01;
    
    return value;
}