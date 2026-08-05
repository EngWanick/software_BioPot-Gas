# Changelog

## Unreleased

### Added
- Added project packaging configuration through `pyproject.toml`.
- Added baseline tests for core calculations, reports, validation, Excel pipeline, CSV input, component lookup, and report print utility.
- Added molar-basis metadata to calculation results.
- Added carbon-conversion model assumption metadata to calculation results.
- Added validation-basis metadata to experimental validation results.
- Added warnings for invalid experimental validation values.
- Added documentation for current model assumptions, operational scope, and known limitations.

### Changed
- Wrapped the Excel runner in a `main()` entry point.
- The Excel pipeline now reuses calculated results instead of recalculating during output writing.
- Excel writer default output now uses a calculated workbook path instead of overwriting the input workbook.
- Removed water from the auxiliary organic component database.
- Experimental validation output cleanup now uses the existing worksheet extent instead of a fixed 100-row range.
- Documented `print_result()` as a manual reporting utility outside the Excel pipeline.

### Fixed
- Active Excel rows with empty `molar_flow` are now rejected.
- Missing Excel global parameters now emit warnings when defaults are used.
- `ELEMENTS` input mode now validates required elemental columns.
- `DATABASE` input mode now suggests similar component names for typos.
- CSV input now reports missing or invalid `molar_flow` values with explicit errors.
- Text and binary file handling is now normalized through `.gitattributes`.

### Known limitations
- Water consumption or production in the Buswell balance is not yet explicitly calculated or reported.
- Automatic unit conversion from declared Excel units is not yet implemented.
- The Excel reader/writer split still contains legacy overlap and will be consolidated in a future refactor.