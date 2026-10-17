import json
import tempfile
import unittest
from pathlib import Path

from astro.book_ingest import (
    SOURCE_MANIFEST,
    build_chunks,
    classify_topics,
    validate_curated_rules,
)


class BookIngestTests(unittest.TestCase):
    def test_chunks_keep_page_spans_and_deterministic_ids(self):
        source = next(item for item in SOURCE_MANIFEST if item.source_id == "raleigh_hermetic")
        pages = [
            (4, "motion number " + " ".join(f"word{i}" for i in range(28))),
            (5, "planet house " + " ".join(f"term{i}" for i in range(28))),
        ]
        first = build_chunks(
            pages, source, "a" * 64, max_words=40, overlap_words=10, min_words=10
        )
        second = build_chunks(
            pages, source, "a" * 64, max_words=40, overlap_words=10, min_words=10
        )
        self.assertEqual([chunk.chunk_id for chunk in first], [chunk.chunk_id for chunk in second])
        self.assertEqual(first[0].page_start, 4)
        self.assertEqual(first[0].page_end, 5)
        self.assertEqual(first[0].status, "pending_review")
        self.assertIn("motion", first[0].topics)

    def test_chunk_parameters_are_validated(self):
        with self.assertRaises(ValueError):
            build_chunks(
                [], SOURCE_MANIFEST[0], "b" * 64, max_words=20, overlap_words=20
            )

    def test_topic_classifier_tags_concepts(self):
        tags = classify_topics(
            "Medical astrology considers planetary strength, houses and aspects."
        )
        self.assertIn("medical_astrology", tags)
        self.assertIn("planets", tags)
        self.assertIn("houses", tags)
        self.assertIn("aspects", tags)

    def test_curated_rules_validate_provenance_and_reject_raw_text(self):
        rule = {
            "id": "raleigh.test.motion",
            "source": "raleigh_hermetic",
            "system": "HERMETIC_HISTORICAL",
            "topics": ["motion"],
            "locator": "pages 4-5",
            "summary": "The text treats motion and number as connected historical principles.",
            "keywords": ["motion", "number"],
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "rules.jsonl"
            path.write_text(json.dumps(rule) + "\n", encoding="utf-8")
            self.assertEqual(validate_curated_rules(path), [])
            path.write_text(json.dumps({**rule, "text": "raw excerpt"}) + "\n", encoding="utf-8")
            self.assertTrue(any("raw source text" in error for error in validate_curated_rules(path)))
            for invalid in ({**rule, "source": []}, {**rule, "topics": [{}]}):
                path.write_text(json.dumps(invalid) + "\n", encoding="utf-8")
                self.assertTrue(validate_curated_rules(path))


if __name__ == "__main__":
    unittest.main()
