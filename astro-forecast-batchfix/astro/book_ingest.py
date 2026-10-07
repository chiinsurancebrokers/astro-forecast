"""Private, page-aware ingestion of historical astrology books.

The extractor creates review candidates only. It does not promote raw book text
into agent-facing rules; a human must curate concise paraphrases with locators
before a rule is made available to the Book Knowledge Agent.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, Sequence

from .book_corpus import SOURCES

WORD_RE = re.compile(r"\S+")
TAG_PATTERNS = {
    "planets": r"\b(planets?|planetary|sun|moon|mercury|venus|mars|jupiter|saturn|uranus|neptune)\b",
    "signs": r"\b(zodiac|signs?|aries|taurus|gemini|cancer|leo|virgo|libra|scorpio|sagittarius|capricorn|aquarius|pisces)\b",
    "motion": r"\b(motion|retrograde|stationary|heliocentric)\b",
    "number": r"\b(number|numerical|arithmetic|measure)\b",
    "houses": r"\b(houses?|ascendant|midheaven|rising sign|mundane)\b",
    "aspects": r"\b(aspects?|conjunction|sextile|square|trine|opposition|orb)\b",
    "dignities": r"\b(dignit(y|ies)|rulership|exaltation|detriment|fall)\b",
    "genethliacal": r"\b(genethliacal|nativity|natal|radix|birth chart)\b",
    "directions": r"\b(directions?|progressions?|primary direction|solar arc)\b",
    "transits": r"\b(transits?|ingress|ingresses)\b",
    "solar_returns": r"\b(solar return|birthday figure|revolution of the sun)\b",
    "medical_astrology": r"\b(medical astrology|anatom(y|ical)|disease|physiolog(y|ical)|health)\b",
    "career": r"\b(employment|profession|vocation|career|business)\b",
    "relationships": r"\b(marriage|relationship|partner|husband|wife|love)\b",
}
COMPILED_TAGS = {tag: re.compile(pattern, re.IGNORECASE) for tag, pattern in TAG_PATTERNS.items()}


@dataclass(frozen=True)
class SourceDefinition:
    source_id: str
    filename: str
    title: str
    author: str
    system: str
    base_topics: tuple[str, ...]


SOURCE_MANIFEST = (
    SourceDefinition(
        "karma_ancient_egyptians", "astrologyofancie00karm(1).pdf",
        "Astrology of the Ancient Egyptians", "Karma",
        "WESTERN_TRADITIONAL", ("genethliacal",),
    ),
    SourceDefinition(
        "raphael_guide", "guidetoastrology00raphiala(1).pdf",
        "The Guide to Astrology: Containing a Complete System of Genethliacal Astrology",
        "Raphael", "WESTERN_TRADITIONAL", ("genethliacal",),
    ),
    SourceDefinition(
        "merton_heliocentric", "heliocentricast00mert(1).pdf",
        "Heliocentric Astrology", "Holmes Whittier Merton",
        "HELIOCENTRIC_HISTORICAL", (),
    ),
    SourceDefinition(
        "daath_medical", "b24886038(1).pdf",
        "Medical Astrology", "Heinrich Daath", "MEDICAL_ASTROLOGY",
        ("medical_astrology",),
    ),
    SourceDefinition(
        "white_guide", "A Guide To Astrology by Fredrick White(1).pdf",
        "A Guide to Astrology", "Fredrick White", "WESTERN_TRADITIONAL",
        ("genethliacal",),
    ),
    SourceDefinition(
        "raleigh_hermetic", "Hermetic-Science-of-Motion-and-Number_-_A-S-Raleigh.pdf",
        "Hermetic Science of Motion and Number", "A. S. Raleigh",
        "HERMETIC_HISTORICAL", (),
    ),
)


@dataclass
class BookChunk:
    chunk_id: str
    source_id: str
    source_title: str
    author: str
    system: str
    source_sha256: str
    page_start: int
    page_end: int
    topics: list[str]
    text: str
    status: str = "pending_review"

    def to_dict(self):
        return asdict(self)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def classify_topics(text: str, base_topics: Sequence[str] = ()) -> list[str]:
    tags = set(base_topics)
    for tag, pattern in COMPILED_TAGS.items():
        if pattern.search(text):
            tags.add(tag)
    return sorted(tags)


def build_chunks(
    pages: Iterable[tuple[int, str]],
    source: SourceDefinition,
    source_sha256: str,
    max_words: int = 350,
    overlap_words: int = 40,
    min_words: int = 35,
) -> list[BookChunk]:
    """Build deterministic overlapping chunks while retaining exact page spans."""
    if max_words < 1 or overlap_words < 0 or overlap_words >= max_words:
        raise ValueError("Require max_words > overlap_words >= 0 and max_words >= 1")

    words: list[tuple[str, int]] = []
    for page_number, page_text in pages:
        words.extend((word, page_number) for word in WORD_RE.findall(page_text or ""))

    chunks = []
    step = max_words - overlap_words
    offset = 0
    while offset < len(words):
        window = words[offset:offset + max_words]
        if len(window) < min_words:
            break
        text = " ".join(word for word, _ in window)
        page_start = min(page for _, page in window)
        page_end = max(page for _, page in window)
        material = f"{source.source_id}:{source_sha256}:{offset}:{page_start}:{page_end}"
        chunk_id = hashlib.sha256(material.encode("utf-8")).hexdigest()[:24]
        chunks.append(BookChunk(
            chunk_id=chunk_id,
            source_id=source.source_id,
            source_title=source.title,
            author=source.author,
            system=source.system,
            source_sha256=source_sha256,
            page_start=page_start,
            page_end=page_end,
            topics=classify_topics(text, source.base_topics),
            text=text,
        ))
        if offset + max_words >= len(words):
            break
        offset += step
    return chunks


def _ocr_page(pdf_path: Path, page_number: int) -> str:
    """OCR one sparse page when Poppler and Tesseract are installed."""
    if not shutil.which("pdftoppm") or not shutil.which("tesseract"):
        return ""
    with tempfile.TemporaryDirectory(prefix="astro-book-ocr-") as directory:
        prefix = Path(directory) / "page"
        render = subprocess.run(
            [
                "pdftoppm", "-f", str(page_number), "-l", str(page_number),
                "-r", "180", "-png", "-singlefile", str(pdf_path), str(prefix),
            ],
            capture_output=True, text=True, timeout=120, check=False,
        )
        image_path = prefix.with_suffix(".png")
        if render.returncode != 0 or not image_path.is_file():
            return ""
        result = subprocess.run(
            ["tesseract", str(image_path), "stdout", "-l", "eng", "--psm", "6"],
            capture_output=True, text=True, timeout=120, check=False,
        )
        return result.stdout if result.returncode == 0 else ""


def extract_pdf(path: Path, source: SourceDefinition, max_words: int = 350,
                overlap_words: int = 40, ocr_sparse: bool = True
                ) -> tuple[list[BookChunk], list[int], int, list[int]]:
    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise RuntimeError("Install pypdf to extract source PDFs") from exc

    reader = PdfReader(str(path), strict=False)
    page_texts = []
    sparse_pages = []
    recovered_pages = []
    ocr_available = ocr_sparse and shutil.which("pdftoppm") and shutil.which("tesseract")
    for index, page in enumerate(reader.pages, start=1):
        text = page.extract_text(extraction_mode="layout") or ""
        cleaned = re.sub(r"[\t\r\f]+", " ", text)
        cleaned = re.sub(r" *\n *", "\n", cleaned)
        if len(WORD_RE.findall(cleaned)) < 20:
            if ocr_available:
                ocr_text = _ocr_page(path, index)
                if len(WORD_RE.findall(ocr_text)) > len(WORD_RE.findall(cleaned)):
                    cleaned = re.sub(r"[\t\r\f]+", " ", ocr_text)
                    cleaned = re.sub(r" *\n *", "\n", cleaned)
                    recovered_pages.append(index)
            if len(WORD_RE.findall(cleaned)) < 20:
                sparse_pages.append(index)
        page_texts.append((index, cleaned))

    chunks = build_chunks(
        page_texts, source, sha256_file(path), max_words=max_words,
        overlap_words=overlap_words,
    )
    return chunks, sparse_pages, len(reader.pages), recovered_pages


def write_jsonl(chunks: Iterable[BookChunk], output: Path) -> int:
    output.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with output.open("w", encoding="utf-8") as stream:
        for chunk in chunks:
            stream.write(json.dumps(chunk.to_dict(), ensure_ascii=False) + "\n")
            count += 1
    return count


def ingest_directory(input_dir: Path, output: Path, ocr_sparse: bool = True) -> dict:
    input_dir = input_dir.expanduser().resolve()
    all_chunks = []
    report = []
    for source in SOURCE_MANIFEST:
        pdf_path = input_dir / source.filename
        if not pdf_path.is_file():
            report.append({"source_id": source.source_id, "status": "missing"})
            continue
        chunks, sparse_pages, page_count, recovered_pages = extract_pdf(
            pdf_path, source, ocr_sparse=ocr_sparse
        )
        all_chunks.extend(chunks)
        report.append({
            "source_id": source.source_id,
            "status": "extracted",
            "pages": page_count,
            "chunks": len(chunks),
            "sparse_pages": sparse_pages,
            "ocr_recovered_pages": recovered_pages,
            "ocr_attempted": bool(ocr_sparse and shutil.which("pdftoppm") and shutil.which("tesseract")),
            "sha256": sha256_file(pdf_path),
        })
    total = write_jsonl(all_chunks, output)
    return {"output": str(output), "total_chunks": total, "sources": report}


def validate_curated_rules(path: Path) -> list[str]:
    """Validate concise, paraphrased rules before they can enter agent retrieval."""
    errors = []
    seen_ids = set()
    required = {"id", "source", "system", "topics", "locator", "summary", "keywords"}
    with path.open(encoding="utf-8") as stream:
        for line_number, line in enumerate(stream, start=1):
            if not line.strip():
                continue
            try:
                item = json.loads(line)
            except json.JSONDecodeError as exc:
                errors.append(f"line {line_number}: invalid JSON ({exc.msg})")
                continue
            if not isinstance(item, dict):
                errors.append(f"line {line_number}: each rule must be a JSON object")
                continue
            missing = sorted(required - set(item))
            if missing:
                errors.append(f"line {line_number}: missing {', '.join(missing)}")
                continue
            if "text" in item or "excerpt" in item:
                errors.append(f"line {line_number}: raw source text is not an agent rule")
            rule_id = item.get("id")
            if not isinstance(rule_id, str) or not rule_id.strip():
                errors.append(f"line {line_number}: id must be a non-empty string")
            elif rule_id in seen_ids:
                errors.append(f"line {line_number}: duplicate id {rule_id}")
            else:
                seen_ids.add(rule_id)
            source_id = item.get("source")
            if not isinstance(source_id, str):
                errors.append(f"line {line_number}: source must be a string")
            else:
                source = SOURCES.get(source_id)
                if source is None:
                    errors.append(f"line {line_number}: unknown source {source_id}")
                elif item.get("system") != source.get("system"):
                    errors.append(f"line {line_number}: system does not match source {source_id}")
            if (not isinstance(item["topics"], list) or not item["topics"]
                    or not all(isinstance(topic, str) and topic.strip() for topic in item["topics"])):
                errors.append(f"line {line_number}: topics must be a non-empty list of strings")
            if not isinstance(item["locator"], str) or not item["locator"].strip():
                errors.append(f"line {line_number}: locator must identify a page or chapter")
            if not isinstance(item["summary"], str) or not 20 <= len(item["summary"]) <= 600:
                errors.append(f"line {line_number}: summary must be a concise 20-600 character paraphrase")
            if (not isinstance(item["keywords"], list)
                    or not all(isinstance(keyword, str) for keyword in item["keywords"])):
                errors.append(f"line {line_number}: keywords must be a list of strings")
    return errors


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", type=Path, help="Folder containing the uploaded source PDFs")
    parser.add_argument("--output", type=Path, help="Private JSONL path for extracted review candidates")
    parser.add_argument("--validate-rules", type=Path, help="Validate a curated, paraphrased rules JSONL file")
    parser.add_argument("--no-ocr", action="store_true", help="Skip OCR fallback for sparse pages")
    args = parser.parse_args(argv)

    if args.validate_rules:
        errors = validate_curated_rules(args.validate_rules)
        if errors:
            print(json.dumps({"valid": False, "errors": errors}, ensure_ascii=False, indent=2))
            return 1
        print(json.dumps({"valid": True, "path": str(args.validate_rules)}, ensure_ascii=False))
        return 0

    if not args.input_dir or not args.output:
        parser.error("provide --input-dir and --output, or use --validate-rules")
    report = ingest_directory(args.input_dir, args.output, ocr_sparse=not args.no_ocr)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
