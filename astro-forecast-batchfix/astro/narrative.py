"""
Builds a Ganesha-report-style narrative: life areas grouped into sections
(Business, Career, Finance, Relationships, General Notes), each broken
into quarters, with LLM-written prose grounded in deterministic quarter
statistics computed here in Python (the LLM never does the arithmetic,
only the writing).

Section prose is generated in BATCHES of a few quarters at a time rather
than in one giant call. A full report (intro + 5 sections x N quarters +
notes + conclusion) is long enough that a single request can hit the
model's max_tokens ceiling mid-response and produce truncated, unparsable
JSON -- this happened in practice at an 8-quarter (24-month) window with
a 4000-token cap. Batching keeps each individual call's output bounded no
matter how long the requested forecast window is. The intro/practical
notes/conclusion are generated separately, in one short call, from the
aggregate quarter statistics rather than the (much longer) per-quarter
prose.
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

# Quarters per section-writing call. 4 quarters x 5 sections x ~200 tokens
# per paragraph is comfortably under a 5000-token cap with headroom; keeps
# a typical 24-month (8-quarter) report to 2 batched calls.
QUARTERS_PER_BATCH = 4
SECTION_MAX_TOKENS = 5000
OVERVIEW_MAX_TOKENS = 900
PROVIDER_TIMEOUT_SECONDS = 60


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


def _chart_and_dasha_lines(chart, dasha_info):
    asc = chart["ascendant"]
    return [
        f"Ascendant: {asc['sign']} {asc['sign_deg']:.2f} degrees.",
        f"Current Mahadasha: {dasha_info.get('current_mahadasha')}, "
        f"current Antardasha: {dasha_info.get('current_antardasha')}.",
        "All figures below are raw, uncalibrated 0-100 transit-activation scores.",
    ]


def _quarters_block(quarters):
    lines = ["QUARTERS:"]
    for q in quarters:
        lines.append(f"- {q['label']}:")
        for group, area_list in AREA_GROUPS.items():
            stats = _group_stats_line(q["areas"], area_list)
            lines.append(f"    [{group}] {stats}")
    return lines


def build_batch_context(chart, dasha_info, quarters_batch, lang="en"):
    """Context for a single section-writing call -- only the quarters in this batch."""
    lines = _chart_and_dasha_lines(chart, dasha_info)
    lines.append("")
    lines += _quarters_block(quarters_batch)
    return "\n".join(lines)


def build_overview_context(chart, dasha_info, all_quarters, house_events, lang="en"):
    """Context for the intro/notes/conclusion call -- all quarters' stats, compact."""
    lines = _chart_and_dasha_lines(chart, dasha_info)
    lines.append(f"Full forecast window: {all_quarters[0]['label'].split(' to ')[0]} to "
                  f"{all_quarters[-1]['label'].split(' to ')[-1]} ({len(all_quarters)} quarters).")
    lines.append("")
    lines += _quarters_block(all_quarters)
    if house_events:
        lines.append("")
        lines.append("Major slow-planet house changes in this window:")
        for ev in house_events:
            retro = " (retrograde)" if ev["retrograde"] else ""
            lines.append(f"  {ev['date']}: {ev['planet']} {ev['from_sign']} -> "
                          f"{ev['to_sign']}{retro}")
    return "\n".join(lines)


SECTIONS_SYSTEM_PROMPT = {
    "en": (
        "You are writing part of a structured astrology forecast report "
        "from a sidereal (Lahiri) Vedic transit-scoring tool. The scores "
        "are RAW and UNCALIBRATED heuristics, never validated against "
        "real outcomes -- write in a grounded, practical register (\"the "
        "data shows elevated pressure in...\", not \"you will...\"). Never "
        "invent facts, gemstones, rituals, or specifics not implied by "
        "the supplied statistics. You will receive ONLY A SUBSET of the "
        "full forecast's quarters -- write sections for exactly those "
        "quarters, nothing more, nothing less. For each quarter in each "
        "of the five sections (business, career, finance, relationships, "
        "general), write ONE paragraph of 2-4 sentences grounded in that "
        "quarter's actual average/range figures, without reciting the "
        "raw numbers verbatim. Keep paragraphs concise -- this keeps the "
        "response short enough to complete. Output ONLY valid JSON, no "
        "markdown fences, no commentary, matching exactly this schema:\n"
        '{"sections": {"business": [{"quarter": "<label>", "text": "<para>"}, ...], '
        '"career": [...], "finance": [...], "relationships": [...], "general": [...]}}\n'
        "Every section must have exactly one entry per quarter you were "
        "given. Do not include an intro, conclusion, or notes -- sections "
        "only. Write in English."
    ),
    "el": (
        "Γράφεις ένα μέρος μιας δομημένης αναφοράς αστρολογικής "
        "πρόβλεψης από ένα εργαλείο βαθμολόγησης διαβατικών περιόδων "
        "Βεδικής αστρολογίας (sidereal, Lahiri). Οι τιμές είναι "
        "ΑΚΑΤΕΡΓΑΣΤΕΣ και ΜΗ ΒΑΘΜΟΝΟΜΗΜΕΝΕΣ ευρετικές, χωρίς επαλήθευση "
        "σε πραγματικά αποτελέσματα -- γράψε σε προσγειωμένο, πρακτικό "
        "ύφος. Μην επινοείς γεγονότα, πολύτιμους λίθους, τελετουργίες ή "
        "λεπτομέρειες που δεν προκύπτουν από τα δεδομένα. Θα λάβεις ΜΟΝΟ "
        "ΕΝΑ ΥΠΟΣΥΝΟΛΟ των τριμήνων της πλήρους πρόβλεψης -- γράψε "
        "ενότητες μόνο για αυτά τα τρίμηνα, ούτε ένα παραπάνω. Για κάθε "
        "τρίμηνο σε καθεμία από τις πέντε ενότητες (business, career, "
        "finance, relationships, general), γράψε ΜΙΑ παράγραφο 2-4 "
        "προτάσεων βασισμένη στα πραγματικά στοιχεία μέσου όρου/εύρους "
        "του τριμήνου, χωρίς να απαγγέλλεις τους αριθμούς αυτολεξεί. "
        "Κράτησε τις παραγράφους σύντομες. Έξοδος ΜΟΝΟ σε έγκυρο JSON, "
        "χωρίς markdown, χωρίς σχόλια, ακριβώς με αυτό το σχήμα:\n"
        '{"sections": {"business": [{"quarter": "<ετικέτα>", "text": "<παράγραφος>"}, ...], '
        '"career": [...], "finance": [...], "relationships": [...], "general": [...]}}\n'
        "Κάθε ενότητα πρέπει να έχει ακριβώς μία καταχώρηση ανά τρίμηνο "
        "που έλαβες. Μην συμπεριλάβεις εισαγωγή, συμπέρασμα ή σημειώσεις "
        "-- μόνο ενότητες. Γράψε στα Ελληνικά."
    ),
}

OVERVIEW_SYSTEM_PROMPT = {
    "en": (
        "You are writing the framing and closing material for a "
        "structured astrology forecast report from a sidereal (Lahiri) "
        "Vedic transit-scoring tool, covering the FULL forecast window "
        "described below. The scores are RAW and UNCALIBRATED, never "
        "validated against real outcomes. Write three short pieces: an "
        "intro (2-3 sentences framing the whole window, mentioning the "
        "governing dasha and the broad shape of the data across "
        "quarters), practical_notes (one short paragraph of grounded, "
        "practical things to pay attention to across the window -- never "
        "gemstones, rituals, or medical/financial advice), and a "
        "conclusion (one short closing paragraph). Do not write "
        "quarter-by-quarter detail -- that is handled elsewhere. Output "
        "ONLY valid JSON, no markdown fences, no commentary:\n"
        '{"intro": "...", "practical_notes": "...", "conclusion": "..."}\n'
        "Write in English."
    ),
    "el": (
        "Γράφεις το πλαίσιο και το κλείσιμο μιας δομημένης αναφοράς "
        "αστρολογικής πρόβλεψης από ένα εργαλείο βαθμολόγησης διαβατικών "
        "περιόδων Βεδικής αστρολογίας (sidereal, Lahiri), που καλύπτει "
        "ΟΛΟΚΛΗΡΟ το παράθυρο πρόβλεψης που περιγράφεται παρακάτω. Οι "
        "τιμές είναι ΑΚΑΤΕΡΓΑΣΤΕΣ και ΜΗ ΒΑΘΜΟΝΟΜΗΜΕΝΕΣ. Γράψε τρία "
        "σύντομα κομμάτια: μια εισαγωγή (2-3 προτάσεις πλαισίωσης όλου "
        "του παραθύρου, αναφέροντας την κυρίαρχη δάσα και τη γενική "
        "εικόνα των δεδομένων στα τρίμηνα), πρακτικές σημειώσεις (μία "
        "σύντομη παράγραφο πρακτικών σημείων προσοχής -- ποτέ πολύτιμοι "
        "λίθοι, τελετουργίες ή ιατρικές/οικονομικές συμβουλές), και ένα "
        "συμπέρασμα (μία σύντομη παράγραφο κλεισίματος). Μη γράψεις "
        "λεπτομέρειες ανά τρίμηνο -- αυτό γίνεται αλλού. Έξοδος ΜΟΝΟ σε "
        "έγκυρο JSON, χωρίς markdown, χωρίς σχόλια:\n"
        '{"intro": "...", "practical_notes": "...", "conclusion": "..."}\n'
        "Γράψε στα Ελληνικά."
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


def _call_claude(system_prompt, user_content, max_tokens):
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return None, "ANTHROPIC_API_KEY is not set.", None
    model = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-6")
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key, timeout=PROVIDER_TIMEOUT_SECONDS)
        resp = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            system=system_prompt,
            messages=[{"role": "user", "content": user_content}],
        )
        raw = "".join(b.text for b in resp.content if hasattr(b, "text"))
        return raw, None, model
    except Exception as e:
        return None, str(e), model


def _call_chatgpt(system_prompt, user_content, max_tokens):
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return None, "OPENAI_API_KEY is not set.", None
    model = os.environ.get("OPENAI_MODEL", "gpt-4o")
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key, timeout=PROVIDER_TIMEOUT_SECONDS)
        resp = client.chat.completions.create(
            model=model,
            max_tokens=max_tokens,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content},
            ],
        )
        raw = resp.choices[0].message.content
        return raw, None, model
    except Exception as e:
        return None, str(e), model


def _call_provider(provider, system_prompt, user_content, max_tokens):
    if provider == "chatgpt":
        return _call_chatgpt(system_prompt, user_content, max_tokens)
    return _call_claude(system_prompt, user_content, max_tokens)


def _batches(items, size):
    for i in range(0, len(items), size):
        yield items[i:i + size]


def build_narrative_report(provider, chart, dasha_info, monthly_scores, house_events, lang="en"):
    quarters = build_quarterly_summary(monthly_scores)
    if not quarters:
        return {"error": "No forecast data available for the requested window."}

    model_used = None
    sections = {key: [] for key in SECTION_ORDER}

    for batch in _batches(quarters, QUARTERS_PER_BATCH):
        context = build_batch_context(chart, dasha_info, batch, lang)
        raw, err, model_used = _call_provider(
            provider, SECTIONS_SYSTEM_PROMPT.get(lang, SECTIONS_SYSTEM_PROMPT["en"]),
            f"DATA:\n{context}", SECTION_MAX_TOKENS,
        )
        if err:
            return {"model": model_used, "error": err}
        parsed, parse_err = _parse_json_response(raw)
        if parse_err:
            return {"model": model_used, "error": parse_err, "raw": raw}
        batch_sections = parsed.get("sections", {})
        for key in SECTION_ORDER:
            sections[key].extend(batch_sections.get(key, []))

    overview_context = build_overview_context(chart, dasha_info, quarters, house_events, lang)
    raw, err, model_used = _call_provider(
        provider, OVERVIEW_SYSTEM_PROMPT.get(lang, OVERVIEW_SYSTEM_PROMPT["en"]),
        f"DATA:\n{overview_context}", OVERVIEW_MAX_TOKENS,
    )
    if err:
        # Sections generated fine; overview failed. Still return the sections
        # rather than discarding a mostly-successful report.
        overview = {"intro": "", "practical_notes": "", "conclusion": ""}
    else:
        parsed, parse_err = _parse_json_response(raw)
        overview = parsed if not parse_err else {"intro": "", "practical_notes": "", "conclusion": ""}

    report = {
        "intro": overview.get("intro", ""),
        "sections": sections,
        "practical_notes": overview.get("practical_notes", ""),
        "conclusion": overview.get("conclusion", ""),
    }
    return {"model": model_used, "report": report}
