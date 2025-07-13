// Victoria 3 Company Optimizer - LP Solver Module
// Extracted from index.html for better modularity and testing

// Load prestige goods mapping
import { prestigeGoodsMapping } from './prestige-goods.mjs';

/**
 * Calculate individual score for a company variant
 * @param {Object} variant - Company variant object
 * @param {Array} selectedBuildings - Array of selected building names
 * @param {Array} priorityBuildings - Array of priority building names
 * @returns {number} Individual score for the variant
 */
function calculateIndividualScore(variant, selectedBuildings, priorityBuildings) {
    let score = 0;
    
    // Building coverage (1 point per unique building type covered)
    const selectedBuildingsCovered = new Set(variant.buildings.filter(b => selectedBuildings.includes(b)));
    score += selectedBuildingsCovered.size * 1;
    
    // Priority building coverage (2 points per unique priority building type covered)
    const priorityBuildingsCovered = new Set(variant.buildings.filter(b => priorityBuildings.includes(b)));
    score += priorityBuildingsCovered.size * 2;
    
    // Prestige goods (0.1 points each)
    score += (variant.prestigeGoods?.length || 0) * 0.1;
    
    // Non-selected buildings (0.01 points each)
    score += variant.buildings.filter(b => !selectedBuildings.includes(b)).length * 0.01;
    
    // Charter penalty (very small)
    if (variant.selectedCharter) score -= 0.001;
    
    return score;
}

/**
 * Solve company optimization using Integer Linear Programming with YALPS
 * @param {Array} variants - Array of company variants
 * @param {number} maxSlots - Maximum number of company slots
 * @param {Array} selectedBuildings - Array of selected building names
 * @param {Array} priorityBuildings - Array of priority building names
 * @param {Array} requiredPrestigeGoods - Array of required prestige good base types
 * @param {Array} requiredCompanies - Array of required company names
 * @returns {Promise<Array>} Array of selected company variants
 */
async function solveIntegerLP(variants, maxSlots, selectedBuildings, priorityBuildings, requiredPrestigeGoods, requiredCompanies) {
    console.log('Using YALPS Linear Programming solver...');
    
    try {
        // Use ES6 module import with .mjs extension for proper MIME type
        const { solve } = await import('./YALPS.mjs');
        
        // Group variants by base company
        const baseCompanyGroups = new Map();
        variants.forEach(variant => {
            const baseCompany = variant.baseCompanyName;
            if (!baseCompanyGroups.has(baseCompany)) {
                baseCompanyGroups.set(baseCompany, []);
            }
            baseCompanyGroups.get(baseCompany).push(variant);
        });

        const baseCompanies = Array.from(baseCompanyGroups.keys());
        console.log(`Setting up LP for ${variants.length} variants from ${baseCompanies.length} base companies`);

        // Create LP model with building coverage indicators
        const variables = {};
        const constraints = {};

        // Company decision variables: x_i for each variant i (binary)
        variants.forEach((variant, i) => {
            const varName = `x${i}`;
            variables[varName] = {
                score: 0, // Will get points from building coverage variables only
                slots: variant.special === 'canal' ? 0 : 1, // Canal companies don't use slots
                [`company_${variant.baseCompanyName}`]: 1, // Company constraint
            };

            // Connect company to buildings it provides
            variant.buildings.forEach(building => {
                variables[varName][`provides_${building}`] = 1;
            });

            // Prestige goods constraints (canal companies are exempt from uniqueness)
            if (variant.prestigeGoods) {
                variant.prestigeGoods.forEach(pg => {
                    // Canal companies don't participate in prestige goods uniqueness constraints
                    const isCanalCompany = variant.special === 'canal';
                    
                    if (!isCanalCompany) {
                        // Regular companies: add to prestige goods uniqueness constraint
                        variables[varName][`prestige_${pg}`] = 1;
                    }
                    
                    // All companies (including canal) can contribute to required prestige goods
                    const baseType = prestigeGoodsMapping[pg];
                    if (baseType && requiredPrestigeGoods.includes(baseType)) {
                        const constraintName = `required_prestige_${baseType}`;
                        variables[varName][constraintName] = 1;
                    }
                });
            }
        });

        // Building coverage indicator variables: b_building (binary)
        // These get the actual points and represent "at least one company covers this building"
        const allBuildings = new Set();
        variants.forEach(variant => {
            variant.buildings.forEach(building => allBuildings.add(building));
        });

        allBuildings.forEach(building => {
            const buildingVar = `covered_${building}`;
            let buildingScore = 0;
            
            // Score for having this building covered (regardless of how many companies provide it)
            if (selectedBuildings.includes(building)) {
                buildingScore = priorityBuildings.includes(building) ? 2 : 1;
            } else {
                buildingScore = 0.01; // Small bonus for coverage of non-selected buildings
            }
            
            variables[buildingVar] = {
                score: buildingScore, // Points for covering this building (once)
            };
            
            // Also add an upper bound constraint to ensure binary behavior
            const boundConstraintName = `bound_${building}`;
            variables[buildingVar][boundConstraintName] = 1; // covered_building <= 1
            constraints[boundConstraintName] = { max: 1 };

            // Add constraint: covered_building <= sum of providers
            const constraintName = `coverage_constraint_${building}`;
            
            // Start with the building variable coefficient
            variables[buildingVar][constraintName] = 1; // covered_building coefficient
            
            // Add provider company coefficients
            variants.forEach((variant, i) => {
                if (variant.buildings.includes(building)) {
                    const companyVar = `x${i}`;
                    if (!variables[companyVar][constraintName]) {
                        variables[companyVar][constraintName] = 0;
                    }
                    variables[companyVar][constraintName] -= 1; // -1 * x_company
                }
            });
            
            // Add the constraint: covered_building - sum(providers) <= 0
            constraints[constraintName] = { max: 0 };
        });

        // Add prestige good bonuses to company variables (these are additive)
        variants.forEach((variant, i) => {
            if (variant.prestigeGoods && variant.prestigeGoods.length > 0) {
                const varName = `x${i}`;
                variables[varName].score = variant.prestigeGoods.length * 0.1; // Prestige goods are additive
            }
        });

        // Constraints
        constraints.slots = { max: maxSlots };

        // At most one variant per base company 
        // This applies to ALL companies (including canal) to prevent infinite selection
        baseCompanies.forEach(baseCompany => {
            constraints[`company_${baseCompany}`] = { max: 1 };
        });

        // At most one company per prestige good (excluding canal companies)
        // Canal companies are exempt from prestige goods uniqueness constraints
        const allPrestigeGoods = new Set();
        variants.forEach(variant => {
            if (variant.prestigeGoods && variant.special !== 'canal') {
                variant.prestigeGoods.forEach(pg => allPrestigeGoods.add(pg));
            }
        });
        allPrestigeGoods.forEach(pg => {
            // Create constraint that only applies to non-canal companies
            constraints[`prestige_${pg}`] = { max: 1 };
        });

        // Required prestige goods - create OR constraints for multiple goods mapping to same base type
        requiredPrestigeGoods.forEach(pg => {
            const mappedGoods = Object.keys(prestigeGoodsMapping).filter(good => 
                prestigeGoodsMapping[good] === pg
            );
            console.log(`Required prestige good '${pg}' maps to:`, mappedGoods);
            if (mappedGoods.length > 0) {
                // Create a single constraint that requires at least 1 of any mapped good
                const constraintName = `required_prestige_${pg}`;
                constraints[constraintName] = { min: 1 };
                console.log(`Setting OR constraint for ${constraintName}`);
                
                // Still set individual constraints for max bounds
                mappedGoods.forEach(mappedGood => {
                    if (!constraints[`prestige_${mappedGood}`]) {
                        constraints[`prestige_${mappedGood}`] = { max: 1 };
                    }
                });
            } else {
                // Required prestige good doesn't exist - create impossible constraint
                console.log(`ERROR: Required prestige good '${pg}' has no mapped goods - LP will be infeasible`);
                const constraintName = `impossible_prestige_${pg}`;
                constraints[constraintName] = { min: 1 }; // Require at least 1 but no variables contribute to this
            }
        });

        // Priority buildings are now just scoring bonuses, not hard requirements
        
        // Required companies - must be included in solution
        requiredCompanies.forEach(requiredCompanyName => {
            variants.forEach((variant, i) => {
                if (variant.baseCompanyName === requiredCompanyName) {
                    const varName = `x${i}`;
                    if (!variables[varName][`required_${requiredCompanyName}`]) {
                        variables[varName][`required_${requiredCompanyName}`] = 1;
                    }
                }
            });
            
            // Require at least one variant of this company to be selected
            constraints[`required_${requiredCompanyName}`] = { min: 1 };
            console.log(`Added required company constraint for: ${requiredCompanyName}`);
        });

        // Charter constraints - at most one company can take each charter type
        const allCharters = new Set();
        variants.forEach(variant => {
            if (variant.selectedCharter) {
                allCharters.add(variant.selectedCharter);
            }
        });
        
        allCharters.forEach(charter => {
            variants.forEach((variant, i) => {
                if (variant.selectedCharter === charter) {
                    const varName = `x${i}`;
                    if (!variables[varName][`charter_${charter}`]) {
                        variables[varName][`charter_${charter}`] = 1;
                    }
                }
            });
            
            // At most one company can take this charter
            constraints[`charter_${charter}`] = { max: 1 };
        });

        // Building coverage tracking for redundancy penalties in scoring
        // Instead of hard constraints, we'll let the scoring function handle redundancy
        selectedBuildings.forEach(building => {
            variants.forEach((variant, i) => {
                const varName = `x${i}`;
                
                // Track all variants that provide this building for potential scoring adjustments
                if (variant.buildings.includes(building)) {
                    if (!variables[varName][`provides_${building}`]) {
                        variables[varName][`provides_${building}`] = 1;
                    }
                }
            });
        });

        const lpModel = {
            direction: 'maximize',
            objective: 'score',
            variables,
            constraints,
            integers: Object.keys(variables) // All variables are binary/integer
        };

        console.log('LP Model:', Object.keys(variables).length, 'variables,', Object.keys(constraints).length, 'constraints');
        
        // Debug: Show sample variables and their scores
        console.log('\n=== SAMPLE LP VARIABLES ===');
        const varEntries = Object.entries(variables);
        varEntries.slice(0, 5).forEach(([varName, varData]) => {
            console.log(`${varName}: score=${varData.score}, constraints=${Object.keys(varData).filter(k => k !== 'score').length}`);
        });
        
        // Debug: Show building coverage variables
        const buildingVars = varEntries.filter(([name]) => name.startsWith('covered_'));
        console.log(`\nBuilding coverage variables: ${buildingVars.length}`);
        buildingVars.slice(0, 5).forEach(([varName, varData]) => {
            const constraintKeys = Object.keys(varData).filter(k => k !== 'score');
            console.log(`${varName}: score=${varData.score}, constraints=${constraintKeys.length}`);
        });
        
        // Debug: Show constraint structure
        console.log(`\nConstraint structure:`);
        const constraintEntries = Object.entries(constraints);
        constraintEntries.slice(0, 5).forEach(([constraintName, constraintData]) => {
            console.log(`${constraintName}: ${JSON.stringify(constraintData)}`);
        });
        
        // Debug: Show top scoring variants
        console.log('\n=== TOP 10 SCORING VARIANTS ===');
        const sortedVariants = variants.map((variant, i) => ({
            name: variant.name,
            baseCompanyName: variant.baseCompanyName,
            score: calculateIndividualScore(variant, selectedBuildings, priorityBuildings),
            buildings: variant.buildings,
            selectedCharter: variant.selectedCharter,
            prestigeGoods: variant.prestigeGoods,
            isRequired: requiredCompanies.includes(variant.baseCompanyName),
            selectedBuildingCount: variant.buildings.filter(b => selectedBuildings.includes(b)).length,
            priorityBuildingCount: variant.buildings.filter(b => priorityBuildings.includes(b)).length
        })).sort((a, b) => b.score - a.score).slice(0, 10);
        
        sortedVariants.forEach((variant, i) => {
            const flags = [];
            if (variant.isRequired) flags.push('REQUIRED');
            if (variant.selectedCharter) flags.push('CHARTER');
            if (variant.priorityBuildingCount > 0) flags.push(`${variant.priorityBuildingCount}★PRIO`);
            if (variant.prestigeGoods && variant.prestigeGoods.length > 0) flags.push('PRESTIGE');
            
            console.log(`${i+1}. [${flags.join(',')}] ${variant.baseCompanyName}${variant.selectedCharter ? ` + ${variant.selectedCharter}` : ''} - Score: ${variant.score.toFixed(3)}`);
            console.log(`   Selected: ${variant.selectedBuildingCount}/${variant.buildings.length} | Priority: ${variant.priorityBuildingCount} | Prestige: ${variant.prestigeGoods ? variant.prestigeGoods.length : 0}`);
            console.log(`   Buildings: [${variant.buildings.map(b => priorityBuildings.includes(b) ? b+'★' : b).join(', ')}]`);
            if (variant.prestigeGoods && variant.prestigeGoods.length > 0) {
                console.log(`   Prestige: [${variant.prestigeGoods.join(', ')}]`);
            }
            console.log('');
        });

        // Solve with YALPS
        console.log('Calling YALPS solve...');
        const solution = solve(lpModel);
        console.log('YALPS solution status:', solution.status);
        console.log('YALPS solution result:', solution.result);
        console.log('YALPS solution variables length:', solution.variables?.length);
        
        // Debug: Show all solution variables
        if (solution.variables) {
            console.log('All solution variables:');
            solution.variables.forEach(([varName, value]) => {
                if (value > 0.1) { // Show variables with significant values
                    console.log(`  ${varName}: ${value}`);
                }
            });
        }

        if (solution.status === 'optimal') {
            const selectedVariants = [];
            solution.variables.forEach(([varName, value]) => {
                if (value > 0.5 && varName.startsWith('x')) { // Only company variables (x0, x1, etc.)
                    const index = parseInt(varName.substring(1));
                    if (variants[index]) { // Make sure variant exists
                        selectedVariants.push(variants[index]);
                    }
                }
            });

            console.log(`YALPS found optimal solution: ${selectedVariants.length} companies, score: ${solution.result}`);
            
            // Debug: Show selected companies and their individual scores
            console.log('LP-optimized selection:');
            selectedVariants.forEach((variant, i) => {
                const score = calculateIndividualScore(variant, selectedBuildings, priorityBuildings);
                console.log(`${i+1}. ${variant.baseCompanyName} ${variant.selectedCharter ? '+ ' + variant.selectedCharter : ''} - Score: ${score.toFixed(3)}`);
                console.log(`   Buildings: [${variant.buildings.map(b => priorityBuildings.includes(b) ? b+'★' : b).join(', ')}]`);
                console.log(`   Prestige: [${variant.prestigeGoods ? variant.prestigeGoods.join(', ') : 'none'}]`);
            });
            
            return selectedVariants;
        } else if (solution.status === 'infeasible') {
            console.error('LP is infeasible - constraints cannot be satisfied');
            
            // Provide helpful diagnostic information
            const diagnostics = [];
            diagnostics.push(`Required companies (${requiredCompanies.length}): ${requiredCompanies.join(', ')}`);
            diagnostics.push(`Available slots: ${maxSlots}`);
            diagnostics.push(`Required prestige goods: ${requiredPrestigeGoods.join(', ')}`);
            
            // Check if too many companies are required
            if (requiredCompanies.length > maxSlots) {
                diagnostics.push(`❌ Problem: ${requiredCompanies.length} required companies exceed ${maxSlots} available slots`);
            }
            
            // Check for prestige good conflicts
            const requiredCompanyPrestigeGoods = new Map();
            requiredCompanies.forEach(companyName => {
                const company = variants.find(v => v.baseCompanyName === companyName && !v.selectedCharter);
                if (company && company.prestigeGoods) {
                    company.prestigeGoods.forEach(pg => {
                        if (!requiredCompanyPrestigeGoods.has(pg)) {
                            requiredCompanyPrestigeGoods.set(pg, []);
                        }
                        requiredCompanyPrestigeGoods.get(pg).push(companyName);
                    });
                }
            });
            
            requiredCompanyPrestigeGoods.forEach((companies, prestigeGood) => {
                if (companies.length > 1) {
                    diagnostics.push(`❌ Prestige good conflict: ${prestigeGood} provided by multiple required companies: ${companies.join(', ')}`);
                }
            });
            
            const errorMessage = `Optimization is impossible with current constraints:\n\n${diagnostics.join('\n')}\n\nSuggestions:\n• Remove some required companies\n• Increase company slots\n• Check for prestige good conflicts`;
            
            throw new Error('LP infeasible - constraints cannot be satisfied');
        } else {
            console.error('YALPS solution:', solution);
            throw new Error(`YALPS failed: ${solution.status} - ${solution.error || 'Unknown error'}`);
        }

    } catch (error) {
        console.error('YALPS error:', error);
        console.error('Error details:', error.message);
        throw error;
    }
}

// Export for ES modules
export { solveIntegerLP, calculateIndividualScore };