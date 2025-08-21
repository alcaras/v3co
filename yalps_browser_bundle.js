// YALPS Browser Bundle - Auto-generated from Node.js modules
(function(global) {
    'use strict';
    
    // Create YALPS namespace
    const YALPS = {};
    const exports = {};
    const module = { exports: exports };
    
    // Internal modules store
    const modules = {};
    
    // Require function for internal modules
    function require(moduleName) {
        if (moduleName.startsWith('./')) {
            const cleanName = moduleName.replace('./', '').replace('.js', '');
            return modules[cleanName] || {};
        }
        return {};
    }
    

    // === util.js ===
    (function() {
        const exports = {};
        const module = { exports: exports };
        
        "use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.roundToPrecision = void 0;
const roundToPrecision = (num, precision) => {
    const rounding = Math.round(1.0 / precision);
    return Math.round((num + Number.EPSILON) * rounding) / rounding;
};
exports.roundToPrecision = roundToPrecision;

        
        modules['util'] = module.exports;
    })();

    // === types.js ===
    (function() {
        const exports = {};
        const module = { exports: exports };
        
        "use strict";
Object.defineProperty(exports, "__esModule", { value: true });

        
        modules['types'] = module.exports;
    })();

    // === constraint.js ===
    (function() {
        const exports = {};
        const module = { exports: exports };
        
        "use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.inRange = exports.equalTo = exports.greaterEq = exports.lessEq = void 0;
/**
 * Returns a `Constraint` that specifies something should be less than or equal to `value`.
 * Equivalent to `{ max: value }`.
 */
const lessEq = (value) => ({ max: value });
exports.lessEq = lessEq;
/**
 * Returns a `Constraint` that specifies something should be greater than or equal to `value`.
 * Equivalent to `{ min: value }`.
 */
const greaterEq = (value) => ({ min: value });
exports.greaterEq = greaterEq;
/**
 * Returns a `Constraint` that specifies something should be exactly equal to `value`.
 * Equivalent to `{ equal: value }`.
 */
const equalTo = (value) => ({ equal: value });
exports.equalTo = equalTo;
/**
 * Returns a `Constraint` that specifies something should be between `lower` and `upper` (both inclusive).
 * Equivalent to `{ min: lower, max: upper }`.
 */
const inRange = (lower, upper) => ({ min: lower, max: upper });
exports.inRange = inRange;

        
        modules['constraint'] = module.exports;
    })();

    // === tableau.js ===
    (function() {
        const exports = {};
        const module = { exports: exports };
        
        "use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.tableauModel = exports.update = exports.index = void 0;
const index = (tableau, row, col) => tableau.matrix[Math.imul(row, tableau.width) + col];
exports.index = index;
const update = (tableau, row, col, value) => {
    tableau.matrix[Math.imul(row, tableau.width) + col] = value;
};
exports.update = update;
const convertToIterable = (seq) => typeof seq[Symbol.iterator] === "function" // eslint-disable-line
    ? seq
    : Object.entries(seq);
// prettier-ignore
const convertToSet = (set) => set === true ? true
    : set === false ? new Set()
        : set instanceof Set ? set
            : new Set(set);
const tableauModel = (model) => {
    const { direction, objective, integers, binaries } = model;
    const sign = direction === "minimize" ? -1.0 : 1.0;
    const constraintsIter = convertToIterable(model.constraints);
    const variablesIter = convertToIterable(model.variables);
    const variables = Array.isArray(variablesIter) ? variablesIter : Array.from(variablesIter);
    const binaryConstraintCol = [];
    const ints = [];
    if (integers != null || binaries != null) {
        const binaryVariables = convertToSet(binaries);
        const integerVariables = binaryVariables === true ? true : convertToSet(integers);
        for (let i = 1; i <= variables.length; i++) {
            const [key] = variables[i - 1];
            if (binaryVariables === true || binaryVariables.has(key)) {
                binaryConstraintCol.push(i);
                ints.push(i);
            }
            else if (integerVariables === true || integerVariables.has(key)) {
                ints.push(i);
            }
        }
    }
    const constraints = new Map();
    for (const [key, constraint] of constraintsIter) {
        const bounds = constraints.get(key) ?? { row: NaN, lower: -Infinity, upper: Infinity };
        bounds.lower = Math.max(bounds.lower, constraint.equal ?? constraint.min ?? -Infinity);
        bounds.upper = Math.min(bounds.upper, constraint.equal ?? constraint.max ?? Infinity);
        // if (rows.lower > rows.upper) return ["infeasible", NaN]
        if (!constraints.has(key))
            constraints.set(key, bounds);
    }
    let numConstraints = 1;
    for (const constraint of constraints.values()) {
        constraint.row = numConstraints;
        numConstraints += (Number.isFinite(constraint.lower) ? 1 : 0) + (Number.isFinite(constraint.upper) ? 1 : 0);
    }
    const width = variables.length + 1;
    const height = numConstraints + binaryConstraintCol.length;
    const numVars = width + height;
    const matrix = new Float64Array(width * height);
    const positionOfVariable = new Int32Array(numVars);
    const variableAtPosition = new Int32Array(numVars);
    const tableau = { matrix, width, height, positionOfVariable, variableAtPosition };
    for (let i = 0; i < numVars; i++) {
        positionOfVariable[i] = i;
        variableAtPosition[i] = i;
    }
    for (let c = 1; c < width; c++) {
        for (const [constraint, coef] of convertToIterable(variables[c - 1][1])) {
            if (constraint === objective) {
                (0, exports.update)(tableau, 0, c, sign * coef);
            }
            const bounds = constraints.get(constraint);
            if (bounds != null) {
                if (Number.isFinite(bounds.upper)) {
                    (0, exports.update)(tableau, bounds.row, c, coef);
                    if (Number.isFinite(bounds.lower)) {
                        (0, exports.update)(tableau, bounds.row + 1, c, -coef);
                    }
                }
                else if (Number.isFinite(bounds.lower)) {
                    (0, exports.update)(tableau, bounds.row, c, -coef);
                }
            }
        }
    }
    for (const bounds of constraints.values()) {
        if (Number.isFinite(bounds.upper)) {
            (0, exports.update)(tableau, bounds.row, 0, bounds.upper);
            if (Number.isFinite(bounds.lower)) {
                (0, exports.update)(tableau, bounds.row + 1, 0, -bounds.lower);
            }
        }
        else if (Number.isFinite(bounds.lower)) {
            (0, exports.update)(tableau, bounds.row, 0, -bounds.lower);
        }
    }
    for (let b = 0; b < binaryConstraintCol.length; b++) {
        const row = numConstraints + b;
        (0, exports.update)(tableau, row, 0, 1.0);
        (0, exports.update)(tableau, row, binaryConstraintCol[b], 1.0);
    }
    return { tableau, sign, variables, integers: ints };
};
exports.tableauModel = tableauModel;

        
        modules['tableau'] = module.exports;
    })();

    // === simplex.js ===
    (function() {
        const exports = {};
        const module = { exports: exports };
        
        "use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.simplex = void 0;
const tableau_js_1 = require("./tableau.js");
const util_js_1 = require("./util.js");
const pivot = (tableau, row, col) => {
    const quotient = (0, tableau_js_1.index)(tableau, row, col);
    const leaving = tableau.variableAtPosition[tableau.width + row];
    const entering = tableau.variableAtPosition[col];
    tableau.variableAtPosition[tableau.width + row] = entering;
    tableau.variableAtPosition[col] = leaving;
    tableau.positionOfVariable[leaving] = col;
    tableau.positionOfVariable[entering] = tableau.width + row;
    const nonZeroColumns = [];
    // (1 / quotient) * R_pivot -> R_pivot
    for (let c = 0; c < tableau.width; c++) {
        const value = (0, tableau_js_1.index)(tableau, row, c);
        if (Math.abs(value) > 1e-16) {
            (0, tableau_js_1.update)(tableau, row, c, value / quotient);
            nonZeroColumns.push(c);
        }
        else {
            (0, tableau_js_1.update)(tableau, row, c, 0.0);
        }
    }
    (0, tableau_js_1.update)(tableau, row, col, 1.0 / quotient);
    // -M[r, col] * R_pivot + R_r -> R_r
    for (let r = 0; r < tableau.height; r++) {
        if (r === row)
            continue;
        const coef = (0, tableau_js_1.index)(tableau, r, col);
        if (Math.abs(coef) > 1e-16) {
            for (let i = 0; i < nonZeroColumns.length; i++) {
                const c = nonZeroColumns[i];
                (0, tableau_js_1.update)(tableau, r, c, (0, tableau_js_1.index)(tableau, r, c) - coef * (0, tableau_js_1.index)(tableau, row, c));
            }
            (0, tableau_js_1.update)(tableau, r, col, -coef / quotient);
        }
    }
};
// Checks if the simplex method has encountered a cycle.
const hasCycle = (history, tableau, row, col) => {
    // This whole function seems somewhat inefficient,
    // but there was no? noticeable impact in the benchmarks.
    history.push([tableau.variableAtPosition[tableau.width + row], tableau.variableAtPosition[col]]);
    // the minimum length of a cycle is 6
    for (let length = 6; length <= Math.trunc(history.length / 2); length++) {
        let cycle = true;
        for (let i = 0; i < length; i++) {
            const item = history.length - 1 - i;
            const [row1, col1] = history[item];
            const [row2, col2] = history[item - length];
            if (row1 !== row2 || col1 !== col2) {
                cycle = false;
                break;
            }
        }
        if (cycle)
            return true;
    }
    return false;
};
// Finds the optimal solution given some basic feasible solution.
const phase2 = (tableau, options) => {
    const pivotHistory = [];
    const { precision, maxPivots, checkCycles } = options;
    for (let iter = 0; iter < maxPivots; iter++) {
        // Find the entering column/variable
        let col = 0;
        let value = precision;
        for (let c = 1; c < tableau.width; c++) {
            const reducedCost = (0, tableau_js_1.index)(tableau, 0, c);
            if (reducedCost > value) {
                value = reducedCost;
                col = c;
            }
        }
        if (col === 0)
            return ["optimal", (0, util_js_1.roundToPrecision)((0, tableau_js_1.index)(tableau, 0, 0), precision)];
        // Find the leaving row/variable
        let row = 0;
        let minRatio = Infinity;
        for (let r = 1; r < tableau.height; r++) {
            const value = (0, tableau_js_1.index)(tableau, r, col);
            if (value <= precision)
                continue; // pivot entry must be positive
            const rhs = (0, tableau_js_1.index)(tableau, r, 0);
            const ratio = rhs / value;
            if (ratio < minRatio) {
                row = r;
                minRatio = ratio;
                if (ratio <= precision)
                    break; // ratio is 0, lowest possible
            }
        }
        if (row === 0)
            return ["unbounded", col];
        if (checkCycles && hasCycle(pivotHistory, tableau, row, col))
            return ["cycled", NaN];
        pivot(tableau, row, col);
    }
    return ["cycled", NaN];
};
// Transforms a tableau into a basic feasible solution.
const phase1 = (tableau, options) => {
    const pivotHistory = [];
    const { precision, maxPivots, checkCycles } = options;
    for (let iter = 0; iter < maxPivots; iter++) {
        // Find the leaving row/variable
        let row = 0;
        let rhs = -precision;
        for (let r = 1; r < tableau.height; r++) {
            const value = (0, tableau_js_1.index)(tableau, r, 0);
            if (value < rhs) {
                rhs = value;
                row = r;
            }
        }
        if (row === 0)
            return phase2(tableau, options);
        // Find the entering column/variable
        let col = 0;
        let maxRatio = -Infinity;
        for (let c = 1; c < tableau.width; c++) {
            const coefficient = (0, tableau_js_1.index)(tableau, row, c);
            if (coefficient < -precision) {
                const ratio = -(0, tableau_js_1.index)(tableau, 0, c) / coefficient;
                if (ratio > maxRatio) {
                    maxRatio = ratio;
                    col = c;
                }
            }
        }
        if (col === 0)
            return ["infeasible", NaN];
        if (checkCycles && hasCycle(pivotHistory, tableau, row, col))
            return ["cycled", NaN];
        pivot(tableau, row, col);
    }
    return ["cycled", NaN];
};
exports.simplex = phase1;

        
        modules['simplex'] = module.exports;
    })();

    // === branchAndCut.js ===
    (function() {
        const exports = {};
        const module = { exports: exports };
        
        "use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.branchAndCut = void 0;
const tableau_js_1 = require("./tableau.js");
const simplex_js_1 = require("./simplex.js");
const heap_1 = __importDefault(require("heap"));
const buffer = (matrixLength, posVarLength) => ({
    matrix: new Float64Array(matrixLength),
    positionOfVariable: new Int32Array(posVarLength),
    variableAtPosition: new Int32Array(posVarLength),
});
// Creates a new tableau with additional cut constraints from a buffer.
const applyCuts = (tableau, { matrix, positionOfVariable, variableAtPosition }, cuts) => {
    const { width, height } = tableau;
    matrix.set(tableau.matrix);
    for (let i = 0; i < cuts.length; i++) {
        const [sign, variable, value] = cuts[i];
        const r = (height + i) * width;
        const pos = tableau.positionOfVariable[variable];
        if (pos < width) {
            matrix[r] = sign * value;
            matrix.fill(0.0, r + 1, r + width);
            matrix[r + pos] = sign;
        }
        else {
            const row = (pos - width) * width;
            matrix[r] = sign * (value - matrix[row]);
            for (let c = 1; c < width; c++) {
                matrix[r + c] = -sign * matrix[row + c];
            }
        }
    }
    positionOfVariable.set(tableau.positionOfVariable);
    variableAtPosition.set(tableau.variableAtPosition);
    const length = width + height + cuts.length;
    for (let i = width + height; i < length; i++) {
        positionOfVariable[i] = i;
        variableAtPosition[i] = i;
    }
    return {
        matrix: matrix.subarray(0, tableau.matrix.length + width * cuts.length),
        width,
        height: height + cuts.length,
        positionOfVariable: positionOfVariable.subarray(0, length),
        variableAtPosition: variableAtPosition.subarray(0, length),
    };
};
// Finds the integer variable with the most fractional value.
const mostFractionalVar = (tableau, intVars) => {
    let highestFrac = 0.0;
    let variable = 0;
    let value = 0.0;
    for (let i = 0; i < intVars.length; i++) {
        const intVar = intVars[i];
        const row = tableau.positionOfVariable[intVar] - tableau.width;
        if (row < 0)
            continue;
        const val = (0, tableau_js_1.index)(tableau, row, 0);
        const frac = Math.abs(val - Math.round(val));
        if (frac > highestFrac) {
            highestFrac = frac;
            variable = intVar;
            value = val;
        }
    }
    return [variable, value, highestFrac];
};
// Runs the branch and cut algorithm to solve an integer problem.
// Requires the non-integer solution as input.
const branchAndCut = (tabmod, initResult, options) => {
    const { tableau, sign, integers } = tabmod;
    const { precision, maxIterations, tolerance, timeout } = options;
    const [initVariable, initValue, initFrac] = mostFractionalVar(tableau, integers);
    // Wow, the initial solution is integer
    if (initFrac <= precision)
        return [tabmod, "optimal", initResult];
    const branches = new heap_1.default((x, y) => x[0] - y[0]);
    branches.push([initResult, [[-1, initVariable, Math.ceil(initValue)]]]);
    branches.push([initResult, [[1, initVariable, Math.floor(initValue)]]]);
    // Set aside arrays/buffers to be reused over the course of the algorithm.
    // One set of buffers stores the state of the current best solution.
    // The other is used to solve the current candidate solution.
    // The two buffers are "swapped" once a new best solution is found.
    const maxExtraRows = integers.length * 2;
    const matrixLength = tableau.matrix.length + maxExtraRows * tableau.width;
    const posVarLength = tableau.positionOfVariable.length + maxExtraRows;
    let candidateBuffer = buffer(matrixLength, posVarLength);
    let solutionBuffer = buffer(matrixLength, posVarLength);
    const optimalThreshold = initResult * (1.0 - sign * tolerance);
    const stopTime = timeout + Date.now();
    let timedout = Date.now() >= stopTime; // in case options.timeout <= 0
    let solutionFound = false;
    let bestEval = Infinity;
    let bestTableau = tableau;
    let iter = 0;
    while (iter < maxIterations && !branches.empty() && bestEval >= optimalThreshold && !timedout) {
        const [relaxedEval, cuts] = branches.pop();
        if (relaxedEval > bestEval)
            break; // the remaining branches are worse than the current best solution
        const currentTableau = applyCuts(tableau, candidateBuffer, cuts);
        const [status, result] = (0, simplex_js_1.simplex)(currentTableau, options);
        // The initial tableau is not unbounded and adding more cuts/constraints cannot make it become unbounded
        // assert(status !== "unbounded")
        if (status === "optimal" && result < bestEval) {
            const [variable, value, frac] = mostFractionalVar(currentTableau, integers);
            if (frac <= precision) {
                // The solution is integer
                solutionFound = true;
                bestEval = result;
                bestTableau = currentTableau;
                const temp = solutionBuffer;
                solutionBuffer = candidateBuffer;
                candidateBuffer = temp;
            }
            else {
                const cutsUpper = [];
                const cutsLower = [];
                for (let i = 0; i < cuts.length; i++) {
                    const cut = cuts[i];
                    const [dir, v] = cut;
                    if (v === variable) {
                        dir < 0 ? cutsLower.push(cut) : cutsUpper.push(cut);
                    }
                    else {
                        cutsUpper.push(cut);
                        cutsLower.push(cut);
                    }
                }
                cutsLower.push([1, variable, Math.floor(value)]);
                cutsUpper.push([-1, variable, Math.ceil(value)]);
                branches.push([result, cutsUpper]);
                branches.push([result, cutsLower]);
            }
        }
        // Otherwise, this branch's result is worse than the current best solution.
        // This could be because this branch is infeasible or cycled.
        // Either way, skip this branch and see if any other branches have a valid, better solution.
        timedout = Date.now() >= stopTime;
        iter++;
    }
    // Did the solver "timeout"?
    const unfinished = (timedout || iter >= maxIterations) && !branches.empty() && bestEval >= optimalThreshold;
    // prettier-ignore
    const status = unfinished ? "timedout"
        : !solutionFound ? "infeasible"
            : "optimal";
    return [{ ...tabmod, tableau: bestTableau }, status, solutionFound ? bestEval : NaN];
};
exports.branchAndCut = branchAndCut;

        
        modules['branchAndCut'] = module.exports;
    })();

    // === YALPS.js ===
    (function() {
        const exports = {};
        const module = { exports: exports };
        
        "use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.solve = exports.defaultOptions = void 0;
const tableau_js_1 = require("./tableau.js");
const util_js_1 = require("./util.js");
const simplex_js_1 = require("./simplex.js");
const branchAndCut_js_1 = require("./branchAndCut.js");
// Creates a solution object representing the optimal solution (if any).
const solution = ({ tableau, sign, variables: vars }, status, result, { precision, includeZeroVariables }) => {
    if (status === "optimal" || (status === "timedout" && !Number.isNaN(result))) {
        const variables = [];
        for (let i = 0; i < vars.length; i++) {
            const [variable] = vars[i];
            const row = tableau.positionOfVariable[i + 1] - tableau.width;
            const value = row >= 0 ? (0, tableau_js_1.index)(tableau, row, 0) : 0.0;
            if (value > precision) {
                variables.push([variable, (0, util_js_1.roundToPrecision)(value, precision)]);
            }
            else if (includeZeroVariables) {
                variables.push([variable, 0.0]);
            }
        }
        return {
            status,
            result: -sign * result,
            variables,
        };
    }
    else if (status === "unbounded") {
        const variable = tableau.variableAtPosition[result] - 1;
        return {
            status: "unbounded",
            result: sign * Infinity,
            // prettier-ignore
            variables: (0 <= variable && variable < vars.length)
                ? [[vars[variable][0], Infinity]]
                : [],
        };
    }
    else {
        // infeasible | cycled | (timedout and result is NaN)
        return {
            status,
            result: NaN,
            variables: [],
        };
    }
};
const defaultOptionValues = {
    precision: 1e-8,
    checkCycles: false,
    maxPivots: 8192,
    tolerance: 0,
    timeout: Infinity,
    maxIterations: 32768,
    includeZeroVariables: false,
};
/**
 * The default options used by the solver.
 */
exports.defaultOptions = { ...defaultOptionValues };
/**
 * Runs the solver on the given model and using the given options (if any).
 * @see `Model` on how to specify/create the model.
 * @see `Options` for the kinds of options available.
 * @see `Solution` for more detailed information on what is returned.
 */
const solve = (model, options) => {
    const tabmod = (0, tableau_js_1.tableauModel)(model);
    const opt = { ...defaultOptionValues, ...options };
    const [status, result] = (0, simplex_js_1.simplex)(tabmod.tableau, opt);
    if (tabmod.integers.length === 0 || status !== "optimal") {
        // If a non-integer problem, return the simplex result.
        // Otherwise, the problem has integer variables, but the initial solution is either:
        // 1) unbounded | infeasible => all branches will also be unbounded | infeasible
        // 2) cycled => cannot get an initial solution, return invalid solution
        return solution(tabmod, status, result, opt);
    }
    else {
        // Integer problem and an optimal non-integer solution was found
        const [intTabmod, intStatus, intResult] = (0, branchAndCut_js_1.branchAndCut)(tabmod, result, opt);
        return solution(intTabmod, intStatus, intResult, opt);
    }
};
exports.solve = solve;

        
        modules['YALPS'] = module.exports;
    })();

    // Export the main solve function
    YALPS.solve = modules.YALPS.solve;
    YALPS.defaultOptions = modules.YALPS.defaultOptions;
    
    // Make available globally
    if (typeof window !== 'undefined') {
        window.YALPS = YALPS;
    } else {
        global.YALPS = YALPS;
    }
    
})(typeof window !== 'undefined' ? window : global);
