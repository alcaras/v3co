# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Victoria 3 Company Optimizer web application that helps players optimize their company selection in the strategy game Victoria 3. The project consists of:

- **Main Application**: `index.html` - Modular single-page web application
- **LP Solver Module**: `lp-solver.mjs` - Linear Programming optimization using YALPS
- **Scoring Module**: `scoring.mjs` - Company scoring and validation functions  
- **Company Data Module**: `company-data.mjs` - Data loading and management
- **Prestige Goods Module**: `prestige-goods.mjs` - Prestige goods mapping and utilities
- **Data Source**: `companies_extracted.json` - Contains company data for basic, flavored, and canal companies
- **Local Server**: `server.py` - Simple Python HTTP server with CORS support for local development
- **Test Suite**: `tests/` directory containing comprehensive test coverage

## Architecture

### Modern Modular Design (Refactored 2025)
- **ES6 Modules**: Separated into focused `.mjs` files for better maintainability
- **Linear Programming**: Uses YALPS library for optimal Integer Linear Programming
- **Test-Driven Development**: Comprehensive test suite with specific bug regression tests
- **Single-page application** with modular architecture:
  - Dynamic company filtering and selection
  - Building type selection interface  
  - LP optimization for company selection
  - Interactive search and filtering

### Data Structure
The application works with three types of companies from `companies_extracted.json`:
- **Basic Companies**: Standard companies available to all players
- **Flavored Companies**: Country/region-specific companies with special requirements
- **Canal Companies**: Special companies (Panama/Suez Canal) that don't count against company slots

### Key Features
- **Building Selection**: Choose which building types to optimize for
- **Company Filtering**: Filter companies by region, search terms, or building coverage
- **Optimization Algorithm**: Uses knapsack algorithm to maximize building coverage and prestige goods
- **Interactive UI**: Click to select companies, regions, and buildings with real-time updates

## Development Commands

### Running the Application
```bash
# Start local development server
python3 server.py

# Then access the application at:
# http://localhost:8080/index.html
```

The Python server (`server.py`) provides:
- Static file serving from the current directory
- CORS headers for cross-origin requests
- Serves on port 8080 by default

### File Structure
```
/
├── index.html                          # Main application (modular)
├── lp-solver.mjs                       # LP optimization module
├── scoring.mjs                         # Scoring functions module  
├── company-data.mjs                    # Data management module
├── prestige-goods.mjs                  # Prestige goods utilities
├── companies_extracted.json            # Company data
├── server.py                           # Development server
├── YALPS.mjs                          # Linear Programming library
├── tests/                             # Test suite
│   ├── test_canal_companies_bug.mjs   # Canal companies regression test
│   ├── test_lp_solver_steel_requirement.mjs  # Steel requirement test
│   └── (many other test files)
└── wiki/
    ├── base.wiki                       # Base company data
    ├── buildings.wiki                  # Building information
    ├── flavored.wiki                   # Flavored company data
    └── list-of-buildings.wiki          # Building lists
```

## Code Architecture Details

### Modular JavaScript Architecture
- **lp-solver.mjs**: YALPS-based Integer Linear Programming optimization
- **scoring.mjs**: Company scoring, validation, and combination scoring functions
- **company-data.mjs**: Data loading, charter expansion, and company management
- **prestige-goods.mjs**: Prestige goods mapping and validation utilities
- **index.html**: Main UI logic with module imports

### Key Modules and Functions

#### LP Solver Module (`lp-solver.mjs`)
- `solveIntegerLP()`: Main optimization using YALPS Integer Linear Programming
- `calculateIndividualScore()`: Individual company variant scoring
- **Handles**: Company slots, prestige goods constraints, charter conflicts, canal companies

#### Scoring Module (`scoring.mjs`)  
- `calculateScore()`: Legacy scoring function for compatibility
- `calculateCombinationScore()`: Alternative scoring approach
- `isValidSolution()`: Solution validation with prestige goods requirements
- `checkPrestigeGoodRequirements()`: Validates prestige goods coverage

#### Company Data Module (`company-data.mjs`)
- `loadCompanyData()`: Asynchronous JSON loading with fallback
- `expandCompaniesWithCharters()`: Creates company variants with charter options
- **Handles**: Company categorization, building extraction, charter generation

#### CSS Architecture
- **Modern CSS**: Uses CSS Grid, Flexbox, and CSS variables
- **Responsive Design**: Adapts to different screen sizes
- **Component-based**: Modular styles for different UI components
- **Animations**: Smooth transitions and hover effects

## Data Format

Companies in `companies_extracted.json` have the following structure:
```json
{
  "name": "Company Name",
  "buildings": ["Building 1", "Building 2"],
  "industryCharters": ["Charter 1"],
  "prestigeGoods": ["Prestige Good 1"],
  "prosperityBonus": "+10% throughput bonus",
  "requirements": "Specific game requirements",
  "region": "Americas|Europe|Asia|Middle East|Africa",
  "country": "Country Name",
  "special": "canal" // For canal companies
}
```

## Core Optimization Algorithm

The heart of the application is an **Integer Linear Programming (ILP) solver** using YALPS that finds optimal company combinations:

### LP Optimization Approach (YALPS)
- **Integer Linear Programming**: Uses YALPS library for guaranteed optimal solutions
- **Binary Variables**: Each company variant gets a binary decision variable (0 or 1)
- **Building Coverage Variables**: Indicator variables for "at least one company covers this building"
- **Constraint-Based**: Hard constraints ensure game rules are followed exactly

### Key Constraints
- **Company Slots**: Regular companies limited by available slots (canal companies exempt)
- **One Variant Per Company**: At most one variant per base company  
- **Prestige Goods Uniqueness**: At most one company per prestige good (canal companies exempt)
- **Required Prestige Goods**: OR constraints for Steel requirement (Refined Steel OR Sheffield Steel)
- **Charter Uniqueness**: At most one company can take each charter type

### Scoring System
- **Building Coverage**: Points for covering selected buildings (once per building type)
- **Priority Buildings**: Higher weight for priority buildings
- **Prestige Goods**: Additive bonus per prestige good
- **Non-Selected Buildings**: Small bonus for covering additional buildings

### Special Handling
- **Canal Companies**: Don't use company slots, exempt from prestige goods uniqueness
- **Charter Variants**: Companies can optionally take one charter for additional buildings
- **Prestige Goods OR Logic**: Steel requirement satisfied by ANY steel-providing company

### Algorithm Flow
1. **Company Expansion**: Generate variants for each company with charter options
2. **LP Model Setup**: Create binary variables and constraints for optimization
3. **YALPS Optimization**: Solve Integer Linear Programming problem
4. **Solution Extraction**: Extract selected company variants from optimal solution

## Key LP Solver Functions

- `solveIntegerLP()`: Main YALPS-based optimization with full constraint modeling
- `calculateIndividualScore()`: Individual company scoring for LP objective function
- `expandCompaniesWithCharters()`: Generate company variants with charter options  
- `displayMultipleResults()`: Renders optimization results with detailed breakdowns

## Development Notes

- **No Build Process**: The application runs directly in the browser without compilation
- **ES6 Modules**: Uses native browser module support with `.mjs` files
- **Local Development**: Requires the Python server for CORS support when loading JSON data
- **Modular Architecture**: Separated into focused modules for maintainability
- **Test-Driven Development**: Comprehensive test suite for regression testing

## Recent Refactoring (2025)

### Major Architectural Changes
- **Extracted LP Solver**: ~400 lines moved from index.html to lp-solver.mjs
- **Modular Design**: Split monolithic file into focused modules
- **Legacy Code Removal**: Removed ~400 lines of unused DP solver functions
- **Test Coverage**: Added regression tests for critical bugs

### Key Bugs Fixed
- **Canal Companies Bug**: Both Panama and Suez Canal companies now selectable simultaneously
- **Steel Requirement**: Fixed OR logic for Steel prestige good (Refined Steel OR Sheffield Steel)
- **Function Conflicts**: Resolved duplicate function declarations causing JavaScript errors
- **Module Scope**: Fixed global scope issues with onclick handlers in ES6 modules

### Testing Strategy
- **Regression Tests**: Specific tests for each major bug (canal companies, steel requirement)
- **LP Solver Tests**: Direct testing of YALPS optimization with real scenarios
- **Module Testing**: Individual testing of extracted modules
- **Integration Testing**: End-to-end testing matching actual application behavior

### Development Best Practices
- **Test-Driven Development**: Write failing test first, then fix the bug
- **Module Separation**: Each module has single responsibility
- **Function Exposure**: Global window functions for HTML onclick compatibility
- **Commit Messages**: Detailed commit messages documenting changes and fixes