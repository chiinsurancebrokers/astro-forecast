"""Retrieval layer for the Book Knowledge Library.

No external vector database is required for the first version. Retrieval combines
topic tags, source/system filters and lightweight lexical scoring. The interface
is intentionally stable so an embedding/vector backend can replace the scorer
later without changing the agents.
"""
import re
from dataclasses import dataclass, asdict
from typing import Iterable

from .book_corpus import SOURCES, ENTRIES, TOPIC_ALIASES

TOKEN_RE = re.compile(r"[A-Za-zΑ-Ωα-ω0-9_]+", re.UNICODE)


def _tokens(text):
    return {t.lower() for t in TOKEN_RE.findall(text or "") if len(t) > 1}


def _normalize_topic(term):
    low = (term or "").strip().lower()
    return TOPIC_ALIASES.get(low, low.replace(" ", "_"))


@dataclass
class KnowledgeHit:
    id: str
    score: float
    source_id: str
    source_title: str
    system: str
    topics: list[str]
    locator: str
    summary: str
    keywords: list[str]

    def to_dict(self):
        return asdict(self)


class BookKnowledgeLibrary:
    def __init__(self, entries=None, sources=None):
        self.entries = list(entries or ENTRIES)
        self.sources = dict(sources or SOURCES)

    def list_sources(self):
        return [{"id": sid, **meta} for sid, meta in self.sources.items()]

    def topics(self):
        out = set()
        for e in self.entries:
            out.update(e.get("topics", []))
        return sorted(out)

    def search(self, query="", topics=None, systems=None, source_ids=None, limit=8):
        q_tokens = _tokens(query)
        topic_set = {_normalize_topic(t) for t in (topics or [])}
        system_set = set(systems or [])
        source_set = set(source_ids or [])
        hits = []

        for e in self.entries:
            if system_set and e["system"] not in system_set:
                continue
            if source_set and e["source"] not in source_set:
                continue

            e_topics = set(e.get("topics", []))
            normalized_topics = {_normalize_topic(t) for t in e_topics}
            if topic_set and not (topic_set & normalized_topics):
                continue

            haystack = " ".join([
                e.get("summary", ""),
                " ".join(e.get("keywords", [])),
                " ".join(e.get("topics", [])),
                e.get("locator", ""),
            ])
            e_tokens = _tokens(haystack)
            lexical = len(q_tokens & e_tokens)
            topic_bonus = 3 * len(topic_set & normalized_topics)
            exact_bonus = 4 if (query or "").strip().lower() in haystack.lower() and (query or "").strip() else 0
            score = lexical + topic_bonus + exact_bonus

            if q_tokens and score <= 0:
                continue

            source = self.sources[e["source"]]
            hits.append(KnowledgeHit(
                id=e["id"],
                score=float(score),
                source_id=e["source"],
                source_title=source["title"],
                system=e["system"],
                topics=list(e.get("topics", [])),
                locator=e["locator"],
                summary=e["summary"],
                keywords=list(e.get("keywords", [])),
            ))

        hits.sort(key=lambda h: (-h.score, h.source_title, h.id))
        return hits[:max(1, min(int(limit), 50))]

    def retrieve_for_analysis(self, life_areas=None, chart_topics=None, timing_topics=None, include_medical=False, limit=12):
        topics = set()
        for group in (life_areas or [], chart_topics or [], timing_topics or []):
            topics.add(_normalize_topic(group))
        if include_medical:
            topics.add("medical_astrology")
        return self.search(topics=sorted(topics), limit=limit)

    def context_block(self, hits: Iterable[KnowledgeHit]):
        lines = []
        for h in hits:
            lines.append(f"[{h.system}] {h.source_title} — {h.locator}: {h.summary}")
        return "\n".join(lines)
