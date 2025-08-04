# Victoria 3 Company Analysis Tool

🌐 **Live Demo: https://alcaras.github.io/v3co/**

An interactive web tool for analyzing Victoria 3 companies, their building requirements, formation conditions, and available industry charters.

## Features

- **Interactive Company Tables**: Sortable tables showing all companies organized by building type
- **Company Tooltips**: Detailed company information including formation requirements, prestige bonuses, and industry charters
- **Visual Icons**: Historical company icons and building/goods icons for easy identification
- **Formation Requirements**: Complete formation requirements from game files including state, technology, and building level requirements
- **Industry Charters**: Shows base buildings and possible extension buildings for each company
- **Country Assignments**: Companies mapped to their historical countries based on Wikipedia data

## Quick Start

1. Open `index.html` in your web browser
2. Browse companies by building type using the navigation menu
3. Hover over company names for detailed information
4. Click column headers to sort tables

## Files

- `index.html` - Main interactive web interface
- `company_data.json` - Parsed company data from Victoria 3 game files
- `victoria3_company_parser.py` - Python parser for extracting company data
- `companies/` - Company icon assets
- `icons/` - Building and goods icon assets
- `game/` - Victoria 3 game data files
- `wiki/` - Wikipedia mapping data

## Data Sources

- Company definitions extracted from Victoria 3 game files
- Historical company names and country assignments from Wikipedia
- Building and formation requirements from game mechanics
- Company icons from Victoria 3 assets

## About

This tool processes Victoria 3's company system to provide a comprehensive overview of:
- 185+ companies across all DLCs
- Formation requirements and prerequisites  
- Available industry charters and extensions
- Historical context and country assignments

Perfect for players planning their industrial development and understanding company mechanics.

## Browser Compatibility

Works in all modern browsers. No server required - runs entirely client-side.