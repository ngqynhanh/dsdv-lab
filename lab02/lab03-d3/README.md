# Lab 3 — Sections 8, 9 and 10

Double-click `index.html` to open the chart directly; no server or internet connection is required. Keep `script.js`, `style.css`, and `d3.v7.min.js` in the same folder.
When opened with `file://`, D3 loads a data URL containing the CSV embedded in the HTML. When served over HTTP, D3 loads `vn-provinces-data.csv` directly. The embedded CSV is a copy of the supplied CSV; update it too if the dataset changes.
Open Developer Tools → Console to see the actual headers, first two raw and converted records, and record counts.

Data source: https://tungth.github.io/data/vn-provinces-data.csv
D3 source: https://d3js.org/d3.v7.min.js

The CSV's fields are `ma`, `province`, `area`, `population`, `density`, `GRDP-VND`, and `GRDP-USD`. The plot uses `GRDP-VND`; its decimal commas are converted to decimal points before numeric parsing. Population is in thousands (consistent with population × 1000 / area ≈ density); GRDP units follow the handout. The source values are preserved, including apparent anomalies.

- x and y use linear scales from zero to the data maximum, rounded with `.nice()`. Zero provides a meaningful baseline. The reversed y range places larger values higher.
- Section 8 initially used 300 × 600. Section 10 now uses 450 × 900. Dimensions and margins are grouped in `script.js`. Radius padding prevents marks from being cut off at the extremes.
- The square-root radius scale starts at zero, making circle area directly proportional to province land area.
- Density bands are <100, 100–<500, 500–<1000, and ≥1000 people/km². These are explicit design categories, not official classifications. The legend uses the same thresholds and colors.
- Missing/non-finite/negative values and non-positive area are rejected and logged with row numbers. Every valid record is drawn. Larger circles are drawn first; fill opacity and outlines reduce, but do not eliminate, overlap.

Names and IDs were carried over from the existing Lab 2 report. The required declaration is reproduced on the page. AI assisted this implementation; review the code and ensure the declaration meets your course's policy before submission.

## Sections 9 and 10

See [SECTIONS-9-10.md](SECTIONS-9-10.md) for step-by-step hypotheses, checks, test data, Bug C reproduction and fix, adaptation details, measured results, and reflection.

Use the links at the bottom of the page to switch between the source CSV, four synthetic test records, and the deliberate Bug C reproduction. The default source-data view passes 11/11 automatic checks. The correct small-data view passes 14/14; the deliberate bug view passes 12/14 and fails both area-proportionality checks. Return to **Source CSV** before submission.

Additional adaptation B is implemented with native SVG hover tooltips showing all five requested fields.
