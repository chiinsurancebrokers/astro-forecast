# Vimshottari Transit Monitor

A sidereal (Lahiri) Vedic astrology engine: natal chart, Vimshottari
Mahadasha/Antardasha, and a raw transit-based monthly activation-score
forecast, served as a small Flask web app.

**This produces raw, uncalibrated pressure scores, not validated
predictions.** The scores are meant to be logged against real outcomes
over time so the model can eventually be calibrated.

## What it computes

- **Natal chart** — planet positions (sidereal/Lahiri), Whole Sign houses,
  nakshatra + pada, via the Swiss Ephemeris.
- **Vimshottari dasha** — full Mahadasha/Antardasha timeline from birth,
  current period lookup.
- **Monthly forecast** — transit-house activation scores (0–100) per life
  area (career, money, love, health-adjacent risk areas, etc.), for any
  date range, weighted by which planet is running as dasha lord.
- **House-change calendar** — dates Jupiter/Saturn/Rahu/Ketu/Mars change
  sign, the slow-moving transits that matter at monthly resolution.

## Local setup

```bash
python3 -m venv .venv
source .venv/bin/activate         # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Open http://localhost:5000.

## API

- `GET /api/natal?year=1975&month=2&day=8&hour=11&minute=20&utc_offset=2&latitude=37.98&longitude=23.73`
- `GET /api/dasha?...` (same birth params)
- `GET /api/forecast?...&months=24&start=2026-08-01`

All birth params are optional and default to the sample chart baked into
`app.py` (`DEFAULTS`). Override any subset via query string.

## Deploying to Railway

1. Push this repo to GitHub (see below).
2. In Railway: **New Project → Deploy from GitHub repo**, select this repo.
3. Railway auto-detects Python via `railway.json` / Nixpacks and reads
   `requirements.txt`. No manual build config needed.
4. Once deployed, Railway assigns a public URL and injects `$PORT`
   automatically — `Procfile` and `app.py` already read it.
5. No environment variables are required for the default (Athens-anchored)
   config; none are read from the environment currently.

## Deploying to GitHub

```bash
git init
git add .
git commit -m "Initial commit: Vedic astro forecast engine"
git branch -M main
git remote add origin https://github.com/<your-username>/<repo-name>.git
git push -u origin main
```

## Project layout

```
app.py                 Flask routes / API
astro/
  ephemeris.py          Sidereal planet + house calculations
  dasha.py               Vimshottari Mahadasha/Antardasha builder
  forecast.py             Transit activation-score engine
templates/index.html    Single-page dashboard
requirements.txt
Procfile                 gunicorn start command
railway.json              Railway build/deploy config
runtime.txt                Python version pin
```

## Notes on accuracy

- Ascendant/house calculations were checked against a known reference
  chart (Athens, 8 Feb 1975, 11:20 local) and matched to within 0.01° on
  the Ascendant degree.
- Birth time uncertainty materially changes house placement near sign
  boundaries — see the app's natal output for the exact Ascendant degree
  before trusting any house-based reading.
- The Rahu/Ketu nodes here use the **Mean Node**; swap to `swe.TRUE_NODE`
  in `ephemeris.py` if you want the true (oscillating) node instead.
