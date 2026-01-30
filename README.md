# pygeofilter-odata-cdse

[![PyPI - Version](https://img.shields.io/pypi/v/pygeocdse.svg)](https://pypi.org/project/pygeocdse)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pygeocdse.svg)](https://pypi.org/project/pygeocdse)

-----

## Table of Contents

- [Installation](#installation)
- [License](#license)

## Installation

```console
pip install pygeocdse
```

## For developers

### Python environment

Use `hatch shell` to create a Python environment.

This environment is created in your HOME and the python path is ~:
```
/home/<user>/.local/share/hatch/env/virtual/pygeocdse/L1xv70IW/pygeocdse/bin/python
```

Note: the value of `L1xv70IW` is certainly different

### Run the tests

To run the tests

```
hatch run default:test
```

## Container Image Strategy & Availability

This project publishes container images to GitHub Container Registry (GHCR) following a clear and deterministic tagging strategy aligned with the Git branching and release model.

### Image Registry

Images are published to:

```
ghcr.io/<repository-owner>/pygeofilter-odata-cdse
```

See https://github.com/orgs/Terradue/packages/container/package/pygeofilter-odata-cdse

The registry owner corresponds to the GitHub repository owner (user or organization).

Images are built using Kaniko and pushed using OCI-compliant tooling.

### Tagging Strategy

The image tag is derived automatically from the Git reference that triggered the build:


| Git reference    | Image tag    | Purpose                            |
| ---------------- | ------------ | ---------------------------------- |
| `develop` branch | `latest-dev` | Development and integration builds |
| `main` branch    | `latest`     | Stable branch builds               |
| Git tag `vX.Y.Z` | `X.Y.Z`      | Immutable release builds           |


## License

`pygeocdse` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
