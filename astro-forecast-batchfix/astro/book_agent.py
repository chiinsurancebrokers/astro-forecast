"""Book Knowledge Agent.

Selects relevant source-derived knowledge units for a concrete chart/question.
It never changes astronomical facts and never turns historical medical astrology
into clinical claims.
"""
from .book_library import BookKnowledgeLibrary


class BookKnowledgeAgent:
    name = "Book Knowledge Agent"

    def __init__(self, library=None):
        self.library = library or BookKnowledgeLibrary()

    def run(self, question="", chart=None, life_areas=None, timing=False, include_medical=False, limit=12):
        chart_topics = ["natal", "dignities", "aspects", "houses"]
        if chart and any(p.get("retrograde") for p in chart.get("planets", {}).values()):
            chart_topics.append("planetary_strength")

        timing_topics = ["transits", "timing", "directions", "solar_returns"] if timing else []
        hits = self.library.retrieve_for_analysis(
            life_areas=life_areas or [],
            chart_topics=chart_topics,
            timing_topics=timing_topics,
            include_medical=include_medical,
            limit=limit,
        )

        lexical_hits = self.library.search(question, limit=limit) if question else []
        merged = {}
        for h in hits + lexical_hits:
            old = merged.get(h.id)
            if old is None or h.score > old.score:
                merged[h.id] = h
        selected = sorted(merged.values(), key=lambda h: (-h.score, h.source_title))[:limit]

        return {
            "agent": self.name,
            "system": "SOURCE_AWARE_LIBRARY",
            "query": question,
            "hits": [h.to_dict() for h in selected],
            "context": self.library.context_block(selected),
            "notes": [
                "Source-derived knowledge is paraphrased and provenance-labelled.",
                "Conflicting schools are not silently reconciled.",
                "Historical medical astrology is symbolic only and not medical advice.",
            ],
        }
