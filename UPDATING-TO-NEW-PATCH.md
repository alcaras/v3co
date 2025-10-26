# Updating to a New Victoria 3 Patch

This guide walks through updating the Victoria 3 Company Optimizer to support a new game patch.

## Prerequisites

- Python 3.x with PIL/Pillow installed (`pip install Pillow`)
- Git configured for GitHub
- Access to Victoria 3 game files

## Step 1: Backup Current Game Files

```bash
cd dist
mv game game_old
```

Add to `.gitignore` if not already present:
```
game_old/
```

## Step 2: Copy New Game Files

Copy the new patch game files to `dist/game/`:

```bash
# Copy from Victoria 3 installation directory
# Windows: C:\Program Files (x86)\Steam\steamapps\common\Victoria 3\game
# macOS: ~/Library/Application Support/Steam/steamapps/common/Victoria 3/game
# Linux: ~/.steam/steam/steamapps/common/Victoria 3/game

cp -r "/path/to/Victoria 3/game" dist/game
```

Key directories needed:
- `game/common/company_types/` - Company definitions
- `game/common/building_groups/` - Building information
- `game/localization/english/` - English text

## Step 3: Update Company Icons

### 3.1 Copy New Icon Files

Copy DDS icon files from the game to the workspace:

```bash
# From Victoria 3 installation
cp -r "/path/to/Victoria 3/game/gfx/interface/icons/company_icons" .
```

This should include:
- Basic company icons (root level)
- `historical_company_icons/` subfolder
- `company_backgrounds/` subfolder

### 3.2 Convert DDS to PNG

Update the conversion script if needed:

```bash
# Edit convert_dds_to_png.py to point to correct directory
# Then run:
python3 convert_dds_to_png.py
```

The script will:
- Convert all DDS files to PNG using PIL/Pillow
- Skip files that are already up-to-date
- Report conversion status

### 3.3 Copy PNGs to dist

```bash
# Backup old icons
cd dist/companies
cp -r png png_old

# Add to .gitignore if not present
echo "companies/png_old/" >> ../.gitignore

# Copy new PNGs
rsync -av --delete ../../company_icons/png/ png/
```

Verify the conversion:
```bash
# Should show all PNG files (210+ expected)
find dist/companies/png -name "*.png" | wc -l

# Check for new historical companies
comm -13 <(ls dist/companies/png_old/historical_company_icons/ | sort) \
         <(ls dist/companies/png/historical_company_icons/ | sort)
```

## Step 4: Run the Parser

```bash
cd dist
python3 victoria3_company_parser.py
```

This will:
- Parse all company types from `game/common/company_types/`
- Extract ownership categories, building requirements, bonuses
- Generate `index.html` with the complete UI
- Update `company_data_v6.json`

Check the output for any warnings or errors about:
- Missing company definitions
- New company categories
- Building types not recognized
- Icon files not found

## Step 5: Test Locally

Open the generated `index.html` in a web browser:

```bash
open dist/index.html
# or
python3 -m http.server 8000  # Then visit http://localhost:8000
```

Test the following:
- [ ] All companies load correctly
- [ ] Company tooltips show ownership category
- [ ] Ownership filter works (checkboxes and counts)
- [ ] Company icons display properly
- [ ] YALPS optimizer runs successfully
- [ ] Building filter works
- [ ] Country filter works
- [ ] Search functionality works

## Step 6: Review Changes

Check what's new in this patch:

```bash
# New companies
git diff company_data_v6.json

# New icons
comm -13 <(ls png_old/historical_company_icons/) \
         <(ls png/historical_company_icons/)

# Changed ownership categories
grep -r "ownership_category" company_data_v6.json | sort | uniq -c
```

## Step 7: Commit and Deploy

### 7.1 Commit Parser Updates

```bash
git add victoria3_company_parser.py index.html company_data_v6.json .gitignore
git commit -m "Update to Victoria 3 patch X.X - Add [feature summary]

- Update company data to patch X.X
- Add [new ownership categories/features]
- [Other significant changes]

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

### 7.2 Commit Icon Updates

```bash
git add companies/png/ icons/
git commit -m "Update company and building icons to Victoria 3 patch X.X

- Update all [N] company icons
- Add [N] new historical company icons: [list notable ones]
- Add new UI icons for [ownership categories/buildings/etc]

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

### 7.3 Push to GitHub

```bash
git push
```

GitHub Pages will automatically deploy the updated `index.html` to:
https://alcaras.github.io/v3co/

## Common Issues

### DDS Conversion Fails

If PIL can't convert DDS files:
```bash
# Install ImageMagick as fallback
brew install imagemagick  # macOS
sudo apt install imagemagick  # Linux
```

### Missing Ownership Categories

If new ownership types are added in a patch, update the parser:

1. Check `game/common/company_types/` for new `category = xxx` values
2. Add to the `category_map` in `victoria3_company_parser.py`:
   ```python
   category_map = {
       'aristocrat_owned': 'Partial Aristocrat',
       'bureaucrat_owned': 'Partial Bureaucrat',
       'academic_owned': 'Partial Academic',
       'shopkeeper_owned': 'Partial Shopkeeper',
       'new_category_owned': 'New Category Name'  # Add new ones here
   }
   ```
3. Add to `ownership_order` in `_generate_ownership_filter_section()`

### Missing Building Types

If companies reference new building types:
1. Check warnings in parser output
2. Add new building icons to `icons/` directory
3. Update building type mappings if needed

### Canal Companies or Special Cases

If the game adds new companies with special mechanics:
1. Review `specialCompanies` array in the JavaScript
2. Update special handling logic if needed

## Versioning

- Parser versioning: Increment in filename if major changes (e.g., `victoria3_company_parser_v8.py`)
- Company data: Uses `company_data_v6.json` (increment if format changes)
- Git commits: Tag releases with patch version (e.g., `git tag v1.9.0`)

## Notes

- The parser is at `dist/victoria3_company_parser.py` (production version)
- Development versions are in parent directory (v1-v7)
- Always work in `dist/` directory for production updates
- Keep `png_old/` and `game_old/` locally but don't commit them
