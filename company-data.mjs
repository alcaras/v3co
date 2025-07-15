// Victoria 3 Company Optimizer - Company Data Management Module
// Extracted from index.html for better modularity and testing

/**
 * Load company data from JSON file
 * @returns {Promise<Object>} Object containing company data arrays
 */
async function loadCompanyData() {
    try {
        console.log('Loading company data...');
        const response = await fetch('companies_extracted.json');
        const data = await response.json();
        
        const companies = {
            basic: data.basicCompanies || [],
            flavored: data.flavoredCompanies || [],
            canal: data.flavoredCompanies.filter(c => c.special === 'canal') || [],
            mandate: []
        };
        
        console.log(`Companies loaded: ${companies.basic.length} basic, ${companies.flavored.length} flavored, ${companies.canal.length} canal`);
        
        // Remove canal companies from flavored list
        companies.flavored = companies.flavored.filter(c => c.special !== 'canal');
        
        // Find United Construction Conglomerate for display
        companies.mandate = companies.basic.filter(c => c.name === 'United Construction Conglomerate');
        
        // Remove United Construction Conglomerate from basic companies to avoid duplication
        companies.basic = companies.basic.filter(c => c.name !== 'United Construction Conglomerate');
        
        // All companies for optimization (basic + flavored + canal)
        const allCompanies = [...companies.basic, ...companies.flavored, ...companies.canal, ...companies.mandate];
        
        // Display companies (basic first, then mandate, then flavored, then canal)
        const visibleCompanies = [...companies.basic, ...companies.mandate, ...companies.flavored, ...companies.canal];
        
        // Extract all unique buildings from displayed companies
        const buildingSet = new Set();
        visibleCompanies.forEach(company => {
            company.buildings.forEach(building => buildingSet.add(building));
        });
        const allBuildings = Array.from(buildingSet).sort();
        
        return {
            companies,
            allCompanies,
            visibleCompanies,
            allBuildings
        };
    } catch (error) {
        console.error('Error loading company data:', error);
        // Fallback to sample data if JSON loading fails
        return loadSampleData();
    }
}

/**
 * Load fallback sample data
 * @returns {Object} Object containing empty company data arrays
 */
function loadSampleData() {
    console.log('Loading fallback sample data...');
    
    const companies = {
        basic: [],
        flavored: [],
        canal: [],
        mandate: []
    };
    
    const allCompanies = [];
    const visibleCompanies = [];
    
    // Extract all unique buildings from companies (empty in sample data)
    const buildingSet = new Set();
    allCompanies.forEach(company => {
        company.buildings.forEach(building => buildingSet.add(building));
    });
    const allBuildings = Array.from(buildingSet).sort();
    
    return {
        companies,
        allCompanies,
        visibleCompanies,
        allBuildings
    };
}

/**
 * Expand companies with charter variants
 * @param {Array} companies - Array of company objects
 * @param {Array} selectedBuildings - Array of selected building names (for charter filtering)
 * @returns {Array} Array of expanded company variants
 */
function expandCompaniesWithCharters(companies, selectedBuildings = []) {
    const expandedCompanies = [];
    
    companies.forEach(company => {
        // Always add the base company (no charter)
        const baseCompany = {
            ...company,
            buildings: [...company.buildings],
            variantType: 'base',
            selectedCharter: null,
            baseCompanyName: company.name
        };
        expandedCompanies.push(baseCompany);
        
        // Add variant for each charter
        if (company.industryCharters && company.industryCharters.length > 0) {
            company.industryCharters.forEach(charter => {
                // Always create charter variants - the LP solver will decide if they're beneficial
                const charterVariant = {
                    ...company,
                    name: `${company.name} + ${charter}`,
                    buildings: [...company.buildings, charter],
                    variantType: 'charter',
                    selectedCharter: charter,
                    baseCompanyName: company.name
                };
                expandedCompanies.push(charterVariant);
            });
        }
    });
    
    // Removed verbose expansion logging
    
    return expandedCompanies;
}

/**
 * Get default building selection
 * @returns {Array} Array of default building names
 */
function getDefaultBuildings() {
    return [
        'Coal Mine', 'Iron Mine', 'Logging Camp', 'Oil Rig', 'Rubber Plantation',
        'Automotive Industries', 'Explosives Factory', 'Glassworks', 'Motor Industries', 'Paper Mill', 'Steel Mills', 'Tooling Workshops',
        'Port', 'Railway', 'Trade Center', 'Power Plant'
    ];
}

/**
 * Get default prestige goods requirements
 * @returns {Array} Array of default required prestige good base types
 */
function getDefaultPrestigeGoods() {
    return ['Tools']; // Tools is mandatory by default
}

/**
 * Get building categories for UI display
 * @returns {Object} Object mapping category names to building arrays
 */
function getBuildingCategories() {
    return {
        'Agriculture': ['Maize Farm', 'Millet Farm', 'Rice Farm', 'Rye Farm', 'Wheat Farm', 'Vineyard'],
        'Extraction': ['Coal Mine', 'Fishing Wharf', 'Gold Mine', 'Iron Mine', 'Lead Mine', 'Logging Camp', 'Oil Rig', 'Rubber Plantation', 'Sulfur Mine', 'Whaling Station'],
        'Plantations': ['Banana Plantation', 'Coffee Plantation', 'Cotton Plantation', 'Dye Plantation', 'Opium Plantation', 'Silk Plantation', 'Sugar Plantation', 'Tea Plantation', 'Tobacco Plantation'],
        'Ranches': ['Livestock Ranch'],
        'Manufacturing Industries': ['Arms Industries', 'Artillery Foundries', 'Automotive Industries', 'Electrics Industries', 'Explosives Factory', 'Fertilizer Plant', 'Food Industry', 'Furniture Manufacturies', 'Glassworks', 'Military Shipyards', 'Motor Industries', 'Munition Plant', 'Paper Mill', 'Shipyards', 'Steel Mills', 'Synthetics Plant', 'Textile Mill', 'Tooling Workshops'],
        'Infrastructure': ['Port', 'Railway', 'Trade Center'],
        'Power Plants': ['Power Plant']
    };
}

/**
 * Filter companies by region
 * @param {Array} companies - Array of company objects
 * @param {string} region - Region name to filter by
 * @returns {Array} Filtered array of companies
 */
function filterCompaniesByRegion(companies, region) {
    return companies.filter(company => company.region === region);
}

/**
 * Search companies by name
 * @param {Array} companies - Array of company objects
 * @param {string} searchTerm - Search term
 * @returns {Array} Filtered array of companies
 */
function searchCompanies(companies, searchTerm) {
    if (!searchTerm) return companies;
    
    const lowerSearchTerm = searchTerm.toLowerCase();
    return companies.filter(company => 
        company.name.toLowerCase().includes(lowerSearchTerm) ||
        company.buildings.some(building => building.toLowerCase().includes(lowerSearchTerm)) ||
        (company.prestigeGoods && company.prestigeGoods.some(pg => pg.toLowerCase().includes(lowerSearchTerm)))
    );
}

/**
 * Get companies that provide specific buildings
 * @param {Array} companies - Array of company objects
 * @param {Array} buildings - Array of building names
 * @returns {Array} Filtered array of companies
 */
function getCompaniesWithBuildings(companies, buildings) {
    return companies.filter(company => 
        buildings.some(building => company.buildings.includes(building))
    );
}

/**
 * Get companies that provide specific prestige goods
 * @param {Array} companies - Array of company objects
 * @param {Array} prestigeGoods - Array of prestige good names
 * @returns {Array} Filtered array of companies
 */
function getCompaniesWithPrestigeGoods(companies, prestigeGoods) {
    return companies.filter(company => 
        company.prestigeGoods && prestigeGoods.some(pg => company.prestigeGoods.includes(pg))
    );
}

// Export all functions
export {
    loadCompanyData,
    loadSampleData,
    expandCompaniesWithCharters,
    getDefaultBuildings,
    getDefaultPrestigeGoods,
    getBuildingCategories,
    filterCompaniesByRegion,
    searchCompanies,
    getCompaniesWithBuildings,
    getCompaniesWithPrestigeGoods
};