# Chemical Compound Database

This directory contains the validated thermophysical property database for chemical compounds used by ChemEng Toolbox.

## Files

- `compounds.json` - Main compound database with 10+ compounds
- `ATTRIBUTION.md` - Data source attribution and citations (see below)

## Data Structure

The database follows the schema defined in `/specs/001-data-foundations/data-model.md`:

```json
{
  "metadata": {
    "version": "1.0.0",
    "source": "CoolProp / NIST WebBook",
    "retrieved_date": "2025-12-29",
    "attribution": "...",
    "compound_count": 10
  },
  "compounds": [
    {
      "cas_number": "7732-18-5",
      "name": "Water",
      "formula": "H2O",
      "iupac_name": "oxidane",
      "coolprop_name": "Water",
      "aliases": ["water", "H2O", "dihydrogen monoxide"],
      "molecular_weight": { "magnitude": 18.01527, "unit": "gram / mole" },
      "critical_properties": { ... },
      "phase_properties": { ... },
      "source": { ... }
    }
  ]
}
```

## Adding New Compounds

Use the provided CLI utility to add new compounds from CoolProp:

```bash
# From repository root
python scripts/add_compound.py <coolprop_name> <cas_number> <name> <formula> <iupac_name> \\
    --aliases <alias1> <alias2> ... \\
    --nist-url <url>

# Example: Add Argon
python scripts/add_compound.py Argon 7440-37-1 "Argon" "Ar" "argon" \\
    --aliases argon Ar
```

See `scripts/add_compound.py --help` for full documentation.

### Manual Addition

You can also manually add compounds by editing `compounds.json`:

1. Extract properties from CoolProp using Python:
   ```python
   from chemeng_core.compounds.extractor import CoolPropDataExtractor

   extractor = CoolPropDataExtractor("Argon")
   argon = extractor.extract_compound_data(
       cas_number="7440-37-1",
       name="Argon",
       formula="Ar",
       iupac_name="argon",
       aliases=["argon", "Ar"]
   )
   print(argon.model_dump_json(indent=2))
   ```

2. Append the JSON output to the `compounds` array
3. Update `metadata.compound_count`
4. Update `metadata.retrieved_date` if needed
5. Validate with: `python -c "from chemeng_core.compounds import create_registry; create_registry()"`

## Validation

All compound data is validated against NIST WebBook reference values. See validation tests in:

```bash
packages/core/tests/validation/test_nist_*.py
```

Run validation tests:

```bash
pytest -m validation packages/core/tests/validation/
```

## Data Sources

- **CoolProp** (MIT License) - Primary thermophysical property source
  - https://github.com/CoolProp/CoolProp
  - Bell et al. (2014). Pure and Pseudo-pure Fluid Thermophysical Property Evaluation

- **NIST WebBook** (Public Domain) - Reference validation data
  - https://webbook.nist.gov/chemistry/
  - NIST Standard Reference Database 69

See `ATTRIBUTION.md` for complete citations.

## Quality Standards

- **Precision**: All properties stored with ≥6 significant figures
- **Validation**: Critical properties within ±0.01% of NIST values
- **Attribution**: Every compound includes source metadata with URL and retrieval date
- **Schema**: Validated with Pydantic models - invalid data rejected at load time

## Maintenance

### Refreshing Data

To update compound properties when CoolProp is updated:

```bash
# Regenerate all 10 compounds
python scripts/generate_compound_data.py

# Re-run validation tests
pytest -m validation packages/core/tests/validation/
```

### Version Control

- `compounds.json` is committed to version control
- Changes should include updated `retrieved_date` in metadata
- Always run validation tests before committing changes

## Support

For issues or questions:
- GitHub: https://github.com/ChE-Toolbox/che-toolbox/issues
- Documentation: https://che-toolbox.github.io/che-toolbox
