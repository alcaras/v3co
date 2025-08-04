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
- [ ] **Test changes took effect**: Use grep to verify HTML contains expected changes
- [ ] Test in browser for layout issues
- [ ] Check that prestige goods appear in correct columns
- [ ] Verify building icons display properly
- [ ] Test back-to-top navigation links
- [ ] Confirm table sorting works

### Verification Testing Process
After making changes to Python code, always verify the changes were applied to the generated HTML:

**CSS/Styling Changes:**
```bash
# Verify specific CSS rules were generated correctly
grep -A10 -B5 "class-name\|css-property" index.html

# Example: Check company icon sizing
grep -A10 "company-tooltip.*company-icon" index.html
```

**JavaScript Changes:**
```bash
# Verify JavaScript functions were generated correctly  
grep -A20 "function functionName" index.html

# Example: Check tooltip positioning
grep -A10 "Smart tooltip positioning" index.html
```

**HTML Content Changes:**
```bash
# Verify specific companies show expected content
grep -A3 -B3 "CompanyName" index.html

# Example: Check prestige goods icons
grep -A2 -B2 "LKAB\|lkab" index.html
```

**Icon/Mapping Changes:**
```bash
# Verify mappings were generated correctly
grep "mapping-name.*expected-value" index.html

# Example: Check historical company mappings  
grep -A5 -B5 "east_india_company.*gb_eic" index.html
```

This verification step is **critical** because:
- Python changes don't automatically appear in HTML until parser runs
- Generated HTML might not match expected changes due to syntax errors
- Verifying in HTML confirms the change worked end-to-end

## Troubleshooting Prestige Goods Icon Issues

### Problem: Company showing services icon instead of correct prestige good icon

**Symptoms**: Company has prestige good in tooltip but shows generic services icon in HTML tables

**Root Causes & Solutions**:

1. **Missing hardcoded prestige goods mapping**
   - **Check**: Search for prestige good in hardcoded dictionary (around line 3240)
   - **Fix**: Add `'prestige_good_name': 'base_good'` to hardcoded dictionary
   - **Example**: `'prestige_good_swedish_bar_iron': 'iron'`

2. **Missing building-to-goods mapping**
   - **Check**: Verify company's buildings produce the right base good
   - **Fix**: Add `'building_name': 'base_good'` to building_to_goods dictionary (around line 60)
   - **Example**: `'building_synthetics_plants': 'dye'`

3. **Missing icon file**
   - **Check**: Look for `icons/24px-Prestige_[name].png` file
   - **Fix**: Add icon mapping to both locations (around lines 885 and 2760):
     ```python
     icon_mappings = {
         'prestige_good_base_name': 'existing_icon_name'
     }
     ```
   - **Example**: `'swedish_bar_iron': 'oregrounds_iron'`

4. **Special case needed**
   - **Check**: If base goods don't match (e.g., `luxury_clothes` vs `clothes`)
   - **Fix**: Add special case to `company_has_prestige_for_building()` method (around line 1875)

### Systematic Debugging Process:
1. Find company in game files: `grep -r "company_name" game/company_types/`
2. Check prestige good definition: `grep "prestige_good_name" game/prestige_goods/00_prestige_goods.txt`
3. Verify building mappings: `grep "building_name" victoria3_company_parser.py`
4. Check hardcoded dictionary: `grep "prestige_good_name" victoria3_company_parser.py`
5. Test available icons: `ls icons/ | grep "prestige_good_base"`

### Examples Fixed:
- **BASF German Aniline**: Missing `building_synthetics_plants` → `dye` mapping
- **Russian-American Company**: Changed `building_whaling_station` from `oil` to `meat`
- **Maison Worth**: Added special case for `luxury_clothes` + `building_textile_mills`
- **Burmese Teak**: Added icon mapping `'burmese_teak': 'teak'`
- **Swedish Bar Iron**: Added hardcoded mapping + icon mapping `'swedish_bar_iron': 'oregrounds_iron'`

## Other Common Issues & Solutions

### Problem: Company tooltip shows blank/missing company icon

**Root Cause**: JavaScript `getCompanyIconPath()` function missing historical company mappings

**Symptoms**: Company icon displays correctly in HTML table but not in tooltip card

**Solution**:
- **Check**: Compare Python `self.historical_mappings` with JavaScript `historicalMappings`
- **Fix**: Ensure JavaScript function is generated dynamically from Python mappings (around line 2846)
- **Example**: East India Company needs `"east_india_company": "gb_eic"` mapping

### Problem: Tooltip positioning goes off-screen

**Root Cause**: Basic boundary detection not accounting for viewport scroll or all edges

**Symptoms**: Tooltips disappear near screen edges, especially when scrolled

**Solution**:
- **Check**: Tooltip positioning logic handles all viewport boundaries
- **Fix**: Use proper coordinate systems (`pageX/pageY` with `scrollX/scrollY + innerWidth/innerHeight`)
- **Implementation**: Smart positioning with fallback strategies for all edge cases

### Problem: Column sorting broken after prestige goods changes

**Root Cause**: Inconsistent logic between HTML generation and sorting functions

**Symptoms**: Tables sort charter buildings between prestige and base instead of prestige > base > charter > blank

**Solution**:
- **Check**: Ensure `get_companies_with_building()` uses same prestige logic as HTML generation
- **Fix**: Synchronize prestige detection logic across all functions
- **Test**: Verify sorting maintains correct order after any prestige goods changes

### Problem: Companies showing missing flags in table rows

**Root Cause**: Country codes assigned to companies but missing from Python `country_flags` and `country_names` dictionaries

**Symptoms**: Empty flag cells (`<td class="flag-column"></td>`) while tooltip shows correct country

**Solution**:
- **Check**: Compare JavaScript tooltip country mappings with Python flag dictionaries (around lines 120-145)
- **Fix**: Add missing country codes to both `country_flags` and `country_names` dictionaries
- **Test**: Verify flags appear in table and match wiki organization in `wiki/flavored.wiki`

**Systematic Debugging Process**:
1. Count missing flags: `grep -o 'flag-column"></td>' index.html | wc -l` 
2. Find non-basic companies: `grep -A8 'flag-column"></td>' index.html | grep 'data-company=' | grep -v 'company_basic_'`
3. Check country assignments in JavaScript tooltip data for reference mappings
4. Cross-reference with `wiki/flavored.wiki` to verify correct country associations
5. Add missing mappings in batches and test

**Important**: Basic companies (`company_basic_*`) correctly have no flags. Focus only on historical companies.

### Key Debugging Principles Learned:

1. **Systematic Company-by-Company Analysis**: When facing widespread issues, use systematic approach rather than trying to fix architecture
2. **Always Push Both Parser AND HTML**: GitHub Pages displays `index.html`, so both files must be committed
3. **Coordinate System Consistency**: Mix of page/viewport coordinates causes positioning bugs
4. **JavaScript-Python Synchronization**: Dynamic generation prevents JavaScript from getting out of sync with Python logic
5. **Icon Mapping Patterns**: Missing icons need mappings in BOTH company name and building column generation functions
6. **Flag Mapping Completeness**: JavaScript tooltip mappings serve as reference for missing Python flag mappings
7. **Wiki Verification**: Always verify country assignments match `wiki/flavored.wiki` organization structure

## Future Considerations
- Company icon coverage could be improved (many missing icons)
- Consider adding search/filter functionality
- Potential for mobile responsiveness improvements
- Could add more detailed tooltips or company comparison features