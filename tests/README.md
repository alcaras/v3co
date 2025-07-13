# Victoria 3 Company Optimizer Test Suite

This directory contains test cases and debug scripts for the Victoria 3 Company Optimizer.

## Running Tests

To run all tests:
```bash
node tests/test-runner.js
```

Or run the test runner directly:
```bash
./tests/test-runner.js
```

## Test File Types

### Test Files (`test_*.js`)
- Algorithm validation tests
- Scoring function tests
- Optimization logic tests
- UI integration tests

### Debug Files (`debug_*.js`)
- Specific bug reproduction tests
- Scoring discrepancy analysis
- Company filtering tests
- Charter handling tests

### HTML Test Files (`*.html`)
- Interactive test pages
- YALPS solver testing
- UI component testing

## Key Test Cases

- **test_final_verification.js** - Core algorithm validation
- **test_optimization_fixes.js** - Bug fixes verification
- **debug_scoring_bug.js** - Scoring calculation issues
- **debug_charter_display.js** - Charter handling problems
- **test_yalps.html** - YALPS solver integration testing

## Test Data

Tests use the main `companies_extracted.json` file for company data and test against various building selection scenarios that have been problematic in the past.