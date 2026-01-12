# Regulus Release Process

## Purpose

This document describes how Regulus versions, releases, and publishes artifacts.

## Versioning scheme

Regulus follows **SemVer**: `MAJOR.MINOR.PATCH`.

- **MAJOR**: breaking API changes, incompatible DB migrations, or architectural overhauls.
- **MINOR**: new features, new endpoints, or additive schema changes with backward compatibility.
- **PATCH**: bug fixes, performance improvements, or documentation updates.

## Release artifacts

- GitHub Release notes (primary changelog)
- Docker images (optional, if published for api/worker/web)
- Migration notes (if DB changes are included)

## Changelog approach

Regulus uses **GitHub Releases** as the canonical changelog.

## Release steps

1. Ensure `main` is green in CI.
2. Update versions:
   - `apps/web/package.json`
   - `services/api/pyproject.toml`
3. Update release notes (GitHub Release draft).
4. Tag the release: `git tag vX.Y.Z`.
5. Push tags: `git push --tags`.
6. Publish GitHub Release notes.
7. Post‑release checks:
   - `make up`
   - `make dev`
   - smoke test `/health` and `/v1/graph/{id}`

## Hotfix process

1. Create a hotfix branch from the last tag.
2. Apply the minimal fix and bump PATCH.
3. Tag `vX.Y.(Z+1)` and publish a GitHub Release.
4. Backport to `main` if needed.

## Backward compatibility

- API versioning is under `/v1`; breaking changes require `/v2`.
- DB migrations must be forward‑compatible when possible.
- Any breaking change must be documented in release notes.

## Security disclosure

Please report vulnerabilities privately via GitHub Security Advisories.
Do not open public issues for security-sensitive findings.
