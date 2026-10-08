import os
import math
import tempfile
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file

from astro.ephemeris import init_ephemeris, build_natal_chart
from astro.dasha import build_mahadashas, current_period
from astro.forecast import monthly_forecast, house_change_calendar
from astro.i18n import get_translations
from astro.report import build_pdf_report, build_narrative_pdf
from astro.synthesis import synthesize
from astro.narrative import build_narrative_report, SECTION_ORDER
from astro.agents import AstrologyOrchestrator
from astro.book_library import BookKnowledgeLibrary
from astro.historical_specialists import run_historical_specialists, plan_catalogue
from astro.natal_books import build_book_natal_report, SUN_READINGS, citation
from astro.personal_journey import build_personal_journey
from astro.zodiac_profiles import build_zodiac_profile
from astro.specialist_agents import (
    AskAgent, CareerAgent, CompatibilityAgent, GeoAstrologyAgent,
    PredictiveTimingEnsemble,
)

app = Flask(__name__)
init_ephemeris()


@app.errorhandler(Exception)
def handle_any_error(e):
    """
    Any unhandled exception on an /api/ route returns JSON instead of
    Flask's default HTML error page -- otherwise the frontend's
    `fetch(...).then(r => r.json())` throws a confusing
    "Unexpected token '<'" instead of the real error. Non-API routes
    (the index page) keep Flask's normal HTML handling.
    """
    app.logger.exception("Unhandled error on %s", request.path)
    if request.path.startswith("/api/"):
        return jsonify({"error": str(e), "type": type(e).__name__}), 500
    raise e

DEFAULTS = {
    "year": 1975, "month": 2, "day": 8,
    "hour": 11, "minute": 20,
    "utc_offset": 2.0,
    "latitude": 37.9838, "longitude": 23.7275,  # Athens
}

SUPPORTED_LANGS = ("en", "el")


def _parse_birth(args):
    d = {**DEFAULTS}
    for key in ("year", "month", "day", "hour", "minute"):
        if key in args:
            d[key] = int(args[key])
    for key in ("utc_offset", "latitude", "longitude"):
        if key in args:
            d[key] = float(args[key])
    return d


def _parse_lang(args):
    lang = args.get("lang", "en")
    return lang if lang in SUPPORTED_LANGS else "en"


def _compute_all(b, months, start):
    """Shared pipeline: natal chart, dasha timeline, forecast, house-change events."""
    chart = build_natal_chart(
        b["year"], b["month"], b["day"], b["hour"], b["minute"],
        b["utc_offset"], b["latitude"], b["longitude"],
    )
    birth_dt = datetime(b["year"], b["month"], b["day"], b["hour"], b["minute"])
    periods = build_mahadashas(birth_dt, chart["planets"]["Moon"]["longitude"])
    now = datetime.now()
    md, ad = current_period(periods, now)
    scores = monthly_forecast(chart, b["latitude"], b["longitude"], start, months, periods)
    events = house_change_calendar(start, months, b["latitude"], b["longitude"])
    return {
        "chart": chart,
        "periods": periods,
        "current_mahadasha": md["lord"] if md else None,
        "current_antardasha": ad["lord"] if ad else None,
        "monthly_scores": scores,
        "house_change_calendar": events,
    }


@app.route("/platform")
def platform_preview():
    """Premium platform preview; the existing production homepage is unchanged."""
    return render_template("platform.html")


@app.route("/")
def index():
    lang = _parse_lang(request.args)
    return render_template("index.html", defaults=DEFAULTS, lang=lang,
                            t=get_translations(lang))


@app.route("/api/i18n")
def api_i18n():
    lang = _parse_lang(request.args)
    return jsonify(get_translations(lang))


@app.route("/api/natal")
def api_natal():
    b = _parse_birth(request.args)
    chart = build_natal_chart(
        b["year"], b["month"], b["day"], b["hour"], b["minute"],
        b["utc_offset"], b["latitude"], b["longitude"],
    )
    if request.args.get("book_report") == "1":
        chart["book_report"] = build_book_natal_report(chart, b["latitude"], b["longitude"])
    return jsonify(chart)


@app.route("/api/dasha")
def api_dasha():
    b = _parse_birth(request.args)
    chart = build_natal_chart(
        b["year"], b["month"], b["day"], b["hour"], b["minute"],
        b["utc_offset"], b["latitude"], b["longitude"],
    )
    birth_dt = datetime(b["year"], b["month"], b["day"], b["hour"], b["minute"])
    periods = build_mahadashas(birth_dt, chart["planets"]["Moon"]["longitude"])
    now = datetime.now()
    md, ad = current_period(periods, now)

    def fmt(p):
        return {
            "lord": p["lord"],
            "start": p["start"].strftime("%Y-%m-%d"),
            "end": p["end"].strftime("%Y-%m-%d"),
            "antardashas": [
                {"lord": a["lord"], "start": a["start"].strftime("%Y-%m-%d"),
                 "end": a["end"].strftime("%Y-%m-%d")}
                for a in p["antardashas"]
            ],
        }

    return jsonify({
        "periods": [fmt(p) for p in periods],
        "current_mahadasha": md["lord"] if md else None,
        "current_antardasha": ad["lord"] if ad else None,
    })


@app.route("/api/forecast")
def api_forecast():
    b = _parse_birth(request.args)
    months = int(request.args.get("months", 60))
    start_str = request.args.get("start")
    start = datetime.strptime(start_str, "%Y-%m-%d") if start_str else datetime.now()

    result = _compute_all(b, months, start)

    return jsonify({
        "ascendant": result["chart"]["ascendant"],
        "monthly_scores": result["monthly_scores"],
        "house_change_calendar": result["house_change_calendar"],
        "current_mahadasha": result["current_mahadasha"],
        "current_antardasha": result["current_antardasha"],
        "disclaimer": (
            "Raw transit activation scores, not run through outcome "
            "calibration. Treat as pressure clustering, not prediction."
        ),
    })


@app.route("/api/report/pdf")
def api_report_pdf():
    b = _parse_birth(request.args)
    lang = _parse_lang(request.args)
    months = int(request.args.get("months", 60))
    start_str = request.args.get("start")
    start = datetime.strptime(start_str, "%Y-%m-%d") if start_str else datetime.now()

    result = _compute_all(b, months, start)
    months_list = list(result["monthly_scores"].keys())
    start_month = months_list[0] if months_list else ""
    end_month = months_list[-1] if months_list else ""

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        out_path = tmp.name

    build_pdf_report(
        out_path, lang, b, result["chart"],
        {"current_mahadasha": result["current_mahadasha"],
         "current_antardasha": result["current_antardasha"]},
        result["monthly_scores"], result["house_change_calendar"],
        start_month, end_month,
    )

    filename = f"forecast_{b['year']}-{b['month']:02d}-{b['day']:02d}_{lang}.pdf"
    return send_file(out_path, mimetype="application/pdf", as_attachment=True,
                      download_name=filename)


@app.route("/api/analysis")
def api_analysis():
    """
    Second-opinion synthesis: takes the raw forecast data and a free-text
    question (career outlook, annual forecast, life reading, etc.) and asks
    both Claude and ChatGPT to answer it, independently, grounded in the
    data. Requires ANTHROPIC_API_KEY / OPENAI_API_KEY as env vars.
    """
    b = _parse_birth(request.args)
    lang = _parse_lang(request.args)
    months = int(request.args.get("months", 24))
    start_str = request.args.get("start")
    start = datetime.strptime(start_str, "%Y-%m-%d") if start_str else datetime.now()
    question = request.args.get("question", "").strip()
    if not question:
        defaults = {
            "en": "Give me an overall annual forecast covering career, money, and relationships.",
            "el": "Δώσε μου μια συνολική ετήσια πρόβλεψη για καριέρα, χρήματα και σχέσεις.",
        }
        question = defaults.get(lang, defaults["en"])

    result = _compute_all(b, months, start)
    dasha_info = {
        "current_mahadasha": result["current_mahadasha"],
        "current_antardasha": result["current_antardasha"],
    }
    analysis = synthesize(
        question, result["chart"], dasha_info,
        result["monthly_scores"], result["house_change_calendar"], lang,
    )
    return jsonify(analysis)


def _resolve_provider(args):
    provider = args.get("provider", "claude")
    return provider if provider in ("claude", "chatgpt") else "claude"


@app.route("/api/narrative")
def api_narrative():
    """
    Full Ganesha-style narrative report: quarterly sections (Business,
    Career, Finance, Relationships, Travel/General) written in prose by
    the chosen provider, grounded in deterministic quarter statistics.
    """
    b = _parse_birth(request.args)
    lang = _parse_lang(request.args)
    provider = _resolve_provider(request.args)
    months = int(request.args.get("months", 24))
    start_str = request.args.get("start")
    start = datetime.strptime(start_str, "%Y-%m-%d") if start_str else datetime.now()

    result = _compute_all(b, months, start)
    dasha_info = {
        "current_mahadasha": result["current_mahadasha"],
        "current_antardasha": result["current_antardasha"],
    }
    narrative = build_narrative_report(
        provider, result["chart"], dasha_info,
        result["monthly_scores"], result["house_change_calendar"], lang,
    )
    return jsonify({"provider": provider, **narrative})


@app.route("/api/narrative/pdf")
def api_narrative_pdf():
    b = _parse_birth(request.args)
    lang = _parse_lang(request.args)
    provider = _resolve_provider(request.args)
    months = int(request.args.get("months", 24))
    start_str = request.args.get("start")
    start = datetime.strptime(start_str, "%Y-%m-%d") if start_str else datetime.now()

    result = _compute_all(b, months, start)
    dasha_info = {
        "current_mahadasha": result["current_mahadasha"],
        "current_antardasha": result["current_antardasha"],
    }
    narrative = build_narrative_report(
        provider, result["chart"], dasha_info,
        result["monthly_scores"], result["house_change_calendar"], lang,
    )
    if "report" not in narrative:
        return jsonify({
            "error": narrative.get("error", "Narrative generation failed."),
            "raw": narrative.get("raw"),
        }), 502

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        out_path = tmp.name

    provider_label = f"{provider} ({narrative.get('model', '')})"
    build_narrative_pdf(out_path, lang, b, result["chart"], narrative["report"],
                         SECTION_ORDER, provider_label)

    filename = f"narrative_{b['year']}-{b['month']:02d}-{b['day']:02d}_{provider}_{lang}.pdf"
    return send_file(out_path, mimetype="application/pdf", as_attachment=True,
                      download_name=filename)


@app.route("/api/knowledge/sources")
def api_knowledge_sources():
    library = BookKnowledgeLibrary()
    return jsonify({
        "sources": library.list_sources(),
        "topics": library.topics(),
    })


@app.route("/api/knowledge/search")
def api_knowledge_search():
    library = BookKnowledgeLibrary()
    query = request.args.get("q", "").strip()
    topics = [x.strip() for x in request.args.get("topics", "").split(",") if x.strip()]
    systems = [x.strip() for x in request.args.get("systems", "").split(",") if x.strip()]
    source_ids = [x.strip() for x in request.args.get("sources", "").split(",") if x.strip()]
    limit = max(1, min(int(request.args.get("limit", 8)), 50))

    hits = library.search(
        query=query,
        topics=topics,
        systems=systems,
        source_ids=source_ids,
        limit=limit,
    )
    return jsonify({
        "query": query,
        "count": len(hits),
        "hits": [h.to_dict() for h in hits],
        "context": library.context_block(hits),
    })


@app.route("/api/agents/analyze")
def api_agents_analyze():
    """Run the v2 specialist-agent pipeline and return inspectable evidence."""
    b = _parse_birth(request.args)
    months = max(1, min(int(request.args.get("months", 24)), 120))
    start_str = request.args.get("start")
    start = datetime.strptime(start_str, "%Y-%m-%d") if start_str else datetime.now()
    question = request.args.get("question", "").strip()

    chart = build_natal_chart(
        b["year"], b["month"], b["day"], b["hour"], b["minute"],
        b["utc_offset"], b["latitude"], b["longitude"],
    )
    birth_dt = datetime(b["year"], b["month"], b["day"], b["hour"], b["minute"])

    orchestrator = AstrologyOrchestrator()
    bundle = orchestrator.run(
        chart=chart,
        birth_dt=birth_dt,
        latitude=b["latitude"],
        longitude=b["longitude"],
        start=start,
        months=months,
        question=question,
        utc_offset=b["utc_offset"],
    )
    return jsonify(bundle)



def _build_prefixed_chart(prefix):
    values = {}
    for key in ("year", "month", "day", "hour", "minute"):
        raw = request.args.get(f"{prefix}_{key}", DEFAULTS[key])
        values[key] = int(raw)
    for key in ("utc_offset", "latitude", "longitude"):
        raw = request.args.get(f"{prefix}_{key}", DEFAULTS[key])
        values[key] = float(raw)
    chart = build_natal_chart(
        values["year"], values["month"], values["day"], values["hour"],
        values["minute"], values["utc_offset"], values["latitude"], values["longitude"],
    )
    return values, chart


@app.route("/api/agents/compatibility")
def api_agent_compatibility():
    if not all(f"b_{key}" in request.args for key in ("year", "month", "day")):
        return jsonify({"error": "Provide b_year, b_month, and b_day for the second chart."}), 400
    a = _parse_birth(request.args)
    chart_a = build_natal_chart(
        a["year"], a["month"], a["day"], a["hour"], a["minute"],
        a["utc_offset"], a["latitude"], a["longitude"],
    )
    _, chart_b = _build_prefixed_chart("b")
    return jsonify(CompatibilityAgent().run(chart_a, chart_b).to_dict())


@app.route("/api/agents/career")
def api_agent_career():
    b = _parse_birth(request.args)
    chart = build_natal_chart(
        b["year"], b["month"], b["day"], b["hour"], b["minute"],
        b["utc_offset"], b["latitude"], b["longitude"],
    )
    return jsonify(CareerAgent().run(chart).to_dict())


@app.route("/api/agents/geo")
def api_agent_geo():
    b = _parse_birth(request.args)
    try:
        latitude = float(request.args["target_latitude"])
        longitude = float(request.args["target_longitude"])
    except (KeyError, ValueError):
        return jsonify({"error": "Provide numeric target_latitude and target_longitude."}), 400
    if not -90 <= latitude <= 90 or not -180 <= longitude <= 180:
        return jsonify({"error": "Target coordinates are outside valid latitude/longitude ranges."}), 400
    natal = build_natal_chart(
        b["year"], b["month"], b["day"], b["hour"], b["minute"],
        b["utc_offset"], b["latitude"], b["longitude"],
    )
    birth = {**b, "chart": natal}
    report = GeoAstrologyAgent().run(birth, latitude, longitude, build_natal_chart)
    return jsonify(report.to_dict())


@app.route("/api/agents/ask")
def api_agent_ask():
    question = request.args.get("question", "").strip()
    if not question:
        return jsonify({"error": "A non-empty question is required."}), 400
    routing = AskAgent().run(
        question,
        ["Natal / Genethliacal Agent", "Vimshottari Timing Agent",
         "Transit Intelligence Agent", "Career Agent", "Compatibility Agent",
         "GeoAstrology Agent"],
    ).to_dict()
    b = _parse_birth(request.args)
    months = max(1, min(int(request.args.get("months", 24)), 120))
    start_str = request.args.get("start")
    start = datetime.strptime(start_str, "%Y-%m-%d") if start_str else datetime.now()
    data = _compute_all(b, months, start)
    synthesis = synthesize(
        question, data["chart"],
        {"current_mahadasha": data["current_mahadasha"],
         "current_antardasha": data["current_antardasha"]},
        data["monthly_scores"], data["house_change_calendar"], _parse_lang(request.args),
    )
    return jsonify({"routing": routing, "answer": synthesis})


@app.route("/api/agents/timing")
def api_agent_timing():
    b = _parse_birth(request.args)
    months = max(1, min(int(request.args.get("months", 24)), 120))
    start_str = request.args.get("start")
    start = datetime.strptime(start_str, "%Y-%m-%d") if start_str else datetime.now()
    data = _compute_all(b, months, start)
    dasha = [{
        "type": "vimshottari_current",
        "mahadasha": data["current_mahadasha"],
        "antardasha": data["current_antardasha"],
    }]
    report = PredictiveTimingEnsemble().run(
        data["monthly_scores"], dasha, data["house_change_calendar"],
    )
    return jsonify(report.to_dict())





@app.route('/api/agents/life-periods')
def api_life_periods():
    b = _parse_birth(request.args)
    chart = build_natal_chart(b['year'],b['month'],b['day'],b['hour'],b['minute'],
                             b['utc_offset'],b['latitude'],b['longitude'])
    report = build_book_natal_report(chart,b['latitude'],b['longitude'])
    return jsonify({'life_report':report['life_report']})


@app.route('/api/platform/plans')
def api_platform_plans():
    return jsonify(plan_catalogue())


@app.route('/api/agents/historical')
def api_historical_specialists():
    b = _parse_birth(request.args)
    chart = build_natal_chart(b['year'], b['month'], b['day'], b['hour'], b['minute'],
                             b['utc_offset'], b['latitude'], b['longitude'])
    reports = run_historical_specialists(chart)
    selected = request.args.get('specialist')
    if selected:
        if selected not in {'merton','daath','raleigh'}:
            return jsonify({'error':'Choose merton, daath or raleigh.'}), 400
        reports = [r for r in reports if r['id'] == selected]
    return jsonify({'historical_specialists':reports})



@app.route('/api/zodiac/profiles')
def api_zodiac_profiles():
    sign = request.args.get('sign')
    if sign:
        if sign not in SUN_READINGS:
            return jsonify({'error':'Choose one of the twelve zodiac signs.'}), 400
        return jsonify({'zodiac_profile':build_zodiac_profile(sign,SUN_READINGS,citation)})
    return jsonify({'profiles':[{'sign':sign,'title':sign+' · understanding yourself'} for sign in SUN_READINGS]})


@app.route('/api/agents/personal-journey', methods=['POST'])
def api_personal_journey():
    if request.content_length and request.content_length>24000:
        return jsonify({'error':'The journey is too long.'}),413
    body=request.get_json(silent=True)
    if not isinstance(body,dict) or not isinstance(body.get('birth'),dict):
        return jsonify({'error':'Provide birth details and dated turning points.'}),400
    try:
        if not all(k in body['birth'] for k in ['year','month','day','hour','minute','utc_offset','latitude','longitude']):
            raise ValueError('Birth details required.')
        b=_parse_birth(body['birth'])
        birth_date=datetime(b['year'],b['month'],b['day'],b['hour'],b['minute'])
        if b['year']<1800 or birth_date>datetime.utcnow():raise ValueError('Birth date is outside the supported range.')
        if not (math.isfinite(b['utc_offset']) and -12<=b['utc_offset']<=14 and math.isfinite(b['latitude']) and -89<=b['latitude']<=89 and math.isfinite(b['longitude']) and -180<=b['longitude']<=180):
            raise ValueError('Birth coordinates invalid.')
        chart=build_natal_chart(b['year'],b['month'],b['day'],b['hour'],b['minute'],b['utc_offset'],b['latitude'],b['longitude'])
        result=build_personal_journey(chart,b['latitude'],b['longitude'],body)
    except (ValueError,TypeError,OverflowError):
        return jsonify({'error':'Check your birth details, dates and text limits. Dates may be YYYY, YYYY-MM or YYYY-MM-DD.'}),400
    response=jsonify({'personal_journey':result})
    response.headers['Cache-Control']='no-store'
    return response

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
