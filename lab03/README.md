# Lab 03 — D3.js: Scales, Axes, and Visual Encoding

Group: Pham Nhu Nguyen Trung (ITCSIU24091), Nguyen Quynh Anh (ITCSIU24005)

Run with a local web server (the CSV cannot be fetched from `file://`):

    python3 -m http.server   # then open http://localhost:8000/

Files: `index.html`, `script.js`, `style.css`, `d3.v7.min.js`, `vn-provinces-data.csv`.

## Scale choices

| Encoding | Field (CSV column) | Scale | Notes |
|---|---|---|---|
| x-position | population (thousand people) | `scaleLinear`, domain `[0, max]`, `.nice()` | Domain from data; zero is a meaningful baseline. Range padded by the max radius. |
| y-position | GRDP per person (`GRDP-VND`, million VND/person/year) | `scaleLinear`, domain `[0, max]`, `.nice()`, range reversed | SVG y grows downward, so larger GRDP appears higher. Decimal commas are converted to numbers. |
| circle size | area (km²) | `scaleSqrt`, domain `[0, max area]`, range `[0, 13]` px | Radius ∝ √area, so circle area ∝ province area. |
| circle color | density (people/km²) | `scaleThreshold` | See density rule below. |

Canvas: 450 × 900 px (Section 10 adaptation, from 300 × 600), set by `width`/`height` in `buildChart`.

## Density-category rule

Fixed descriptive thresholds (chart design choice, not official classifications). A boundary value belongs to the higher band.

| Band | Density (people/km²) | Color | Provinces |
|---|---|---|---|
| 1 | < 100 | #4477AA | 9 |
| 2 | 100 to < 500 | #228833 | 33 |
| 3 | 500 to < 1,000 | #EEAA33 | 13 |
| 4 | ≥ 1,000 | #AA3377 | 8 |

The legend is generated from the same threshold and color arrays as the scale.

## Verification note

- **Bug tested:** Bug C — misleading circles (province area mapped directly to radius).
- **Reproduce:** `index.html?test=1&bug=area` swaps `scaleSqrt` for `scaleLinear` on the small test dataset.
- **Fix:** `areaScale` uses `d3.scaleSqrt()` on the real chart.
- **Evidence:** the small test dataset has Test Low (area 100) and Test Medium (area 400). With the fix the rendered circle-area ratio is 4 (matches 400/100); with the bug it is 16, and the "Circle area is proportional to province area" check shows FAIL. Other checks on the page (63 circles for 63 valid records, y increases upward, axes meet at zero, legend colors match marks, density exactly 500 enters the higher band, canvas is 450 × 900) all report PASS.
- **Data checks:** 63 rows, no blank numeric fields; Hồ Chí Minh has the largest population, Quảng Bình the highest GRDP per person; Đồng Tháp (density exactly 500) is colored in band 3.

## Homework (Section 14)

Tooltip (name, population, GRDP, area, density) plus a density-category highlight selector. Interpretations of Hồ Chí Minh and Quảng Bình and three tooltip test cases (including the edge case Đồng Tháp at density 500) are shown at the bottom of the page.

Tests run in headless Chromium against the source CSV:

| Case | Expected | Observed |
|---|---|---|
| Tooltip, Hồ Chí Minh (largest population, decimal comma `43,60`) | 8,598.7 / 43.6 / 2,061.4 / 4,171, purple | PASS |
| Tooltip, Quảng Bình (highest GRDP, top edge) | 887.6 / 154.84 / 8,000 / 111, green | PASS |
| Tooltip, Đồng Tháp (edge: density exactly 500) | 1,693.3 / 41.1 / 3,383.8 / 500, orange (higher band) | PASS |
| Highlight density < 100 | 9 of 63 | 9 (54 dimmed) |
| Highlight 100 to < 500 | 33 of 63 | 33 |
| Highlight 500 to < 1,000 | 13 of 63 (includes Đồng Tháp) | 13 |
| Highlight ≥ 1,000 | 8 of 63 | 8 |
| "All provinces" | 63 of 63 | 63 |

The four band counts add up to 63, and highlighting only changes opacity and outline, so the encodings stay correct.

Limitation: overlapping circles can hide small provinces, and circle area is hard to compare precisely by eye.

## AI use

AI helped write the code, explain the highlighting logic and run tests. The group independently checked circle counts, highlight counts and the Đồng Tháp boundary case against the CSV in the browser.
