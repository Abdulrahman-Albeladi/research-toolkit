# Project index

## Portfolio structure

This index describes the recovered publish-eligible project material currently present in `research-paper-analysis-toolkit`. Descriptions are limited to the available filenames and repository structure; they do not assert completed analyses, validated findings, or successful execution.

| Area | Files | Purpose | Data requirement | Validation status | Provenance |
|---|---|---|---|---|---|
| Reusable detection pipeline | `src/pipeline/code_detection_pipeline.py` | Recovered Python pipeline material related to code detection. | May require user-supplied code samples and detector-related configuration; exact requirements should be determined from source imports and configuration usage. | Not executed or independently reviewed from the supplied inventory. | Recovered from the research-paper assignment collection. |
| Repository code extraction | `src/pipeline/repo_code_extraction.py` | Recovered Python material for extracting code samples from repositories. | Requires repositories or repository exports supplied by the user; respect repository licenses and access restrictions. | Not executed or independently reviewed from the supplied inventory. | Recovered from the research-paper assignment collection. |
| Synthetic analysis overview | `notebooks/analysis_overview_synthetic.ipynb` | Public-facing synthetic overview of an analysis workflow. | Designed for synthetic inputs; no original corpus is included. | Notebook execution was not supplied. | Synthetic derivative retained for public review. |
| Synthetic multivariable analysis | `notebooks/multivariable_analysis_synthetic.ipynb` | Public-facing synthetic version of the multivariable analysis workflow. | Synthetic data only in the distributed example; original analytical data are not included. | Notebook execution was not supplied. | Synthetic derivative retained for public review. |
| Synthetic sample-detection testing | `notebooks/testing_sample_detection_synthetic.ipynb` | Public-facing synthetic workflow for testing sample detection. | Synthetic inputs only in the distributed example; real testing samples are not included. | Notebook execution was not supplied. | Synthetic derivative retained for public review. |
| Workflow record | `notebooks/workflows/assignments-workflow.ipynb` | Retained workflow notebook associated with the assignment-era project sequence. | May reference unavailable historical inputs or local setup. | Not executed or independently reviewed from the supplied inventory. | Recovered workflow artifact; not a grading or hidden-test artifact. |

## Source-cleaned notebook collection

The following notebooks preserve cleaned, recovered workflow material. Their names retain recovery-era duplication so that lineage can be traced to the original files. They should be read with `docs/data-boundaries.md` and `docs/notebook-lineage.md`.

| Notebook | Recovered workflow topic indicated by filename | Private-data or external-input boundary | Validation status |
|---|---|---|---|
| `copy-of-generating-ai-prompts-copy-of-generating-ai-prompts.ipynb` | Generating AI prompts. | May require a prompt source, model access, or locally defined inputs; none should be committed if private or credential-bearing. | Not executed. |
| `copy-of-ai-code-detection-copy-of-ai-code-detection.ipynb` | AI code detection. | May require code samples and a detector or detector output not included in the repository. | Not executed. |
| `copy-of-arabic-coding-ai-pipeline-copy-of-arabic-coding-ai-pipeline.ipynb` | Arabic coding and AI pipeline. | May require Arabic-language text or code data and language-specific processing dependencies. Source data are not included. | Not executed. |
| `copy-of-ai-trimming-copy-of-ai-trimming.ipynb` | AI-related trimming or text preparation. | May require source text or documents not included in the repository. | Not executed. |
| `copy-of-primary-sample-ai-detection-copy-of-primary-sample-ai-detection.ipynb` | Primary-sample AI detection. | The referenced primary sample is not distributed and may be private, restricted, or otherwise non-public. | Not executed. |
| `copy-of-generating-ai-humanized-testing-samples-copy-of-generating-ai-humanized-testing-samples.ipynb` | Generation of AI and humanized testing samples. | May require model access and sample sources. Treat generated and source samples as research artifacts requiring provenance records. | Not executed. |
| `copy-of-trimming-arabic-pdf-into-txt-copy-of-trimming-arabic-pdf-into-txt.ipynb` | Trimming Arabic PDFs into text. | Requires user-supplied PDFs. Confirm permission to extract, store, and process their text. | Not executed. |
| `copy-of-extracting-code-samples-copy-of-extracting-code-samples.ipynb` | Extracting code samples. | Requires accessible repositories or code archives. Preserve license, attribution, and access restrictions. | Not executed. |
| `copy-of-testing-sample-ai-detection-copy-of-testing-sample-ai-detection.ipynb` | Testing-sample AI detection. | The referenced testing sample is not included; detector configuration or outputs may also be absent. | Not executed. |
| `copy-of-ai-detection-analysis-copy-of-ai-detection-analysis.ipynb` | AI-detection analysis. | Requires analytical inputs and possibly prior detector output not included in this repository. | Not executed. |
| `copy-of-paper-2-openai-textual-pattern-analysis-assignment-corpus-fixed-v3-copy-of-paper-2-openai-textual-pattern-analysis-assignment-corpus-fixed-v3.ipynb` | Textual-pattern analysis associated with a paper-two workflow. | The filename references an assignment corpus that is not distributed. Do not infer that its contents are public. | Not executed. |
| `copy-of-paper-2-adjusted-multivariable-analysis-year-fix-copy-of-paper-2-adjusted-multivariable-analysis-year-fix.ipynb` | Adjusted multivariable analysis with a year-related correction. | Requires the underlying analysis table or corpus and a documented variable schema. Neither is established by the file list. | Not executed. |
| `copy-of-conflict-analysis-testing-sample-copy-of-conflict-analysis-testing-sample.ipynb` | Conflict analysis on a testing sample. | Requires a testing sample and conflicting-result definitions not included in the repository. | Not executed. |
| `copy-of-paper-3-copy-of-paper-3.ipynb` | Paper-three workflow material. | Input requirements are not determinable from the filename alone; inspect the notebook before use. | Not executed. |
| `copy-of-paper-2-high-impact-detector-conflict-analysis-copy-of-paper-2-high-impact-detector-conflict-analysis.ipynb` | High-impact detector-conflict analysis associated with a paper-two workflow. | Requires detector outputs, impact criteria, and source data not included in the repository. | Not executed. |

## Documentation and repository controls

| File | Role |
|---|---|
| `docs/data-boundaries.md` | Documents publication, privacy, and input-data boundaries for the recovered work. |
| `docs/notebook-lineage.md` | Records notebook origin and relationship between recovered and public-facing material. |
| `CONTRIBUTING.md` | Contribution guidance. |
| `SECURITY.md` | Security reporting guidance. |
| `LICENSE_REVIEW.md` | License-review documentation. |
| `.github/workflows/ci.yml` | CI configuration is present, but no CI outcome was supplied. |
| `.ruff_cache/` | Generated Ruff cache material; not a project subcomponent or source of research provenance. |

## Cross-project limitations

1. The repository inventory does not identify a canonical dataset, data dictionary, dependency lockfile, or environment specification.
2. Notebook filenames indicate historical workflow intent but do not establish the exact methods, data schemas, or conclusions of the original work.
3. Detector-oriented analyses should not be interpreted as definitive attribution without documented ground truth, detector versioning, and an evaluation protocol.
4. Any reproduction with private documents, repositories, or generated samples requires separate provenance, consent or license review, and local data protection.
5. Source-cleaned notebooks may still require modernization before they can be executed in a current environment.
