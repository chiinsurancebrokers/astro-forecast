"""Retrieval layer for the Book Knowledge Library.

No external vector database is required for the first version. Retrieval combines
topic tags, source/system filters and lightweight lexical scoring. The interface
is intentionally stable so an embedding/vector backend can replace the scorer
later without changing the agents.
"""
import json
import os
import re
from dataclasses import dataclass, asdict
from pathlib import Path
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
    def __init__(self, entries=None, sources=None, rules_path=None):
        self.entries = list(ENTRIES if entries is None else entries)
        self.sources = dict(SOURCES if sources is None else sources)
        configured_path = rules_path or os.environ.get("ASTRO_KNOWLEDGE_RULES_PATH")
        if configured_path:
            self.entries.extend(self._load_curated_rules(Path(configured_path), self.sources))

    @staticmethod
    def _load_curated_rules(path, sources):
        """Load approved paraphrased rules from private or deployment-mounted JSONL."""
        required = {"id", "source", "system", "topics", "locator", "summary", "keywords"}
        loaded = []
        seen_ids = {entry.get("id") for entry in ENTRIES}
        with path.open(encoding="utf-8") as stream:
            for line_number, line in enumerate(stream, start=1):
                if not line.strip():
                    continue
                try:
                    rule = json.loads(line)
                except json.JSONDecodeError as exc:
                    raise ValueError(f"{path}:{line_number}: invalid JSON") from exc
                if not isinstance(rule, dict):
                    raise ValueError(f"{path}:{line_number}: each rule must be a JSON object")
                missing = sorted(required - set(rule))
                if missing:
                    raise ValueError(f"{path}:{line_number}: missing fields: {', '.join(missing)}")
                if "text" in rule or "excerpt" in rule:
                    raise ValueError(f"{path}:{line_number}: raw source text cannot be loaded as a rule")
                rule_id = rule["id"]
                source_id = rule["source"]
                system = rule["system"]
                if not isinstance(rule_id, str) or not rule_id.strip():
                    raise ValueError(f"{path}:{line_number}: id must be a non-empty string")
                if not isinstance(source_id, str) or not isinstance(system, str):
                    raise ValueError(f"{path}:{line_number}: source and system must be strings")
                source = sources.get(source_id)
                if source is None or source.get("system") != system:
                    raise ValueError(f"{path}:{line_number}: source/system provenance mismatch")
                if rule_id in seen_ids:
                    raise ValueError(f"{path}:{line_number}: duplicate rule id {rule_id}")
                if (not isinstance(rule["topics"], list) or not rule["topics"]
                        or not all(isinstance(topic, str) and topic.strip() for topic in rule["topics"])):
                    raise ValueError(f"{path}:{line_number}: topics must be a non-empty list of strings")
                if not isinstance(rule["locator"], str) or not rule["locator"].strip():
                    raise ValueError(f"{path}:{line_number}: locator must be a non-empty string")
                if not isinstance(rule["summary"], str) or not 20 <= len(rule["summary"]) <= 600:
                    raise ValueError(f"{path}:{line_number}: summary must be a 20-600 character paraphrase")
                if (not isinstance(rule["keywords"], list)
                        or not all(isinstance(keyword, str) for keyword in rule["keywords"])):
                    raise ValueError(f"{path}:{line_number}: keywords must be a list of strings")
                seen_ids.add(rule_id)
                loaded.append(rule)
        return loaded

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
        # Each input is a list of topics. Flatten these lists before normalizing;
        # passing the list itself to _normalize_topic caused the agent endpoint
        # to fail with AttributeError as soon as it requested chart context.
        for group in (life_areas or [], chart_topics or [], timing_topics or []):
            terms = group if isinstance(group, (list, tuple, set)) else [group]
            topics.update(_normalize_topic(term) for term in terms if term)
        if include_medical:
            topics.add("medical_astrology")
        return self.search(topics=sorted(topics), limit=limit)

    def context_block(self, hits: Iterable[KnowledgeHit]):
        lines = []
        for h in hits:
            lines.append(f"[{h.system}] {h.source_title} — {h.locator}: {h.summary}")
        return "\n".join(lines)
