"""
Turns the raw transit/dasha data into a compact, grounded context, then
asks two different LLMs (Claude and ChatGPT) to answer the person's actual
question against it -- career outlook, annual forecast, life-area reading,
etc. Both are presented as independent "second opinions"; this module does
not try to merge or arbitrate between them.

Requires ANTHROPIC_API_KEY / OPENAI_API_KEY as environment variables
(set as Railway service variables in production). Missing keys degrade
gracefully -- that provider's slot reports an error, the other still runs.
"""
import os

DEFAULT_ANTHROPIC_MODEL = "claude-sonnet-4-6"
DEFAULT_OPENAI_MODEL = "gpt-4o"

SYSTEM_PROMPT = {
    "en": (
        "You are reading output from a sidereal (Lahiri) Vedic astrology "
        "transit-scoring tool for a client. The scores are RAW and "
        "UNCALIBRATED -- house-activation and dasha-weighted heuristics, "
        "never validated against real outcomes. Do not present them as "
        "settled predictions. Answer the client's specific question using "
        "the data provided: name the concrete months, dasha periods, or "
        "planetary transits that support each point, and be explicit "
        "about where the data is genuinely suggestive versus thin. Keep a "
        "grounded, practical tone -- this is a working analysis for "
        "someone using the tool to plan, not a mystical reading. Answer "
        "in English."
    ),
    "el": (
        "Διαβάζεις την έξοδο ενός εργαλείου βαθμολόγησης διαβατικών "
        "περιόδων Βεδικής αστρολογίας (sidereal, Lahiri) για έναν πελάτη. "
        "Οι τιμές είναι ΑΚΑΤΕΡΓΑΣΤΕΣ και ΜΗ ΒΑΘΜΟΝΟΜΗΜΕΝΕΣ -- ευρετικές, "
        "βασισμένες σε ενεργοποίηση οίκων και στάθμιση δάσα, χωρίς "
        "επαλήθευση σε πραγματικά αποτελέσματα. Μην τις παρουσιάζεις ως "
        "βέβαιες προβλέψεις. Απάντησε στη συγκεκριμένη ερώτηση του πελάτη "
        "χρησιμοποιώντας τα δεδομένα που δίνονται: ανέφερε συγκεκριμένους "
        "μήνες, περιόδους δάσα ή διαβατικές θέσεις πλανητών που "
        "υποστηρίζουν κάθε σημείο, και να είσαι σαφής για το πού τα "
        "δεδομένα είναι πράγματι ενδεικτικά και πού είναι αδύναμα. "
        "Διατήρησε προσγειωμένο, πρακτικό τόνο. Απάντησε στα Ελληνικά."
    ),
}


def _top_and_bottom(area_scores, n=3):
    ranked = sorted(area_scores.items(), key=lambda kv: kv[1], reverse=True)
    peaks = ranked[:n]
    troughs = sorted(ranked[-n:], key=lambda kv: kv[1])
    avg = round(sum(v for _, v in area_scores.items()) / len(area_scores), 1)
    return avg, peaks, troughs


def build_context(chart, dasha_info, monthly_scores, house_events, lang="en"):
    """Compact, information-dense text summary -- not the full monthly table."""
    asc = chart["ascendant"]
    lines = []
    lines.append(f"Ascendant: {asc['sign']} {asc['sign_deg']:.2f} degrees.")
    lines.append("Natal planets (sign, house, nakshatra):")
    for name, p in chart["planets"].items():
        retro = " retrograde" if p["retrograde"] else ""
        lines.append(f"  {name}: {p['sign']} {p['sign_deg']:.2f}°, house {p['house']}, "
                      f"{p['nakshatra']}{retro}")
    lines.append(f"Current Mahadasha: {dasha_info.get('current_mahadasha')}, "
                  f"current Antardasha: {dasha_info.get('current_antardasha')}.")

    months = list(monthly_scores.keys())
    if months:
        lines.append(f"Forecast window: {months[0]} to {months[-1]} "
                      f"({len(months)} months). All scores are 0-100, raw/uncalibrated.")
        area_keys = list(monthly_scores[months[0]].keys())
        lines.append("Per-area summary (average, top peak months, top trough months):")
        for area in area_keys:
            series = {m: monthly_scores[m][area] for m in months}
            avg, peaks, troughs = _top_and_bottom(series)
            peak_str = ", ".join(f"{m}={v}" for m, v in peaks)
            trough_str = ", ".join(f"{m}={v}" for m, v in troughs)
            lines.append(f"  {area}: avg={avg}, peaks=[{peak_str}], troughs=[{trough_str}]")

    if house_events:
        lines.append("Major slow-planet house changes in this window:")
        for ev in house_events:
            retro = " (retrograde)" if ev["retrograde"] else ""
            lines.append(f"  {ev['date']}: {ev['planet']} {ev['from_sign']} -> "
                          f"{ev['to_sign']}{retro}")

    return "\n".join(lines)


def call_claude(question, context, lang="en"):
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return {"error": "ANTHROPIC_API_KEY is not set."}
    model = os.environ.get("ANTHROPIC_MODEL", DEFAULT_ANTHROPIC_MODEL)
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        resp = client.messages.create(
            model=model,
            max_tokens=1400,
            system=SYSTEM_PROMPT.get(lang, SYSTEM_PROMPT["en"]),
            messages=[{
                "role": "user",
                "content": f"DATA:\n{context}\n\nQUESTION:\n{question}",
            }],
        )
        text = "".join(block.text for block in resp.content if hasattr(block, "text"))
        return {"model": model, "text": text}
    except Exception as e:
        return {"error": str(e)}


def call_chatgpt(question, context, lang="en"):
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return {"error": "OPENAI_API_KEY is not set."}
    model = os.environ.get("OPENAI_MODEL", DEFAULT_OPENAI_MODEL)
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        resp = client.chat.completions.create(
            model=model,
            max_tokens=1400,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT.get(lang, SYSTEM_PROMPT["en"])},
                {"role": "user", "content": f"DATA:\n{context}\n\nQUESTION:\n{question}"},
            ],
        )
        text = resp.choices[0].message.content
        return {"model": model, "text": text}
    except Exception as e:
        return {"error": str(e)}


def synthesize(question, chart, dasha_info, monthly_scores, house_events, lang="en"):
    context = build_context(chart, dasha_info, monthly_scores, house_events, lang)
    return {
        "question": question,
        "claude": call_claude(question, context, lang),
        "chatgpt": call_chatgpt(question, context, lang),
    }
