# Security policy

## Scope

This repository contains research tooling and should be treated as sensitive because the surrounding workflow may depend on non-public inputs.

## Reporting

Report suspected security issues privately to the repository owner through a non-public channel already used for this project. Do not disclose potential vulnerabilities or sensitive findings in public issues.

## Sensitive material handling

If you find any of the following, stop and report privately:
- credentials or tokens
- private dataset content
- identifying metadata from non-public sources
- notebook outputs containing private material
- hard-coded local paths or infrastructure details

## Current validation evidence

Provided validation shows:
- secret/privacy scan passed with zero findings
- detect-secrets did not report actionable repository secrets
- Bandit reported issues in `src/pipeline/repo_code_extraction.py`, including subprocess-related findings and SHA1 usage findings

These results do not guarantee the repository is secure.

## Release guidance

Do not make the repository public until manual review confirms that sensitive data, identifiers, and history have been sanitized.
