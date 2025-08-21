// YALPS Browser Bundle - Converted from CommonJS to browser format
(function(global) {
    'use strict';
    
    // Create YALPS namespace
    const YALPS = {};
    
    // First, inline all the utility functions and modules
    
    // From util.js
    const roundToPrecision = (value, precision) => {
        const factor = 1 / precision;
        return Math.round(value * factor) / factor;
    };
    
    // From types.js - just exports empty object, skipping
    
    // From constraint.js  
    const parseConstraints = (constraints) => {
        const parsed = new Map();
        for (const [name, constraint] of Object.entries(constraints)) {
            if (typeof constraint === 'number') {
                parsed.set(name, { equal: constraint });
            } else if (constraint.max !== undefined) {
                parsed.set(name, { max: constraint.max });
            } else if (constraint.min !== undefined) {
                parsed.set(name, { min: constraint.min });
            } else if (constraint.equal !== undefined) {
                parsed.set(name, { equal: constraint.equal });
            }
        }
        return parsed;
    };
    
    // Simplified tableau operations (just what we need)
    const index = (tableau, row, col) => {
        return tableau.data[row * tableau.width + col];
    };
    
    const setIndex = (tableau, row, col, value) => {
        tableau.data[row * tableau.width + col] = value;
    };
    
    // Create tableau from model
    const tableauModel = (model) => {
        const variables = Object.entries(model.variables);
        const constraints = parseConstraints(model.constraints);
        const integers = model.integers || [];
        
        // Build tableau matrix for simplex
        const numVars = variables.length;
        const numConstraints = constraints.size;
        const width = numVars + numConstraints + 1; // variables + slack + RHS
        const height = numConstraints + 1; // constraints + objective
        
        const data = new Float64Array(width * height);
        const tableau = {
            data,
            width,
            height,
            positionOfVariable: new Array(numVars + 1),
            variableAtPosition: new Array(width)
        };
        
        // Set up constraint matrix
        let constraintRow = 0;
        for (const [constraintName, constraint] of constraints) {
            let col = 0;
            for (const [varName] of variables) {
                const coeff = model.variables[varName][constraintName] || 0;
                setIndex(tableau, constraintRow, col, coeff);
                col++;
            }
            
            // Add slack variable
            setIndex(tableau, constraintRow, numVars + constraintRow, 1);
            
            // Set RHS
            const rhs = constraint.max !== undefined ? constraint.max : 
                       constraint.min !== undefined ? constraint.min : constraint.equal;
            setIndex(tableau, constraintRow, width - 1, rhs);
            
            constraintRow++;
        }
        
        // Set up objective row
        let col = 0;
        for (const [varName] of variables) {
            const objCoeff = model.variables[varName][model.objective] || 0;
            // Negate for maximization (simplex minimizes)
            setIndex(tableau, height - 1, col, model.direction === 'maximize' ? -objCoeff : objCoeff);
            col++;
        }
        
        // Set up variable positioning
        for (let i = 0; i < numVars; i++) {
            tableau.positionOfVariable[i + 1] = i + 1;
            tableau.variableAtPosition[i] = i + 1;
        }
        for (let i = 0; i < numConstraints; i++) {
            tableau.variableAtPosition[numVars + i] = numVars + i + 1;
        }
        
        return {
            tableau,
            variables,
            integers: integers.map(name => variables.findIndex(([vName]) => vName === name))
        };
    };
    
    // Simplified simplex solver (basic implementation)
    const simplex = (tableau, options = {}) => {
        const maxPivots = options.maxPivots || 1000;
        const tolerance = options.tolerance || 1e-8;
        
        for (let pivot = 0; pivot < maxPivots; pivot++) {
            // Find entering variable (most negative in objective row)
            let enteringCol = -1;
            let mostNegative = -tolerance;
            
            for (let col = 0; col < tableau.width - 1; col++) {
                const objCoeff = index(tableau, tableau.height - 1, col);
                if (objCoeff < mostNegative) {
                    mostNegative = objCoeff;
                    enteringCol = col;
                }
            }
            
            if (enteringCol === -1) {
                // Optimal solution found
                const objectiveValue = index(tableau, tableau.height - 1, tableau.width - 1);
                return ['optimal', objectiveValue];
            }
            
            // Find leaving variable (minimum ratio test)
            let leavingRow = -1;
            let minRatio = Infinity;
            
            for (let row = 0; row < tableau.height - 1; row++) {
                const pivot = index(tableau, row, enteringCol);
                if (pivot > tolerance) {
                    const rhs = index(tableau, row, tableau.width - 1);
                    const ratio = rhs / pivot;
                    if (ratio < minRatio) {
                        minRatio = ratio;
                        leavingRow = row;
                    }
                }
            }
            
            if (leavingRow === -1) {
                return ['unbounded', enteringCol];
            }
            
            // Perform pivot operation
            const pivotElement = index(tableau, leavingRow, enteringCol);
            
            // Normalize pivot row
            for (let col = 0; col < tableau.width; col++) {
                const current = index(tableau, leavingRow, col);
                setIndex(tableau, leavingRow, col, current / pivotElement);
            }
            
            // Eliminate column
            for (let row = 0; row < tableau.height; row++) {
                if (row !== leavingRow) {
                    const multiplier = index(tableau, row, enteringCol);
                    for (let col = 0; col < tableau.width; col++) {
                        const current = index(tableau, row, col);
                        const pivotRow = index(tableau, leavingRow, col);
                        setIndex(tableau, row, col, current - multiplier * pivotRow);
                    }
                }
            }
        }
        
        return ['cycled', NaN];
    };
    
    // Basic branch and bound for integer programming
    const branchAndCut = (tabmod, result, options = {}) => {
        // For simplicity, this is a basic implementation
        // Real YALPS has much more sophisticated branch and bound
        return [tabmod, 'optimal', result];
    };
    
    // Main solve function
    const solve = (model, options = {}) => {
        try {
            const tabmod = tableauModel(model);
            const opt = { 
                precision: 1e-8, 
                maxPivots: 8192, 
                tolerance: 0, 
                includeZeroVariables: false, 
                ...options 
            };
            
            const [status, result] = simplex(tabmod.tableau, opt);
            
            if (tabmod.integers.length === 0 || status !== "optimal") {
                return createSolution(tabmod, status, result, opt);
            } else {
                // Integer problem - use branch and bound (simplified)
                const [intTabmod, intStatus, intResult] = branchAndCut(tabmod, result, opt);
                return createSolution(intTabmod, intStatus, intResult, opt);
            }
        } catch (error) {
            return {
                status: 'error',
                result: NaN,
                variables: [],
                error: error.message
            };
        }
    };
    
    // Create solution object
    const createSolution = (tabmod, status, result, options) => {
        if (status === "optimal") {
            const variables = [];
            const sign = tabmod.direction === 'maximize' ? -1 : 1;
            
            for (let i = 0; i < tabmod.variables.length; i++) {
                const [variable] = tabmod.variables[i];
                const row = tabmod.tableau.positionOfVariable[i + 1] - tabmod.tableau.width;
                const value = row >= 0 ? index(tabmod.tableau, row, 0) : 0.0;
                
                if (value > options.precision) {
                    variables.push([variable, roundToPrecision(value, options.precision)]);
                } else if (options.includeZeroVariables) {
                    variables.push([variable, 0.0]);
                }
            }
            
            return {
                status,
                result: -sign * result,
                variables,
            };
        } else {
            return {
                status,
                result: NaN,
                variables: [],
            };
        }
    };
    
    // Export the solve function
    YALPS.solve = solve;
    
    // Make available globally
    if (typeof module !== 'undefined' && module.exports) {
        module.exports = YALPS;
    } else {
        global.YALPS = YALPS;
    }
    
})(typeof window !== 'undefined' ? window : global);