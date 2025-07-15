// Prestige goods mapping - automatically generated from game data
// Generated from Victoria 3 game files - do not edit manually
// Regenerate using update_from_game_files.mjs

/**
 * Prestige goods mapping from display names to base types
 * Generated from game data on: 2025-07-15T04:55:44.540Z
 */
export const prestigeGoodsMapping = {
    "Fine Grain": "Grain",
    "Prime Meat": "Meat",
    "Pure Opium": "Opium",
    "Reserve Coffee": "Coffee",
    "Select Fish": "Fish",
    "Gourmet Groceries": "Groceries",
    "Craft Paper": "Paper",
    "Stylish Furniture": "Furniture",
    "Designer Clothes": "Clothes",
    "Refined Steel": "Steel",
    "Precision Tools": "Tools",
    "Enriched Fertilizer": "Fertilizer",
    "High-grade Explosives": "Explosives",
    "High-powered Small Arms": "Small Arms",
    "mit afifi": "Fabric",
    "Swift Merchant Marine": "Merchant Marine",
    "rosewood": "Hardwood",
    "bengal opium": "Opium",
    "turkish tobacco": "Tobacco",
    "canton porcelain": "Porcelain",
    "philips chapel radio": "Electronics",
    "ericsson apparatus": "Electronics",
    "swedish bar iron": "Steel",
    "Quick-fire Artillery": "Artillery",
    "schneider guns": "Artillery",
    "champagne": "Wine",
    "saint etienne rifles": "Small Arms",
    "krupp guns": "Artillery",
    "schichau engines": "Engines",
    "german aniline": "Dye",
    "armstrong ships": "Small Arms",
    "clyde built liners": "Merchant Marine",
    "sheffield steel": "Steel",
    "burmese teak": "Tea",
    "assam tea": "Tea",
    "turin automobiles": "Automobiles",
    "tomioka silk": "Clothes",
    "washi paper": "Paper",
    "bohemian crystal": "Glass",
    "river plate beef": "Meat",
    "meissen porcelain": "Porcelain",
    "suzhou silk": "Clothes",
    "haute couture": "Clothes",
    "sea island cotton": "Clothes",
    "colt revolvers": "Small Arms",
    "bentwood furniture": "Furniture",
    "satsuma ware": "Porcelain",
    "english upholstery": "Furniture",
    "china tea": "Tea",
    "sicilian sulfur": "Sulfur",
    "como silk": "Clothes",
    "smirnoff vodka": "Liquor",
    "baku oil": "Oil",
    "russia iron": "Steel",
    "gros michel banana": "Fruit",
    "radiola radios": "Electronics",
    "ford automobiles": "Automobiles"
};

/**
 * All unique base types for prestige goods
 */
export const prestigeGoodBaseTypes = [
    "Artillery",
    "Automobiles",
    "Clothes",
    "Coffee",
    "Dye",
    "Electronics",
    "Engines",
    "Explosives",
    "Fabric",
    "Fertilizer",
    "Fish",
    "Fruit",
    "Furniture",
    "Glass",
    "Grain",
    "Groceries",
    "Hardwood",
    "Liquor",
    "Meat",
    "Merchant Marine",
    "Oil",
    "Opium",
    "Paper",
    "Porcelain",
    "Small Arms",
    "Steel",
    "Sulfur",
    "Tea",
    "Tobacco",
    "Tools",
    "Wine"
];

/**
 * All unique prestige goods found in game data
 */
export const uniquePrestigeGoods = [
    "Craft Paper",
    "Designer Clothes",
    "Enriched Fertilizer",
    "Fine Grain",
    "Gourmet Groceries",
    "High-grade Explosives",
    "High-powered Small Arms",
    "Precision Tools",
    "Prime Meat",
    "Pure Opium",
    "Quick-fire Artillery",
    "Refined Steel",
    "Reserve Coffee",
    "Select Fish",
    "Stylish Furniture",
    "Swift Merchant Marine",
    "armstrong ships",
    "assam tea",
    "baku oil",
    "bengal opium",
    "bentwood furniture",
    "bohemian crystal",
    "burmese teak",
    "canton porcelain",
    "champagne",
    "china tea",
    "clyde built liners",
    "colt revolvers",
    "como silk",
    "english upholstery",
    "ericsson apparatus",
    "ford automobiles",
    "german aniline",
    "gros michel banana",
    "haute couture",
    "krupp guns",
    "meissen porcelain",
    "mit afifi",
    "philips chapel radio",
    "radiola radios",
    "river plate beef",
    "rosewood",
    "russia iron",
    "saint etienne rifles",
    "satsuma ware",
    "schichau engines",
    "schneider guns",
    "sea island cotton",
    "sheffield steel",
    "sicilian sulfur",
    "smirnoff vodka",
    "suzhou silk",
    "swedish bar iron",
    "tomioka silk",
    "turin automobiles",
    "turkish tobacco",
    "washi paper"
];

/**
 * Get base type from prestige good name
 * @param {string} prestigeGood - Prestige good name
 * @returns {string} - Base type
 */
export function getPrestigeGoodBaseType(prestigeGood) {
    return prestigeGoodsMapping[prestigeGood] || 'Unknown';
}

/**
 * Check if companies satisfy prestige good requirements
 * @param {Array} companies - Array of company objects
 * @param {Array} requiredPrestigeGoods - Array of required prestige good base types
 * @returns {boolean} - True if all requirements are met
 */
export function checkPrestigeGoodRequirements(companies, requiredPrestigeGoods) {
    if (requiredPrestigeGoods.length === 0) {
        return true;
    }
    
    const providedPrestigeGoods = new Set();
    companies.forEach(company => {
        if (company.prestigeGoods) {
            company.prestigeGoods.forEach(pg => {
                const baseType = getPrestigeGoodBaseType(pg);
                if (baseType) {
                    providedPrestigeGoods.add(baseType);
                }
            });
        }
    });
    
    return requiredPrestigeGoods.every(required => providedPrestigeGoods.has(required));
}

// Generated on: 2025-07-15T04:55:44.540Z
// Total unique prestige goods: 57
// Total base types: 31
