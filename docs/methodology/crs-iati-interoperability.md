# CRS × IATI interoperability

The `/crs-iati` page (and sheet 5 of the workbook) measures, per IATI reporting organisation, **how often each of the three CRS-relevant `other-identifier` types — A1, A2, A9 — is populated**.

This is the floor for whether GPEDC indicator 3.2.1's financial-coverage adjustment can shift from comparing aggregate flow-type totals to reconciling IATI activities and CRS records project by project.

## Why these three identifier types

IATI's `other-identifier` element on an activity can carry three values that a CRS record can be matched against:

- **A1** — the publishing organisation's internal activity identifier. Some donors place CRS-compatible identifiers here.
- **A2** — explicitly the CRS Activity Identifier. A direct match to the CRS ID field. The OECD-DAC paper recommends donors populate this.
- **A9** — any other activity identifier; often used in the `XM-DAC-{donor}-{project}` format that embeds a CRS-compatible project number.

Where a publisher populates any of these, an IATI activity can be tied back to a specific CRS record at high confidence. Where they don't, the matching has to fall back to looser methods (donor-specific identifier parsing, or text-similarity matching of titles and descriptions) — which is what the OECD-DAC's pipeline does in its later layers.

## Per-publisher rates and the three-tier classification

For each IATI reporting organisation, the page shows the share of activities populating A1, A2, and A9 separately, and the combined "any of the three" rate. Publishers are then placed into one of three tiers based on that combined rate:

- **Project-level reconciliation possible** — combined A1/A2/A9 rate is at least 80 %. The publisher's IATI activities can be tied to CRS records project by project at high confidence.
- **Mixed: partial reconciliation + parsing fallback** — combined rate between 30 % and 80 %. Some structured matching plus donor-specific identifier-parsing fallbacks.
- **Aggregate ratio only (or parsing fallback if known)** — below 30 %. Project-level matching from `other-identifier` alone isn't feasible; the OECD-DAC pipeline either falls back to parsing donor-specific identifier patterns embedded in the IATI activity identifier, or to text-similarity matching against CRS records.

The 30 % and 80 % cuts are calibrated to the OECD-DAC paper's published per-donor match rates. At above 80 % structured-identifier coverage, OECD reports very high project-level match confidence; below 30 %, the structured-identifier contribution becomes minor relative to the parsing and text-matching fallbacks.

## What this project tests vs what the OECD-DAC paper does

The OECD-DAC paper *DCD/DAC/STAT(2026)22 — Linking IATI and CRS* defines four matching layers, applied in cascade:

1. **CRS Identification number match** via A1/A2 — highest confidence.
2. **Project Number match** via A9 — high confidence.
3. **Donor-specific identifier parsing** — patterns embedded in the IATI activity identifier itself (e.g. Sweden's structured identifier convention).
4. **Text-similarity matching** of titles and descriptions — the fallback.

This project tests the **first two layers** directly, because they're the ones where publishers can act today simply by populating the right `other-identifier` types. The OECD-DAC paper finds that these two layers account for roughly half of all matches in their analysis; the rest require the parsing or text-matching fallbacks for publishers that don't populate structured cross-reference identifiers.

The third and fourth layers are out of scope here — they would require donor-by-donor parsing rules and a CRS records corpus to compare IATI activities against. The point of the per-publisher A1/A2/A9 rates is not to reproduce the OECD-DAC pipeline; it's to show **where each publisher sits today on the path to project-level interoperability**, and which publishers could move that needle just by adding A2 to their IATI publication.

## Cross-checks

The OECD paper publishes per-donor identifier-coverage figures (its Table 7). Where our scan and theirs cover the same publisher, the numbers should align — and they do, within a few percentage points. The Netherlands MFA, BMZ, Australia, EC INTPA, and the Norwegian Norad agency all match closely. FAO is the canonical false positive: it populates A1 on 100 % of activities but with non-CRS IDs, so the OECD pipeline catches a near-zero match rate where a presence-only metric like this one places FAO in the highest tier. That caveat is worth keeping in mind anywhere the tier classification is used to prioritise donors.

## Caveats

- **Presence is not correctness.** Whether a published A1/A2/A9 value resolves to a real CRS record requires running the OECD pipeline against actual CRS data, which this project doesn't do. The metric here is the floor — does the publisher even populate the field?
- **Parsing fallbacks are not credited.** Sweden achieves a healthy match rate in the OECD paper despite publishing zero A1/A2/A9, because its IATI activity identifier has a structured pattern the OECD pipeline can parse. Our metric correctly classifies Sweden as low-coverage on `other-identifier`, but a fuller methodology would credit publishers like Sweden for a parseable identifier convention.
- **Historical archive vs current activities.** Our scan reads each publisher's full archive. Publishers whose recent practice differs from their historical pattern will read slightly differently between this project and a year-by-year matching analysis.
