#!/usr/bin/env node

/**
 * Comprehensive Prestige Goods Tests
 * Tests the new prestige goods system with LP optimization
 */

import { readFileSync } from 'fs';
import { join } from 'path';
import { fileURLToPath } from 'url';
import { dirname } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Import modules
import { solveIntegerLP, calculateIndividualScore } from '../lp-solver.mjs';
import { expandCompaniesWithCharters } from '../company-data.mjs';
import { checkPrestigeGoodRequirements } from '../prestige-goods.mjs';
import { prestigeGoodsMapping, prestigeGoodBaseTypes } from '../prestige-goods.mjs';

const projectRoot = join(__dirname, '..');

let testCount = 0;
let passedTests = 0;
let failedTests = 0;

function assert(condition, message) {
    testCount++;
    if (condition) {
        passedTests++;
        console.log(`✅ Test ${testCount}: ${message}`);
    } else {
        failedTests++;
        console.log(`❌ Test ${testCount}: ${message}`);
    }
}

function assertDeepEqual(actual, expected, message) {
    testCount++;
    const actualStr = JSON.stringify(actual, null, 2);
    const expectedStr = JSON.stringify(expected, null, 2);
    if (actualStr === expectedStr) {
        passedTests++;
        console.log(`✅ Test ${testCount}: ${message}`);
    } else {
        failedTests++;
        console.log(`❌ Test ${testCount}: ${message}`);
        console.log(`   Expected: ${expectedStr}`);
        console.log(`   Actual: ${actualStr}`);
    }
}

function runTests() {
    console.log('🧪 Starting Comprehensive Prestige Goods Tests');
    console.log('=' .repeat(60));
    
    // Load test data directly from JSON file
    const data = JSON.parse(readFileSync(join(projectRoot, 'companies_extracted.json'), 'utf8'));
    
    let companies = {
        basic: data.basicCompanies || [],
        flavored: data.flavoredCompanies || [],
        canal: []
    };
    
    // Find canal companies and separate them
    const allRaw = [...companies.basic, ...companies.flavored];
    companies.canal = allRaw.filter(c => c.special === 'canal');
    companies.flavored = companies.flavored.filter(c => c.special !== 'canal');
    
    const allCompanies = [...companies.basic, ...companies.flavored, ...companies.canal];
    const expandedCompanies = expandCompaniesWithCharters(allCompanies);
    
    // Test 1: Prestige Goods Mapping Accuracy
    console.log('\n📋 Test 1: Prestige Goods Mapping Accuracy');
    
    // Check edge cases are correctly mapped
    assert(prestigeGoodsMapping['mit afifi'] === 'Clothes', 'mit afifi maps to Clothes');
    assert(prestigeGoodsMapping['satsuma ware'] === 'Porcelain', 'satsuma ware maps to Porcelain');
    
    // Verify no prestige goods map to themselves
    let selfMappingCount = 0;
    for (const [good, baseType] of Object.entries(prestigeGoodsMapping)) {
        if (good === baseType) {
            selfMappingCount++;
        }
    }
    assert(selfMappingCount === 0, 'No prestige goods map to themselves as base types');
    
    // Verify total counts
    const totalPrestigeGoods = Object.keys(prestigeGoodsMapping).length;
    const totalBaseTypes = prestigeGoodBaseTypes.length;
    assert(totalPrestigeGoods === 57, `Total prestige goods is 57 (got ${totalPrestigeGoods})`);
    assert(totalBaseTypes === 30, `Total base types is 30 (got ${totalBaseTypes})`);
    
    // Test 2: Steel Requirement OR Logic
    console.log('\n🔩 Test 2: Steel Requirement OR Logic');
    
    const steelCompanies = expandedCompanies.filter(c => 
        c.prestigeGoods && c.prestigeGoods.some(pg => 
            prestigeGoodsMapping[pg] === 'Steel'
        )
    );
    
    assert(steelCompanies.length >= 2, 'Found multiple steel-providing companies');
    
    // Test checkPrestigeGoodRequirements with steel
    const steelRequirement = ['Steel'];
    const refinedSteelCompany = expandedCompanies.find(c => 
        c.prestigeGoods && c.prestigeGoods.includes('Refined Steel')
    );
    const sheffieldSteelCompany = expandedCompanies.find(c => 
        c.prestigeGoods && c.prestigeGoods.includes('Sheffield Steel')
    );
    
    if (refinedSteelCompany) {
        assert(checkPrestigeGoodRequirements([refinedSteelCompany], steelRequirement), 
            'Refined Steel satisfies steel requirement');
    }
    
    if (sheffieldSteelCompany) {
        assert(checkPrestigeGoodRequirements([sheffieldSteelCompany], steelRequirement), 
            'Sheffield Steel satisfies steel requirement');
    }
    
    // Test 3: Prestige Goods Uniqueness in LP
    console.log('\n🎯 Test 3: Prestige Goods Uniqueness in LP');
    
    // Find companies with same prestige good
    const prestigeGoodCounts = {};
    expandedCompanies.forEach(company => {
        if (company.prestigeGoods) {
            company.prestigeGoods.forEach(pg => {
                if (!prestigeGoodCounts[pg]) prestigeGoodCounts[pg] = [];
                prestigeGoodCounts[pg].push(company);
            });
        }
    });
    
    // Find a prestige good with multiple companies
    let testPrestigeGood = null;
    let testCompanies = [];
    for (const [pg, companies] of Object.entries(prestigeGoodCounts)) {
        if (companies.length >= 2 && !companies.some(c => c.special === 'canal')) {
            testPrestigeGood = pg;
            testCompanies = companies.slice(0, 2);
            break;
        }
    }
    
    if (testPrestigeGood && testCompanies.length >= 2) {
        // Test LP with conflicting prestige goods
        const lpResult = solveIntegerLP(
            testCompanies,
            ['Steel Mills'], // Simple building selection
            [], // No priority buildings
            [], // No required prestige goods
            [], // No required companies
            2, // Company slots
            false // No debug
        );
        
        if (lpResult.status === 'optimal') {
            const selectedCompanies = lpResult.selectedCompanies;
            const selectedWithTestPrestigeGood = selectedCompanies.filter(c => 
                c.prestigeGoods && c.prestigeGoods.includes(testPrestigeGood)
            );
            assert(selectedWithTestPrestigeGood.length <= 1, 
                `At most 1 company selected with prestige good: ${testPrestigeGood}`);
        }
    }
    
    // Test 4: Canal Companies Prestige Goods Exemption
    console.log('\n🚢 Test 4: Canal Companies Prestige Goods Exemption');
    
    const canalCompanies = expandedCompanies.filter(c => c.special === 'canal');
    assert(canalCompanies.length >= 2, 'Found canal companies');
    
    if (canalCompanies.length >= 2) {
        // Test both canal companies can be selected even with same prestige good
        const lpResult = solveIntegerLP(
            canalCompanies,
            ['Steel Mills'], // Simple building selection
            [], // No priority buildings
            [], // No required prestige goods
            [], // No required companies
            10, // Plenty of slots
            false // No debug
        );
        
        if (lpResult.status === 'optimal') {
            const selectedCanals = lpResult.selectedCompanies.filter(c => c.special === 'canal');
            assert(selectedCanals.length >= 2, 'Multiple canal companies can be selected');
        }
    }
    
    // Test 5: Prestige Goods Requirements Validation
    console.log('\n✅ Test 5: Prestige Goods Requirements Validation');
    
    // Test with empty requirements
    assert(checkPrestigeGoodRequirements([], []), 'Empty requirements always pass');
    assert(checkPrestigeGoodRequirements([expandedCompanies[0]], []), 'Empty requirements with companies pass');
    
    // Test with single requirement
    const toolsCompany = expandedCompanies.find(c => 
        c.prestigeGoods && c.prestigeGoods.some(pg => prestigeGoodsMapping[pg] === 'Tools')
    );
    if (toolsCompany) {
        assert(checkPrestigeGoodRequirements([toolsCompany], ['Tools']), 
            'Tools company satisfies Tools requirement');
        assert(!checkPrestigeGoodRequirements([toolsCompany], ['Steel']), 
            'Tools company does not satisfy Steel requirement');
    }
    
    // Test 6: Multi-Prestige Good Companies
    console.log('\n🎪 Test 6: Multi-Prestige Good Companies');
    
    const multiPrestigeCompanies = expandedCompanies.filter(c => 
        c.prestigeGoods && c.prestigeGoods.length > 1
    );
    
    if (multiPrestigeCompanies.length > 0) {
        const testCompany = multiPrestigeCompanies[0];
        assert(testCompany.prestigeGoods.length > 1, 
            `Company has multiple prestige goods: ${testCompany.name}`);
        
        // Test that all prestige goods are properly mapped
        const mappedGoods = testCompany.prestigeGoods.map(pg => prestigeGoodsMapping[pg]);
        const hasValidMappings = mappedGoods.every(bg => bg && bg !== 'Unknown');
        assert(hasValidMappings, 'All prestige goods have valid base type mappings');
    }
    
    // Test 7: Prestige Goods in LP Scoring
    console.log('\n🏆 Test 7: Prestige Goods in LP Scoring');
    
    const company1 = expandedCompanies.find(c => 
        c.prestigeGoods && c.prestigeGoods.length > 0 && c.buildings.length > 0
    );
    const company2 = expandedCompanies.find(c => 
        c.prestigeGoods && c.prestigeGoods.length === 0 && c.buildings.length > 0
    );
    
    if (company1 && company2) {
        const score1 = calculateIndividualScore(company1, company1.buildings, []);
        const score2 = calculateIndividualScore(company2, company2.buildings, []);
        
        // Company with prestige goods should score higher (all else being equal)
        if (company1.buildings.length === company2.buildings.length) {
            assert(score1 > score2, 'Company with prestige goods scores higher');
        }
    }
    
    // Test 8: Charter Variants with Prestige Goods
    console.log('\n📜 Test 8: Charter Variants with Prestige Goods');
    
    const originalWithCharter = expandedCompanies.find(c => 
        c.isCharter && c.prestigeGoods && c.prestigeGoods.length > 0
    );
    
    if (originalWithCharter) {
        const originalCompany = expandedCompanies.find(c => 
            c.name === originalWithCharter.name && !c.isCharter
        );
        
        if (originalCompany) {
            assertDeepEqual(originalCompany.prestigeGoods, originalWithCharter.prestigeGoods,
                'Charter variant maintains original prestige goods');
        }
    }
    
    // Test 9: Comprehensive Real-World Scenario
    console.log('\n🌍 Test 9: Comprehensive Real-World Scenario');
    
    const selectedBuildings = ['Steel Mills', 'Textile Mills', 'Paper Mills'];
    const priorityBuildings = ['Steel Mills'];
    const requiredPrestigeGoods = ['Steel'];
    const companySlots = 5;
    
    const lpResult = solveIntegerLP(
        expandedCompanies,
        selectedBuildings,
        priorityBuildings,
        requiredPrestigeGoods,
        [], // No required companies
        companySlots,
        false // No debug
    );
    
    assert(lpResult.status === 'optimal', 'Real-world scenario produces optimal solution');
    
    if (lpResult.status === 'optimal') {
        const selectedCompanies = lpResult.selectedCompanies;
        
        // Check steel requirement is satisfied
        const providedPrestigeGoods = new Set();
        selectedCompanies.forEach(company => {
            if (company.prestigeGoods) {
                company.prestigeGoods.forEach(pg => {
                    const baseType = prestigeGoodsMapping[pg];
                    if (baseType) providedPrestigeGoods.add(baseType);
                });
            }
        });
        
        assert(providedPrestigeGoods.has('Steel'), 'Steel requirement satisfied in real-world scenario');
        
        // Check company slots respected (excluding canals)
        const nonCanalCompanies = selectedCompanies.filter(c => c.special !== 'canal');
        assert(nonCanalCompanies.length <= companySlots, 
            `Company slots respected: ${nonCanalCompanies.length}/${companySlots}`);
    }
    
    // Test 10: Prestige Goods Error Handling
    console.log('\n⚠️ Test 10: Prestige Goods Error Handling');
    
    // Test with unknown prestige good
    const testCompanyWithUnknown = {
        name: 'Test Company',
        buildings: ['Steel Mills'],
        prestigeGoods: ['Unknown Prestige Good'],
        region: 'Test'
    };
    
    const unknownScore = calculateIndividualScore(testCompanyWithUnknown, ['Steel Mills'], []);
    assert(unknownScore >= 0, 'Unknown prestige good handled gracefully');
    
    // Test checkPrestigeGoodRequirements with unknown goods
    const unknownResult = checkPrestigeGoodRequirements([testCompanyWithUnknown], ['Unknown']);
    assert(unknownResult === false, 'Unknown prestige good requirement fails gracefully');
    
    // Results
    console.log('\n' + '='.repeat(60));
    console.log(`🧪 Test Results: ${passedTests}/${testCount} passed`);
    if (failedTests > 0) {
        console.log(`❌ ${failedTests} tests failed`);
        process.exit(1);
    } else {
        console.log('✅ All tests passed!');
    }
}

// Run tests
runTests();