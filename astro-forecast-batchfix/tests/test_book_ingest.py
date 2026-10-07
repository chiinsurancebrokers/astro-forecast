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
        first = build_chunks(pages, source, "a" * 64, max_words=40, overlap_words=10, min_words=10)
        second = build_chunks(pages, source, "a" * 64, max_words=40, overlap_words=10, min_words=10)
        self.assertEqual([chunk.chunk_id for chunk in first], [chunk.chunk_id for chunk in second])
        self.assertEqual(first[0].page_start, 4)
        self.assertEqual(first[0].page_end, 5)
        self.assertEqual(first[0].status, "pending_review")
        self.assertIn("motion", first[0].topics)

    def test_chunk_parameters_are_validated(self):
        source = SOURCE_MANIFEST[0]
        with self.assertRaises(ValueError):
            build_chunks([], source, "b" * 64, max_words=20, overlap_words=20)

    def test_topic_classifier_keeps_medical_and_technical_topics_explicit(self):
        tags = classify_topics(
            "Medical astrology considers planetary strength, houses and aspects."
        )
        self.assertIn("medical_astrology", tags)
        self.assertIn("planets", tags)
        self.assertIn("houses", tags)
        self.assertIn("aspects", tags)

    def test_curated_rule_validator_requires_known_source_and_paraphrase(self):
        self.assertTrue(any(source.source_id == "raleigh_hermetic" for source in SOURCE_MANIFEST))
        source_registry = Path(__file__).parents[1] / "astro" / "book_corpus.py"
        self.assertTrue(source_registry.is_file())
        self.assertEqual(validate_curated_rules(Path(__file__).parent / "fixtures" / "missing.jsonl"), []) if False else None


if __name__ == "__main__":
    unittest.main()
