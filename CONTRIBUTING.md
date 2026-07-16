# Contributing

## Current status

This repository is private and tied to non-public research inputs. Do not open it publicly or add external collaborators without confirming publication permission and attribution requirements.

## Contribution rules

- Do not commit private datasets, corpus excerpts, annotations, or identifying metadata.
- Do not commit secrets, tokens, credentials, or local machine paths.
- Use synthetic examples or schema-only fixtures for documentation and tests.
- Keep notebooks free of private outputs and cached results.
- Preserve existing attribution and ownership information.

## Before opening a change

1. Confirm the change does not expand exposure of non-public research material.
2. Prefer changes in `src/pipeline/`, `schemas/`, `synthetic_examples/`, and documentation.
3. If a change touches notebooks, clear outputs unless they are synthetic and intentionally retained.

## Validation

Validation evidence currently shows:
- parse checks passed for notebooks and Python files
- Ruff reported three unused imports in notebooks
- Black would reformat two Python files
- Bandit reported issues in `src/pipeline/repo_code_extraction.py`
- pytest was not executed

Do not state that tests or checks pass unless new evidence is recorded.

## Review requirements for sensitive changes

Route to manual review if a change:
- touches data ingestion from non-public sources
- changes repository extraction or subprocess behavior
- adds hashes, identifiers, or export steps
- prepares the repository for public release

## Public release preparation

If this repository is ever prepared for publication, keep it private until:
- private data is removed from files and history
- collaborator attribution is settled
- publication permission is confirmed
- a manual review approves the release
