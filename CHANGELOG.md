## Unreleased

### Added
- Added project packaging configuration through `pyproject.toml`.
- Added baseline tests for core calculations, reports, validation, Excel pipeline, CSV input, component lookup, and report print utility.
- Added molar-basis metadata to calculation results.
- Added carbon-conversion model assumption metadata to calculation results.
- Added validation-basis metadata documenting signed and absolute validation deviations.
- Added warnings for invalid experimental validation values.
- Added warnings for Excel output key mismatches between calculated results and the `02_OUTPUTS` template.
- Added documentation for current model assumptions, operational scope, and known limitations.
- Added Buswell water balance reporting through `H2O_mol`, `H2O_mass`, and water-balance notes.
- Added Excel support for free-water rows using `WATER`/`H2O` entries.
- Added `water_available_mol`, `net_water_balance_mol`, `net_water_balance_mass`, and `net_water_balance_note` to the Excel pipeline output.
- Added support for global molar and mass input bases in the Excel pipeline through `input_basis_type`, `input_unit`, and `input_quantity`.
- Added mass-based input conversion using molecular weights calculated from elemental composition (`C`, `H`, `O`, `N`, `S`).
- Added automatic output unit writing in `02_OUTPUTS`, with units reported next to each calculated value.
- Added CSV support for free-water rows using the same `WATER`/`H2O` convention used by the Excel pipeline.
- Added CSV support for the current input contract through `component_name`, `input_quantity`, `input_basis_type`, and `input_unit`.
- Added backward compatibility for legacy CSV files using `name` and `molar_flow`.
- Added CSV unit conversion using the same internal molar-basis conversion used by the Excel pipeline.

### Changed
- Wrapped the Excel runner in a `main()` entry point.
- Simplified `run_from_excel.py` console output by removing the JSON-style terminal report.
- The Excel pipeline now reuses calculated results instead of recalculating during output writing.
- Excel writer default output now uses a calculated workbook path instead of overwriting the input workbook.
- Removed water from the auxiliary organic component database.
- Experimental validation output cleanup now uses the existing worksheet extent instead of a fixed 100-row range.
- Documented `print_result()` as a manual reporting utility outside the Excel pipeline.
- Replaced the Excel-facing `molar_flow` input concept with the more general `input_quantity` to support both amount and rate inputs on molar or mass bases.
- Removed `include_non_degradable` from the Excel-facing calculation contract. Components marked as non-degradable are now consistently excluded from the Buswell calculation.
- Removed Excel-facing control of non-negative validation; physical validity checks are handled internally by the model.
- Standardized output units by physical dimension instead of preserving the input unit.
- Energy outputs for rate-based inputs are now reported as `MJ/h` and `kW`.

### Fixed
- Active Excel rows with empty quantity values are now rejected.
- Missing Excel global parameters now emit warnings when defaults are used.
- `ELEMENTS` input mode now validates required elemental columns.
- `DATABASE` input mode now suggests similar component names for typos.
- CSV input now reports missing or invalid `molar_flow` values with explicit errors.
- Text and binary file handling is now normalized through `.gitattributes`.

### Clarified
- Documented validation classification thresholds as internal BioPot-Gas criteria.
- Documented that `inert_carbon_mol` represents only the unconverted fraction of degradable carbon controlled by `carbon_conversion`.
- Clarified that non-degradable components are excluded from the Buswell calculation and do not contribute to `inert_carbon_mol`.
- Clarified that the `03_COMPONENT_DATABASE` expansion is intentionally out of scope for this release and will be reviewed separately.

### Known limitations
- The `03_COMPONENT_DATABASE` expansion is intentionally out of scope for this release and will be reviewed separately.