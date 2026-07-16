# Data boundaries

## Purpose

This document defines what may remain in this repository while it is private and what would be required for any future public release.

## Verified context

Repository role from the manifest:
- research tooling repository for methods and analysis
- potential future public research code sample after sanitization

Release blockers from the manifest:
- maximum private-data dependence and manual review requirement
- public code must use schemas or synthetic examples
- full manual review required before any visibility change

## Allowed content for a future public-safe version

- code implementing general pipeline structure
- schema definitions describing expected inputs and outputs
- synthetic examples created to demonstrate interfaces
- notebooks that run only on synthetic data
- configuration templates with placeholder values only
- documentation describing required non-public inputs without exposing them

## Content that must not be published

- private research datasets or excerpts
- records, annotations, or labels derived from non-public corpora
- identifiers for people, organizations, repositories, or documents when they are not already approved for release
- notebook cell outputs containing private text or metadata
- cached intermediate files derived from private inputs
- secrets, tokens, credentials, or local environment details
- git history that still contains removed sensitive material

## Repository-specific notes

Observed files include synthetic notebooks and pipeline modules under `src/pipeline/`.

Any future public release should verify that:
- notebooks contain only synthetic inputs and synthetic outputs
- pipeline code does not hard-code private paths, private URLs, or private identifiers
- examples are schema-only or synthetic
- local caches and temporary artifacts are excluded from version control

## Required review before visibility change

Manual review should cover:
1. notebook source and outputs
2. Python source for private-path assumptions and sensitive identifiers
3. commit history and large-file storage, if used
4. ownership and collaborator publication permission
5. whether a license can be added without conflicting with third-party or starter-code restrictions

## Validation evidence relevant to boundaries

Provided scans reported:
- secret/privacy scan passed with zero findings
- detect-secrets reported no actionable repository secrets, though a cache file triggered an entropy match in `.ruff_cache/CACHEDIR.TAG`

This does not replace manual review of history or research-data provenance.
