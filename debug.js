const fs = require('fs');
const companiesData = JSON.parse(fs.readFileSync('companies_extracted.json', 'utf8'));

// Set up the global variables that the script expects
let companies = {
    basic: companiesData.basicCompanies || [],
    flavored: companiesData.flavoredCompanies || [],
    canal: []
};

// Find canal companies
const allRaw = [...companies.basic, ...companies.flavored];
companies.canal = allRaw.filter(c => c.special === 'canal');
companies.flavored = companies.flavored.filter(c => c.special !== 'canal');

let selectedBuildings = ['Tooling Workshops', 'Motor Industries', 'Automotive Industries', 'Explosives Factory', 'Railway', 'Oil Rig'];
let priorityBuildings = ['Tooling Workshops', 'Motor Industries', 'Automotive Industries', 'Explosives Factory', 'Railway'];
let allCompanies = [...companies.basic, ...companies.flavored, ...companies.canal];
let requiredPrestigeGoods = ['Tools'];

// Prestige goods mapping
const prestigeGoodsMapping = {
    'Fine Grain': 'Food', 'Prime Meat': 'Food', 'River Plate Beef': 'Food', 'Select Fish': 'Food',
    'Gourmet Groceries': 'Food', 'Gros Michel Banana': 'Food', 'Mit Afifi': 'Food',
    'Reserve Coffee': 'Beverages', 'China Tea': 'Beverages', 'Assam Tea': 'Beverages',
    'Champagne': 'Beverages', 'Smirnoff Vodka': 'Beverages', 'Turkish Tobacco': 'Beverages',
    'Designer Clothes': 'Textiles', 'Haute Couture': 'Textiles', 'Suzhou Silk': 'Textiles',
    'Tomioka Silk': 'Textiles', 'Como Silk': 'Textiles', 'Sea Island Cotton': 'Textiles',
    'Craft Paper': 'Paper', 'Washi Paper': 'Paper',
    'Stylish Furniture': 'Furniture', 'Bentwood Furniture': 'Furniture', 'English Upholstery': 'Furniture',
    'Refined Steel': 'Steel', 'Sheffield Steel': 'Steel', 'Russia Iron': 'Steel', 'Oregrounds Iron': 'Steel',
    'Precision Tools': 'Tools',
    'High-powered Small Arms': 'Weapons', 'Colt Revolvers': 'Weapons', 'Saint-Etienne Rifles': 'Weapons',
    'Krupp Guns': 'Weapons', 'Schneider Guns': 'Weapons', 'Quick-fire Artillery': 'Weapons',
    'Canton Porcelain': 'Ceramics', 'Meissen Porcelain': 'Ceramics', 'Satsuma Ware': 'Ceramics', 'Bohemian Crystal': 'Ceramics',
    'Rosewood': 'Wood', 'Teak': 'Wood',
    'Pure Opium': 'Chemicals', 'Bengal Opium': 'Chemicals', 'German Aniline': 'Chemicals',
    'Sicilian Sulfur': 'Chemicals', 'Baku Oil': 'Chemicals', 'High-grade Explosives': 'Chemicals', 'Enriched Fertilizer': 'Chemicals',
    'Swift Merchant Marine': 'Transportation', 'Clyde-Built Liners': 'Transportation', 'Armstrong Ships': 'Transportation',
    'Ford Automobiles': 'Transportation', 'Turin Automobiles': 'Transportation',
    'Radiola Radios': 'Electronics', 'Chapel Radios': 'Electronics', 'Ericsson Apparatus': 'Electronics',
    'Schichau Engines': 'Engines'
};

// Scoring function from the original script
function calculateScore(companies) {
    // Building coverage (selected buildings only)
    const selectedBuildingTypes = new Set();
    let totalSelectedBuildings = 0;
    companies.forEach(company => {
        company.buildings.forEach(building => {
            if (selectedBuildings.includes(building)) {
                selectedBuildingTypes.add(building);
                totalSelectedBuildings++;
            }
        });
    });

    // Industry charters logic: only take charter if it's for a selected building AND not already covered by buildings
    const industryCharters = [];
    const charterCounts = new Map();
    companies.forEach(company => {
        if (company.industryCharters && company.industryCharters.length > 0) {
            const charter = company.industryCharters[0]; // Take first charter
            if (selectedBuildings.includes(charter) && !selectedBuildingTypes.has(charter)) {
                industryCharters.push(charter);
                charterCounts.set(charter, (charterCounts.get(charter) || 0) + 1);
                selectedBuildingTypes.add(charter);
                totalSelectedBuildings++;
            }
        }
    });

    // Priority building analysis
    let priorityFromBuildings = 0;
    let priorityFromCharters = 0;
    selectedBuildingTypes.forEach(building => {
        if (priorityBuildings.includes(building)) {
            const fromBuildings = companies.filter(c => c.buildings.includes(building)).length;
            const fromCharters = industryCharters.filter(c => c === building).length;
            if (fromBuildings > 0) priorityFromBuildings++;
            if (fromCharters > 0) priorityFromCharters++;
        }
    });

    // Non-selected buildings (buildings not in selectedBuildings)
    const nonSelectedBuildingTypes = new Set();
    companies.forEach(company => {
        company.buildings.forEach(building => {
            if (!selectedBuildings.includes(building)) {
                nonSelectedBuildingTypes.add(building);
            }
        });
    });

    // Prestige goods
    const prestigeGoods = companies.reduce((count, company) => count + company.prestigeGoods.length, 0);

    // Building overlaps (duplicate buildings in selectedBuildings only)
    const selectedOverlaps = totalSelectedBuildings - selectedBuildingTypes.size;

    // Charter penalties: duplicates only count for useful charters
    let charterPenalty = 0;
    charterCounts.forEach((count, charter) => {
        if (count > 1) {
            charterPenalty += (count - 1) * 0.2;
        }
    });

    // Scoring calculation
    let score = 0;

    // Building coverage points
    score += selectedBuildingTypes.size; // +1 per unique building covered

    // Priority building points (only count each priority building once)
    score += priorityFromBuildings * 2; // +2 per priority building covered by buildings
    score += priorityFromCharters * 2; // +2 per priority building covered by charters

    // Industry charter points (useful charters)
    score += industryCharters.length * 1; // +1 per useful charter

    // Prestige goods
    score += prestigeGoods * 0.1; // +0.1 per prestige good

    // Non-selected buildings
    score += nonSelectedBuildingTypes.size * 0.01; // +0.01 per non-selected building covered

    // Penalties
    score -= selectedOverlaps * 0.2; // -0.2 per overlap in selected buildings
    score -= charterPenalty; // -0.2 per duplicate charter

    return score;
}

// Check prestige goods requirements
function checkPrestigeGoodRequirements(companies) {
    if (requiredPrestigeGoods.length === 0) return true;

    const providedPrestigeGoods = new Set();
    companies.forEach(company => {
        company.prestigeGoods.forEach(prestigeGood => {
            const baseType = prestigeGoodsMapping[prestigeGood];
            if (baseType) {
                providedPrestigeGoods.add(baseType);
            }
        });
    });

    return requiredPrestigeGoods.every(required => providedPrestigeGoods.has(required));
}

console.log('=== VICTORIA 3 COMPANY OPTIMIZER DEBUG ===');
console.log('Basic companies:', companies.basic.length);
console.log('Flavored companies:', companies.flavored.length);
console.log('Canal companies:', companies.canal.length);
console.log('Total companies:', allCompanies.length);
console.log('Selected buildings:', selectedBuildings);
console.log('Priority buildings:', priorityBuildings);
console.log('Required prestige goods:', requiredPrestigeGoods);

// Find the specific companies
const bungeAndBorn = allCompanies.find(c => c.name === 'Bunge & Born');
const basicPaper = allCompanies.find(c => c.name === 'Basic Paper');

console.log('\n=== TARGET COMPANIES ===');
console.log('Bunge & Born found:', !!bungeAndBorn);
console.log('Basic Paper found:', !!basicPaper);

if (bungeAndBorn) {
    console.log('Bunge & Born details:');
    console.log('  Buildings:', bungeAndBorn.buildings);
    console.log('  Charters:', bungeAndBorn.industryCharters);
    console.log('  Prestige:', bungeAndBorn.prestigeGoods);
}

if (basicPaper) {
    console.log('Basic Paper details:');
    console.log('  Buildings:', basicPaper.buildings);  
    console.log('  Charters:', basicPaper.industryCharters);
    console.log('  Prestige:', basicPaper.prestigeGoods);
}

if (bungeAndBorn && basicPaper) {
    console.log('\n=== INDIVIDUAL SCORING TEST ===');
    const bungeScore = calculateScore([bungeAndBorn]);
    const basicPaperScore = calculateScore([basicPaper]);
    
    console.log('Bunge & Born individual score:', bungeScore.toFixed(3));
    console.log('Basic Paper individual score:', basicPaperScore.toFixed(3));
    console.log('Score difference (Bunge - Basic):', (bungeScore - basicPaperScore).toFixed(3));

    // Now test in combination context - find the base companies from previous debug
    const baseCompanies = [
        allCompanies.find(c => c.name === 'Basic Metalworks'),
        allCompanies.find(c => c.name === 'Basic Shipyards'),
        allCompanies.find(c => c.name === 'Basic Motors'),
        allCompanies.find(c => c.name === 'Basic Munitions'),
        allCompanies.find(c => c.name === 'Ferrocarril Central Córdoba'),
        allCompanies.find(c => c.name === 'Caribbean Petroleum Company')
    ].filter(c => c);

    console.log('\n=== COMBINATION TEST ===');
    console.log('Base companies found:', baseCompanies.length);
    console.log('Base companies:', baseCompanies.map(c => c.name));

    if (baseCompanies.length === 6) {
        const comboWithBunge = [...baseCompanies, bungeAndBorn];
        const comboWithBasicPaper = [...baseCompanies, basicPaper];

        // Check prestige goods
        const bungePrestigeCheck = checkPrestigeGoodRequirements(comboWithBunge);
        const basicPaperPrestigeCheck = checkPrestigeGoodRequirements(comboWithBasicPaper);

        console.log('Combo with Bunge & Born satisfies prestige goods:', bungePrestigeCheck);
        console.log('Combo with Basic Paper satisfies prestige goods:', basicPaperPrestigeCheck);

        if (bungePrestigeCheck && basicPaperPrestigeCheck) {
            const bungeComboScore = calculateScore(comboWithBunge);
            const basicPaperComboScore = calculateScore(comboWithBasicPaper);

            console.log('Combo with Bunge & Born score:', bungeComboScore.toFixed(3));
            console.log('Combo with Basic Paper score:', basicPaperComboScore.toFixed(3));
            console.log('Score difference (Bunge - Basic):', (bungeComboScore - basicPaperComboScore).toFixed(3));

            if (bungeComboScore > basicPaperComboScore) {
                console.log('🚨 BUG CONFIRMED: Bunge combination scores higher!');
                
                console.log('\n=== DETAILED ANALYSIS ===');
                
                function analyzeCombo(companies, name) {
                    console.log(`\n${name}:`);
                    
                    // Building coverage
                    const selectedBuildingTypes = new Set();
                    let totalSelectedBuildings = 0;
                    companies.forEach(company => {
                        company.buildings.forEach(building => {
                            if (selectedBuildings.includes(building)) {
                                selectedBuildingTypes.add(building);
                                totalSelectedBuildings++;
                            }
                        });
                    });

                    // Charter analysis
                    const takenCharters = [];
                    companies.forEach(company => {
                        if (company.industryCharters && company.industryCharters.length > 0) {
                            const charter = company.industryCharters[0];
                            if (selectedBuildings.includes(charter) && !selectedBuildingTypes.has(charter)) {
                                takenCharters.push(charter);
                            }
                        }
                    });

                    // Priority analysis
                    let priorityFromBuildings = 0;
                    let priorityFromCharters = 0;
                    selectedBuildingTypes.forEach(building => {
                        if (priorityBuildings.includes(building)) priorityFromBuildings++;
                    });
                    takenCharters.forEach(charter => {
                        if (priorityBuildings.includes(charter)) priorityFromCharters++;
                    });

                    // Non-selected buildings
                    const nonSelectedBuildingTypes = new Set();
                    companies.forEach(company => {
                        company.buildings.forEach(building => {
                            if (!selectedBuildings.includes(building)) {
                                nonSelectedBuildingTypes.add(building);
                            }
                        });
                    });

                    // Prestige goods
                    const prestigeGoods = companies.reduce((count, company) => count + company.prestigeGoods.length, 0);

                    // Overlaps
                    const selectedOverlaps = totalSelectedBuildings - selectedBuildingTypes.size;

                    console.log(`  Selected buildings covered: ${selectedBuildingTypes.size} (${Array.from(selectedBuildingTypes).join(', ')})`);
                    console.log(`  Priority buildings from buildings: ${priorityFromBuildings}`);
                    console.log(`  Priority buildings from charters: ${priorityFromCharters}`);
                    console.log(`  Useful charters: ${takenCharters.length} (${takenCharters.join(', ')})`);
                    console.log(`  Non-selected buildings: ${nonSelectedBuildingTypes.size}`);
                    console.log(`  Prestige goods: ${prestigeGoods}`);
                    console.log(`  Building overlaps: ${selectedOverlaps}`);
                    console.log(`  Total score: ${calculateScore(companies).toFixed(3)}`);

                    // Score breakdown
                    let buildingScore = selectedBuildingTypes.size;
                    let priorityScore = (priorityFromBuildings + priorityFromCharters) * 2;
                    let charterScore = takenCharters.length;
                    let prestigeScore = prestigeGoods * 0.1;
                    let nonSelectedScore = nonSelectedBuildingTypes.size * 0.01;
                    let overlapPenalty = selectedOverlaps * 0.2;

                    console.log(`  Score breakdown:`);
                    console.log(`    Buildings: +${buildingScore}`);
                    console.log(`    Priority (x2): +${priorityScore}`);
                    console.log(`    Charters: +${charterScore}`);
                    console.log(`    Prestige: +${prestigeScore.toFixed(1)}`);
                    console.log(`    Non-selected: +${nonSelectedScore.toFixed(2)}`);
                    console.log(`    Overlap penalty: -${overlapPenalty.toFixed(1)}`);
                    console.log(`    Total: ${(buildingScore + priorityScore + charterScore + prestigeScore + nonSelectedScore - overlapPenalty).toFixed(3)}`);
                }
                
                analyzeCombo(comboWithBunge, 'Combo with Bunge & Born');
                analyzeCombo(comboWithBasicPaper, 'Combo with Basic Paper');
                
            } else {
                console.log('✅ Basic Paper combination scores higher as expected');
            }
        } else {
            console.log('⚠️  Prestige goods requirement issue - one combo rejected');
        }
    } else {
        console.log('❌ Could not find all base companies for combination test');
    }
} else {
    console.log('❌ Could not find both target companies');
}