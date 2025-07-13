// Victoria 3 Company Optimizer - Scoring and Validation Module
// Extracted from index.html for better modularity and testing

// Load prestige goods mapping
import { prestigeGoodsMapping } from './prestige-goods.mjs';

/**
 * Calculate score for a combination of companies
 * @param {Array} companies - Array of company objects
 * @param {Array} selectedBuildings - Array of selected building names
 * @param {Array} priorityBuildings - Array of priority building names
 * @returns {number} Score for the company combination
 */
function calculateScore(companies, selectedBuildings, priorityBuildings) {
    // Count building coverage from company buildings
    const selectedBuildingTypes = new Set();
    let totalSelectedBuildings = 0;
    const nonSelectedBuildingTypes = new Set();
    
    companies.forEach(company => {
        company.buildings.forEach(building => {
            if (selectedBuildings.includes(building)) {
                selectedBuildingTypes.add(building);
                totalSelectedBuildings++;
            } else {
                // Track non-selected buildings for 0.01 point bonus
                nonSelectedBuildingTypes.add(building);
            }
        });
    });
    
    // Charter selection: Simple approach - take first useful charter if it provides new coverage
    const takenCharters = [];
    const charterCounts = new Map();
    
    companies.forEach(company => {
        if (company.industryCharters && company.industryCharters.length > 0) {
            // Only take charter if it's for a selected building AND not already covered by buildings
            const charter = company.industryCharters[0]; // Take first charter
            if (selectedBuildings.includes(charter) && !selectedBuildingTypes.has(charter)) {
                takenCharters.push(charter);
                charterCounts.set(charter, (charterCounts.get(charter) || 0) + 1);
            }
        }
    });
    
    // Calculate charter contribution and penalties
    const industryCharters = new Set();
    let redundantCharterPenalty = 0;
    
    charterCounts.forEach((count, charter) => {
        if (selectedBuildingTypes.has(charter)) {
            // Charter is redundant with buildings - penalty
            redundantCharterPenalty += count * 2.0;
        } else if (count > 1) {
            // Multiple companies providing same charter - penalty for extras
            industryCharters.add(charter);
            redundantCharterPenalty += (count - 1) * 3.0;
        } else {
            // Unique useful charter
            industryCharters.add(charter);
        }
    });
    
    const selectedOverlaps = totalSelectedBuildings - selectedBuildingTypes.size;
    const prestigeGoods = companies.reduce((count, company) => 
        count + company.prestigeGoods.length, 0);
    
    // Calculate priority building bonus
    let priorityScore = 0;
    selectedBuildingTypes.forEach(building => {
        if (priorityBuildings.includes(building)) {
            priorityScore += 2;
        }
    });
    
    // Add priority bonus for taken charters
    industryCharters.forEach(charter => {
        if (priorityBuildings.includes(charter)) {
            priorityScore += 2;
        }
    });
    
    // Score: buildings + charters + priority bonus + prestige + non-selected buildings - overlaps - charter penalties
    return selectedBuildingTypes.size + industryCharters.size + priorityScore + (prestigeGoods * 0.1) + (nonSelectedBuildingTypes.size * 0.01) - (selectedOverlaps * 0.2) - redundantCharterPenalty;
}

/**
 * Check if companies satisfy prestige good requirements
 * @param {Array} companies - Array of company objects
 * @param {Array} requiredPrestigeGoods - Array of required prestige good base types
 * @returns {boolean} True if requirements are satisfied
 */
function checkPrestigeGoodRequirements(companies, requiredPrestigeGoods) {
    if (requiredPrestigeGoods.length === 0) {
        return true; // No requirements, always satisfied
    }
    
    // Collect all prestige goods from the companies
    const providedPrestigeGoods = new Set();
    companies.forEach(company => {
        company.prestigeGoods.forEach(prestigeGood => {
            const baseType = prestigeGoodsMapping[prestigeGood];
            if (baseType) {
                providedPrestigeGoods.add(baseType);
            }
        });
    });
    
    // Check if all required prestige goods are provided
    return requiredPrestigeGoods.every(required => providedPrestigeGoods.has(required));
}

/**
 * Alternative scoring function for company combinations
 * @param {Array} companies - Array of company objects
 * @param {Array} selectedBuildings - Array of selected building names
 * @param {Array} priorityBuildings - Array of priority building names
 * @returns {number} Score for the company combination
 */
function calculateCombinationScore(companies, selectedBuildings, priorityBuildings) {
    const coveredBuildings = new Set();
    const usedPrestigeGoods = new Set();
    const usedCharters = new Map();
    let totalScore = 0;
    
    // First pass: collect all buildings from base companies  
    for (const company of companies) {
        const baseBuildings = company.buildings.filter(b => b !== company.selectedCharter);
        baseBuildings.forEach(b => coveredBuildings.add(b));
        
        // Add prestige goods
        if (company.prestigeGoods) {
            company.prestigeGoods.forEach(pg => usedPrestigeGoods.add(pg));
        }
    }
    
    // Score for unique building coverage
    const selectedCovered = [...coveredBuildings].filter(b => selectedBuildings.includes(b));
    const priorityCovered = [...coveredBuildings].filter(b => priorityBuildings.includes(b));
    const nonSelectedCovered = [...coveredBuildings].filter(b => !selectedBuildings.includes(b));
    
    totalScore += selectedCovered.length * 10;
    totalScore += priorityCovered.length * 20;
    totalScore += nonSelectedCovered.length * 0.1;
    totalScore += usedPrestigeGoods.size * 1;
    
    // Evaluate charters - heavily penalize overlaps
    for (const company of companies) {
        if (company.selectedCharter) {
            const charter = company.selectedCharter;
            const currentUses = usedCharters.get(charter) || 0;
            usedCharters.set(charter, currentUses + 1);
            
            totalScore -= 0.01; // Base charter cost
            totalScore -= currentUses * 50; // Strong overlap penalty
            
            // Charter value only if provides new coverage
            if (selectedBuildings.includes(charter)) {
                if (!coveredBuildings.has(charter)) {
                    // Charter provides new coverage
                    if (priorityBuildings.includes(charter)) {
                        totalScore += 20; // Priority building bonus
                    } else {
                        totalScore += 10; // Regular building bonus
                    }
                    coveredBuildings.add(charter);
                } else {
                    // Charter provides no new coverage - heavily penalize
                    totalScore -= 100;
                }
            }
        }
    }
    
    return totalScore;
}

/**
 * Check if a variant can be added to the current selection
 * @param {Object} variant - Company variant to check
 * @param {Array} currentSelection - Current selection of variants
 * @returns {boolean} True if variant can be added
 */
function isValidAddition(variant, currentSelection) {
    // Check prestige good conflicts
    const usedPrestigeGoods = new Set();
    currentSelection.forEach(v => {
        if (v.prestigeGoods) {
            v.prestigeGoods.forEach(pg => usedPrestigeGoods.add(pg));
        }
    });
    
    if (variant.prestigeGoods) {
        for (const pg of variant.prestigeGoods) {
            if (usedPrestigeGoods.has(pg)) {
                return false;
            }
        }
    }
    
    // Check company conflicts (only one variant per base company)
    return !currentSelection.some(v => v.baseCompanyName === variant.baseCompanyName);
}

/**
 * Validate if a solution is valid
 * @param {Array} solution - Array of company objects
 * @param {Array} requiredPrestigeGoods - Array of required prestige good base types
 * @returns {boolean} True if solution is valid
 */
function isValidSolution(solution, requiredPrestigeGoods) {
    // Check prestige good conflicts
    const usedPrestigeGoods = new Set();
    for (const company of solution) {
        if (company.prestigeGoods) {
            for (const pg of company.prestigeGoods) {
                if (usedPrestigeGoods.has(pg)) {
                    return false; // Duplicate prestige good
                }
                usedPrestigeGoods.add(pg);
            }
        }
    }
    
    // Check required prestige goods are satisfied
    if (requiredPrestigeGoods.length > 0) {
        const providedBaseTypes = new Set();
        for (const company of solution) {
            if (company.prestigeGoods) {
                for (const pg of company.prestigeGoods) {
                    const baseType = prestigeGoodsMapping[pg];
                    if (baseType) {
                        providedBaseTypes.add(baseType);
                    }
                }
            }
        }
        
        for (const requiredType of requiredPrestigeGoods) {
            if (!providedBaseTypes.has(requiredType)) {
                return false; // Missing required prestige good
            }
        }
    }
    
    return true;
}

// Export all functions
export {
    calculateScore,
    checkPrestigeGoodRequirements,
    calculateCombinationScore,
    isValidAddition,
    isValidSolution
};