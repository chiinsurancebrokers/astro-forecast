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

All birth params are optional and default to the sample chart baked into
`app.py` (`DEFAULTS`). Override any subset via query string. Add `&lang=el`
to any route to get Greek where applicable.

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
