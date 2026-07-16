from __future__ import annotations

import csv
import json
import math
import os
import re
import time
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Dict, Iterable, List, Optional, Protocol, Sequence

try:
    import requests
except ImportError:  # pragma: no cover
    requests = None  # type: ignore[assignment]


SEPARATOR_MARKERS = {"############", "##########", "==========", "-----", "__________"}
KNOWN_CODE_EXTS = {
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".json",
    ".css",
    ".scss",
    ".sass",
    ".less",
    ".html",
    ".htm",
    ".vue",
    ".md",
    ".xml",
    ".yml",
    ".yaml",
    ".graphql",
    ".gql",
    ".sql",
    ".mjs",
    ".cjs",
    ".py",
    ".java",
    ".cpp",
    ".c",
    ".h",
    ".hpp",
    ".go",
    ".rs",
}


@dataclass(frozen=True)
class PipelineConfig:
    input_root: Path
    output_root: Path
    run_detection: bool = False
    api_url: str = "https://text.api.pangram.com/v3"
    api_key_env_var: str = "PANGRAM_API_KEY"
    max_words_per_chunk: int = 2500
    timeout_seconds: int = 180
    max_retries: int = 5
    seconds_between_requests: float = 1.0
    credit_buffer_multiplier: float = 1.10

    @classmethod
    def from_env(cls) -> "PipelineConfig":
        input_root = Path(
            os.environ.get(
                "CODE_DETECTION_INPUT_ROOT", "synthetic_examples/code_submissions"
            )
        )
        output_root = Path(
            os.environ.get("CODE_DETECTION_OUTPUT_ROOT", "synthetic_examples/output")
        )
        run_detection = os.environ.get(
            "CODE_DETECTION_RUN_DETECTION", "false"
        ).strip().lower() in {
            "1",
            "true",
            "yes",
            "on",
        }
        return cls(
            input_root=input_root,
            output_root=output_root,
            run_detection=run_detection,
            api_url=os.environ.get(
                "PANGRAM_API_URL", "https://text.api.pangram.com/v3"
            ),
            api_key_env_var=os.environ.get(
                "PANGRAM_API_KEY_ENV_VAR", "PANGRAM_API_KEY"
            ),
            max_words_per_chunk=int(
                os.environ.get("CODE_DETECTION_MAX_WORDS_PER_CHUNK", "2500")
            ),
            timeout_seconds=int(
                os.environ.get("CODE_DETECTION_TIMEOUT_SECONDS", "180")
            ),
            max_retries=int(os.environ.get("CODE_DETECTION_MAX_RETRIES", "5")),
            seconds_between_requests=float(
                os.environ.get("CODE_DETECTION_SECONDS_BETWEEN_REQUESTS", "1.0")
            ),
            credit_buffer_multiplier=float(
                os.environ.get("CODE_DETECTION_CREDIT_BUFFER_MULTIPLIER", "1.10")
            ),
        )


@dataclass(frozen=True)
class InternalCodeFile:
    path: str
    content: str
    word_count: int


@dataclass(frozen=True)
class SubmissionRecord:
    source_path: Path
    relative_path: str
    submission_id: str
    internal_files: Sequence[InternalCodeFile]


class DetectorClient(Protocol):
    def detect(
        self, text: str, public_dashboard_link: bool = False
    ) -> Dict[str, Any]: ...


class PangramDetectorClient:
    def __init__(self, config: PipelineConfig) -> None:
        if requests is None:
            raise ImportError("requests is required to run remote detection")
        self._config = config
        self._api_key = os.environ.get(config.api_key_env_var, "").strip()
        if not self._api_key:
            raise ValueError(
                f"Missing API key in environment variable: {config.api_key_env_var}"
            )

    def detect(self, text: str, public_dashboard_link: bool = False) -> Dict[str, Any]:
        headers = {
            "Content-Type": "application/json",
            "x-api-key": self._api_key,
            "Accept": "application/json",
        }
        payload = {
            "text": text,
            "public_dashboard_link": public_dashboard_link,
        }

        last_error: Optional[Exception] = None
        for attempt in range(1, self._config.max_retries + 1):
            try:
                response = requests.post(
                    self._config.api_url,
                    headers=headers,
                    json=payload,
                    timeout=self._config.timeout_seconds,
                )

                if (
                    response.status_code == 401
                    and "Insufficient credits" in response.text
                ):
                    raise RuntimeError(f"HTTP 401: {response.text}")

                if response.status_code in (429, 500, 502, 503, 504):
                    time.sleep(min(60, 2**attempt))
                    continue

                if response.status_code >= 400:
                    raise RuntimeError(
                        f"HTTP {response.status_code}: {response.text[:1000]}"
                    )

                return response.json()
            except Exception as exc:  # pragma: no cover - network path
                last_error = exc
                if "Insufficient credits" in str(exc):
                    raise
                if attempt < self._config.max_retries:
                    time.sleep(min(60, 2**attempt))

        raise RuntimeError(f"All retries failed. Last error: {last_error}")


class SyntheticDetectorClient:
    """Deterministic placeholder for schema-only or synthetic demonstrations."""

    def detect(self, text: str, public_dashboard_link: bool = False) -> Dict[str, Any]:
        del public_dashboard_link
        tokens = re.findall(r"\S+", text)
        token_count = len(tokens)
        if token_count == 0:
            return {
                "fraction_ai": 0.0,
                "fraction_ai_assisted": 0.0,
                "fraction_human": 1.0,
                "num_ai_segments": 0,
                "num_ai_assisted_segments": 0,
                "num_human_segments": 0,
                "version": "synthetic-demo",
                "headline": "empty input",
                "prediction": "Human",
                "prediction_short": "Human",
                "dashboard_link": "",
            }

        heuristic_score = min(
            0.95,
            max(
                0.05,
                (text.count("TODO") + text.count("function") + text.count("class"))
                / max(1, token_count),
            ),
        )
        fraction_ai = round(min(0.9, heuristic_score * 4), 4)
        fraction_ai_assisted = round(min(0.2, heuristic_score), 4)
        fraction_human = round(max(0.0, 1.0 - fraction_ai - fraction_ai_assisted), 4)
        prediction = max(
            [
                ("AI", fraction_ai),
                ("AI-Assisted", fraction_ai_assisted),
                ("Human", fraction_human),
            ],
            key=lambda item: item[1],
        )[0]
        return {
            "fraction_ai": fraction_ai,
            "fraction_ai_assisted": fraction_ai_assisted,
            "fraction_human": fraction_human,
            "num_ai_segments": 1 if prediction == "AI" else 0,
            "num_ai_assisted_segments": 1 if prediction == "AI-Assisted" else 0,
            "num_human_segments": 1 if prediction == "Human" else 0,
            "version": "synthetic-demo",
            "headline": "synthetic detector output",
            "prediction": prediction,
            "prediction_short": prediction,
            "dashboard_link": "",
        }


def sanitize_filename(name: str) -> str:
    cleaned = re.sub(r"[^\w.\-]+", "_", name.strip(), flags=re.UNICODE)
    cleaned = re.sub(r"_+", "_", cleaned).strip("._")
    return cleaned or "submission"


def normalize_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n").replace("\x00", "")
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def word_count(text: str) -> int:
    return len(re.findall(r"\S+", text))


def sanitize_rel_path(rel_path: str) -> str:
    rel_path = rel_path.replace("\\", "/").strip()
    parts: List[str] = []
    for part in PurePosixPath(rel_path).parts:
        if part in ("", ".", ".."):
            continue
        clean = re.sub(r'[<>:"|?*]', "_", part).replace("\x00", "").strip()
        if clean:
            parts.append(clean)
    cleaned = "/".join(parts)
    return cleaned[:240] if cleaned else "main.txt"


def looks_like_path_line(line: str) -> bool:
    line = line.strip()
    if (
        not line
        or line in SEPARATOR_MARKERS
        or line.startswith(("http://", "https://"))
        or len(line) > 260
    ):
        return False

    lower = line.lower()
    if not any(lower.endswith(ext) for ext in KNOWN_CODE_EXTS):
        return False

    bad_tokens = [
        "import ",
        "from ",
        "const ",
        "let ",
        "var ",
        "function ",
        "class ",
        "<",
        ">",
        "{",
        "}",
        ";",
        "=>",
        "(",
        ")",
        "=",
        "require(",
    ]
    if any(token in line for token in bad_tokens):
        return False

    return bool(re.fullmatch(r"[A-Za-z0-9_\-./\\ @()\[\]{}+]+", line))


def is_probable_header(lines: Sequence[str], index: int) -> bool:
    current = lines[index].strip()
    if not looks_like_path_line(current):
        return False

    previous_nonempty: Optional[str] = None
    for j in range(index - 1, -1, -1):
        candidate = lines[j].strip()
        if candidate:
            previous_nonempty = candidate
            break

    return index == 0 or previous_nonempty in SEPARATOR_MARKERS


def parse_internal_code_files(text: str) -> List[InternalCodeFile]:
    normalized = normalize_text(text)
    lines = normalized.splitlines()

    files: List[InternalCodeFile] = []
    current_path: Optional[str] = None
    current_lines: List[str] = []
    found_header = False
    skip_one_blank_after_header = False

    def flush_current() -> None:
        nonlocal current_path, current_lines
        if current_path is not None:
            content = "\n".join(current_lines).strip()
            if content:
                files.append(
                    InternalCodeFile(
                        path=current_path,
                        content=content,
                        word_count=word_count(content),
                    )
                )
        current_path = None
        current_lines = []

    for index, line in enumerate(lines):
        stripped = line.strip()

        if stripped in SEPARATOR_MARKERS:
            continue

        if is_probable_header(lines, index):
            found_header = True
            flush_current()
            current_path = sanitize_rel_path(stripped)
            skip_one_blank_after_header = True
            continue

        if not found_header:
            current_lines.append(line)
            continue

        if skip_one_blank_after_header and stripped == "":
            skip_one_blank_after_header = False
            continue

        skip_one_blank_after_header = False
        if current_path is None:
            current_path = "main.txt"
        current_lines.append(line)

    if found_header:
        flush_current()
    else:
        content = "\n".join(lines).strip()
        if content:
            files = [
                InternalCodeFile(
                    path="main.txt", content=content, word_count=word_count(content)
                )
            ]

    seen: Dict[str, int] = {}
    deduped: List[InternalCodeFile] = []
    for item in files:
        seen[item.path] = seen.get(item.path, 0) + 1
        if seen[item.path] == 1:
            deduped.append(item)
            continue
        path_obj = Path(item.path)
        new_name = f"{path_obj.stem}__dup{seen[item.path]}{path_obj.suffix}"
        parent = str(path_obj.parent).replace("\\", "/")
        new_path = f"{parent}/{new_name}" if parent not in ("", ".") else new_name
        deduped.append(
            InternalCodeFile(
                path=new_path, content=item.content, word_count=item.word_count
            )
        )

    return deduped


def split_code_by_line_word_limit(text: str, max_words: int) -> List[str]:
    if word_count(text) <= max_words:
        return [text]

    lines = text.splitlines()
    chunks: List[str] = []
    current_lines: List[str] = []
    current_words = 0

    for line in lines:
        line_words = word_count(line)

        if line_words > max_words:
            if current_lines:
                chunks.append("\n".join(current_lines).strip())
                current_lines = []
                current_words = 0

            tokens = re.findall(r"\S+|\s+", line)
            piece: List[str] = []
            piece_word_count = 0
            for token in tokens:
                if token.isspace():
                    piece.append(token)
                    continue
                if piece_word_count + 1 > max_words:
                    chunk = "".join(piece).strip()
                    if chunk:
                        chunks.append(chunk)
                    piece = [token]
                    piece_word_count = 1
                else:
                    piece.append(token)
                    piece_word_count += 1

            chunk = "".join(piece).strip()
            if chunk:
                chunks.append(chunk)
            continue

        if current_words + line_words <= max_words:
            current_lines.append(line)
            current_words += line_words
        else:
            chunk = "\n".join(current_lines).strip()
            if chunk:
                chunks.append(chunk)
            current_lines = [line]
            current_words = line_words

    if current_lines:
        chunk = "\n".join(current_lines).strip()
        if chunk:
            chunks.append(chunk)

    return chunks


def aggregate_chunk_results(
    chunk_results: Sequence[Dict[str, Any]], chunk_word_counts: Sequence[int]
) -> Dict[str, Any]:
    total_weight = sum(max(1, count) for count in chunk_word_counts)
    fraction_ai = 0.0
    fraction_ai_assisted = 0.0
    fraction_human = 0.0
    num_ai_segments = 0
    num_ai_assisted_segments = 0
    num_human_segments = 0
    dashboard_links: List[str] = []
    versions: List[str] = []
    headlines: List[str] = []
    predictions: List[str] = []
    prediction_shorts: List[str] = []

    for result, count in zip(chunk_results, chunk_word_counts):
        weight = max(1, count)
        fraction_ai += float(result.get("fraction_ai", 0) or 0) * weight
        fraction_ai_assisted += (
            float(result.get("fraction_ai_assisted", 0) or 0) * weight
        )
        fraction_human += float(result.get("fraction_human", 0) or 0) * weight
        num_ai_segments += int(result.get("num_ai_segments", 0) or 0)
        num_ai_assisted_segments += int(result.get("num_ai_assisted_segments", 0) or 0)
        num_human_segments += int(result.get("num_human_segments", 0) or 0)

        if result.get("dashboard_link"):
            dashboard_links.append(str(result["dashboard_link"]))
        if result.get("version"):
            versions.append(str(result["version"]))
        if result.get("headline"):
            headlines.append(str(result["headline"]))
        if result.get("prediction"):
            predictions.append(str(result["prediction"]))
        if result.get("prediction_short"):
            prediction_shorts.append(str(result["prediction_short"]))

    if total_weight > 0:
        fraction_ai /= total_weight
        fraction_ai_assisted /= total_weight
        fraction_human /= total_weight

    dominant = max(
        [
            ("AI", fraction_ai),
            ("AI-Assisted", fraction_ai_assisted),
            ("Human", fraction_human),
        ],
        key=lambda item: item[1],
    )[0]
    if (
        sorted([fraction_ai, fraction_ai_assisted, fraction_human], reverse=True)[0]
        < 0.60
    ):
        dominant = "Mixed"

    return {
        "fraction_ai": fraction_ai,
        "fraction_ai_assisted": fraction_ai_assisted,
        "fraction_human": fraction_human,
        "dominant_class": dominant,
        "num_ai_segments": num_ai_segments,
        "num_ai_assisted_segments": num_ai_assisted_segments,
        "num_human_segments": num_human_segments,
        "version": versions[-1] if versions else "",
        "headline_last_chunk": headlines[-1] if headlines else "",
        "prediction_last_chunk": predictions[-1] if predictions else "",
        "prediction_short_last_chunk": (
            prediction_shorts[-1] if prediction_shorts else ""
        ),
        "dashboard_links_joined": " | ".join(dashboard_links),
    }


def discover_submissions(input_root: Path) -> List[SubmissionRecord]:
    txt_files = sorted(path for path in input_root.rglob("*.txt") if path.is_file())
    submissions: List[SubmissionRecord] = []
    for path in txt_files:
        raw_text = path.read_text(encoding="utf-8", errors="ignore")
        internal_files = parse_internal_code_files(raw_text)
        submissions.append(
            SubmissionRecord(
                source_path=path,
                relative_path=str(path.relative_to(input_root)).replace("\\", "/"),
                submission_id=path.stem,
                internal_files=internal_files,
            )
        )
    return submissions


def estimate_submission_credits(
    submission: SubmissionRecord, max_words_per_chunk: int
) -> Dict[str, int]:
    total_request_credits = 0
    total_requests = 0
    total_code_words = sum(item.word_count for item in submission.internal_files)

    for item in submission.internal_files:
        for chunk in split_code_by_line_word_limit(item.content, max_words_per_chunk):
            chunk_words = word_count(chunk)
            total_request_credits += (
                math.ceil(chunk_words / 1000) if chunk_words > 0 else 0
            )
            total_requests += 1

    return {
        "internal_file_count": len(submission.internal_files),
        "code_word_count": total_code_words,
        "estimated_credits_for_this_submission": total_request_credits,
        "estimated_request_count": total_requests,
    }


def write_csv(path: Path, rows: Iterable[Dict[str, Any]]) -> None:
    rows = list(rows)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fieldnames = list(rows[0].keys())
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def run_pipeline(
    config: PipelineConfig, detector: Optional[DetectorClient] = None
) -> Dict[str, Any]:
    config.output_root.mkdir(parents=True, exist_ok=True)
    raw_json_dir = config.output_root / "raw_json"
    raw_json_dir.mkdir(parents=True, exist_ok=True)

    submissions = discover_submissions(config.input_root)
    if not submissions:
        raise FileNotFoundError(f"No .txt submissions found under {config.input_root}")

    word_rows: List[Dict[str, Any]] = []
    total_code_words = 0
    total_internal_files = 0

    for submission in submissions:
        code_words = sum(item.word_count for item in submission.internal_files)
        total_code_words += code_words
        total_internal_files += len(submission.internal_files)
        credit_info = estimate_submission_credits(
            submission, config.max_words_per_chunk
        )
        word_rows.append(
            {
                "source_rel_path": submission.relative_path,
                "file_name": submission.source_path.name,
                "submission_id": submission.submission_id,
                "internal_file_count": len(submission.internal_files),
                "code_word_count": code_words,
                "estimated_credits_for_this_submission": credit_info[
                    "estimated_credits_for_this_submission"
                ],
                "estimated_request_count": credit_info["estimated_request_count"],
            }
        )

    word_counts_csv = config.output_root / "code_detection_word_counts.csv"
    write_csv(word_counts_csv, word_rows)

    exact_credits_needed = (
        math.ceil(total_code_words / 1000) if total_code_words > 0 else 0
    )
    recommended_credits = math.ceil(
        exact_credits_needed * config.credit_buffer_multiplier
    )
    word_summary = {
        "input_root": str(config.input_root),
        "txt_submission_count": len(submissions),
        "total_internal_code_files": total_internal_files,
        "total_code_words_excluding_headers_and_separators": total_code_words,
        "exact_credits_needed_ceiling_total_words_div_1000": exact_credits_needed,
        "recommended_credits_with_buffer": recommended_credits,
        "note": "Credit estimates are computational estimates derived from parsed content and chunking rules.",
    }
    word_summary_json = config.output_root / "code_detection_word_summary.json"
    word_summary_json.write_text(
        json.dumps(word_summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    summary: Dict[str, Any] = {
        "word_counts_csv": str(word_counts_csv),
        "word_summary_json": str(word_summary_json),
        "detection_results_csv": None,
        "raw_json_dir": str(raw_json_dir),
        "run_detection": config.run_detection,
    }

    if not config.run_detection:
        return summary

    detector = detector or PangramDetectorClient(config)
    detection_rows: List[Dict[str, Any]] = []

    for submission in submissions:
        try:
            if not submission.internal_files:
                raise RuntimeError(
                    "No internal code files were parsed from this submission."
                )

            all_chunk_results: List[Dict[str, Any]] = []
            all_chunk_word_counts: List[int] = []
            internal_file_outputs: List[Dict[str, Any]] = []
            credit_info = estimate_submission_credits(
                submission, config.max_words_per_chunk
            )

            for internal_file in submission.internal_files:
                chunks = split_code_by_line_word_limit(
                    internal_file.content, config.max_words_per_chunk
                )
                file_chunk_results: List[Dict[str, Any]] = []
                file_chunk_word_counts: List[int] = []

                for chunk in chunks:
                    chunk_wc = word_count(chunk)
                    result = detector.detect(chunk, public_dashboard_link=False)
                    file_chunk_results.append(result)
                    file_chunk_word_counts.append(chunk_wc)
                    all_chunk_results.append(result)
                    all_chunk_word_counts.append(chunk_wc)
                    time.sleep(config.seconds_between_requests)

                internal_file_outputs.append(
                    {
                        "path": internal_file.path,
                        "word_count": internal_file.word_count,
                        "chunk_count": len(chunks),
                        "aggregated": aggregate_chunk_results(
                            file_chunk_results, file_chunk_word_counts
                        ),
                        "raw_responses": file_chunk_results,
                    }
                )

            submission_agg = aggregate_chunk_results(
                all_chunk_results, all_chunk_word_counts
            )
            raw_json_path = (
                raw_json_dir / f"{sanitize_filename(submission.submission_id)}.json"
            )
            raw_payload = {
                "source_rel_path": submission.relative_path,
                "internal_file_count": len(submission.internal_files),
                "total_code_word_count": sum(
                    item.word_count for item in submission.internal_files
                ),
                "estimated_credits_for_this_submission": credit_info[
                    "estimated_credits_for_this_submission"
                ],
                "estimated_request_count": credit_info["estimated_request_count"],
                "internal_files": internal_file_outputs,
                "submission_aggregated": submission_agg,
            }
            raw_json_path.write_text(
                json.dumps(raw_payload, ensure_ascii=False, indent=2), encoding="utf-8"
            )

            detection_rows.append(
                {
                    "source_rel_path": submission.relative_path,
                    "file_name": submission.source_path.name,
                    "submission_id": submission.submission_id,
                    "internal_file_count": len(submission.internal_files),
                    "code_word_count": sum(
                        item.word_count for item in submission.internal_files
                    ),
                    "estimated_credits_for_this_submission": credit_info[
                        "estimated_credits_for_this_submission"
                    ],
                    "fraction_ai": submission_agg["fraction_ai"],
                    "fraction_ai_assisted": submission_agg["fraction_ai_assisted"],
                    "fraction_human": submission_agg["fraction_human"],
                    "dominant_class": submission_agg["dominant_class"],
                    "num_ai_segments": submission_agg["num_ai_segments"],
                    "num_ai_assisted_segments": submission_agg[
                        "num_ai_assisted_segments"
                    ],
                    "num_human_segments": submission_agg["num_human_segments"],
                    "version": submission_agg["version"],
                    "headline_last_chunk": submission_agg["headline_last_chunk"],
                    "prediction_last_chunk": submission_agg["prediction_last_chunk"],
                    "prediction_short_last_chunk": submission_agg[
                        "prediction_short_last_chunk"
                    ],
                    "dashboard_links_joined": submission_agg["dashboard_links_joined"],
                    "raw_json_path": str(raw_json_path),
                    "status": "ok",
                    "error": "",
                }
            )
        except Exception as exc:
            detection_rows.append(
                {
                    "source_rel_path": submission.relative_path,
                    "file_name": submission.source_path.name,
                    "submission_id": submission.submission_id,
                    "internal_file_count": "",
                    "code_word_count": "",
                    "estimated_credits_for_this_submission": "",
                    "fraction_ai": "",
                    "fraction_ai_assisted": "",
                    "fraction_human": "",
                    "dominant_class": "",
                    "num_ai_segments": "",
                    "num_ai_assisted_segments": "",
                    "num_human_segments": "",
                    "version": "",
                    "headline_last_chunk": "",
                    "prediction_last_chunk": "",
                    "prediction_short_last_chunk": "",
                    "dashboard_links_joined": "",
                    "raw_json_path": "",
                    "status": "failed",
                    "error": str(exc),
                }
            )
            if "Insufficient credits" in str(exc):
                break

    detection_results_csv = config.output_root / "code_detection_results.csv"
    write_csv(detection_results_csv, detection_rows)
    summary["detection_results_csv"] = str(detection_results_csv)
    return summary


def main() -> None:
    config = PipelineConfig.from_env()
    detector: Optional[DetectorClient] = None
    if config.run_detection and os.environ.get(
        "CODE_DETECTION_USE_SYNTHETIC_DETECTOR", "false"
    ).strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }:
        detector = SyntheticDetectorClient()
    result = run_pipeline(config, detector=detector)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
