# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Victoria 3 Company Optimizer web application that helps players optimize their company selection in the strategy game Victoria 3. The project consists of:

- **Main Application**: `victoria3_company_optimizer_v2.html` - A single-page web application with embedded JavaScript
- **Data Source**: `companies_extracted.json` - Contains company data for basic, flavored, and canal companies
- **Local Server**: `server.py` - Simple Python HTTP server with CORS support for local development
- **Draft Version**: `draft/company_optimizer.html` - Earlier version of the optimizer
- **Wiki Data**: `wiki/` directory containing `.wiki` files with game data

## Architecture

### Frontend (HTML/CSS/JavaScript)
- **Single-page application** with no external dependencies
- **Embedded styling** using CSS Grid and Flexbox for responsive layout
- **Vanilla JavaScript** for all functionality including:
  - Dynamic company filtering and selection
  - Building type selection interface
  - Knapsack optimization algorithm for company selection
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
# http://localhost:8080/victoria3_company_optimizer_v2.html
```

The Python server (`server.py`) provides:
- Static file serving from the current directory
- CORS headers for cross-origin requests
- Serves on port 8080 by default

### File Structure
```
/
├── victoria3_company_optimizer_v2.html  # Main application
├── companies_extracted.json            # Company data
├── server.py                           # Development server
├── draft/
│   └── company_optimizer.html          # Draft version
└── wiki/
    ├── base.wiki                       # Base company data
    ├── buildings.wiki                  # Building information
    ├── flavored.wiki                   # Flavored company data
    └── list-of-buildings.wiki          # Building lists
```

## Code Architecture Details

### JavaScript Application Structure
- **Data Loading**: Asynchronous loading of company data from JSON file
- **State Management**: Global variables for selected buildings, companies, and filters
- **UI Updates**: Event-driven updates using DOM manipulation
- **Optimization**: Knapsack algorithm implementation for optimal company selection

### CSS Architecture
- **Modern CSS**: Uses CSS Grid, Flexbox, and CSS variables
- **Responsive Design**: Adapts to different screen sizes
- **Component-based**: Modular styles for different UI components
- **Animations**: Smooth transitions and hover effects

### Key JavaScript Functions
- `loadCompanyData()`: Loads and processes company data from JSON
- `optimizeCompanies()`: Runs knapsack optimization algorithm
- `displayCompanies()`: Renders company list with filtering
- `calculateScore()`: Scoring function for optimization (building coverage + prestige goods)

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

The heart of the application is a **knapsack optimization algorithm** that finds the best company combinations:

### Scoring System
- **Building Coverage**: +1 point per unique building type covered
- **Industry Charters**: +1 point per useful charter (non-redundant)
- **Priority Buildings**: +2 points per priority building covered
- **Prestige Goods**: +0.1 points per prestige good
- **Non-Selected Buildings**: +0.01 points per non-selected building type
- **Overlap Penalty**: -0.2 points per duplicate building
- **Charter Penalties**: Various penalties for redundant charters

### Charter Selection Rules
- Companies can have multiple charters but can only take **one**
- Charters are **optional** - only taken if they provide new building coverage
- Only take charters for buildings that are **selected** by the user
- Charters for unselected buildings contribute 0 to score

### Algorithm Flow
1. **Company Filtering**: User selects which companies to consider
2. **Building Selection**: User selects which building types to optimize for
3. **DP Optimization**: `generateTopCombinations()` uses dynamic programming to find optimal combinations
4. **Multiple Solutions**: Generates top N combinations, prioritizing those using all available company slots

## Key Functions

- `calculateScore(companies)`: Core scoring function implementing the game rules
- `generateTopCombinations(companies, maxSlots, topN, canalCompanies)`: DP knapsack optimization
- `optimizeCompanies()`: Main optimization entry point, separates regular vs canal companies
- `displayMultipleResults(combinations)`: Renders optimization results with detailed breakdowns

## Development Notes

- **No Build Process**: The application runs directly in the browser without compilation
- **No External Dependencies**: Uses only vanilla HTML, CSS, and JavaScript
- **Local Development**: Requires the Python server for CORS support when loading JSON data
- **Self-contained**: All code is embedded in the HTML file for easy deployment
- **Debug Mode**: Use "Debug Tests" button to run scoring validation tests