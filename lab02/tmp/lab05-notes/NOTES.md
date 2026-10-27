# Lab 05 - Interactive COVID-19 Scatterplot

**Course:** Data Science and Data Visualization - International University  
**Students:** Phạm Như Nguyên Trung - ITCSIU24091; Nguyễn Quỳnh Anh - ITCSIU24005  
**Date:** 27 October 2026

## 1. Data source, date and schema

We use the Johns Hopkins University CSSE confirmed global time-series CSV:

[time_series_covid19_confirmed_global.csv](https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv)

The selected date is **5 April 2020**. The lab writes this as `05/04/2020` (DD/MM/YYYY), while the CSV column is `4/5/20` (M/D/YY). It is not `5/4/20`, which would mean 4 May. The script checks that the selected date column exists before drawing.

| CSV field | Cleaned field | Use |
| --- | --- | --- |
| `Country/Region` | `country` | Tooltip and status |
| `Province/State` | `province` | Tooltip, when available |
| `Lat` | `lat` | Vertical position |
| `Long` | `long` | Horizontal position |
| `4/5/20` | `value` | Confirmed cases and circle size |

One valid source row produces one circle; the code does not aggregate rows by country.

### Cleaning rules and counts

`rowConverter()` first checks for blank or missing latitude, longitude and case values. This happens before conversion because `Number("")` returns `0`. It then uses `Number()` and rejects non-finite values, negative cases, latitude outside -90 to 90, and longitude outside -180 to 180. A missing province/state is allowed. Numeric coordinates equal to zero are allowed.

Missing case values are excluded. A real case count of zero is retained. Because the radius scale starts at zero, those records have SVG circles with radius 0 and cannot be seen or hovered.

The public CSV was downloaded on 27 October 2026 and checked using the current script's actual `rowConverter()` function:

| Check | Count |
| --- | ---: |
| Loaded source rows | 289 |
| Valid records | 287 |
| Excluded records | 2 |
| Valid records with zero cases | 27 |
| Valid records with positive cases | 260 |

Both exclusions have blank latitude and longitude: **Canada / Repatriated Travellers** (0 cases), and **China / Unknown** (1,873 cases). The second record is excluded because of missing coordinates, despite having a positive case count. Counts describe the downloaded source version and should be compared with the browser console when submitting.

Three cleaned examples:

| Country | Latitude | Longitude | Cases |
| --- | ---: | ---: | ---: |
| Afghanistan | 33.93911 | 67.709953 | 299 |
| Albania | 41.1533 | 20.1683 | 361 |
| Algeria | 28.0339 | 1.6596 | 1,320 |

## 2. THINK answers

These answers were revised with AI assistance; they are not claimed as an unassisted five-minute exercise.

1. **Which records could have missing coordinates?** Records for unknown locations, repatriated travellers, or other groups without a specific geographic location may have missing coordinates. In the downloaded CSV, the two excluded records listed above have blank coordinates. A blank province/state alone does not mean the coordinates are missing.
2. **Why might nearby circles overlap?** Similar latitude and longitude values place circles close together. Large case counts create larger circles, so their edges can overlap. Different records can also share coordinates. Partial opacity helps reveal overlap, although it does not make every covered point easy to hover.
3. **What should a tooltip show?** Country/region, province/state when available, latitude, longitude, and the confirmed case count for 5 April 2020.

## 3. Representation and interaction

The chart uses D3 v7 and an 800 by 700 SVG viewBox, with margins of top 40, right 40, bottom 60 and left 70. The inner plot is 690 by 600 units.

- Longitude uses `scaleLinear()`, domain `[-180, 180]`, range `[0, 690]`.
- Latitude uses `scaleLinear()`, domain `[-90, 90]`, range `[600, 0]`. The range is reversed because SVG y-coordinates increase downward.
- Cases use `scaleSqrt()`, domain `[0, maximum cases]`, radius range `[0, 60]`. With a zero-based square-root radius, circle area is proportional to cases. The larger maximum radius makes small positive counts easier to see, but increases overlap.
- Circles are steel blue with fill opacity 0.5. Axis labels give coordinates in degrees. The title gives the selected date. There are no permanent place labels.

This is a longitude-latitude scatterplot, not a projected world map; equal coordinate differences do not imply equal physical distances everywhere.

`pointerenter` calls `showTooltip(event, d)`, fills the tooltip from the bound record and highlights the circle. `pointermove` calls `moveTooltip(event)` and positions the fixed tooltip using `clientX` and `clientY`. `pointerleave` calls `hideTooltip(event)`, hides the tooltip, resets the outline and restores the status message. CSS `pointer-events: none` prevents the tooltip from taking the pointer away from the circle.

## 4. Verification: expected result -> actual result

The following checks combine source review with code-level execution. Tooltip functions were called with simulated events and lightweight selection stubs; these checks are not a browser hover test. Browser checks that have not been performed are marked pending.

| Test | Expected result | Actual result and status |
| --- | --- | --- |
| V1 - data count | Number of SVG circles equals valid records, including zero-radius circles. | The actual converter returns 287 valid records, and `.data(data).join("circle")` specifies one circle per record. **The browser DOM count is pending**; it should be 287, not 260. |
| V2 - geography | Longitude 0 is central; northern latitude appears above southern latitude. | Executing the actual D3 scale definitions gives `x(0) = 345`, `y(45) = 150`, and `y(-45) = 450`. **Scale calculation passed.** Whole-circle containment and overlap still need visual inspection. |
| V3 - zero / invalid | Zero cases are retained with radius 0. Missing, non-finite, negative-case and out-of-range numeric fields are rejected. | The converter retained a zero-case fixture and rejected blank latitude, blank cases, nonnumeric latitude, infinite latitude, latitude 91, longitude 181, and cases -1. The source has 27 valid zero-case rows. Actual scale checks returned radius 0 for zero and 60 for the maximum. **Code-level checks passed.** |
| V4 - hover | Tooltip content matches the record, follows the pointer and hides on exit; no permanent place labels. | Actual handlers passed simulated show/move/hide checks for Afghanistan (299), Albania (361), and Algeria (1,320). Tooltip content matched, movement updated its position, hiding set `display: none`, and the outline reset. Source review confirms no permanent place labels. **Hovering three circles in the browser remains pending.** |

To finish the browser checks, run `python -m http.server 8000` in the lab folder and open `http://localhost:8000`. In DevTools Console, compare the logged valid count with `document.querySelectorAll("#chart circle").length`. Hover three visible circles and check their contents, movement and disappearance; also inspect circles near the plot edges.

## 5. One bug and fix

**Failed observation:** The graph did not appear, as reported during development.

**Cause:** The code used `d3.select("chart")`. This searches for a `<chart>` element, but the HTML contains `<svg id="chart">`, so the selection was empty.

**Change:** Replace the selector with `d3.select("#chart")` and set its viewBox. This selects the existing SVG instead of creating another chart container.

**Retest:** The current HTML contains `id="chart"`, and the current JavaScript uses `d3.select("#chart")`; the mismatch is fixed in the source. Data conversion and scale checks also pass. A refreshed-browser visual retest is still required before recording this as a fully verified rendering fix.

## 6. Required ADAPT: click-to-pin

**Current status: not implemented in the submitted script at the time these notes were written.** The code has hover handlers but no click handler, Escape handler, or selected-point state. It would be inaccurate to claim that pinning already works.

The intended design is to keep a temporary `hoveredRecord` separate from a persistent `selectedRecord`:

- Hover may update temporary state, but must not replace tooltip content while a record is selected.
- Clicking a circle selects it and pins its tooltip. Clicking the same circle again clears the selection; clicking another circle may explicitly select that record.
- Leaving a circle hides only a temporary tooltip. A pinned tooltip stays visible.
- Escape clears the selection and dismisses the pinned tooltip.

This design still needs implementation and browser testing. The optional rectangular brush is also not implemented.

## 7. Pre-lab results and explanations

The worked example uses fictional study rooms, separate from the COVID-19 dataset. The original notes and interaction exercise recorded these outcomes:

| Edit | Expected result -> observed result |
| --- | --- |
| Media Room visitors: 28 to 55 | Larger circle and updated tooltip -> the tooltip showed 55 visitors and the circle used the larger size. |
| Quiet Study x: 53 to 83 | Move right without changing height or size -> the point moved right to x=83 with the same height and size. |
| Remove `pointerleave` temporarily | Tooltip stays visible after leaving -> the previous tooltip remained until another circle updated it. The handler was restored afterward. |

The practice CSV inspection records **5 raw rows and 4 valid rows**. The `Overflow` record contains `not-a-number` and is rejected after numeric conversion and finite-value checking. `Empty Lab`, with 0 visitors, is retained. Raw CSV values are strings; conversion makes the coordinate and quantity fields numeric.

The three interaction explanations are:

1. **`event` versus `d`:** `event` describes the browser interaction, including pointer position and the target element. `d` is the data record bound to that circle.
2. **Hide or reposition a tooltip:** Repositioning keeps it associated with the pointer; hiding prevents stale details from remaining after departure. With fixed positioning, `clientX` and `clientY` use the matching viewport coordinate system.
3. **Evidence for one mark per valid row:** Compare the valid-record count with the SVG circle count, inspect numeric attributes for `NaN`, and check that tooltips match the bound records. Zero-radius circles count as elements even though they are invisible.

## 8. Remaining work before submission

- Implement and verify the required click-to-pin/Escape behaviour.
- Complete the pending browser checks in section 4 and the visual retest in section 5, then record the actual results.
- Fix or remove the leftover keyboard-focus handler: it still reads `d.name` and `d.visitors`, which are not fields in the cleaned COVID data. Circles also need `tabindex="0"` if keyboard focus is supported.
- Add names/IDs, course and lab details, and a visible source credit to the page. The current page already shows the title and date, but not the student details or data-source credit.
- Keep any authorship declaration consistent with the assistance disclosure below.
- Submit one ZIP containing `index.html`, `script.js`, `style.css` and `NOTES.md`, plus any local CSV actually used. The current code loads the CSV remotely.

## 9. AI and example-code disclosure

ChatGPT assisted with explaining the assignment, answering conceptual questions, supplying and fixing bugs in HTML/CSS/JavaScript files, diagnosing CSV-loading and SVG-selector errors, and explaining radius scaling. Tooltip techniques were adapted from the supplied worked interaction example. AI-assisted checks executed the current data converter, scale definitions and tooltip handlers; browser checks remain distinguished above. We do not claim that all code and answers were produced without external assistance.
