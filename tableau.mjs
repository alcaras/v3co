export const index = (tableau, row, col) => tableau.matrix[Math.imul(row, tableau.width) + col];
export const update = (tableau, row, col, value) => {
    tableau.matrix[Math.imul(row, tableau.width) + col] = value;
};
const convertToIterable = (seq) => typeof seq[Symbol.iterator] === "function" // eslint-disable-line
    ? seq
    : Object.entries(seq);
// prettier-ignore
const convertToSet = (set) => set === true ? true
    : set === false ? new Set()
        : set instanceof Set ? set
            : new Set(set);
export const tableauModel = (model) => {
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
                update(tableau, 0, c, sign * coef);
            }
            const bounds = constraints.get(constraint);
            if (bounds != null) {
                if (Number.isFinite(bounds.upper)) {
                    update(tableau, bounds.row, c, coef);
                    if (Number.isFinite(bounds.lower)) {
                        update(tableau, bounds.row + 1, c, -coef);
                    }
                }
                else if (Number.isFinite(bounds.lower)) {
                    update(tableau, bounds.row, c, -coef);
                }
            }
        }
    }
    for (const bounds of constraints.values()) {
        if (Number.isFinite(bounds.upper)) {
            update(tableau, bounds.row, 0, bounds.upper);
            if (Number.isFinite(bounds.lower)) {
                update(tableau, bounds.row + 1, 0, -bounds.lower);
            }
        }
        else if (Number.isFinite(bounds.lower)) {
            update(tableau, bounds.row, 0, -bounds.lower);
        }
    }
    for (let b = 0; b < binaryConstraintCol.length; b++) {
        const row = numConstraints + b;
        update(tableau, row, 0, 1.0);
        update(tableau, row, binaryConstraintCol[b], 1.0);
    }
    return { tableau, sign, variables, integers: ints };
};
