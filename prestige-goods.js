// Prestige goods mapping - shared between index.html and tests
const prestigeGoodsMapping = {
    // Generic prestige goods
    'Quick-fire Artillery': 'Artillery',
    'Designer Clothes': 'Clothes',
    'Reserve Coffee': 'Coffee',
    'High-grade Explosives': 'Explosives',
    'Enriched Fertilizer': 'Fertilizer',
    'Select Fish': 'Fish',
    'Stylish Furniture': 'Furniture',
    'Fine Grain': 'Grain',
    'Gourmet Groceries': 'Groceries',
    'Prime Meat': 'Meat',
    'Swift Merchant Marine': 'Merchant Marine',
    'Pure Opium': 'Opium',
    'Craft Paper': 'Paper',
    'High-powered Small Arms': 'Small Arms',
    'Refined Steel': 'Steel',
    'Precision Tools': 'Tools',
    
    // Flavored prestige goods
    'Krupp Guns': 'Artillery',
    'Schneider Guns': 'Artillery',
    'Ford Automobiles': 'Automobiles',
    'Turin Automobiles': 'Automobiles',
    'German Aniline': 'Dye',
    'Schichau Engines': 'Engines',
    'Mit Afifi': 'Fabric',
    'Sea Island Cotton': 'Fabric',
    'Gros Michel Banana': 'Fruit',
    'Bentwood Furniture': 'Furniture',
    'Bohemian Crystal': 'Glass',
    'Rosewood': 'Hardwood',
    'Teak': 'Hardwood',
    'Oregrounds Iron': 'Iron',
    'Russia Iron': 'Iron',
    'Armstrong Ships': 'Ironclads',
    'Smirnoff Vodka': 'Liquor',
    'Haute Couture': 'Luxury Clothes',
    'English Upholstery': 'Luxury Furniture',
    'River Plate Beef': 'Meat',
    'Baku Oil': 'Oil',
    'Bengal Opium': 'Opium',
    'Washi Paper': 'Paper',
    'Canton Porcelain': 'Porcelain',
    'Meissen Porcelain': 'Porcelain',
    'Satsuma Ware': 'Porcelain',
    'Chapel Radios': 'Radios',
    'Radiola Radios': 'Radios',
    'Colt Revolvers': 'Small Arms',
    'Saint-Etienne Rifles': 'Small Arms',
    'Como Silk': 'Silk',
    'Suzhou Silk': 'Silk',
    'Tomioka Silk': 'Silk',
    'Clyde-Built Liners': 'Steamers',
    'Sheffield Steel': 'Steel',
    'Sicilian Sulfur': 'Sulfur',
    'Assam Tea': 'Tea',
    'China Tea': 'Tea',
    'Ericsson Apparatus': 'Telephones',
    'Turkish Tobacco': 'Tobacco',
    'Champagne': 'Wine'
};

// Get all unique base types
const prestigeGoodBaseTypes = [...new Set(Object.values(prestigeGoodsMapping))].sort();

// Helper function to get base type from prestige good
function getPrestigeGoodBaseType(prestigeGood) {
    return prestigeGoodsMapping[prestigeGood] || 'Unknown';
}

// Check if companies satisfy prestige good requirements
function checkPrestigeGoodRequirements(companies, requiredPrestigeGoods) {
    if (requiredPrestigeGoods.length === 0) {
        return true;
    }
    
    const providedPrestigeGoods = new Set();
    companies.forEach(company => {
        company.prestigeGoods.forEach(pg => {
            const baseType = getPrestigeGoodBaseType(pg);
            if (baseType) {
                providedPrestigeGoods.add(baseType);
            }
        });
    });
    
    return requiredPrestigeGoods.every(required => providedPrestigeGoods.has(required));
}

// Export for both Node.js (tests) and browser (index.html)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        prestigeGoodsMapping,
        prestigeGoodBaseTypes,
        getPrestigeGoodBaseType,
        checkPrestigeGoodRequirements
    };
} else {
    // Browser globals
    window.prestigeGoodsMapping = prestigeGoodsMapping;
    window.prestigeGoodBaseTypes = prestigeGoodBaseTypes;
    window.getPrestigeGoodBaseType = getPrestigeGoodBaseType;
    window.checkPrestigeGoodRequirements = checkPrestigeGoodRequirements;
}