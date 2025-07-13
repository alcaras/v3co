# Victoria 3 Company Optimizer

A sophisticated web-based optimization tool for selecting companies in Victoria 3, using **Linear Programming** to find optimal company combinations based on building coverage, prestige goods, and industry charters.

## 🎯 Features

- **Linear Programming Optimization**: Uses YALPS (Yet Another Linear Programming Solver) for mathematically optimal company selection
- **Building Coverage Optimization**: Maximizes coverage of selected buildings while avoiding redundancy
- **Charter System**: Treats industry charters as company variants for optimal selection
- **Priority Buildings**: Higher weighting for strategically important buildings
- **Prestige Goods Management**: Ensures required prestige goods are covered without conflicts
- **Required Companies**: Mark specific companies as mandatory for the solution
- **Canal Company Support**: Special handling for Panama/Suez Canal companies (don't use regular slots)
- **Export/Import**: Save and load your optimization configurations

## 🚀 Quick Start

1. **Run the local server**:
   ```bash
   python3 server.py
   ```

2. **Open the application**:
   Navigate to `http://localhost:8081/victoria3_company_optimizer_v3.html`

3. **Select your preferences**:
   - Choose buildings to optimize for
   - Mark priority buildings (right-click)
   - Select companies to consider
   - Mark required companies (right-click)
   - Set required prestige goods

4. **Optimize**:
   Click "🎯 Optimize Companies" to find the optimal selection

## 🔧 Technology

- **Frontend**: Pure HTML, CSS, and JavaScript (no external dependencies)
- **Optimization**: YALPS Linear Programming solver with custom heap implementation
- **Algorithm**: Integer Linear Programming with constraint satisfaction
- **Data**: Victoria 3 company data extracted from the game

## 📊 How It Works

The optimizer uses a **linearized constraint optimization model**:

### Decision Variables
- `x_i`: Binary variables for each company variant (base company + charter combinations)
- `covered_building`: Binary indicators for whether each building type is covered

### Objective Function
```
Maximize: Σ(building_scores × covered_building) + Σ(prestige_scores × x_i)
```

### Key Constraints
- **Slot limit**: `Σ(x_i × slots_used) ≤ max_slots`
- **Building coverage**: `covered_building ≤ Σ(x_i for companies providing building)`
- **Company uniqueness**: At most one variant per base company
- **Prestige good conflicts**: At most one company per prestige good
- **Required constraints**: Specific companies/prestige goods must be included

This approach naturally avoids redundancy because:
- Building coverage points are awarded only once per building type
- The LP selects the minimum companies needed to maximize coverage
- Remaining slots are used for additional coverage rather than redundant buildings

## 📁 Project Structure

```
/
├── victoria3_company_optimizer_v3.html  # Main application
├── companies_extracted.json            # Company data
├── server.py                           # Development server
├── CLAUDE.md                          # Development documentation
├── heap.js                            # Custom heap implementation for YALPS
├── YALPS-0.5.6/                      # Linear Programming solver
└── README.md                          # This file
```

## 🎮 Game Integration

The optimizer uses real Victoria 3 data including:
- **26 Basic Companies**: Available to all nations
- **158 Flavored Companies**: Country/region-specific companies with requirements
- **2 Canal Companies**: Panama and Suez Canal (don't use regular company slots)
- **47 Building Types**: All production buildings that companies can provide
- **49 Prestige Goods**: Correctly mapped to their base types

## 🔄 Recent Improvements

- **✅ Fixed redundancy issues**: LP now properly avoids selecting multiple companies for the same building
- **✅ Linearized constraints**: Proper constraint optimization model replacing flawed dynamic programming
- **✅ Canal company support**: Panama/Suez can take charters without using regular slots
- **✅ Corrected prestige goods**: Fixed all prestige good mappings based on official game data
- **✅ Enhanced UI**: Priority building indicators, export/import functionality
- **✅ Comprehensive debugging**: Detailed optimization output for analysis

## 🤝 Contributing

This project was developed collaboratively using Claude Code. The optimization algorithm evolved from simple greedy approaches to sophisticated linear programming through iterative debugging and improvement.

## 📄 License

Open source project for Victoria 3 community use.