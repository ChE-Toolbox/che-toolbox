# ChemEng Core Data Directory

This directory contains small reference data files that ship with the package.

## What belongs here

- Small reference data files (< 100 KB recommended)
- Chemical property tables (JSON, YAML)
- Physical constants and coefficients
- Unit conversion factors
- Element/compound reference data

Examples:
- `periodic_table.json` - Element properties
- `critical_properties.json` - Critical point data for common compounds
- `antoine_coefficients.json` - Vapor pressure equation coefficients

## What does NOT belong here

Large data files should NOT be committed to git. These include:
- Experimental datasets (CSV, Excel files)
- Database files (SQLite, HDF5)
- Process simulation results
- Large property databases

For large datasets:
1. Host them externally (cloud storage, data repositories)
2. Download them programmatically when needed
3. Store them in user cache directories (`~/.cache/chemeng_toolbox/`)

## File formats

Prefer JSON or YAML for reference data:
- Easy to version control
- Human-readable
- Well-supported in Python

## Adding new reference data

1. Keep files small (< 100 KB)
2. Use descriptive names
3. Include units in field names or metadata
4. Document the source and date of data
5. Validate data with tests
