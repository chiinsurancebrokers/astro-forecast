import json
import tempfile
import unittest
from pathlib import Path

from astro.book_agent import BookKnowledgeAgent
from astro.book_library import BookKnowledgeLibrary


class BookKnowledgeLibraryTests(unittest.TestCase):
    def setUp(self):
        self.library = BookKnowledgeLibrary()

    def test_analysis_retrieval_flattens_topic_groups(self):
        hits = self.library.retrieve_for_analysis(
            life_areas=["career", "money"],
            chart_topics=["natal", "dignities", "aspects", "houses"],
            timing_topics=["transits", "timing"],
        )
        self.assertTrue(hits)
        self.assertTrue(
            any(
                set(hit.topics) & {"natal", "dignities", "aspects", "houses"}
                for hit in hits
            )
        )

    def test_medical_material_is_opt_in(self):
        default_hits = self.library.retrieve_for_analysis(chart_topics=["natal"])
        medical_hits = self.library.retrieve_for_analysis(
            chart_topics=["natal"], include_medical=True
        )
        self.assertFalse(any(hit.system == "MEDICAL_ASTROLOGY" for hit in default_hits))
        self.assertTrue(any(hit.system == "MEDICAL_ASTROLOGY" for hit in medical_hits))

    def test_system_filter_keeps_traditions_separate(self):
        hits = self.library.search(
            topics=["medical astrology"], systems=["MEDICAL_ASTROLOGY"]
        )
        self.assertTrue(hits)
        self.assertTrue(all(hit.system == "MEDICAL_ASTROLOGY" for hit in hits))

    def test_agent_uses_retrieval_without_crashing(self):
        result = BookKnowledgeAgent(self.library).run(
            question="career timing", life_areas=["career"], timing=True
        )
        self.assertEqual(result["system"], "SOURCE_AWARE_LIBRARY")
        self.assertTrue(result["hits"])
        self.assertIn("Guide to Astrology", result["context"])

    def test_result_limit_is_capped_and_positive(self):
        self.assertLessEqual(len(self.library.search(limit=500)), 50)
        self.assertLessEqual(len(self.library.search(limit=2)), 2)
        self.assertEqual(len(self.library.search(limit=0)), 1)

    def test_private_curated_rules_join_agent_retrieval(self):
        rule = {
            "id": "raleigh.test.motion",
            "source": "raleigh_hermetic",
            "system": "HERMETIC_HISTORICAL",
            "topics": ["motion", "number"],
            "locator": "pages 4-5",
            "summary": "The text treats motion and number as connected historical principles.",
            "keywords": ["motion", "number"],
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "rules.jsonl"
            path.write_text(json.dumps(rule) + "\n", encoding="utf-8")
            library = BookKnowledgeLibrary(rules_path=path)
            hits = library.search(
                query="motion", source_ids=["raleigh_hermetic"]
            )
        self.assertEqual([hit.id for hit in hits], ["raleigh.test.motion"])
        self.assertEqual(hits[0].system, "HERMETIC_HISTORICAL")

    def test_private_curated_rules_reject_raw_text_and_system_mismatch(self):
        cases = [
            {
                "id": "raleigh.test.bad-source",
                "source": [],
                "system": "HERMETIC_HISTORICAL",
                "topics": ["motion"],
                "locator": "page 4",
                "summary": "A concise paraphrase of the historical source material.",
                "keywords": ["motion"],
            },
            {
                "id": "raleigh.test.bad-topics",
                "source": "raleigh_hermetic",
                "system": "HERMETIC_HISTORICAL",
                "topics": [{}],
                "locator": "page 4",
                "summary": "A concise paraphrase of the historical source material.",
                "keywords": ["motion"],
            },
            {
                "id": "raleigh.test.raw",
                "source": "raleigh_hermetic",
                "system": "HERMETIC_HISTORICAL",
                "topics": ["motion"],
                "locator": "page 4",
                "summary": "A concise paraphrase of the historical source material.",
                "keywords": ["motion"],
                "text": "Raw source text must not enter agent-facing rules.",
            },
            {
                "id": "raleigh.test.mixed",
                "source": "raleigh_hermetic",
                "system": "WESTERN_TRADITIONAL",
                "topics": ["motion"],
                "locator": "page 4",
                "summary": "A concise paraphrase of the historical source material.",
                "keywords": ["motion"],
            },
        ]
        for rule in cases:
            with self.subTest(rule=rule["id"]), tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / "rules.jsonl"
                path.write_text(json.dumps(rule) + "\n", encoding="utf-8")
                with self.assertRaises(ValueError):
                    BookKnowledgeLibrary(rules_path=path)


if __name__ == "__main__":
    unittest.main()
