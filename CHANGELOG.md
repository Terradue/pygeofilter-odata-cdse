# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Added a quality pipeline covering mypy, Ruff, Bandit, and pytest with coverage
  across Python 3.10 through 3.14.
- Added pre-commit configuration for the project's quality checks.

### Changed

- Updated the project documentation URL and license badge.
- Tightened the supported Python requirement to Python 3.10 or newer and
  reorganized the Hatch test and development environments.
- Updated source and test code to satisfy the expanded type, lint, and security
  checks.

## [0.7.0] - 2026-05-20

### Added

- Added a configurable HTTP connection timeout to the `odata-client search`
  command and evaluator API.
- Added a pytest matrix for Python 3.10 through 3.14.

### Fixed

- Removed an invalid OData type fragment from generated STAC `derived_from`
  links.
- Made integration tests resilient to service timeouts.

## [0.6.0] - 2026-04-27

### Added

- Added request and response logging for OData calls, including redaction of
  bearer tokens.

### Changed

- Replaced `requests` with `httpx` for OData HTTP calls.
- Removed unused runtime dependencies and declared the wheel's `src/pygeocdse`
  package explicitly.
- Renamed the distribution metadata from `pygeocdse` to
  `pygeofilter-odata-cdse`.
- Modernized the package publishing workflow and related GitHub Actions.

### Fixed

- Replaced the inline `IN`-filter mapper lambda with a regular function.
- Corrected test, lint, documentation, and branch references in the build
  tooling.

## [0.5.0] - 2026-04-03

### Added

- Added Sentinel-1 `sliceNumber` mapping to the STAC Sentinel-1 extension.
- Added Dependabot configuration for Python and GitHub Actions dependencies.

### Changed

- Pinned runtime and development dependency versions for reproducible builds.
- Updated the checkout, Python setup, and cache GitHub Actions.

### Fixed

- Added missing XML/GML runtime libraries used by the conversion stack.

## [0.4.0] - 2026-02-06

### Changed

- Use the OData `beginningDateTime` attribute as the STAC Item datetime instead
  of `OriginDate`.

### Fixed

- Normalize UTC STAC property timestamps to RFC 3339 `Z` notation.
- Fail with a clear error when an OData product has no `beginningDateTime`
  attribute.

## [0.3.0] - 2026-02-04

### Added

- Added an OData-to-STAC field crosswalk to the documentation.

### Changed

- Unified OData request invocation behind a single evaluator entry point.
- Improved type annotations in the CLI and evaluator.

## [0.2.0] - 2026-02-03

First tagged release.

### Added

- Added translation from CQL2/pygeofilter expressions to Copernicus Data Space
  Ecosystem OData filters, including comparison, temporal, interval, and
  spatial-intersection expressions.
- Added time-delta support for temporal intervals and timezone-aware OData date
  formatting.
- Added the `odata-client search` CLI with CQL2 text/JSON filters, collections,
  bounding boxes, datetimes, result limits, and file output.
- Added OData product conversion to GeoJSON and STAC Item Collections, including
  attributes, assets, locations, checksums, processing metadata, and
  `derived_from` links.
- Added mappings for common Sentinel collection and product attributes.
- Added a container image build and publishing workflow alongside package,
  test, and documentation workflows.
- Added user documentation, executable notebook examples, and package metadata.

### Changed

- Relicensed the project under the Apache License 2.0.

[Unreleased]: https://github.com/Terradue/pygeofilter-odata-cdse/compare/v0.7.0...develop
[0.7.0]: https://github.com/Terradue/pygeofilter-odata-cdse/compare/v0.6.0...v0.7.0
[0.6.0]: https://github.com/Terradue/pygeofilter-odata-cdse/compare/v0.5.0...v0.6.0
[0.5.0]: https://github.com/Terradue/pygeofilter-odata-cdse/compare/v0.4.0...v0.5.0
[0.4.0]: https://github.com/Terradue/pygeofilter-odata-cdse/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/Terradue/pygeofilter-odata-cdse/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/Terradue/pygeofilter-odata-cdse/releases/tag/v0.2.0
