import os
import tempfile
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file

from astro.ephemeris import init_ephemeris, build_natal_chart
from astro.dasha import build_mahadashas, current_period
from astro.forecast import monthly_forecast, house_change_calendar
from astro.i18n import get_translations
from astro.report import build_pdf_report

app = Flask(__name__)
init_ephemeris()

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


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
