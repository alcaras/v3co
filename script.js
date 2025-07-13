        // Company data will be loaded from the extracted JSON file
        let companies = {
            basic: [],
            flavored: [],
            canal: []
        };
        
        let selectedBuildings = [];
        let priorityBuildings = []; // Buildings marked as priority (higher weight)
        let selectedCompanies = [];
        let allCompanies = []; // All companies for optimization
        let visibleCompanies = []; // Companies to show to user
        let allBuildings = [];
        let requiredPrestigeGoods = ['Tools']; // Required prestige good base types
        
        // Prestige goods mapping to base types
        const prestigeGoodsMapping = {
            // Food & Agriculture
            'Fine Grain': 'Food',
            'Prime Meat': 'Food', 
            'River Plate Beef': 'Food',
            'Select Fish': 'Food',
            'Gourmet Groceries': 'Food',
            'Gros Michel Banana': 'Food',
            'Mit Afifi': 'Food',
            
            // Beverages
            'Reserve Coffee': 'Beverages',
            'China Tea': 'Beverages',
            'Assam Tea': 'Beverages',
            'Champagne': 'Beverages',
            'Smirnoff Vodka': 'Beverages',
            'Turkish Tobacco': 'Beverages',
            
            // Textiles & Clothing
            'Designer Clothes': 'Textiles',
            'Haute Couture': 'Textiles',
            'Suzhou Silk': 'Textiles',
            'Tomioka Silk': 'Textiles',
            'Como Silk': 'Textiles',
            'Sea Island Cotton': 'Textiles',
            
            // Paper
            'Craft Paper': 'Paper',
            'Washi Paper': 'Paper',
            
            // Furniture
            'Stylish Furniture': 'Furniture',
            'Bentwood Furniture': 'Furniture',
            'English Upholstery': 'Furniture',
            
            // Metals & Steel
            'Refined Steel': 'Steel',
            'Sheffield Steel': 'Steel',
            'Russia Iron': 'Steel',
            'Oregrounds Iron': 'Steel',
            
            // Tools & Machinery
            'Precision Tools': 'Tools',
            
            // Weapons & Military
            'High-powered Small Arms': 'Weapons',
            'Colt Revolvers': 'Weapons',
            'Saint-Etienne Rifles': 'Weapons',
            'Krupp Guns': 'Weapons',
            'Schneider Guns': 'Weapons',
            'Quick-fire Artillery': 'Weapons',
            
            // Ceramics & Porcelain
            'Canton Porcelain': 'Ceramics',
            'Meissen Porcelain': 'Ceramics',
            'Satsuma Ware': 'Ceramics',
            'Bohemian Crystal': 'Ceramics',
            
            // Wood Products
            'Rosewood': 'Wood',
            'Teak': 'Wood',
            
            // Chemicals & Drugs
            'Pure Opium': 'Chemicals',
            'Bengal Opium': 'Chemicals',
            'German Aniline': 'Chemicals',
            'Sicilian Sulfur': 'Chemicals',
            'Baku Oil': 'Chemicals',
            'High-grade Explosives': 'Chemicals',
            'Enriched Fertilizer': 'Chemicals',
            
            // Transportation
            'Swift Merchant Marine': 'Transportation',
            'Clyde-Built Liners': 'Transportation',
            'Armstrong Ships': 'Transportation',
            'Ford Automobiles': 'Transportation',
            'Turin Automobiles': 'Transportation',
            
            // Electronics
            'Radiola Radios': 'Electronics',
            'Chapel Radios': 'Electronics',
            'Ericsson Apparatus': 'Electronics',
            
            // Engines
            'Schichau Engines': 'Engines'
        };
        
        // Get all unique base types
        const prestigeGoodBaseTypes = [...new Set(Object.values(prestigeGoodsMapping))].sort();

        // Load company data from the extracted JSON
        async function loadCompanyData() {
            try {
                console.log('Starting to load company data...');
                const response = await fetch('companies_extracted.json');
                console.log('Fetch response:', response.status, response.ok);
                const data = await response.json();
                console.log('JSON data loaded:', data);
                
                companies.basic = data.basicCompanies || [];
                companies.flavored = data.flavoredCompanies || [];
                companies.canal = data.flavoredCompanies.filter(c => c.special === 'canal') || [];
                
                console.log('Companies loaded - Basic:', companies.basic.length, 'Flavored:', companies.flavored.length, 'Canal:', companies.canal.length);
                
                // Remove canal companies from flavored list
                companies.flavored = companies.flavored.filter(c => c.special !== 'canal');
                
                // Find United Construction Conglomerate for display
                companies.mandate = companies.basic.filter(c => c.name === 'United Construction Conglomerate');
                
                // Remove United Construction Conglomerate from basic companies to avoid duplication
                companies.basic = companies.basic.filter(c => c.name !== 'United Construction Conglomerate');
                
                // All companies for optimization (basic + flavored + canal)
                allCompanies = [...companies.basic, ...companies.flavored, ...companies.canal, ...companies.mandate];
                
                // Display companies (basic first, then mandate, then flavored, then canal)
                visibleCompanies = [...companies.basic, ...companies.mandate, ...companies.flavored, ...companies.canal];
                
                console.log('All companies array length:', allCompanies.length);
                console.log('Visible companies array length:', visibleCompanies.length);
                
                // Extract all unique buildings from displayed companies
                const buildingSet = new Set();
                visibleCompanies.forEach(company => {
                    company.buildings.forEach(building => buildingSet.add(building));
                });
                allBuildings = Array.from(buildingSet).sort();
                
                initializeInterface();
            } catch (error) {
                console.error('Error loading company data:', error);
                // Fallback to sample data if JSON loading fails
                loadSampleData();
            }
        }

        // Sample data for testing/fallback
        function loadSampleData() {
            // Fallback sample data
            companies.basic = [];
            companies.flavored = [];
            companies.canal = [];
            companies.mandate = [];
            
            allCompanies = [];
            visibleCompanies = [];
            
            // Extract all unique buildings from flavored and canal companies
            const buildingSet = new Set();
            allCompanies.forEach(company => {
                company.buildings.forEach(building => buildingSet.add(building));
            });
            allBuildings = Array.from(buildingSet).sort();
            
            initializeInterface();
        }

        function initializeInterface() {
            // Set default selected buildings
            selectedBuildings = [
                'Coal Mine', 'Fishing Wharf', 'Iron Mine', 'Logging Camp', 'Oil Rig', 'Rubber Plantation', 'Whaling Station',
                'Automotive Industries', 'Explosives Factory', 'Glassworks', 'Motor Industries', 'Paper Mill', 'Steel Mills', 'Tooling Workshops',
                'Port', 'Railway', 'Trade Center', 'Power Plant'
            ];
            
            displayBuildings();
            displayPrestigeGoods();
            
            // Mark default prestige goods as selected in the UI
            requiredPrestigeGoods.forEach(baseType => {
                const prestigeElement = document.getElementById(`prestige-${baseType.replace(/\s+/g, '_')}`);
                if (prestigeElement) {
                    prestigeElement.classList.add('selected');
                }
            });
            
            // Set default priority buildings
            priorityBuildings = [
                'Coal Mine', 'Iron Mine', 'Steel Mills', 'Paper Mill', 'Tooling Workshops', 'Logging Camp'
            ];
            
            // Mark default buildings as selected in the UI and show priority indicators
            selectedBuildings.forEach(building => {
                const buildingElement = document.getElementById(`building-${building.replace(/\s+/g, '_')}`);
                if (buildingElement) {
                    buildingElement.classList.add('selected');
                }
                
                // Show priority indicator if this is a priority building
                if (priorityBuildings.includes(building)) {
                    const priorityElement = document.getElementById(`priority-${building.replace(/\s+/g, '_')}`);
                    if (priorityElement) {
                        priorityElement.style.display = 'block';
                    }
                }
            });
            
            displayCompanies();
            
            // Set default selected companies
            setDefaultCompanySelection();
            
            updateStats();
            updateRegionStats();
        }
        
        function setDefaultCompanySelection() {
            const defaultCompanies = [];
            
            // 1. All basic companies (use the pre-defined companies.basic array)
            defaultCompanies.push(...companies.basic);
            
            // 2. United Construction Conglomerate (commented out - not selected by default)
            // const unitedConstruction = allCompanies.find(c => c.name === 'United Construction Conglomerate');
            // if (unitedConstruction) {
            //     defaultCompanies.push(unitedConstruction);
            // }
            
            // 3. American companies excluding Brazil, Canada, Mexico, US
            // Also exclude Centro Vitivinícola Nacional (requires being Argentina)
            const excludedCountries = ['Brazil', 'Canada', 'Mexico', 'United States'];
            const excludedCompanies = ['Centro Vitivinícola Nacional'];
            const americanCompanies = allCompanies.filter(c => 
                c.region === 'Americas' && 
                c.country && 
                !excludedCountries.includes(c.country) &&
                !excludedCompanies.includes(c.name)
            );
            defaultCompanies.push(...americanCompanies);
            
            // 4. De Beers
            const deBeers = allCompanies.find(c => c.name === 'De Beers Consolidated Mines Ltd.');
            if (deBeers) {
                defaultCompanies.push(deBeers);
            }
            
            // Set as selected
            selectedCompanies = defaultCompanies;
            
            // Update UI to show selection
            defaultCompanies.forEach(company => {
                const companyCards = document.querySelectorAll(`[data-company-name="${company.name}"]`);
                companyCards.forEach(card => {
                    card.classList.add('selected');
                });
            });
        }
        
        function displayBuildings() {
            const buildingContainer = document.getElementById('buildingSelection');
            
            // Group buildings by type (using actual building names from JSON data)
            const buildingsByType = {
                'Agriculture': ['Maize Farm', 'Millet Farm', 'Rice Farm', 'Rye Farm', 'Wheat Farm', 'Vineyard'],
                'Extraction': ['Coal Mine', 'Fishing Wharf', 'Gold Mine', 'Iron Mine', 'Lead Mine', 'Logging Camp', 'Oil Rig', 'Rubber Plantation', 'Sulfur Mine', 'Whaling Station'],
                'Plantations': ['Banana Plantation', 'Coffee Plantation', 'Cotton Plantation', 'Dye Plantation', 'Opium Plantation', 'Silk Plantation', 'Sugar Plantation', 'Tea Plantation', 'Tobacco Plantation'],
                'Ranches': ['Livestock Ranch'],
                'Manufacturing Industries': ['Arms Industries', 'Artillery Foundries', 'Automotive Industries', 'Electrics Industries', 'Explosives Factory', 'Fertilizer Plant', 'Food Industry', 'Furniture Manufacturies', 'Glassworks', 'Military Shipyards', 'Motor Industries', 'Munition Plant', 'Paper Mill', 'Shipyards', 'Steel Mills', 'Synthetics Plant', 'Textile Mill', 'Tooling Workshops'],
                'Infrastructure': ['Port', 'Railway', 'Trade Center'],
                'Power Plants': ['Power Plant']
            };
            
            let html = '';
            Object.entries(buildingsByType).forEach(([type, buildings]) => {
                const availableBuildings = buildings.filter(building => allBuildings.includes(building));
                if (availableBuildings.length > 0) {
                    html += `
                        <div class="region-section">
                            <div class="region-header">
                                <div class="region-title">${type} Buildings</div>
                                <div class="region-actions">
                                    <button class="select-all-btn" onclick="selectAllBuildings('${type}', event)">Select All</button>
                                    <button class="select-all-btn" onclick="clearAllBuildings('${type}', event)" style="margin-left: 10px;">Clear All</button>
                                </div>
                            </div>
                            <div class="region-content">
                                <div class="building-grid">
                                    ${availableBuildings.map(building => `
                                        <div class="building-item" onclick="toggleBuilding('${building}')" id="building-${building.replace(/\s+/g, '_')}" oncontextmenu="togglePriorityBuilding('${building}', event)" style="position: relative;">
                                            ${building}
                                            <div class="priority-indicator" id="priority-${building.replace(/\s+/g, '_')}" style="display: none; position: absolute; top: 2px; right: 2px; background: #007bff; color: white; border-radius: 50%; width: 16px; height: 16px; font-size: 10px; text-align: center; line-height: 16px;">★</div>
                                        </div>
                                    `).join('')}
                                </div>
                            </div>
                        </div>
                    `;
                }
            });
            
            buildingContainer.innerHTML = html;
        }

        function displayPrestigeGoods() {
            const prestigeContainer = document.getElementById('prestigeGoodsSelection');
            
            let html = `
                <div class="region-section">
                    <div class="region-header">
                        <div class="region-title">Prestige Good Base Types</div>
                        <div class="region-actions">
                            <button class="select-all-btn" onclick="selectAllPrestigeGoods(event)">Select All</button>
                            <button class="select-all-btn" onclick="clearAllPrestigeGoods(event)" style="margin-left: 10px;">Clear All</button>
                        </div>
                    </div>
                    <div class="region-content">
                        <div class="building-grid">
                            ${prestigeGoodBaseTypes.map(baseType => `
                                <div class="building-item" onclick="togglePrestigeGood('${baseType}')" id="prestige-${baseType.replace(/\s+/g, '_')}" style="position: relative;">
                                    ${baseType}
                                </div>
                            `).join('')}
                        </div>
                    </div>
                </div>
            `;
            
            prestigeContainer.innerHTML = html;
        }

        function displayCompanies() {
            const regionsContainer = document.getElementById('companyRegions');
            regionsContainer.innerHTML = '';
            
            // Show only flavored, canal, and mandate companies for display
            let relevantCompanies = visibleCompanies;
            
            // Group companies by region, putting basic companies at the top for visibility
            const regions = {
                'Basic Companies': relevantCompanies.filter(c => companies.basic.some(bc => bc.name === c.name)),
                'Mandate Companies': relevantCompanies.filter(c => c.name === 'United Construction Conglomerate'),
                'Americas': relevantCompanies.filter(c => c.region === 'Americas'),
                'Europe': relevantCompanies.filter(c => c.region === 'Europe'),
                'Asia': relevantCompanies.filter(c => c.region === 'Asia'),
                'Middle East': relevantCompanies.filter(c => c.region === 'Middle East'),
                'Africa': relevantCompanies.filter(c => c.region === 'Africa')
            };
            
            // Create region sections
            Object.entries(regions).forEach(([regionName, regionCompanies]) => {
                if (regionCompanies.length === 0) return;
                
                const regionDiv = document.createElement('div');
                regionDiv.className = 'region-section';
                
                const selectedInRegion = regionCompanies.filter(c => 
                    selectedCompanies.some(sc => sc.name === c.name)
                ).length;
                
                const safeRegionName = regionName.replace(/[^a-zA-Z0-9]/g, '_');
                
                regionDiv.innerHTML = `
                    <div class="region-header">
                        <div class="region-title">${regionName}</div>
                        <div class="region-actions">
                            <button class="select-all-btn" onclick="selectAllInRegion('${safeRegionName}', event)">Select All</button>
                            <button class="select-all-btn" onclick="clearAllInRegion('${safeRegionName}', event)" style="margin-left: 10px;">Clear All</button>
                            <div class="region-stats">
                                ${selectedInRegion}/${regionCompanies.length} selected
                            </div>
                        </div>
                    </div>
                    <div class="region-content" id="content-${safeRegionName}">
                        <div class="company-grid">
                            ${regionCompanies.map(company => createCompanyCard(company)).join('')}
                        </div>
                    </div>
                `;
                
                regionsContainer.appendChild(regionDiv);
            });
        }
        
        function toggleBuilding(buildingName) {
            const index = selectedBuildings.indexOf(buildingName);
            const buildingElement = document.getElementById(`building-${buildingName.replace(/\s+/g, '_')}`);
            
            if (index > -1) {
                selectedBuildings.splice(index, 1);
                buildingElement.classList.remove('selected');
            } else {
                selectedBuildings.push(buildingName);
                buildingElement.classList.add('selected');
            }
            
            displayCompanies();
            updateStats();
            updateRegionStats();
        }
        
        function selectAllBuildings(type, event) {
            if (event) event.stopPropagation();
            
            const buildingsByType = {
                'Agriculture': ['Maize Farm', 'Millet Farm', 'Rice Farm', 'Rye Farm', 'Wheat Farm', 'Vineyard'],
                'Extraction': ['Coal Mine', 'Fishing Wharf', 'Gold Mine', 'Iron Mine', 'Lead Mine', 'Logging Camp', 'Oil Rig', 'Rubber Plantation', 'Sulfur Mine', 'Whaling Station'],
                'Plantations': ['Banana Plantation', 'Coffee Plantation', 'Cotton Plantation', 'Dye Plantation', 'Opium Plantation', 'Silk Plantation', 'Sugar Plantation', 'Tea Plantation', 'Tobacco Plantation'],
                'Ranches': ['Livestock Ranch'],
                'Manufacturing Industries': ['Arms Industries', 'Artillery Foundries', 'Automotive Industries', 'Electrics Industries', 'Explosives Factory', 'Fertilizer Plant', 'Food Industry', 'Furniture Manufacturies', 'Glassworks', 'Military Shipyards', 'Motor Industries', 'Munition Plant', 'Paper Mill', 'Shipyards', 'Steel Mills', 'Synthetics Plant', 'Textile Mill', 'Tooling Workshops'],
                'Infrastructure': ['Port', 'Railway', 'Trade Center'],
                'Power Plants': ['Power Plant']
            };
            
            const buildings = buildingsByType[type] || [];
            buildings.forEach(building => {
                if (allBuildings.includes(building) && !selectedBuildings.includes(building)) {
                    selectedBuildings.push(building);
                    const buildingElement = document.getElementById(`building-${building.replace(/\s+/g, '_')}`);
                    if (buildingElement) {
                        buildingElement.classList.add('selected');
                    }
                }
            });
            
            displayCompanies();
            updateStats();
            updateRegionStats();
        }
        
        function clearAllBuildings(type, event) {
            if (event) event.stopPropagation();
            
            const buildingsByType = {
                'Agriculture': ['Maize Farm', 'Millet Farm', 'Rice Farm', 'Rye Farm', 'Wheat Farm', 'Vineyard'],
                'Extraction': ['Coal Mine', 'Fishing Wharf', 'Gold Mine', 'Iron Mine', 'Lead Mine', 'Logging Camp', 'Oil Rig', 'Rubber Plantation', 'Sulfur Mine', 'Whaling Station'],
                'Plantations': ['Banana Plantation', 'Coffee Plantation', 'Cotton Plantation', 'Dye Plantation', 'Opium Plantation', 'Silk Plantation', 'Sugar Plantation', 'Tea Plantation', 'Tobacco Plantation'],
                'Ranches': ['Livestock Ranch'],
                'Manufacturing Industries': ['Arms Industries', 'Artillery Foundries', 'Automotive Industries', 'Electrics Industries', 'Explosives Factory', 'Fertilizer Plant', 'Food Industry', 'Furniture Manufacturies', 'Glassworks', 'Military Shipyards', 'Motor Industries', 'Munition Plant', 'Paper Mill', 'Shipyards', 'Steel Mills', 'Synthetics Plant', 'Textile Mill', 'Tooling Workshops'],
                'Infrastructure': ['Port', 'Railway', 'Trade Center'],
                'Power Plants': ['Power Plant']
            };
            
            const buildings = buildingsByType[type] || [];
            buildings.forEach(building => {
                if (allBuildings.includes(building) && selectedBuildings.includes(building)) {
                    const index = selectedBuildings.indexOf(building);
                    selectedBuildings.splice(index, 1);
                    const buildingElement = document.getElementById(`building-${building.replace(/\s+/g, '_')}`);
                    if (buildingElement) {
                        buildingElement.classList.remove('selected');
                    }
                }
            });
            
            displayCompanies();
            updateStats();
            updateRegionStats();
        }
        
        function togglePrestigeGood(baseType) {
            const index = requiredPrestigeGoods.indexOf(baseType);
            const prestigeElement = document.getElementById(`prestige-${baseType.replace(/\s+/g, '_')}`);
            
            if (index > -1) {
                requiredPrestigeGoods.splice(index, 1);
                prestigeElement.classList.remove('selected');
            } else {
                requiredPrestigeGoods.push(baseType);
                prestigeElement.classList.add('selected');
            }
            
            displayCompanies();
            updateStats();
            updateRegionStats();
        }
        
        function selectAllPrestigeGoods(event) {
            if (event) event.stopPropagation();
            
            prestigeGoodBaseTypes.forEach(baseType => {
                if (!requiredPrestigeGoods.includes(baseType)) {
                    requiredPrestigeGoods.push(baseType);
                    const prestigeElement = document.getElementById(`prestige-${baseType.replace(/\s+/g, '_')}`);
                    if (prestigeElement) {
                        prestigeElement.classList.add('selected');
                    }
                }
            });
            
            displayCompanies();
            updateStats();
            updateRegionStats();
        }
        
        function clearAllPrestigeGoods(event) {
            if (event) event.stopPropagation();
            
            requiredPrestigeGoods.forEach(baseType => {
                const prestigeElement = document.getElementById(`prestige-${baseType.replace(/\s+/g, '_')}`);
                if (prestigeElement) {
                    prestigeElement.classList.remove('selected');
                }
            });
            
            requiredPrestigeGoods.length = 0;
            
            displayCompanies();
            updateStats();
            updateRegionStats();
        }

        function createCompanyCard(company) {
            const isSelected = selectedCompanies.some(c => c.name === company.name);
            const isCanal = company.special === 'canal';
            
            return `
                <div class="company-item ${isSelected ? 'selected' : ''}" data-company-name="${company.name}" onclick="toggleCompanyByElement(this, event)">
                    <div class="company-name">${company.name}${isCanal ? ' 🚢' : ''}</div>
                    <div class="company-buildings">Buildings: ${company.buildings.join(', ')}</div>
                    ${company.industryCharters && company.industryCharters.length > 0 ? `<div class="company-charters" style="font-size: 13px; color: #6f42c1; margin-bottom: 6px;">Industry Charters: ${company.industryCharters.join(', ')}</div>` : ''}
                    <div class="company-bonus">${company.prosperityBonus}</div>
                    ${company.prestigeGoods.length > 0 ? `<div class="company-prestige">Prestige: ${company.prestigeGoods.join(', ')}</div>` : ''}
                    <div class="company-requirements">${company.requirements}</div>
                    ${company.country ? `<div style="font-size: 12px; color: #6c757d; margin-top: 5px;">${company.country}</div>` : ''}
                    ${isCanal ? `<div style="font-size: 12px; color: #007bff; margin-top: 5px; font-weight: bold;">Canal Company - No slot cost</div>` : ''}
                </div>
            `;
        }

        function toggleRegion(regionName) {
            const content = document.getElementById(`content-${regionName}`);
            const icon = document.getElementById(`icon-${regionName}`);
            
            if (content.classList.contains('expanded')) {
                content.classList.remove('expanded');
                icon.classList.remove('expanded');
            } else {
                content.classList.add('expanded');
                icon.classList.add('expanded');
            }
        }

        function toggleCompanyByElement(element, event) {
            if (event) event.stopPropagation();
            
            const companyName = element.getAttribute('data-company-name');
            toggleCompany(companyName, event);
        }
        
        function toggleCompany(companyName, event) {
            if (event) event.stopPropagation();
            
            const company = allCompanies.find(c => c.name === companyName);
            if (!company) {
                console.error('Company not found:', companyName);
                return;
            }
            
            const index = selectedCompanies.findIndex(c => c.name === companyName);
            
            if (index > -1) {
                selectedCompanies.splice(index, 1);
            } else {
                selectedCompanies.push(company);
            }
            
            // Update only the specific company card instead of redrawing everything
            const companyCard = event ? event.target.closest('.company-item') : null;
            if (companyCard) {
                if (index > -1) {
                    companyCard.classList.remove('selected');
                } else {
                    companyCard.classList.add('selected');
                }
            }
            
            updateStats();
            updateRegionStats();
        }

        function clearSelection() {
            selectedCompanies = [];
            selectedBuildings = [];
            priorityBuildings = [];
            requiredPrestigeGoods = [];
            displayBuildings();
            displayPrestigeGoods();
            displayCompanies();
            updateStats();
            updateRegionStats();
        }
        
        function togglePriorityBuilding(buildingName, event) {
            event.preventDefault();
            event.stopPropagation();
            
            const index = priorityBuildings.indexOf(buildingName);
            const priorityElement = document.getElementById(`priority-${buildingName.replace(/\s+/g, '_')}`);
            
            if (index > -1) {
                priorityBuildings.splice(index, 1);
                priorityElement.style.display = 'none';
            } else {
                // Can only mark as priority if it's already selected
                if (selectedBuildings.includes(buildingName)) {
                    priorityBuildings.push(buildingName);
                    priorityElement.style.display = 'block';
                } else {
                    alert('Please select the building first before marking it as priority.');
                }
            }
            
            updateStats();
        }
        
        function selectAllInRegion(regionName, event) {
            if (event) event.stopPropagation();
            
            // Find all companies in this region
            const regionContent = document.getElementById(`content-${regionName}`);
            if (!regionContent) return;
            
            const companyCards = regionContent.querySelectorAll('.company-item');
            
            companyCards.forEach(card => {
                const companyName = card.querySelector('.company-name').textContent.replace(' 🚢', '').trim();
                const company = allCompanies.find(c => c.name === companyName);
                
                if (company && !selectedCompanies.some(sc => sc.name === company.name)) {
                    selectedCompanies.push(company);
                    card.classList.add('selected');
                }
            });
            
            updateStats();
            updateRegionStats();
        }
        
        function clearAllInRegion(regionName, event) {
            if (event) event.stopPropagation();
            
            // Find all companies in this region
            const regionContent = document.getElementById(`content-${regionName}`);
            if (!regionContent) return;
            
            const companyCards = regionContent.querySelectorAll('.company-item');
            
            companyCards.forEach(card => {
                const companyName = card.querySelector('.company-name').textContent.replace(' 🚢', '').trim();
                const company = allCompanies.find(c => c.name === companyName);
                
                if (company && selectedCompanies.some(sc => sc.name === company.name)) {
                    const index = selectedCompanies.findIndex(sc => sc.name === company.name);
                    selectedCompanies.splice(index, 1);
                    card.classList.remove('selected');
                }
            });
            
            updateStats();
            updateRegionStats();
        }
        
        function updateRegionStats() {
            // Update all region stats
            document.querySelectorAll('.region-section').forEach(section => {
                const regionHeader = section.querySelector('.region-header');
                const regionTitle = regionHeader.querySelector('.region-title').textContent;
                const regionContent = section.querySelector('.region-content');
                const companyCards = regionContent.querySelectorAll('.company-item');
                
                const selectedInRegion = Array.from(companyCards).filter(card => 
                    card.classList.contains('selected')
                ).length;
                
                const statsDiv = regionHeader.querySelector('.region-stats');
                if (statsDiv) {
                    statsDiv.textContent = `${selectedInRegion}/${companyCards.length} selected`;
                }
            });
        }

        function updateStats() {
            document.getElementById('selectedBuildings').textContent = selectedBuildings.length;
            
            // Show counts for displayed companies vs all companies used in optimization
            document.getElementById('availableCompanies').textContent = `${visibleCompanies.length} (${allCompanies.length} w/ basic)`;
            document.getElementById('selectedCount').textContent = selectedCompanies.length;
            
            // Calculate prestige goods
            const prestigeGoods = selectedCompanies.reduce((count, company) => 
                count + company.prestigeGoods.length, 0);
            document.getElementById('prestigeGoods').textContent = prestigeGoods;
        }

        function searchCompanies() {
            const searchTerm = document.getElementById('searchBox').value.toLowerCase();
            
            if (searchTerm === '') {
                displayCompanies();
                return;
            }
            
            const filtered = allCompanies.filter(company => 
                company.name.toLowerCase().includes(searchTerm) ||
                company.buildings.some(building => building.toLowerCase().includes(searchTerm)) ||
                company.prosperityBonus.toLowerCase().includes(searchTerm) ||
                (company.country && company.country.toLowerCase().includes(searchTerm))
            );
            
            // Display filtered results in a single section
            const regionsContainer = document.getElementById('companyRegions');
            regionsContainer.innerHTML = `
                <div class="region-section">
                    <div class="region-header" onclick="toggleRegion('search')">
                        <div class="region-title">Search Results</div>
                        <div class="region-stats">
                            ${filtered.length} companies found
                            <span class="collapse-icon expanded" id="icon-search">▼</span>
                        </div>
                    </div>
                    <div class="region-content expanded" id="content-search">
                        <div class="company-grid">
                            ${filtered.map(company => createCompanyCard(company)).join('')}
                        </div>
                    </div>
                </div>
            `;
        }

        function optimizeCompanies() {
            const slots = parseInt(document.getElementById('companySlots').value);
            
            if (selectedCompanies.length === 0) {
                alert('Please select at least one company to optimize.');
                return;
            }
            
            // Separate canal companies from selected companies
            const regularCompanies = selectedCompanies.filter(c => c.special !== 'canal');
            const canalCompanies = selectedCompanies.filter(c => c.special === 'canal');
            
            // Generate top 10 combinations with canal companies included in scoring
            const topCombinations = generateTopCombinations(regularCompanies, slots, 10, canalCompanies);
            
            // Add canal companies to each combination for display
            topCombinations.forEach(combo => {
                combo.companies = [...combo.companies, ...canalCompanies];
            });
            
            displayMultipleResults(topCombinations, slots);
        }

        function calculateScore(companies) {
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
        
        function checkPrestigeGoodRequirements(companies) {
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

        function generateTopCombinations(companies, maxSlots, topN = 10, canalCompanies = []) {
            const startTime = performance.now();
            console.log('Starting linear programming optimization...');
            
            // Use LP solver to find optimal solution
            const results = solveCompanyOptimization(
                companies, 
                maxSlots, 
                canalCompanies, 
                requiredPrestigeGoods, 
                selectedBuildings, 
                priorityBuildings
            );
            
            const endTime = performance.now();
            console.log(`LP optimization completed in ${(endTime - startTime).toFixed(2)}ms`);
            
            return results;
        }
            const n = filteredCompanies.length;
            
            // DP table: dp[i][w] = {score, companies} for using first i companies with w slots
            const dp = Array(n + 1).fill(null).map(() => 
                Array(maxSlots + 1).fill(null).map(() => ({ score: 0, companies: [] }))
            );
            
            // Fill the DP table
            for (let i = 1; i <= n; i++) {
                const company = filteredCompanies[i - 1];
                
                for (let w = 0; w <= maxSlots; w++) {
                    // Option 1: Don't take this company
                    dp[i][w] = { ...dp[i-1][w] };
                    
                    // Option 2: Take this company (if we have space)
                    if (w >= 1) {
                        const prevCombination = dp[i-1][w-1];
                        const newCombination = [...prevCombination.companies, company];
                        const allCompaniesWithCanal = [...newCombination, ...canalCompanies];
                        
                        // Only consider this combination if it satisfies prestige goods requirements
                        // OR if we haven't specified any prestige goods requirements
                        if (requiredPrestigeGoods.length === 0 || checkPrestigeGoodRequirements(allCompaniesWithCanal)) {
                            const newScore = calculateScore(allCompaniesWithCanal);
                            
                            if (newScore > dp[i][w].score) {
                                dp[i][w] = {
                                    score: newScore,
                                    companies: newCombination
                                };
                            }
                        }
                    }
                }
            }
            
            // Generate multiple good combinations, prioritizing maxSlots solutions
            const results = [];
            
            // Primary strategy: Find the best solution for maxSlots
            if (dp[n][maxSlots].companies.length > 0 && dp[n][maxSlots].score > 0) {
                results.push({
                    companies: dp[n][maxSlots].companies,
                    totalScore: dp[n][maxSlots].score,
                    slotsUsed: maxSlots
                });
            }
            
            // Secondary strategy: Generate alternative maxSlots combinations by exploring suboptimal paths
            const maxSlotScore = dp[n][maxSlots].score;
            const minAcceptableScore = maxSlotScore * 0.95; // Within 5% of optimal
            
            // Look for alternative good combinations by checking different final company choices
            for (let lastCompanyIdx = 0; lastCompanyIdx < n; lastCompanyIdx++) {
                const lastCompany = filteredCompanies[lastCompanyIdx];
                
                // Check if this company is in the optimal solution (skip to avoid duplicates)
                if (dp[n][maxSlots].companies.includes(lastCompany)) continue;
                
                // Try building a combination that ends with this company
                const prevState = dp[lastCompanyIdx][maxSlots - 1];
                if (prevState.companies.length === maxSlots - 1) {
                    const altCombination = [...prevState.companies, lastCompany];
                    const altScore = calculateScore([...altCombination, ...canalCompanies]);
                    
                    if (altScore >= minAcceptableScore && altScore > 0) {
                        results.push({
                            companies: altCombination,
                            totalScore: altScore,
                            slotsUsed: maxSlots
                        });
                    }
                }
            }
            
            // Fallback: Include lower slot solutions only if we don't have enough maxSlots solutions
            if (results.length < topN) {
                for (let w = maxSlots - 1; w >= 1; w--) {
                    if (dp[n][w].companies.length > 0 && dp[n][w].score > 0) {
                        results.push({
                            companies: dp[n][w].companies,
                            totalScore: dp[n][w].score,
                            slotsUsed: w
                        });
                    }
                }
            }
            
            // Sort by score descending, then by slots used descending (prefer using more slots)
            results.sort((a, b) => {
                const scoreDiff = b.totalScore - a.totalScore;
                if (Math.abs(scoreDiff) < 0.01) {
                    // If scores are very close, prefer using more slots
                    return b.slotsUsed - a.slotsUsed;
                }
                return scoreDiff;
            });
            
            // Remove duplicates
            const seen = new Set();
            const uniqueResults = results.filter(result => {
                const key = result.companies.map(c => c.name).sort().join(',');
                if (seen.has(key)) return false;
                seen.add(key);
                return true;
            });
            
            // No need to filter since we enforced requirements during DP
            const validResults = uniqueResults;
            
            console.log(`Knapsack optimization complete. Found ${uniqueResults.length} unique solutions (all satisfy prestige goods requirements).`);
            
            // Debug prestige goods filtering
            if (requiredPrestigeGoods.length > 0) {
                console.log('Required prestige goods:', requiredPrestigeGoods);
                
                // Show which companies in the selection can provide required goods
                console.log('Companies that can provide required prestige goods:');
                requiredPrestigeGoods.forEach(requiredType => {
                    const providingCompanies = filteredCompanies.filter(company => {
                        return company.prestigeGoods.some(prestigeGood => {
                            const baseType = prestigeGoodsMapping[prestigeGood];
                            return baseType === requiredType;
                        });
                    });
                    console.log(`  ${requiredType}: ${providingCompanies.length} companies -`, providingCompanies.map(c => c.name));
                    
                    // Show score and details for each providing company
                    providingCompanies.forEach(company => {
                        const score = calculateScore([company]);
                        console.log(`    ${company.name}: Score=${score.toFixed(2)}, Buildings=[${company.buildings.join(', ')}], PrestigeGoods=[${company.prestigeGoods.join(', ')}]`);
                    });
                });
                
                console.log('Checking first few solutions for prestige goods:');
                uniqueResults.slice(0, 3).forEach((result, i) => {
                    const allCompanies = [...result.companies, ...canalCompanies];
                    const providedGoods = new Set();
                    const prestigeGoodDetails = [];
                    allCompanies.forEach(company => {
                        company.prestigeGoods.forEach(prestigeGood => {
                            const baseType = prestigeGoodsMapping[prestigeGood];
                            if (baseType) {
                                providedGoods.add(baseType);
                                prestigeGoodDetails.push(`${prestigeGood} (${baseType})`);
                            }
                        });
                    });
                    console.log(`  Solution ${i+1} provides:`, Array.from(providedGoods));
                    console.log(`  Solution ${i+1} prestige goods:`, prestigeGoodDetails);
                    console.log(`  Satisfies requirements:`, checkPrestigeGoodRequirements(allCompanies));
                });
            }
            
            // Debug: Check if maxSlots solution exists and analyze gaps
            console.log('DP results analysis:');
            console.log(`  Best 7-slot solution: ${dp[n][maxSlots].score > 0 ? dp[n][maxSlots].score.toFixed(2) : 'NONE FOUND'}`);
            console.log(`  Best 6-slot solution: ${dp[n][maxSlots-1].score > 0 ? dp[n][maxSlots-1].score.toFixed(2) : 'NONE FOUND'}`);
            console.log(`  Best 5-slot solution: ${dp[n][maxSlots-2].score > 0 ? dp[n][maxSlots-2].score.toFixed(2) : 'NONE FOUND'}`);
            
            // Debug: Log slot utilization for top results
            console.log('Top 3 solutions slot utilization:');
            validResults.slice(0, 3).forEach((result, i) => {
                console.log(`  Option ${i+1}: ${result.slotsUsed}/${maxSlots} slots, Score: ${result.totalScore.toFixed(2)}`);
                if (result.slotsUsed < maxSlots) {
                    console.log(`    ⚠️  Option ${i+1} not using all slots!`);
                }
            });
            
            // Debug: Performance check
            const endTime = performance.now();
            console.log(`DP processed ${filteredCompanies.length} companies successfully in ${(endTime - startTime).toFixed(0)}ms`);
            
            return validResults.slice(0, topN);
        }

        function displayMultipleResults(combinations, slots) {
            const resultsSection = document.getElementById('resultsSection');
            const resultsDiv = document.getElementById('optimizationResults');
            
            if (combinations.length === 0) {
                resultsDiv.innerHTML = '<p>No valid combinations found.</p>';
                resultsSection.classList.remove('hidden');
                return;
            }
            
            if (selectedBuildings.length === 0) {
                resultsDiv.innerHTML = '<p>Please select some buildings to optimize for.</p>';
                resultsSection.classList.remove('hidden');
                return;
            }
            
            if (selectedCompanies.length === 0) {
                resultsDiv.innerHTML = '<p>Please select some companies to optimize.</p>';
                resultsSection.classList.remove('hidden');
                return;
            }
            
            let html = '<h3>Top Company Combinations</h3>';
            
            // Add requirements summary
            html += `
                <div style="margin-bottom: 20px; padding: 15px; background: #f8f9fa; border-radius: 8px; border-left: 4px solid #007bff;">
                    <h4 style="margin: 0 0 10px 0; color: #2c3e50;">Selection Summary</h4>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; font-size: 14px;">
                        <div>
                            <strong>Selected Buildings (${selectedBuildings.length}):</strong>
                            <div style="margin-top: 5px; display: flex; flex-wrap: wrap; gap: 3px;">
                                ${selectedBuildings.map(building => {
                                    const isPriority = priorityBuildings.includes(building);
                                    return `<span style="background: ${isPriority ? '#e3f2fd' : '#e8f5e8'}; padding: 2px 6px; border-radius: 4px; font-size: 11px; ${isPriority ? 'border: 1px solid #007bff; font-weight: bold;' : ''}">${building}${isPriority ? ' ★' : ''}</span>`;
                                }).join('')}
                            </div>
                            ${priorityBuildings.length > 0 ? `
                                <div style="margin-top: 8px;">
                                    <strong>Priority Buildings (${priorityBuildings.length}):</strong>
                                    <div style="margin-top: 3px; display: flex; flex-wrap: wrap; gap: 3px;">
                                        ${priorityBuildings.map(building => 
                                            `<span style="background: #007bff; color: white; padding: 2px 6px; border-radius: 4px; font-size: 11px; font-weight: bold;">${building} ★</span>`
                                        ).join('')}
                                    </div>
                                </div>
                            ` : ''}
                        </div>
                        <div>
                            <strong>Selected Companies (${selectedCompanies.length}):</strong>
                            <div style="margin-top: 5px; max-height: 120px; overflow-y: auto;">
                                ${selectedCompanies.map((company, index) => {
                                    const isBasic = companies.basic && companies.basic.some(c => c.name === company.name);
                                    const isFlavored = companies.flavored && companies.flavored.some(c => c.name === company.name);
                                    const isCanal = company.special === 'canal';
                                    const isMandate = company.name === 'United Construction Conglomerate';
                                    
                                    let color = '#28a745';
                                    let typeLabel = 'Unknown';
                                    if (isCanal) { color = '#007bff'; typeLabel = 'Canal'; }
                                    else if (isMandate) { color = '#6f42c1'; typeLabel = 'Mandate'; }
                                    else if (isFlavored) { color = '#fd7e14'; typeLabel = 'Flavored'; }
                                    else if (isBasic) { color = '#6c757d'; typeLabel = 'Basic'; }
                                    
                                    // Debug: log company details for first few companies
                                    if (index < 5) {
                                        console.log(`Company ${index}: ${company.name} - ${typeLabel} (isBasic:${isBasic}, isFlavored:${isFlavored}, isCanal:${isCanal}, isMandate:${isMandate})`);
                                    }
                                    
                                    return `<span style="background: ${color}; color: white; padding: 2px 6px; border-radius: 4px; font-size: 11px; margin: 1px; display: inline-block;" title="${typeLabel}">${company.name}</span>`;
                                }).join('')}
                            </div>
                        </div>
                    </div>
                </div>
            `;
            
            combinations.forEach((combo, index) => {
                const regularCompanies = combo.companies.filter(c => c.special !== 'canal');
                const canalCompanies = combo.companies.filter(c => c.special === 'canal');
                
                // Calculate coverage (all buildings first, charters added later after industryCharters is defined)
                const buildingTypes = new Set();
                let totalBuildings = 0;
                combo.companies.forEach(company => {
                    // Add buildings
                    company.buildings.forEach(building => {
                        buildingTypes.add(building);
                        totalBuildings++;
                    });
                });
                
                let overlaps = totalBuildings - buildingTypes.size; // Will be updated after adding charters
                
                // Calculate selected buildings coverage for display (including charters)
                const selectedBuildingTypes = new Set();
                let totalSelectedBuildings = 0;
                combo.companies.forEach(company => {
                    // Only check buildings, NOT charters (charters are calculated separately)
                    company.buildings.forEach(building => {
                        if (selectedBuildings.includes(building)) {
                            selectedBuildingTypes.add(building);
                            totalSelectedBuildings++;
                        }
                    });
                });
                
                const selectedOverlaps = totalSelectedBuildings - selectedBuildingTypes.size;
                
                const prestigeGoods = combo.companies.reduce((count, company) => 
                    count + company.prestigeGoods.length, 0);
                
                // Charter selection: same logic as scoring function
                const takenCharters = [];
                const charterCounts = new Map();
                combo.companies.forEach(company => {
                    if (company.industryCharters && company.industryCharters.length > 0) {
                        // Same logic as scoring: only take charter if it's for a selected building AND not already covered by buildings
                        const charter = company.industryCharters[0]; // Take first charter
                        if (selectedBuildings.includes(charter) && !selectedBuildingTypes.has(charter)) {
                            takenCharters.push(charter);
                            charterCounts.set(charter, (charterCounts.get(charter) || 0) + 1);
                            console.log(`DISPLAY: ${company.name} takes charter: ${charter}`);
                        } else {
                            console.log(`DISPLAY: ${company.name} does NOT take charter: ${charter} (selected: ${selectedBuildings.includes(charter)}, covered: ${selectedBuildingTypes.has(charter)})`);
                        }
                    }
                });
                
                console.log(`DISPLAY: Total taken charters: ${takenCharters.length}`, takenCharters);
                
                // Use takenCharters for display
                const industryCharters = takenCharters;
                
                // Now add the taken charters to buildingTypes (after industryCharters is defined)
                industryCharters.forEach(charter => {
                    buildingTypes.add(charter);
                    totalBuildings++;
                    // Also add to selectedBuildingTypes since charters are for selected buildings
                    selectedBuildingTypes.add(charter);
                });
                
                // Update overlaps calculation now that charters are included
                overlaps = totalBuildings - buildingTypes.size;
                
                html += `
                    <div style="margin-bottom: 20px; padding: 15px; background: ${index === 0 ? '#f0f8ff' : '#f8f9fa'}; border-radius: 8px; border: ${index === 0 ? '2px solid #007bff' : '1px solid #dee2e6'};">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                            <h4 style="margin: 0; color: ${index === 0 ? '#007bff' : '#2c3e50'};">Option ${index + 1} ${index === 0 ? '(Best)' : ''}</h4>
                            <div style="font-size: 18px; font-weight: bold; color: ${index === 0 ? '#007bff' : '#2c3e50'};">Score: ${combo.totalScore.toFixed(2)}</div>
                        </div>
                        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: 10px; margin-bottom: 10px; font-size: 13px;">
                            <div><strong>Selected Buildings:</strong> ${selectedBuildingTypes.size}/${selectedBuildings.length}</div>
                            <div style="color: #007bff;"><strong>Priority Coverage:</strong> ${(() => {
                                const priorityCoverage = new Set();
                                selectedBuildingTypes.forEach(b => {
                                    if (priorityBuildings.includes(b)) priorityCoverage.add(b);
                                });
                                industryCharters.forEach(c => {
                                    if (priorityBuildings.includes(c)) priorityCoverage.add(c);
                                });
                                return priorityCoverage.size;
                            })()}/${priorityBuildings.length}</div>
                            <div><strong>All Buildings:</strong> ${buildingTypes.size}</div>
                            <div><strong>Prestige:</strong> ${prestigeGoods}</div>
                            <div><strong>Charters:</strong> ${industryCharters.length}</div>
                            <div><strong>Slots:</strong> ${regularCompanies.length}/${slots}</div>
                            <div style="color: ${selectedOverlaps > 0 ? '#dc3545' : '#28a745'};"><strong>Overlaps:</strong> ${selectedOverlaps}</div>
                        </div>
                        
                        <div style="margin-bottom: 10px;">
                            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 8px;">
                                ${combo.companies.map(company => {
                                    const isBasic = companies.basic.some(c => c.name === company.name);
                                    const isFlavored = companies.flavored.some(c => c.name === company.name);
                                    const isCanal = company.special === 'canal';
                                    const isMandate = company.name === 'United Construction Conglomerate';
                                    
                                    let borderColor = '#28a745'; // Default green
                                    let bgColor = '#f8f9fa';
                                    let companyType = '';
                                    
                                    if (isCanal) {
                                        borderColor = '#007bff';
                                        bgColor = '#f0f8ff';
                                        companyType = 'Canal';
                                    } else if (isMandate) {
                                        borderColor = '#6f42c1';
                                        bgColor = '#f8f0ff';
                                        companyType = 'Mandate';
                                    } else if (isFlavored) {
                                        borderColor = '#fd7e14';
                                        bgColor = '#fff3e0';
                                        companyType = 'Flavored';
                                    } else if (isBasic) {
                                        borderColor = '#6c757d';
                                        bgColor = '#f8f9fa';
                                        companyType = 'Basic';
                                    }
                                    
                                    return `
                                        <div style="padding: 6px; background: ${bgColor}; border-radius: 4px; border-left: 3px solid ${borderColor}; font-size: 11px;">
                                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 2px;">
                                                <strong style="font-size: 12px;">${company.name}${isCanal ? ' 🚢' : ''}</strong>
                                                <span style="background: ${borderColor}; color: white; padding: 1px 4px; border-radius: 3px; font-size: 9px;">${companyType}</span>
                                            </div>
                                            
                                            <div style="display: flex; flex-wrap: wrap; gap: 2px; margin-bottom: 2px;">
                                                ${company.buildings.map(building => {
                                                    const isSelected = selectedBuildings.includes(building);
                                                    const isPriority = priorityBuildings.includes(building);
                                                    const bgColor = isPriority ? '#e3f2fd' : (isSelected ? '#e8f5e8' : '#f5f5f5');
                                                    const textColor = isPriority ? '#1976d2' : '';
                                                    return `<span style="background: ${bgColor}; color: ${textColor}; padding: 1px 3px; border-radius: 3px; font-size: 9px; ${!isSelected ? 'opacity: 0.6;' : ''} ${isPriority ? 'font-weight: bold;' : ''}">${building}</span>`;
                                                }).join('')}
                                            </div>
                                            
                                            ${company.prosperityBonus ? `<div style="color: #28a745; font-weight: 500; margin-bottom: 2px;">⚡ ${company.prosperityBonus}</div>` : ''}
                                            
                                            ${company.prestigeGoods && company.prestigeGoods.length > 0 ? `<div style="color: #e83e8c; margin-bottom: 2px;">👑 ${company.prestigeGoods.map(pg => `${pg} (${prestigeGoodsMapping[pg] || 'Unknown'})`).join(', ')}</div>` : ''}
                                            
                                            ${(() => {
                                                // Show charter only if this company's charter is in the taken charters list
                                                if (company.industryCharters && company.industryCharters.length > 0) {
                                                    const charter = company.industryCharters[0];
                                                    // Check if this charter is in the taken charters for this combination
                                                    if (takenCharters.includes(charter)) {
                                                        const isPriority = priorityBuildings.includes(charter);
                                                        return `<div style="color: ${isPriority ? '#1976d2' : '#6f42c1'}; margin-bottom: 2px; ${isPriority ? 'font-weight: bold;' : ''}">📜 ${charter}</div>`;
                                                    }
                                                }
                                                return '';
                                            })()}
                                            
                                            ${company.requirements && (isFlavored || isCanal) ? `<div style="color: #dc3545; font-size: 10px; font-style: italic;">⚠️ ${company.requirements}</div>` : ''}
                                        </div>
                                    `;
                                }).join('')}
                            </div>
                        </div>
                        
                        <div style="display: grid; grid-template-columns: 2fr 1fr; gap: 15px; margin-bottom: 10px;">
                            <div>
                                <strong>Building Coverage:</strong>
                                <div style="margin-top: 3px;">
                                    <div style="display: flex; flex-wrap: wrap; gap: 2px; margin-bottom: 3px;">
                                        <span style="font-size: 10px; font-weight: bold; color: #007bff;">Priority (${Array.from(selectedBuildingTypes).filter(b => priorityBuildings.includes(b)).length + Array.from(industryCharters).filter(c => priorityBuildings.includes(c)).length}/${priorityBuildings.length}):</span>
                                        ${priorityBuildings.map(building => {
                                            // Check if priority building is covered by company buildings or industry charters
                                            const buildingCount = combo.companies.filter(c => c.buildings.includes(building)).length;
                                            const takenCharterCount = industryCharters.filter(charter => charter === building).length;
                                            const count = buildingCount + takenCharterCount;
                                            const covered = count > 0;
                                            return `<span style="background: ${!covered ? '#ffebee' : count > 1 ? '#fff3cd' : '#e3f2fd'}; padding: 1px 4px; border-radius: 3px; font-size: 9px; ${count > 1 ? 'border: 1px solid #ffc107;' : ''} ${!covered ? 'border: 1px solid #dc3545;' : 'border: 1px solid #007bff;'} font-weight: bold;">★${building}${count > 1 ? ` (${count})` : ''}${!covered ? ' ✗' : ''}</span>`;
                                        }).join('')}
                                    </div>
                                    <div style="display: flex; flex-wrap: wrap; gap: 2px; margin-bottom: 3px;">
                                        <span style="font-size: 10px; font-weight: bold; color: #28a745;">Other Selected (${selectedBuildingTypes.size - Array.from(selectedBuildingTypes).filter(b => priorityBuildings.includes(b)).length}/${selectedBuildings.length - priorityBuildings.filter(b => selectedBuildings.includes(b)).length}):</span>
                                        ${selectedBuildings.filter(b => !priorityBuildings.includes(b)).map(building => {
                                            // Check if building is covered by company buildings or industry charters (only first charter counts)
                                            const buildingCount = combo.companies.filter(c => c.buildings.includes(building)).length;
                                            const takenCharterCount = industryCharters.filter(charter => charter === building).length;
                                            const count = buildingCount + takenCharterCount;
                                            const covered = buildingTypes.has(building);
                                            return `<span style="background: ${!covered ? '#ffebee' : count > 1 ? '#fff3cd' : '#d4edda'}; padding: 1px 4px; border-radius: 3px; font-size: 9px; ${count > 1 ? 'border: 1px solid #ffc107;' : ''} ${!covered ? 'border: 1px solid #dc3545;' : ''}">${building}${count > 1 ? ` (${count})` : ''}${!covered ? ' ✗' : ''}</span>`;
                                        }).join('')}
                                    </div>
                                    <div style="display: flex; flex-wrap: wrap; gap: 2px;">
                                        <span style="font-size: 10px; font-weight: bold; color: #6c757d;">Other Buildings (${buildingTypes.size - selectedBuildingTypes.size}):</span>
                                        ${Array.from(buildingTypes).filter(b => !selectedBuildings.includes(b)).sort().map(building => {
                                            // Check if building is covered by company buildings or industry charters (only first charter counts)
                                            const buildingCount = combo.companies.filter(c => c.buildings.includes(building)).length;
                                            const takenCharterCount = industryCharters.filter(charter => charter === building).length;
                                            const count = buildingCount + takenCharterCount;
                                            return `<span style="background: #f8f9fa; padding: 1px 4px; border-radius: 3px; font-size: 9px; opacity: 0.7;">${building}${count > 1 ? ` (${count})` : ''}</span>`;
                                        }).join('')}
                                    </div>
                                </div>
                            </div>
                            
                            ${industryCharters.length > 0 ? `
                                <div>
                                    <strong>Industry Charters (${industryCharters.length}):</strong>
                                    <div style="display: flex; flex-wrap: wrap; gap: 3px; margin-top: 3px;">
                                        ${Array.from(charterCounts.entries()).sort().map(([charter, count]) => 
                                            `<span style="background: ${count > 1 ? '#ffcccb' : '#e7d4f7'}; padding: 2px 6px; border-radius: 8px; font-size: 10px;">${charter}${count > 1 ? ` (×${count})` : ''}</span>`
                                        ).join('')}
                                    </div>
                                </div>
                            ` : '<div></div>'}
                        </div>
                        
                        ${(() => {
                            // Calculate prestige goods coverage
                            const providedPrestigeGoods = new Set();
                            const prestigeGoodsByType = new Map();
                            
                            combo.companies.forEach(company => {
                                company.prestigeGoods.forEach(prestigeGood => {
                                    const baseType = prestigeGoodsMapping[prestigeGood];
                                    if (baseType) {
                                        providedPrestigeGoods.add(baseType);
                                        if (!prestigeGoodsByType.has(baseType)) {
                                            prestigeGoodsByType.set(baseType, []);
                                        }
                                        prestigeGoodsByType.get(baseType).push(prestigeGood);
                                    }
                                });
                            });
                            
                            if (requiredPrestigeGoods.length > 0 || providedPrestigeGoods.size > 0) {
                                return `
                                    <div style="margin-top: 10px; padding: 8px; background: #f8f9fa; border-radius: 4px;">
                                        <strong>Prestige Goods Coverage:</strong>
                                        ${requiredPrestigeGoods.length > 0 ? `
                                            <div style="margin-top: 5px;">
                                                <span style="font-size: 10px; font-weight: bold; color: #007bff;">Required (${requiredPrestigeGoods.filter(req => providedPrestigeGoods.has(req)).length}/${requiredPrestigeGoods.length}):</span>
                                                <div style="display: flex; flex-wrap: wrap; gap: 2px; margin-top: 2px;">
                                                    ${requiredPrestigeGoods.map(baseType => {
                                                        const isProvided = providedPrestigeGoods.has(baseType);
                                                        const goods = prestigeGoodsByType.get(baseType) || [];
                                                        return `<span style="background: ${isProvided ? '#e3f2fd' : '#ffebee'}; padding: 2px 4px; border-radius: 3px; font-size: 9px; border: 1px solid ${isProvided ? '#007bff' : '#dc3545'}; font-weight: bold;">${baseType}${isProvided ? ` (${goods.join(', ')})` : ' ✗'}</span>`;
                                                    }).join('')}
                                                </div>
                                            </div>
                                        ` : ''}
                                        ${providedPrestigeGoods.size > 0 ? `
                                            <div style="margin-top: 5px;">
                                                <span style="font-size: 10px; font-weight: bold; color: #6c757d;">All Provided (${providedPrestigeGoods.size}):</span>
                                                <div style="display: flex; flex-wrap: wrap; gap: 2px; margin-top: 2px;">
                                                    ${Array.from(prestigeGoodsByType.entries()).sort().map(([baseType, goods]) => 
                                                        `<span style="background: #f0f0f0; padding: 2px 4px; border-radius: 3px; font-size: 9px;">${baseType}: ${goods.join(', ')}</span>`
                                                    ).join('')}
                                                </div>
                                            </div>
                                        ` : ''}
                                    </div>
                                `;
                            }
                            return '';
                        })()}
                    </div>
                `;
            });
            
            resultsDiv.innerHTML = html;
            resultsSection.classList.remove('hidden');
        }

        // Test functions for debugging
        function runTests() {
            console.log('=== OPTIMIZATION DEBUG TESTS ===');
            
            // Current UI state analysis
            console.log('Current selectedBuildings:', selectedBuildings);
            console.log('Current priorityBuildings:', priorityBuildings);
            console.log('Paper Mill selected?', selectedBuildings.includes('Paper Mill'));
            console.log('Paper Mill priority?', priorityBuildings.includes('Paper Mill'));
            
            // Top solution analysis
            console.log('\n=== TOP SOLUTION ANALYSIS ===');
            const topSolution = document.querySelector('#optimizationResults .result-item');
            if (topSolution) {
                const companyElements = topSolution.querySelectorAll('strong');
                const companyNames = [];
                companyElements.forEach(el => {
                    const text = el.textContent.trim().replace(' 🚢', '');
                    if (text && !text.includes('Option') && !text.includes('Score') && !text.includes('Building') && !text.includes('Prestige')) {
                        companyNames.push(text);
                    }
                });
                console.log('Companies in top solution:', companyNames);
                
                const hasBunge = companyNames.some(name => name.includes('Bunge & Born'));
                const hasBasicPaper = companyNames.some(name => name.includes('Basic Paper'));
                
                console.log('Contains Bunge & Born:', hasBunge);
                console.log('Contains Basic Paper:', hasBasicPaper);
            } else {
                console.log('No optimization results found - run optimization first');
            }
            
            // Individual company analysis
            const basicPaper = allCompanies.find(c => c.name === 'Basic Paper');
            const bungeAndBorn = allCompanies.find(c => c.name === 'Bunge & Born');
            
            if (basicPaper && bungeAndBorn) {
                const basicPaperScore = calculateScore([basicPaper]);
                const bungeScore = calculateScore([bungeAndBorn]);
                
                console.log('\n=== INDIVIDUAL SCORES WITH CURRENT CONFIG ===');
                console.log('Basic Paper individual score:', basicPaperScore.toFixed(3));
                console.log('Bunge & Born individual score:', bungeScore.toFixed(3));
                console.log('Score difference (Basic Paper - Bunge):', (basicPaperScore - bungeScore).toFixed(3));
                
                console.log('\nBasic Paper covers selected buildings:', basicPaper.buildings.filter(b => selectedBuildings.includes(b)));
                console.log('Bunge & Born covers selected buildings:', bungeAndBorn.buildings.filter(b => selectedBuildings.includes(b)));
                
                console.log('\nBasic Paper covers priority buildings:', basicPaper.buildings.filter(b => priorityBuildings.includes(b)));
                console.log('Bunge & Born covers priority buildings:', bungeAndBorn.buildings.filter(b => priorityBuildings.includes(b)));
                
                if (basicPaperScore < bungeScore) {
                    console.log('\n🚨 BUG: Bunge & Born scores higher than Basic Paper despite Basic Paper covering priority building!');
                    console.log('This suggests there may be an issue with the DP algorithm or scoring logic.');
                } else {
                    console.log('\n✅ Basic Paper correctly scores higher than Bunge & Born');
                }
            }
            
            // Test case: Why is Bunge & Born chosen over Basic Paper?
            testBungeVsBasicPaper();
            
            // Debug charter processing in detail
            console.log('\n=== CHARTER PROCESSING DEBUG ===');
            const baseCompanies = [
                allCompanies.find(c => c.name === 'Basic Metalworks'),
                allCompanies.find(c => c.name === 'Basic Shipyards'),
                allCompanies.find(c => c.name === 'Basic Motors'),
                allCompanies.find(c => c.name === 'Basic Munitions'),
                allCompanies.find(c => c.name === 'Ferrocarril Central Córdoba'),
                allCompanies.find(c => c.name === 'Caribbean Petroleum Company')
            ].filter(c => c);
            
            if (basicPaper) {
                const comboWithBasicPaper = [...baseCompanies, basicPaper];
                
                console.log('Companies in Basic Paper combo:');
                comboWithBasicPaper.forEach((company, index) => {
                    console.log(`  ${index + 1}. ${company.name}:`);
                    console.log(`     Buildings: ${company.buildings.join(', ')}`);
                    console.log(`     Charters: ${company.industryCharters ? company.industryCharters.join(', ') : 'none'}`);
                });
                
                // Manually trace through charter processing
                console.log('\nManual charter processing trace:');
                const selectedBuildingTypes = new Set();
                let totalSelectedBuildings = 0;
                
                // First pass: add all buildings
                comboWithBasicPaper.forEach(company => {
                    company.buildings.forEach(building => {
                        if (selectedBuildings.includes(building)) {
                            selectedBuildingTypes.add(building);
                            totalSelectedBuildings++;
                            console.log(`  Added building: ${building} (from ${company.name})`);
                        }
                    });
                });
                
                console.log(`After buildings: selectedBuildingTypes = [${Array.from(selectedBuildingTypes).join(', ')}]`);
                
                // Second pass: process charters
                const takenCharters = [];
                comboWithBasicPaper.forEach(company => {
                    if (company.industryCharters && company.industryCharters.length > 0) {
                        const charter = company.industryCharters[0];
                        const isSelected = selectedBuildings.includes(charter);
                        const alreadyCovered = selectedBuildingTypes.has(charter);
                        
                        console.log(`  ${company.name} charter "${charter}": selected=${isSelected}, alreadyCovered=${alreadyCovered}`);
                        
                        if (isSelected && !alreadyCovered) {
                            takenCharters.push(charter);
                            selectedBuildingTypes.add(charter);
                            console.log(`    ✅ Charter taken: ${charter}`);
                        } else {
                            console.log(`    ❌ Charter rejected: ${charter} (selected=${isSelected}, covered=${alreadyCovered})`);
                        }
                    }
                });
                
                console.log(`Final taken charters: [${takenCharters.join(', ')}]`);
            }
            
            alert('Debug tests completed. Check browser console (F12) for detailed output.');
        }
        
        function testBungeVsBasicPaper() {
            console.log('\n=== TEST CASE: Bunge & Born vs Basic Paper ===');
            
            const bungeAndBorn = allCompanies.find(c => c.name === 'Bunge & Born');
            const basicPaper = allCompanies.find(c => c.name === 'Basic Paper');
            
            if (!bungeAndBorn || !basicPaper) {
                console.log('❌ Could not find one of the companies');
                return;
            }
            
            console.log('\n--- COMPANY DETAILS ---');
            console.log('Bunge & Born:');
            console.log('  Buildings:', bungeAndBorn.buildings);
            console.log('  Industry Charters:', bungeAndBorn.industryCharters);
            console.log('  Prestige Goods:', bungeAndBorn.prestigeGoods);
            console.log('  Prosperity Bonus:', bungeAndBorn.prosperityBonus);
            
            console.log('Basic Paper:');
            console.log('  Buildings:', basicPaper.buildings);
            console.log('  Industry Charters:', basicPaper.industryCharters);
            console.log('  Prestige Goods:', basicPaper.prestigeGoods);
            console.log('  Prosperity Bonus:', basicPaper.prosperityBonus);
            
            console.log('\n--- INDIVIDUAL SCORES ---');
            const bungeScore = calculateScore([bungeAndBorn]);
            const basicPaperScore = calculateScore([basicPaper]);
            console.log('Bunge & Born score:', bungeScore.toFixed(3));
            console.log('Basic Paper score:', basicPaperScore.toFixed(3));
            console.log('Score difference (Bunge - Basic Paper):', (bungeScore - basicPaperScore).toFixed(3));
            
            console.log('\n--- SCORE BREAKDOWN ---');
            
            // Analyze Bunge & Born score components
            console.log('Bunge & Born breakdown:');
            analyzeSingleCompanyScore(bungeAndBorn, 'Bunge & Born');
            
            console.log('Basic Paper breakdown:');
            analyzeSingleCompanyScore(basicPaper, 'Basic Paper');
            
            console.log('\n--- BUILDING COVERAGE ANALYSIS ---');
            console.log('Selected buildings:', selectedBuildings);
            console.log('Priority buildings:', priorityBuildings);
            
            const bungeSelectedBuildings = bungeAndBorn.buildings.filter(b => selectedBuildings.includes(b));
            const bungePriorityBuildings = bungeAndBorn.buildings.filter(b => priorityBuildings.includes(b));
            const basicSelectedBuildings = basicPaper.buildings.filter(b => selectedBuildings.includes(b));
            const basicPriorityBuildings = basicPaper.buildings.filter(b => priorityBuildings.includes(b));
            
            console.log('Bunge & Born covers selected buildings:', bungeSelectedBuildings);
            console.log('Bunge & Born covers priority buildings:', bungePriorityBuildings);
            console.log('Basic Paper covers selected buildings:', basicSelectedBuildings);
            console.log('Basic Paper covers priority buildings:', basicPriorityBuildings);
            
            if (bungeScore > basicPaperScore) {
                console.log('🚨 BUG FOUND: Bunge & Born scores higher than Basic Paper!');
                console.log('This should not happen given that Basic Paper covers selected/priority buildings and Bunge & Born covers none.');
            } else {
                console.log('✅ Individual scoring is correct. Issue must be in combination context.');
                
                // Now debug the DP combination issue
                debugDPCombinationIssue(bungeAndBorn, basicPaper);
            }
        }
        
        function debugDPCombinationIssue(bungeAndBorn, basicPaper) {
            console.log('\n=== DP COMBINATION DEBUGGING ===');
            
            // Test with a realistic combination from the current solution
            const baseCompanies = [
                allCompanies.find(c => c.name === 'Basic Metalworks'),
                allCompanies.find(c => c.name === 'Basic Shipyards'),
                allCompanies.find(c => c.name === 'Basic Motors'),
                allCompanies.find(c => c.name === 'Basic Munitions'),
                allCompanies.find(c => c.name === 'Ferrocarril Central Córdoba'),
                allCompanies.find(c => c.name === 'Caribbean Petroleum Company')
            ].filter(c => c);
            
            console.log('Base combination (6 companies):', baseCompanies.map(c => c.name));
            
            // Test adding Bunge & Born vs Basic Paper as the 7th company
            const comboWithBunge = [...baseCompanies, bungeAndBorn];
            const comboWithBasicPaper = [...baseCompanies, basicPaper];
            
            console.log('\n--- COMBINATION SCORING ---');
            
            // Check prestige goods requirements first
            const bungePrestigeCheck = checkPrestigeGoodRequirements(comboWithBunge);
            const basicPaperPrestigeCheck = checkPrestigeGoodRequirements(comboWithBasicPaper);
            
            console.log('Combo with Bunge & Born satisfies prestige goods:', bungePrestigeCheck);
            console.log('Combo with Basic Paper satisfies prestige goods:', basicPaperPrestigeCheck);
            
            if (!bungePrestigeCheck && !basicPaperPrestigeCheck) {
                console.log('🚨 NEITHER combination satisfies prestige goods requirements!');
                return;
            }
            
            if (!basicPaperPrestigeCheck) {
                console.log('🚨 BUG: Basic Paper combination rejected due to prestige goods - but it should satisfy Tools requirement');
                
                // Debug prestige goods in detail
                console.log('\n--- PRESTIGE GOODS DEBUG ---');
                console.log('Required prestige goods:', requiredPrestigeGoods);
                
                const basicPaperPrestigeGoods = new Set();
                comboWithBasicPaper.forEach(company => {
                    company.prestigeGoods.forEach(prestigeGood => {
                        const baseType = prestigeGoodsMapping[prestigeGood];
                        if (baseType) {
                            basicPaperPrestigeGoods.add(baseType);
                        }
                    });
                });
                
                console.log('Basic Paper combo provides prestige goods:', Array.from(basicPaperPrestigeGoods));
                console.log('Should include Tools:', basicPaperPrestigeGoods.has('Tools'));
                return;
            }
            
            // If prestige goods are satisfied, compare scores
            const bungeComboScore = calculateScore(comboWithBunge);
            const basicPaperComboScore = calculateScore(comboWithBasicPaper);
            
            console.log('Combo with Bunge & Born score:', bungeComboScore.toFixed(3));
            console.log('Combo with Basic Paper score:', basicPaperComboScore.toFixed(3));
            console.log('Score difference (Bunge - Basic Paper):', (bungeComboScore - basicPaperComboScore).toFixed(3));
            
            if (bungeComboScore > basicPaperComboScore) {
                console.log('🚨 BUG: Bunge combination scores higher than Basic Paper combination!');
                
                // Detailed combination analysis
                console.log('\n--- DETAILED COMBINATION ANALYSIS ---');
                analyzeCombinationScore(comboWithBunge, 'Combo with Bunge & Born');
                analyzeCombinationScore(comboWithBasicPaper, 'Combo with Basic Paper');
            } else {
                console.log('✅ Basic Paper combination scores higher as expected');
                console.log('🤔 DP algorithm issue: Not exploring Basic Paper path correctly');
            }
        }
        
        function analyzeCombinationScore(companies, name) {
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
            
            // Prestige goods
            const prestigeGoods = companies.reduce((count, company) => count + company.prestigeGoods.length, 0);
            
            // Overlaps
            const selectedOverlaps = totalSelectedBuildings - selectedBuildingTypes.size;
            
            console.log(`  Selected buildings covered: ${selectedBuildingTypes.size} (${Array.from(selectedBuildingTypes).join(', ')})`);
            console.log(`  Priority buildings from buildings: ${priorityFromBuildings}`);
            console.log(`  Priority buildings from charters: ${priorityFromCharters}`);
            console.log(`  Useful charters: ${takenCharters.length} (${takenCharters.join(', ')})`);
            console.log(`  Prestige goods: ${prestigeGoods}`);
            console.log(`  Building overlaps: ${selectedOverlaps}`);
            console.log(`  Total score: ${calculateScore(companies).toFixed(3)}`);
        }
        
        function analyzeSingleCompanyScore(company, name) {
            // Buildings
            const selectedBuildingCount = company.buildings.filter(b => selectedBuildings.includes(b)).length;
            const priorityBuildingCount = company.buildings.filter(b => priorityBuildings.includes(b)).length;
            
            console.log(`  ${name}:`);
            console.log(`    Selected buildings: ${selectedBuildingCount} (${company.buildings.filter(b => selectedBuildings.includes(b)).join(', ')})`);
            console.log(`    Priority buildings: ${priorityBuildingCount} (${company.buildings.filter(b => priorityBuildings.includes(b)).join(', ')})`);
            console.log(`    Prestige goods: ${company.prestigeGoods.length} (${company.prestigeGoods.join(', ')})`);
            console.log(`    Industry charters: ${company.industryCharters ? company.industryCharters.length : 0} (${company.industryCharters ? company.industryCharters.join(', ') : 'none'})`);
            
            // Calculate component scores
            let buildingScore = selectedBuildingCount;
            let priorityScore = priorityBuildingCount * 2;
            let prestigeScore = company.prestigeGoods.length * 0.1;
            
            console.log(`    Score components:`);
            console.log(`      Buildings: +${buildingScore}`);
            console.log(`      Priority bonus: +${priorityScore}`);
            console.log(`      Prestige: +${prestigeScore.toFixed(1)}`);
            console.log(`      Total individual: ${(buildingScore + priorityScore + prestigeScore).toFixed(1)}`);
        }
        
        // Initialize the application
        document.addEventListener('DOMContentLoaded', function() {
            loadCompanyData();
        });
        
        // Keep the old knapsack function for reference (not used anymore)
        function knapsackOptimize(companies, maxSlots) {
            const n = companies.length;
            
            // Calculate scores for each company
            const companyScores = companies.map(company => calculateScore([company]));
            
            // DP table: dp[i][w] = maximum score using first i companies with w slots
            const dp = Array(n + 1).fill().map(() => Array(maxSlots + 1).fill(0));
            const selected = Array(n + 1).fill().map(() => Array(maxSlots + 1).fill(false));
            
            // Fill DP table
            for (let i = 1; i <= n; i++) {
                for (let w = 0; w <= maxSlots; w++) {
                    const companyScore = companyScores[i - 1];
                    
                    if (1 <= w) { // Each company costs 1 slot
                        const withItem = dp[i - 1][w - 1] + companyScore;
                        const withoutItem = dp[i - 1][w];
                        
                        if (withItem > withoutItem) {
                            dp[i][w] = withItem;
                            selected[i][w] = true;
                        } else {
                            dp[i][w] = withoutItem;
                        }
                    } else {
                        dp[i][w] = dp[i - 1][w];
                    }
                }
            }
            
            // Backtrack to find selected companies
            const result = [];
            let w = maxSlots;
            for (let i = n; i > 0; i--) {
                if (selected[i][w]) {
                    result.push(companies[i - 1]);
                    w -= 1;
                }
            }
            
            return {
                companies: result,
                totalScore: dp[n][maxSlots],
                remainingSlots: maxSlots - result.length
            };
        }
