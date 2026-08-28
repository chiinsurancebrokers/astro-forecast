# Vimshottari Transit Monitor

A sidereal (Lahiri) Vedic astrology engine: natal chart, Vimshottari
Mahadasha/Antardasha, and a raw transit-based monthly activation-score
forecast — served as a bilingual (English/Greek) Flask web app with
PDF export.

**This produces raw, uncalibrated pressure scores, not validated
predictions.** The scores are meant to be logged against real outcomes
over time so the model can eventually be calibrated.

## What it computes

- **Natal chart** — planet positions (sidereal/Lahiri), Whole Sign houses,
  nakshatra + pada, via the Swiss Ephemeris.
- **Vimshottari dasha** — full Mahadasha/Antardasha timeline from birth,
  current period lookup.
- **Monthly forecast** — transit-house activation scores (0–100) per life
  area (career, money, love, financial risk, social friction, etc.), for
  any date range, weighted by which planet is running as dasha lord.
- **House-change calendar** — dates Jupiter/Saturn/Rahu/Ketu/Mars change
  sign, the slow-moving transits that matter at monthly resolution.
- **PDF report** — the same natal chart, dasha, monthly forecast, and
  house-change calendar, laid out as a downloadable PDF in either language.

## Languages

The UI and PDF report are available in **English** (`en`) and **Greek**
(`el`). Switch language with the `EN` / `EL` toggle in the header, or pass
`?lang=el` to any route. Internally, area/planet/sign codes stay in
English (e.g. `financial_risk`, `Jupiter`) — only display labels are
translated, via `astro/i18n.py`, so calibration logs stay comparable
across languages.

Greek PDF rendering uses bundled DejaVu Sans fonts (`fonts/`) registered
explicitly in `astro/report.py`, so Greek glyphs render correctly
regardless of what fonts the deploy host happens to have installed.

## Local setup

```bash
python3 -m venv .venv
source .venv/bin/activate         # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Open http://localhost:5000 (or http://localhost:5000/?lang=el for Greek).

## API

- `GET /api/natal?year=1975&month=2&day=8&hour=11&minute=20&utc_offset=2&latitude=37.98&longitude=23.73`
- `GET /api/dasha?...` (same birth params)
- `GET /api/forecast?...&months=24&start=2026-08-01`
- `GET /api/report/pdf?...&months=24&lang=el` — downloads a PDF
- `GET /api/i18n?lang=el` — raw translation dictionary (used by the frontend)
- `GET /api/analysis?...&months=24&lang=el&question=...` — asks Claude and
  ChatGPT independently to answer the question against the forecast data
  (see "Second-opinion analysis" below)
- `GET /api/narrative?...&months=24&lang=el&provider=claude` — a full
  Ganesha-style structured narrative report (see "Narrative report" below)
- `GET /api/narrative/pdf?...&provider=chatgpt` — same, as a downloadable PDF

All birth params are optional and default to the sample chart baked into
`app.py` (`DEFAULTS`). Override any subset via query string. Add `&lang=el`
to any route to get Greek where applicable.

## Second-opinion analysis (Claude + ChatGPT)

`/api/analysis` builds a compact, information-dense summary of the natal
chart, current dasha, per-area score peaks/troughs across the forecast
window, and the slow-planet house-change calendar — then sends that
summary plus the person's free-text question to **both** Claude and
ChatGPT, independently, and returns both answers side by side. Neither
model sees the other's answer; nothing is merged or arbitrated. The
frontend renders them as two columns so the person can compare.

Both system prompts explicitly tell the model the scores are raw and
uncalibrated, and ask it to ground its answer in specific months/dasha
periods/transits from the data rather than write a generic reading.

**Required environment variables** (set as Railway service variables —
Project → Variables, not committed to the repo):

| Variable | Required | Default | Notes |
|---|---|---|---|
| `ANTHROPIC_API_KEY` | yes, for Claude | — | from console.anthropic.com |
| `OPENAI_API_KEY` | yes, for ChatGPT | — | from platform.openai.com |
| `ANTHROPIC_MODEL` | no | `claude-sonnet-4-6` | override to pin a different Claude model |
| `OPENAI_MODEL` | no | `gpt-4o` | override to pin a different OpenAI model |

If a key is missing, that provider's panel shows an error (e.g.
`ANTHROPIC_API_KEY is not set.`) while the other still returns normally —
the endpoint never hard-fails because one provider isn't configured.
Model names move fast on both sides; the two `*_MODEL` variables exist so
you can update the model without a code change or redeploy from source.

## Narrative report (Ganesha-style)

`/api/narrative` produces a structured, section-by-section report in the
style of a traditional yearly astrology report: an overview paragraph,
then **Business / Career / Finance / Relationships / Travel & General
Notes** sections, each broken into the same quarters as the forecast
window, with one grounded prose paragraph per quarter — followed by a
"Points to Watch" section and a closing summary.

The quarter-level averages/min/max per area are computed deterministically
in Python (`astro/narrative.py`, `build_quarterly_summary`) — the LLM is
only asked to write prose from those numbers, never to do the arithmetic
itself, which keeps the figures trustworthy regardless of which model
wrote the report. Pick `provider=claude` or `provider=chatgpt`; each
returns strict JSON matching a fixed schema (`intro`, `sections`,
`practical_notes`, `conclusion`), which either renders in the web UI or
gets laid out as a PDF via `astro/report.py::build_narrative_pdf`. If a
model's response fails to parse as valid JSON, the endpoint returns the
raw text alongside a parse error rather than silently dropping it.

Section prose is generated in **batches of 4 quarters per call** rather
than one giant request — a full report (5 sections x every quarter,
written at professional-forecast length) is long enough to hit a
model's max_tokens ceiling mid-response and come back truncated and
unparsable, which happened in practice at a 24-month window under an
earlier, single-call version of this endpoint. Batching keeps each
individual call's output bounded regardless of how long a window is
requested; the intro/practical-notes/conclusion are written separately,
in one short call, from the aggregate quarter statistics rather than the
much longer per-quarter prose. A 24-month report is 3 calls total (2
section batches + 1 overview); longer windows add one more call per 4
extra quarters.

The prompt explicitly forbids inventing gemstone/ritual remedies or any
fact not implied by the supplied statistics — "Points to Watch" is framed
as practical, behavioral notice rather than mystical prescription.

## Deploying to Railway

1. Push this repo to GitHub (see below).
2. In Railway: **New Project → Deploy from GitHub repo**, select this repo.
3. Railway auto-detects Python via `railway.json` / Nixpacks and reads
   `requirements.txt`. No manual build config needed — `app.py`,
   `requirements.txt`, `Procfile`, and `railway.json` all live at the repo
   root, which is what Railway's build step expects.
4. Once deployed, Railway assigns a public URL and injects `$PORT`
   automatically — `Procfile` and `app.py` already read it.
5. No environment variables are required for the default (Athens-anchored)
   config; none are read from the environment currently.

## Deploying to GitHub

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/<your-username>/<repo-name>.git
git push -u origin main
```

## Project layout

```
app.py                    Flask routes / API
astro/
  ephemeris.py              Sidereal planet + house calculations
  dasha.py                    Vimshottari Mahadasha/Antardasha builder
  forecast.py                   Transit activation-score engine
  i18n.py                         English/Greek translation dictionaries
  report.py                        Bilingual PDF report builder (reportlab)
  synthesis.py                       Claude + ChatGPT second-opinion analysis
  narrative.py                         Quarterly aggregation + narrative report generation
fonts/                     Bundled DejaVu Sans TTFs (Greek glyph support)
templates/index.html      Bilingual single-page dashboard
requirements.txt
Procfile                   gunicorn start command
railway.json                 Railway build/deploy config
runtime.txt                    Python version pin
```

## Notes on accuracy

- Ascendant/house calculations were checked against a known reference
  chart (Athens, 8 Feb 1975, 11:20 local) and matched to within 0.01° on
  the Ascendant degree.
- Birth time uncertainty materially changes house placement near sign
  boundaries — see the app's natal output for the exact Ascendant degree
  before trusting any house-based reading.
- The Rahu/Ketu nodes here use the **Mean Node**; swap to `swe.TRUE_NODE`
  in `astro/ephemeris.py` if you want the true (oscillating) node instead.
- The monthly activation-score formula in `astro/forecast.py` is a
  documented heuristic, not a validated predictive model — treat it as a
  starting point to calibrate against logged real-world outcomes.
