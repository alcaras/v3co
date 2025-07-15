// Victoria 3 Game Data Importer
// Reads company and building data directly from game files to create authoritative JSON

import { readFileSync, writeFileSync } from 'fs';
import { join } from 'path';
import { prestigeGoodToDisplayName, companyToDisplayName } from './game-localizations.mjs';

// Console logging utilities for better debugging
const log = {
    info: (message, data = null) => {
        console.log(`[INFO] ${message}`, data ? data : '');
    },
    debug: (message, data = null) => {
        console.log(`[DEBUG] ${message}`, data ? data : '');
    },
    warn: (message, data = null) => {
        console.warn(`[WARN] ${message}`, data ? data : '');
    },
    error: (message, data = null) => {
        console.error(`[ERROR] ${message}`, data ? data : '');
    }
};

// Removed dynamic localization loading - now using static mappings from game-localizations.mjs

/**
 * Parse a Paradox script file and extract key-value pairs
 * @param {string} content - File content
 * @returns {Object} - Parsed data structure
 */
function parseParadoxScript(content) {
    const result = {};
    
    // Remove BOM and comments
    content = content.replace(/^\uFEFF/, ''); // Remove BOM
    content = content.replace(/#.*$/gm, ''); // Remove comments
    
    // Find company definitions with proper brace matching
    const lines = content.split('\n');
    let currentCompany = null;
    let braceDepth = 0;
    let companyBody = '';
    
    for (let i = 0; i < lines.length; i++) {
        const line = lines[i].trim();
        
        // Skip empty lines and comments
        if (!line || line.startsWith('#') || line.startsWith('//')) {
            continue;
        }
        
        // Check if this is a company definition start
        const companyMatch = line.match(/^(\w+)\s*=\s*\{/);
        if (companyMatch && braceDepth === 0) {
            currentCompany = companyMatch[1];
            companyBody = '';
            braceDepth = 1;
            continue;
        }
        
        // If we're inside a company definition
        if (currentCompany && braceDepth > 0) {
            // Count braces to track depth
            const openBraces = (line.match(/\{/g) || []).length;
            const closeBraces = (line.match(/\}/g) || []).length;
            braceDepth += openBraces - closeBraces;
            
            // Add line to company body
            companyBody += line + '\n';
            
            // If we've closed all braces, parse the company
            if (braceDepth === 0) {
                result[currentCompany] = parseCompanyBody(companyBody);
                currentCompany = null;
                companyBody = '';
            }
        }
    }
    
    return result;
}

/**
 * Parse the body of a company definition
 * @param {string} body - Company body content
 * @returns {Object} - Company data
 */
function parseCompanyBody(body) {
    const company = {};
    
    // Extract building_types using more robust parsing
    const buildingTypesMatch = extractSection(body, 'building_types');
    if (buildingTypesMatch) {
        company.building_types = extractList(buildingTypesMatch);
    }
    
    // Extract extension_building_types (charters)
    const extensionMatch = extractSection(body, 'extension_building_types');
    if (extensionMatch) {
        company.extension_building_types = extractList(extensionMatch);
    }
    
    // Extract possible_prestige_goods
    const prestigeMatch = extractSection(body, 'possible_prestige_goods');
    if (prestigeMatch) {
        company.possible_prestige_goods = extractList(prestigeMatch);
    }
    
    // Extract flavored_company flag
    const flavoredMatch = body.match(/flavored_company\s*=\s*(\w+)/);
    if (flavoredMatch) {
        company.flavored_company = flavoredMatch[1] === 'yes';
    }
    
    // Extract prosperity_modifier for bonus description
    const prosperityMatch = extractSection(body, 'prosperity_modifier');
    if (prosperityMatch) {
        company.prosperity_modifier = prosperityMatch.trim();
    }
    
    // Extract possible conditions for requirements
    const possibleMatch = extractSection(body, 'possible');
    if (possibleMatch) {
        company.possible_conditions = possibleMatch.trim();
    }
    
    return company;
}

/**
 * Extract a section from the company body (handles nested braces)
 * @param {string} body - Company body content
 * @param {string} sectionName - Name of the section to extract
 * @returns {string|null} - Section content or null if not found
 */
function extractSection(body, sectionName) {
    const lines = body.split('\n');
    let inSection = false;
    let braceDepth = 0;
    let sectionContent = '';
    
    for (const line of lines) {
        const trimmed = line.trim();
        
        // Check if this line starts the section
        if (trimmed.startsWith(sectionName + ' =')) {
            inSection = true;
            braceDepth = 0;
            sectionContent = '';
            
            // Count braces in the starting line
            const openBraces = (trimmed.match(/\{/g) || []).length;
            const closeBraces = (trimmed.match(/\}/g) || []).length;
            braceDepth += openBraces - closeBraces;
            
            // If section ends on same line, extract content
            if (braceDepth === 0 && openBraces > 0) {
                const match = trimmed.match(new RegExp(`${sectionName}\\s*=\\s*\\{([^}]*)\\}`));
                return match ? match[1] : '';
            }
            
            continue;
        }
        
        // If we're inside the section
        if (inSection) {
            // Count braces
            const openBraces = (trimmed.match(/\{/g) || []).length;
            const closeBraces = (trimmed.match(/\}/g) || []).length;
            braceDepth += openBraces - closeBraces;
            
            // Add line to content (but don't include the closing brace line)
            if (braceDepth > 0) {
                sectionContent += line + '\n';
            }
            
            // If we've closed all braces, we're done
            if (braceDepth === 0) {
                return sectionContent;
            }
        }
    }
    
    return null;
}

/**
 * Extract a list of items from a Paradox script list
 * @param {string} listContent - Content inside braces
 * @returns {Array} - Array of items
 */
function extractList(listContent) {
    return listContent
        .split(/\s+/)
        .map(item => item.trim())
        .filter(item => item && !item.startsWith('//') && !item.startsWith('#'))
        .map(item => item.replace(/^building_/, '')); // Remove building_ prefix
}

/**
 * Convert building internal name to display name
 * @param {string} buildingName - Internal building name
 * @returns {string} - Display name
 */
function buildingToDisplayName(buildingName) {
    const displayNameMap = {
        'food_industry': 'Food Industry',
        'textile_mills': 'Textile Mills',
        'furniture_manufacturies': 'Furniture Manufacturies',
        'glassworks': 'Glassworks',
        'tooling_workshops': 'Tooling Workshops',
        'paper_mills': 'Paper Mills',
        'chemical_plants': 'Chemical Plants',
        'explosives_factory': 'Explosives Factory',
        'synthetics_plants': 'Synthetics Plants',
        'steel_mills': 'Steel Mills',
        'motor_industry': 'Motor Industries',
        'shipyards': 'Shipyards',
        'military_shipyards': 'Military Shipyards',
        'automotive_industry': 'Automotive Industries',
        'electrics_industry': 'Electrics Industries',
        'arms_industry': 'Arms Industries',
        'artillery_foundries': 'Artillery Foundries',
        'munition_plants': 'Munition Plants',
        'wheat_farm': 'Wheat Farm',
        'rye_farm': 'Rye Farm',
        'rice_farm': 'Rice Farm',
        'millet_farm': 'Millet Farm',
        'maize_farm': 'Maize Farm',
        'livestock_ranch': 'Livestock Ranch',
        'vineyard_plantation': 'Vineyard',
        'iron_mine': 'Iron Mine',
        'coal_mine': 'Coal Mine',
        'lead_mine': 'Lead Mine',
        'sulfur_mine': 'Sulfur Mine',
        'gold_mine': 'Gold Mine',
        'coffee_plantation': 'Coffee Plantation',
        'cotton_plantation': 'Cotton Plantation',
        'dye_plantation': 'Dye Plantation',
        'opium_plantation': 'Opium Plantation',
        'tea_plantation': 'Tea Plantation',
        'tobacco_plantation': 'Tobacco Plantation',
        'sugar_plantation': 'Sugar Plantation',
        'banana_plantation': 'Banana Plantation',
        'silk_plantation': 'Silk Plantation',
        'rubber_plantation': 'Rubber Plantation',
        'port': 'Port',
        'railway': 'Railway',
        'trade_center': 'Trade Center',
        'power_plant': 'Power Plant',
        'logging_camp': 'Logging Camp',
        'oil_rig': 'Oil Rig',
        'fishing_wharf': 'Fishing Wharf',
        'whaling_station': 'Whaling Station'
    };
    
    return displayNameMap[buildingName] || buildingName.split('_').map(word => 
        word.charAt(0).toUpperCase() + word.slice(1)
    ).join(' ');
}

// Remove manual mapping - now using English localization files


/**
 * Convert requirements to human-readable description
 * @param {string} requirements - Raw requirements
 * @returns {string} - Human-readable requirements
 */
function requirementsToDisplayName(requirements) {
    if (!requirements) return '';
    
    // This is complex to parse fully, so for now return a simplified version
    // In a full implementation, we'd parse the Paradox script conditions
    return requirements
        .replace(/building_(\w+)/g, (match, building) => buildingToDisplayName(building))
        .replace(/is_building_type = /g, '')
        .replace(/level >= (\d+)/g, 'level $1 or higher')
        .replace(/any_scope_state/g, 'Owns')
        .replace(/any_scope_building/g, '')
        .replace(/\s+/g, ' ')
        .trim();
}

// Remove manual company mapping - now using English localization files

/**
 * Import all company data from game files
 * @param {string} gameDir - Path to game directory
 * @returns {Object} - Imported company data
 */
function importGameData(gameDir) {
    const companyTypesDir = join(gameDir, 'company_types');
    const result = {
        basicCompanies: [],
        flavoredCompanies: []
    };
    
    log.info('Starting game data import...');
    log.info('Importing basic companies...');
    
    // Import basic companies
    const basicCompaniesFile = join(companyTypesDir, '99_basic_companies.txt');
    const basicContent = readFileSync(basicCompaniesFile, 'utf8');
    const basicCompanies = parseParadoxScript(basicContent);
    
    for (const [companyId, companyData] of Object.entries(basicCompanies)) {
        // Convert basic company ID to "Basic X" format
        const basicName = companyId.replace(/^company_basic_/, '').replace(/_/g, ' ').split(' ').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ');
        const company = {
            name: `Basic ${basicName}`,
            buildings: companyData.building_types?.map(buildingToDisplayName) || [],
            industryCharters: companyData.extension_building_types?.map(buildingToDisplayName) || [],
            prestigeGoods: companyData.possible_prestige_goods?.map(prestigeGoodToDisplayName) || [],
            prosperityBonus: companyData.prosperity_modifier || '',
            requirements: requirementsToDisplayName(companyData.possible_conditions),
            region: null,
            country: null,
            special: null
        };
        
        result.basicCompanies.push(company);
    }
    
    log.info(`Imported ${result.basicCompanies.length} basic companies`);
    
    // Import flavored companies from all regional files
    const flavoredFiles = [
        '00_companies_africa.txt',
        '00_companies_americas.txt', 
        '00_companies_asia.txt',
        '00_companies_austria_hungary.txt',
        '00_companies_china.txt',
        '00_companies_cots.txt',
        '00_companies_europe.txt',
        '00_companies_france.txt',
        '00_companies_germany.txt',
        '00_companies_great_britain.txt',
        '00_companies_ip2.txt',
        '00_companies_italy.txt',
        '00_companies_japan.txt',
        '00_companies_mp1.txt',
        '00_companies_russia.txt',
        '00_companies_soi.txt',
        '00_companies_usa.txt'
    ];
    
    log.info('Importing flavored companies...');
    
    for (const filename of flavoredFiles) {
        const filepath = join(companyTypesDir, filename);
        try {
            const content = readFileSync(filepath, 'utf8');
            const companies = parseParadoxScript(content);
            
            for (const [companyId, companyData] of Object.entries(companies)) {
                const company = {
                    name: companyToDisplayName(companyId),
                    buildings: companyData.building_types?.map(buildingToDisplayName) || [],
                    industryCharters: companyData.extension_building_types?.map(buildingToDisplayName) || [],
                    prestigeGoods: companyData.possible_prestige_goods?.map(prestigeGoodToDisplayName) || [],
                    prosperityBonus: companyData.prosperity_modifier || '',
                    requirements: requirementsToDisplayName(companyData.possible_conditions),
                    region: extractRegionFromFilename(filename),
                    country: null, // Would need more complex parsing to extract country
                    special: extractSpecialFromCompany(companyId, companyData)
                };
                
                result.flavoredCompanies.push(company);
            }
            
            log.debug(`Imported ${Object.keys(companies).length} companies from ${filename}`);
        } catch (error) {
            log.warn(`Could not read ${filename}: ${error.message}`);
        }
    }
    
    log.info(`Imported ${result.flavoredCompanies.length} flavored companies`);
    log.info(`Total companies imported: ${result.basicCompanies.length + result.flavoredCompanies.length}`);
    
    return result;
}

/**
 * Extract region from filename
 * @param {string} filename - Company file name
 * @returns {string|null} - Region name
 */
function extractRegionFromFilename(filename) {
    const regionMap = {
        'africa': 'Africa',
        'americas': 'Americas',
        'asia': 'Asia',
        'europe': 'Europe',
        'usa': 'Americas',
        'great_britain': 'Europe',
        'france': 'Europe',
        'germany': 'Europe',
        'austria_hungary': 'Europe',
        'italy': 'Europe',
        'russia': 'Europe',
        'china': 'Asia',
        'japan': 'Asia'
    };
    
    for (const [key, region] of Object.entries(regionMap)) {
        if (filename.includes(key)) {
            return region;
        }
    }
    
    return null;
}

/**
 * Extract special flags from company data
 * @param {string} companyId - Company ID
 * @param {Object} companyData - Company data
 * @returns {string|null} - Special flag
 */
function extractSpecialFromCompany(companyId, companyData) {
    // Check for canal companies
    if (companyId.includes('canal') || companyId.includes('panama') || companyId.includes('suez')) {
        return 'canal';
    }
    
    return null;
}

// Main execution
if (import.meta.url === `file://${process.argv[1]}`) {
    const gameDir = process.argv[2] || './game';
    const outputFile = process.argv[3] || 'companies_game_imported.json';
    
    log.info('Starting Victoria 3 game data import...');
    log.info(`Game directory: ${gameDir}`);
    log.info(`Output file: ${outputFile}`);
    
    try {
        const gameData = importGameData(gameDir);
        
        writeFileSync(outputFile, JSON.stringify(gameData, null, 2));
        log.info(`Successfully wrote ${outputFile}`);
        log.info(`Final counts: ${gameData.basicCompanies.length} basic, ${gameData.flavoredCompanies.length} flavored`);
    } catch (error) {
        log.error('Import failed:', error);
        process.exit(1);
    }
}

export { importGameData, parseParadoxScript };