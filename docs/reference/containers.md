# Container build reference

The repository container workflow uses Kaniko to build an image archive and Skopeo to publish it to `ghcr.io/<repository-owner>/pygeofilter-odata-cdse` (owner and repository names are lowercased).

| Trigger | Tag |
| --- | --- |
| `develop` branch | `latest-dev` |
| `main` branch | `latest` |
| Git tag `vX.Y.Z` | `X.Y.Z`, checked against the package version |

Published artifacts, when available, are listed in the [Terradue container package](https://github.com/orgs/Terradue/packages/container/package/pygeofilter-odata-cdse).

The Dockerfile builds a wheel with Hatch, installs it in a Rocky Linux runtime image, and runs as user `neo` (UID/GID 2000). It does not define an application entrypoint.

## Current build limitations

The Dockerfile checks the installed CLI with `odata-client --help`. The container workflow invokes `hatch run dev:test`, while the current Hatch development environment has no `test` script. This configuration mismatch can prevent new images from being published. The tag table describes the configured strategy, not a guarantee that any particular tag is available.
