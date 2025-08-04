# Victoria 3 Company Analysis Tool - Development Notes

## Project Overview
Interactive web tool for analyzing Victoria 3 companies, their building requirements, formation conditions, and available industry charters. Processes game data files to generate comprehensive HTML reports.

**Live Demo**: https://alcaras.github.io/v3co/
**Repository**: https://github.com/alcaras/v3co

## Key Architecture

### Core Components
- **`victoria3_company_parser.py`** - Main Python script that parses game files and generates HTML
- **`index.html`** - Generated interactive web interface (DO NOT EDIT MANUALLY)
- **`company_data.json`** - Parsed company data cache
- **Game data directories** - Victoria 3 game files for parsing

### Directory Structure
```
dist/                           # Root directory (git repository)
├── victoria3_company_parser.py # Main parser script
├── index.html                  # Generated HTML (auto-generated)
├── company_data.json          # Company data cache
├── buildings/                 # Building icon assets (64px PNGs)
├── companies/png/             # Company icon assets
├── icons/                     # Goods and UI icons (24px/40px PNGs)
├── game/                      # Victoria 3 game data files (gitignored)
│   ├── company_types/         # Company definitions (.txt files)
│   ├── buildings/             # Building definitions
│   └── [other game data]/
└── wiki/                      # Wikipedia mapping data
    └── flavored.wiki          # Company-to-country mappings
```

## Key Technical Details

### Building Order & Categorization
The tool organizes buildings in a specific logical order based on Victoria 3 wiki structure:
1. **Extraction** - Mining, logging, etc.
2. **Manufacturing Industries** - Processing and production
3. **Infrastructure + Urban Facilities** - Railways, ports, urban centers
4. **Agriculture + Plantations + Ranches** - Food production

This order is defined in `wiki_building_order` list in the Python script.

### Icon System
- **Building Icons**: Uses `building_name_mappings` dictionary for icon path resolution
- **Company Icons**: Historical company icons in `companies/png/` directory
- **Missing Icons**: Script warns about missing company icons but continues processing

### UI Features
- **Three-column table of contents** with building icons
- **Back-to-top navigation** buttons on each building section
- **Sortable tables** with company data
- **Tooltips** showing detailed company information
- **Symbol legend** explaining prestige goods and other symbols

## Development Workflow

### Running the Parser
```bash
python3 victoria3_company_parser.py
```
This regenerates `index.html` with latest data. Always use Python 3 for UTF-8 encoding support.

### Testing Changes
1. Run the parser script
2. Open `index.html` in browser to verify changes
3. Check for encoding errors or missing icons in terminal output

### Deployment
**CRITICAL**: Always commit and push both the parser changes AND the updated `index.html` file.
```bash
git add victoria3_company_parser.py index.html
git commit -m "Your commit message"
git push
```
The `index.html` file is what GitHub Pages displays, so it must be pushed for changes to appear on the live site.

## Common Issues & Solutions

### Encoding Errors
- **Problem**: ASCII codec errors when processing international characters
- **Solution**: Always use `python3` (not `python`) and ensure UTF-8 encoding in file operations

### Missing Building Icons
- **Problem**: Building icons show alt text instead of images
- **Solution**: Use existing `get_building_icon_path()` method and `building_name_mappings` dictionary

### Directory Navigation
- **Problem**: Running commands in wrong directory
- **Solution**: Always check `pwd` and ensure you're in the git repository root

## Code Structure

### Main Classes & Methods
- `CompanyParser` - Main parser class
- `setup_building_to_goods()` - Maps buildings to prestige goods (CRITICAL for bug fix)
- `get_building_icon_path()` - Resolves building icon paths
- `generate_html_report()` - Creates the interactive HTML interface

### HTML Generation
The script generates a complete HTML page with:
- Embedded CSS styling
- JavaScript for tooltips and interactivity
- Three-column flexbox layout for table of contents
- Sortable tables with company data

### Key Data Mappings
- **`building_to_goods`** - Maps buildings to their prestige goods
- **`building_name_mappings`** - Maps building IDs to icon filenames
- **`wiki_companies`** - Maps company names to countries from Wikipedia data

## Recent Changes
- Fixed prestige goods categorization bug (2025-08-04)
- Added logical building order based on Victoria 3 wiki structure
- Implemented three-column table of contents with building icons
- Added back-to-top navigation buttons
- Consolidated directory structure (removed nested v3co-repo folder)
- Restored live demo URL in README

## Testing Checklist
When making changes:
- [ ] Run `python3 victoria3_company_parser.py` successfully
- [ ] Check terminal for encoding errors or warnings
- [ ] Verify `index.html` generates properly
- [ ] Test in browser for layout issues
- [ ] Check that prestige goods appear in correct columns
- [ ] Verify building icons display properly
- [ ] Test back-to-top navigation links
- [ ] Confirm table sorting works

## Future Considerations
- Company icon coverage could be improved (many missing icons)
- Consider adding search/filter functionality
- Potential for mobile responsiveness improvements
- Could add more detailed tooltips or company comparison features