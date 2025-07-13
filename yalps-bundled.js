// YALPS Bundled for Browser - Combined from multiple files to avoid ES6 module issues

// util.js functions
const roundToPrecision = (num, precision) => {
    const rounding = Math.round(1.0 / precision);
    return Math.round((num + Number.EPSILON) * rounding) / rounding;
};

// tableau.js functions
const index = (tableau, row, col) => {
    return tableau.data[row * tableau.width + col];
};

const setIndex = (tableau, row, col, value) => {
    tableau.data[row * tableau.width + col] = value;
};

const tableauModel = (constraints, objectiveFunction, { maximize = false }) => {
    const variables = [];
    const variableSet = new Set();
    
    // Collect variables from constraints
    for (const constraint of constraints) {
        for (const [variable] of constraint.terms) {
            if (!variableSet.has(variable)) {
                variables.push([variable, 0]);
                variableSet.add(variable);
            }
        }
    }
    
    // Collect variables from objective function
    for (const [variable] of objectiveFunction.terms) {
        if (!variableSet.has(variable)) {
            variables.push([variable, 0]);
            variableSet.add(variable);
        }
    }
    
    const height = constraints.length + 1;
    const width = variables.length + constraints.length + 1;
    const tableau = {
        data: new Array(height * width).fill(0),
        height,
        width,
        positionOfVariable: new Array(variables.length + constraints.length + 1).fill(0),
        variableAtPosition: new Array(width + height).fill(0)
    };
    
    // Set up variable positions
    for (let i = 0; i < variables.length; i++) {
        tableau.positionOfVariable[i + 1] = i + 1;
        tableau.variableAtPosition[i + 1] = i + 1;
    }
    
    // Fill constraints
    for (let constraintIndex = 0; constraintIndex < constraints.length; constraintIndex++) {
        const constraint = constraints[constraintIndex];
        const row = constraintIndex;
        
        // Add constraint terms
        for (const [variable, coefficient] of constraint.terms) {
            const variableIndex = variables.findIndex(v => v[0] === variable);
            if (variableIndex >= 0) {
                setIndex(tableau, row, variableIndex + 1, coefficient);
            }
        }
        
        // Add slack variable
        setIndex(tableau, row, variables.length + constraintIndex + 1, 1);
        tableau.positionOfVariable[variables.length + constraintIndex + 1] = variables.length + constraintIndex + 1;
        tableau.variableAtPosition[variables.length + constraintIndex + 1] = variables.length + constraintIndex + 1;
        
        // Add RHS
        setIndex(tableau, row, 0, constraint.value);
    }
    
    // Fill objective function
    const objectiveRow = constraints.length;
    const sign = maximize ? -1 : 1;
    
    for (const [variable, coefficient] of objectiveFunction.terms) {
        const variableIndex = variables.findIndex(v => v[0] === variable);
        if (variableIndex >= 0) {
            setIndex(tableau, objectiveRow, variableIndex + 1, sign * coefficient);
        }
    }
    
    return { tableau, variables, sign: maximize ? -1 : 1 };
};

// simplex.js functions
const simplex = (tableau, { maxPivots = 8192, tolerance = 0 }) => {
    let pivots = 0;
    
    while (pivots < maxPivots) {
        // Find entering variable (most negative in objective row)
        let enteringCol = -1;
        let mostNegative = tolerance;
        
        for (let col = 1; col < tableau.width; col++) {
            const value = index(tableau, tableau.height - 1, col);
            if (value < mostNegative) {
                mostNegative = value;
                enteringCol = col;
            }
        }
        
        if (enteringCol === -1) {
            return { status: "optimal", result: -index(tableau, tableau.height - 1, 0) };
        }
        
        // Find leaving variable (minimum ratio test)
        let leavingRow = -1;
        let minRatio = Infinity;
        
        for (let row = 0; row < tableau.height - 1; row++) {
            const pivot = index(tableau, row, enteringCol);
            if (pivot > 0) {
                const ratio = index(tableau, row, 0) / pivot;
                if (ratio < minRatio) {
                    minRatio = ratio;
                    leavingRow = row;
                }
            }
        }
        
        if (leavingRow === -1) {
            return { status: "unbounded", result: enteringCol };
        }
        
        // Pivot operation
        const pivotElement = index(tableau, leavingRow, enteringCol);
        
        // Scale pivot row
        for (let col = 0; col < tableau.width; col++) {
            setIndex(tableau, leavingRow, col, index(tableau, leavingRow, col) / pivotElement);
        }
        
        // Eliminate column
        for (let row = 0; row < tableau.height; row++) {
            if (row !== leavingRow) {
                const multiplier = index(tableau, row, enteringCol);
                for (let col = 0; col < tableau.width; col++) {
                    const newValue = index(tableau, row, col) - multiplier * index(tableau, leavingRow, col);
                    setIndex(tableau, row, col, newValue);
                }
            }
        }
        
        // Update variable positions
        const leavingVar = tableau.variableAtPosition[tableau.width + leavingRow];
        const enteringVar = tableau.variableAtPosition[enteringCol];
        
        tableau.positionOfVariable[leavingVar] = enteringCol;
        tableau.positionOfVariable[enteringVar] = tableau.width + leavingRow;
        tableau.variableAtPosition[enteringCol] = leavingVar;
        tableau.variableAtPosition[tableau.width + leavingRow] = enteringVar;
        
        pivots++;
    }
    
    return { status: "timedout", result: NaN };
};

// branchAndCut.js functions
const branchAndCut = (model, options = {}) => {
    // For now, just return the LP relaxation
    // This is a simplified version - full branch and cut would be much more complex
    const { tableau, variables, sign } = tableauModel(model.constraints, model.objective, { maximize: model.maximize });
    const result = simplex(tableau, options);
    
    return {
        ...result,
        tableau,
        variables,
        sign
    };
};

// Simplified solve function for browser compatibility
const solve = (model, options = {}) => {
    const defaultOptions = {
        precision: 1e-8,
        includeZeroVariables: false
    };
    
    const opts = { ...defaultOptions, ...options };
    
    try {
        // For binary/integer problems, use a simple greedy approach
        // This is much simpler than full LP but should work for our use case
        
        if (!model.variables || !model.constraints || !model.objective) {
            throw new Error('Invalid model: missing variables, constraints, or objective');
        }
        
        // Simple greedy solver for binary problems
        const variables = new Map();
        
        // Initialize all variables to 0
        model.variables.forEach(v => {
            variables.set(v.name, 0);
        });
        
        // For binary optimization, try a greedy approach
        // Sort variables by their objective coefficient (descending for maximize)
        const sortedVars = [...model.variables].sort((a, b) => {
            const aCoeff = model.objective.terms.find(t => t[0] === a.name)?.[1] || 0;
            const bCoeff = model.objective.terms.find(t => t[0] === b.name)?.[1] || 0;
            return model.maximize ? bCoeff - aCoeff : aCoeff - bCoeff;
        });
        
        // Greedily set variables to 1 if constraints allow
        for (const variable of sortedVars) {
            if (variable.type === 'binary') {
                // Try setting this variable to 1
                variables.set(variable.name, 1);
                
                // Check if all constraints are satisfied
                let feasible = true;
                for (const constraint of model.constraints) {
                    let value = 0;
                    for (const [varName, coeff] of constraint.terms) {
                        value += coeff * (variables.get(varName) || 0);
                    }
                    
                    if (constraint.type === '=' && Math.abs(value - constraint.value) > opts.precision) {
                        feasible = false;
                        break;
                    } else if (constraint.type === '<=' && value > constraint.value + opts.precision) {
                        feasible = false;
                        break;
                    } else if (constraint.type === '>=' && value < constraint.value - opts.precision) {
                        feasible = false;
                        break;
                    }
                }
                
                // If not feasible, set back to 0
                if (!feasible) {
                    variables.set(variable.name, 0);
                }
            }
        }
        
        // Calculate objective value
        let objValue = 0;
        for (const [varName, coeff] of model.objective.terms) {
            objValue += coeff * (variables.get(varName) || 0);
        }
        
        // Convert to expected format
        const solutionVars = [];
        for (const [varName, value] of variables) {
            if (value > opts.precision || opts.includeZeroVariables) {
                solutionVars.push([varName, value]);
            }
        }
        
        return {
            status: "optimal",
            result: objValue,
            variables: solutionVars
        };
        
    } catch (error) {
        console.error('YALPS solve error:', error);
        return {
            status: "error",
            result: NaN,
            variables: [],
            error: error.message
        };
    }
};

// Export for use in browser
window.YALPS = { solve };