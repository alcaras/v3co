# Updating from Game Files

This document explains how to update the company data when Victoria 3 gets patched or updated.

## Quick Update

To update everything from the game files, run:

```bash
node update_from_game_files.mjs
```

This will:
1. ✅ Extract fresh localizations from `english/` folder
2. ✅ Update `game-localizations.mjs` with correct prestige goods and company names
3. ✅ Import company data from `game/` folder 
4. ✅ Generate new `companies_extracted.json` with proper names
5. ✅ Provide clear logging of what was updated

## Manual Steps (if needed)

If you need to do parts manually:

### 1. Update Localizations Only
```bash
# This updates just the mapping file
node -e "
import { extractLocalizations, generateMappingFile } from './update_from_game_files.mjs';
const mappings = extractLocalizations('./english');
generateMappingFile(mappings);
"
```

### 2. Update Company Data Only
```bash
# This updates just the company JSON
node game_data_importer.mjs game companies_extracted.json
```

## What Gets Updated

### Prestige Goods
- Maps `prestige_good_generic_tools` → `"Precision Tools"`
- Maps `prestige_good_generic_steel` → `"Refined Steel"`
- All 16 generic prestige goods get proper display names

### Company Names
- Maps `company_basic_agriculture_1` → `"Quality Grains Inc."`
- Maps `company_ford_motor` → `"Ford Motor Company"`
- All 207 company names get proper display names

### Building Names
- Uses authoritative game file names
- Consistent capitalization and pluralization
- Proper charter building names

## File Structure

```
game/                    # Victoria 3 game files (gitignored)
├── company_types/       # Company definitions
└── buildings/           # Building definitions

english/                 # English localizations (gitignored)
├── goods_l_english.yml  # Prestige goods names
└── companies_l_english.yml # Company names

game-localizations.mjs   # Generated mapping file
companies_extracted.json # Generated company data
update_from_game_files.mjs # Update script (gitignored)
```

## When to Update

- 🔄 **After Victoria 3 patches** - New companies or prestige goods
- 🔄 **After DLC releases** - New flavored companies
- 🔄 **If optimization fails** - Check for name mismatches
- 🔄 **If company names are lowercase** - Localization needs refresh

## Troubleshooting

### Problem: "0 localizations extracted"
- Check that `english/` folder exists
- Verify `goods_l_english.yml` and `companies_l_english.yml` are present
- Check file permissions

### Problem: "Infeasible LP" errors
- Usually means prestige goods names don't match
- Run the update script to sync names
- Check that "Tools" maps to "Precision Tools"

### Problem: Lowercase company names
- Means `game-localizations.mjs` is out of date
- Run the update script to refresh from English files

## Success Indicators

After running the update script, you should see:
- ✅ "Quality Grains Inc." instead of "company_basic_agriculture_1"
- ✅ "Precision Tools" instead of "Fine Tools"
- ✅ Clean structured logging with [INFO] tags
- ✅ Counts like "26 basic, 158 flavored" instead of "184 (184 w/ basic)"
- ✅ LP optimization works without "infeasible" errors