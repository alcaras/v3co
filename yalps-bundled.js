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

// Main solve function
const solve = (model, options = {}) => {
    const defaultOptions = {
        precision: 1e-8,
        checkCycles: false,
        maxPivots: 8192,
        tolerance: 0,
        includeZeroVariables: false
    };
    
    const opts = { ...defaultOptions, ...options };
    
    try {
        let result;
        
        // Check if we need integer programming
        const hasIntegerVars = model.variables && model.variables.some(v => v.type === 'integer' || v.type === 'binary');
        
        if (hasIntegerVars) {
            result = branchAndCut(model, opts);
        } else {
            const { tableau, variables, sign } = tableauModel(model.constraints, model.objective, { maximize: model.maximize });
            result = simplex(tableau, opts);
            result.tableau = tableau;
            result.variables = variables;
            result.sign = sign;
        }
        
        // Build solution
        if (result.status === "optimal" || (result.status === "timedout" && !Number.isNaN(result.result))) {
            const solutionVars = [];
            for (let i = 0; i < result.variables.length; i++) {
                const [variable] = result.variables[i];
                const row = result.tableau.positionOfVariable[i + 1] - result.tableau.width;
                const value = row >= 0 ? index(result.tableau, row, 0) : 0.0;
                if (value > opts.precision || opts.includeZeroVariables) {
                    solutionVars.push([variable, roundToPrecision(Math.max(0, value), opts.precision)]);
                }
            }
            
            return {
                status: result.status,
                result: -result.sign * result.result,
                variables: solutionVars
            };
        } else if (result.status === "unbounded") {
            const variable = result.tableau.variableAtPosition[result.result] - 1;
            return {
                status: "unbounded",
                result: result.sign * Infinity,
                variables: (0 <= variable && variable < result.variables.length)
                    ? [[result.variables[variable][0], Infinity]]
                    : []
            };
        } else {
            return {
                status: result.status,
                result: NaN,
                variables: []
            };
        }
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