# Astrology Intelligence Engine v2 — Agents

The v2 architecture separates astronomical calculation, timing, traditional
interpretation, historical medical-astrology symbolism, calibration and synthesis.

## Agents

1. **Natal / Genethliacal Agent**
   - Ascendant and ruler
   - Planet placements by sign/house
   - Nakshatra/pada
   - Classical dignity flags
   - Major natal aspects with exactness/orb

2. **Vimshottari Timing Agent**
   - Current Mahadasha and Antardasha
   - Uses corrected birth-period Antardasha clipping

3. **Transit Intelligence Agent**
   - Monthly activation evidence
   - Slow-planet sign-change calendar
   - Does not present heuristic scores as validated predictions

4. **Traditional Knowledge Agent**
   - Source-aware rule selection
   - Keeps Western/traditional material separate from Vedic doctrine

5. **Historical Medical Astrology Agent**
   - Historical symbolic correspondences only
   - Hard guardrail: no diagnosis, prognosis, treatment or clinical-risk claims

6. **Calibration Agent**
   - Reserved for dated real-world outcomes
   - No personal calibration claim until sufficient outcomes exist

7. **Synthesis Agent**
   - Orchestrates specialist outputs
   - Calculated facts first, source-aware rules second, prose last

## API

`GET /api/agents/analyze`

Uses the same birth parameters as the existing endpoints and accepts:
- `months` (1–120)
- `start=YYYY-MM-DD`
- `question=...`

The response contains every specialist's evidence, rules, notes and global guardrails.

8. **Career Agent**
   - Summarizes the 2nd, 6th, 10th and 11th house evidence and Ascendant ruler.
   - Does not declare a guaranteed occupation or outcome.

9. **Compatibility Agent**
   - Compares selected cross-chart planetary aspects and placements.
   - Notes birth-time uncertainty and avoids relationship outcome predictions.

10. **GeoAstrology Agent**
    - Compares natal and relocated whole-sign houses at supplied coordinates.
    - Does not claim to calculate astrocartography lines.

11. **Ask Agent**
    - Routes a question to relevant evidence domains before synthesis.

12. **Multi-model Predictive Timing Agent**
    - Presents monthly transit, ingress, Vimshottari and calibration evidence.
    - Reports availability and validation state; no probabilities are invented.

## Knowledge policy

Historical source material is stored as compact paraphrased rules with provenance.
The application must not silently merge incompatible schools of astrology. Each
rule carries a system tag such as `VEDIC`, `WESTERN_TRADITIONAL`, or
`MEDICAL_ASTROLOGY`.

## Method comparison and observation journal

- `/methods` and `/api/agents/methods` expose Western tropical chart/transit
  geometry separately from Vedic Lahiri/Vimshottari timing.
- Use the same birth instant and declare coordinate origin, house system,
  ephemeris version, node convention and calculation timestamp.
- Agreement between agents using shared calculations is dependent testimony,
  not independent validation. Do not produce confidence percentages from votes.
- No outcome-count threshold establishes predictive validity or enables an
  empirical calibration claim.
- The journal is explicit-save browser storage with JSON export. It preserves
  original expectations in the UI and permits a one-time outcome review after
  the observation window. Browser storage and device clocks are editable; never
  describe this as a tamper-proof registry or a validation study.
