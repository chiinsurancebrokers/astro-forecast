"""
Builds a Ganesha-report-style narrative: life areas grouped into sections
(Business, Career, Finance, Relationships, General Notes), each broken
into quarters, with LLM-written prose grounded in deterministic quarter
statistics computed here in Python (the LLM never does the arithmetic,
only the writing).
"""
import json
import os

AREA_GROUPS = {
    "business": ["business", "external_money", "claims_settlements"],
    "career": ["career", "earned_income", "major_change"],
    "finance": ["money", "sudden_gain", "financial_risk", "spending_loss_risk",
                "luxury_assets", "home_property"],
    "relationships": ["love", "marriage_commitment", "sex_chemistry", "socialization"],
    "general": ["travel_foreign", "social_isolation", "social_friction"],
}

SECTION_ORDER = ["business", "career", "finance", "relationships", "general"]


def build_quarterly_summary(monthly_scores, months_per_quarter=3):
    """
    Groups the monthly_scores dict (ordered YYYY-MM keys) into consecutive
    quarters and returns:
    [{"label": "2026-08 to 2026-10", "months": [...], "areas": {area: {avg,min,max}}}, ...]
    """
    months = list(monthly_scores.keys())
    quarters = []
    for i in range(0, len(months), months_per_quarter):
        chunk = months[i:i + months_per_quarter]
        if not chunk:
            continue
        label = chunk[0] if len(chunk) == 1 else f"{chunk[0]} to {chunk[-1]}"
        area_keys = list(monthly_scores[chunk[0]].keys())
        areas = {}
        for area in area_keys:
            vals = [monthly_scores[m][area] for m in chunk]
            areas[area] = {
                "avg": round(sum(vals) / len(vals), 1),
                "min": min(vals),
                "max": max(vals),
            }
        quarters.append({"label": label, "months": chunk, "areas": areas})
    return quarters


def _group_stats_line(areas, area_list):
    parts = []
    for a in area_list:
        st = areas.get(a)
        if st:
            parts.append(f"{a}: avg={st['avg']}, range={st['min']}-{st['max']}")
    return "; ".join(parts)


def build_narrative_context(chart, dasha_info, quarters, house_events, lang="en"):
    asc = chart["ascendant"]
    lines = []
    lines.append(f"Ascendant: {asc['sign']} {asc['sign_deg']:.2f} degrees.")
    lines.append(f"Current Mahadasha: {dasha_info.get('current_mahadasha')}, "
                  f"current Antardasha: {dasha_info.get('current_antardasha')}.")
    lines.append("All figures below are raw, uncalibrated 0-100 transit-activation scores.")
    lines.append("")
    lines.append("QUARTERS:")
    for q in quarters:
        lines.append(f"- {q['label']}:")
        for group, area_list in AREA_GROUPS.items():
            stats = _group_stats_line(q["areas"], area_list)
            lines.append(f"    [{group}] {stats}")
    if house_events:
        lines.append("")
        lines.append("Major slow-planet house changes in this window:")
        for ev in house_events:
            retro = " (retrograde)" if ev["retrograde"] else ""
            lines.append(f"  {ev['date']}: {ev['planet']} {ev['from_sign']} -> "
                          f"{ev['to_sign']}{retro}")
    return "\n".join(lines)


NARRATIVE_SYSTEM_PROMPT = {
    "en": (
        "You are writing a structured astrology forecast report from a "
        "sidereal (Lahiri) Vedic transit-scoring tool. The underlying "
        "scores are RAW and UNCALIBRATED heuristics, never validated "
        "against real outcomes -- write in a grounded, practical register "
        "(\"the data shows elevated pressure in...\", not \"you will...\"). "
        "Never invent facts, gemstones, rituals, or specifics not implied "
        "by the supplied statistics. For each quarter in each section, "
        "write one natural paragraph (3-5 sentences) that reads like a "
        "professional forecast, grounded in that quarter's actual average/"
        "range figures, without reciting the raw numbers verbatim. Output "
        "ONLY valid JSON, no markdown fences, no commentary, matching "
        "exactly this schema:\n"
        '{"intro": "2-3 sentence framing paragraph", '
        '"sections": {"business": [{"quarter": "<label>", "text": "<para>"}, ...], '
        '"career": [...], "finance": [...], "relationships": [...], "general": [...]}, '
        '"practical_notes": "short paragraph of grounded, practical things to pay '
        'attention to -- never gemstones, rituals, or medical/financial advice", '
        '"conclusion": "closing paragraph"}\n'
        "Every section must have one entry per quarter given. Write in English."
    ),
    "el": (
        "Γράφεις μια δομημένη αναφορά αστρολογικής πρόβλεψης από ένα "
        "εργαλείο βαθμολόγησης διαβατικών περιόδων Βεδικής αστρολογίας "
        "(sidereal, Lahiri). Οι τιμές είναι ΑΚΑΤΕΡΓΑΣΤΕΣ και ΜΗ "
        "ΒΑΘΜΟΝΟΜΗΜΕΝΕΣ ευρετικές, χωρίς επαλήθευση σε πραγματικά "
        "αποτελέσματα -- γράψε σε προσγειωμένο, πρακτικό ύφος (\"τα "
        "δεδομένα δείχνουν αυξημένη πίεση σε...\", όχι \"θα σας συμβεί...\"). "
        "Μην επινοείς γεγονότα, πολύτιμους λίθους, τελετουργίες ή "
        "λεπτομέρειες που δεν προκύπτουν από τα δεδομένα. Για κάθε τρίμηνο "
        "σε κάθε ενότητα, γράψε μία φυσική παράγραφο (3-5 προτάσεις) σε "
        "επαγγελματικό ύφος πρόβλεψης, βασισμένη στα πραγματικά στοιχεία "
        "μέσου όρου/εύρους του τριμήνου, χωρίς να απαγγέλλεις τους "
        "ακατέργαστους αριθμούς αυτολεξεί. Έξοδος ΜΟΝΟ σε έγκυρο JSON, "
        "χωρίς markdown, χωρίς σχόλια, ακριβώς με αυτό το σχήμα:\n"
        '{"intro": "παράγραφος πλαισίωσης 2-3 προτάσεων", '
        '"sections": {"business": [{"quarter": "<ετικέτα>", "text": "<παράγραφος>"}, ...], '
        '"career": [...], "finance": [...], "relationships": [...], "general": [...]}, '
        '"practical_notes": "σύντομη παράγραφος με πρακτικά σημεία προσοχής -- ποτέ '
        'πολύτιμοι λίθοι, τελετουργίες ή ιατρικές/οικονομικές συμβουλές", '
        '"conclusion": "παράγραφος κλεισίματος"}\n'
        "Κάθε ενότητα πρέπει να έχει μία καταχώρηση ανά τρίμηνο. Γράψε στα Ελληνικά."
    ),
}


def _strip_fences(text):
    t = text.strip()
    if t.startswith("```"):
        t = t.split("\n", 1)[1] if "\n" in t else t
        if t.endswith("```"):
            t = t.rsplit("```", 1)[0]
    return t.strip()


def _extract_json_span(text):
    """Fallback: pull the first {...} span out of text that may contain
    stray prose around the JSON (e.g. a model preface like 'Here is the
    report:'). Uses brace matching so nested braces don't break it."""
    start = text.find("{")
    if start == -1:
        return None
    depth = 0
    for i in range(start, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                return text[start:i + 1]
    return None


def _parse_json_response(raw_text):
    candidate = _strip_fences(raw_text)
    try:
        return json.loads(candidate), None
    except Exception as e:
        span = _extract_json_span(candidate)
        if span:
            try:
                return json.loads(span), None
            except Exception:
                pass
        return None, f"Could not parse model output as JSON ({e})"


def request_narrative_claude(context, lang="en"):
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return {"error": "ANTHROPIC_API_KEY is not set."}
    model = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-6")
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key, timeout=90)
        resp = client.messages.create(
            model=model,
            max_tokens=4000,
            system=NARRATIVE_SYSTEM_PROMPT.get(lang, NARRATIVE_SYSTEM_PROMPT["en"]),
            messages=[
                {"role": "user", "content": f"DATA:\n{context}"},
            ],
        )
        raw = "".join(b.text for b in resp.content if hasattr(b, "text"))
        parsed, err = _parse_json_response(raw)
        if err:
            return {"model": model, "error": err, "raw": raw}
        return {"model": model, "report": parsed}
    except Exception as e:
        return {"error": str(e)}


def request_narrative_chatgpt(context, lang="en"):
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return {"error": "OPENAI_API_KEY is not set."}
    model = os.environ.get("OPENAI_MODEL", "gpt-4o")
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key, timeout=90)
        resp = client.chat.completions.create(
            model=model,
            max_tokens=4000,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": NARRATIVE_SYSTEM_PROMPT.get(lang, NARRATIVE_SYSTEM_PROMPT["en"])},
                {"role": "user", "content": f"DATA:\n{context}"},
            ],
        )
        raw = resp.choices[0].message.content
        parsed, err = _parse_json_response(raw)
        if err:
            return {"model": model, "error": err, "raw": raw}
        return {"model": model, "report": parsed}
    except Exception as e:
        return {"error": str(e)}


def build_narrative_report(provider, chart, dasha_info, monthly_scores, house_events, lang="en"):
    quarters = build_quarterly_summary(monthly_scores)
    context = build_narrative_context(chart, dasha_info, quarters, house_events, lang)
    if provider == "chatgpt":
        return request_narrative_chatgpt(context, lang)
    return request_narrative_claude(context, lang)
