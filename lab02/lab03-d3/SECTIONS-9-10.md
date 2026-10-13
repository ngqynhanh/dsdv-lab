# Lab 3 — Sections 9 and 10

Implementation and verification record, 13 October 2026.

## How to repeat the work

1. Double-click `index.html`. The normal view uses the supplied province CSV, embedded in the HTML for direct opening.
2. Scroll to **Sections 9 and 10 — Verification and adaptation**. The page shows the checks and evidence. Open the browser console to see the raw headers, two raw records, two converted records, record counts, and the verification table.
3. Click **Small test dataset** to temporarily replace the data with four synthetic rows. No source file is modified.
4. Click **Reproduce Bug C** to deliberately demonstrate incorrect linear radius sizing on those synthetic rows.
5. Click **Small test dataset** again to see the corrected sizing.
6. Click **Source CSV** to restore the actual 63 provinces before submission. This is also the default whenever `index.html` is opened without query parameters.

Browser evidence below was collected using a localhost preview. Direct `file://` opening uses the same rendering and verification functions; the browser automation tool does not permit `file://` URLs, so that mode was not visually verified by the tool.

## Section 9.1 — Verify the source chart

### Step 1: State hypotheses before running the checks

- If every valid CSV row becomes a mark, circle count will equal valid record count.
- If conversion is correct, all four numeric measures will be finite numbers, including decimal-comma GRDP values.
- If dynamic scales and radius padding are correct, all circle edges will remain inside the plotting area.
- If the y range is reversed, larger GRDP values will have smaller SVG y coordinates.
- If size encodes land area correctly, the ratio of rendered radius squared will equal the ratio of land areas.
- If the legend uses the chart's threshold rule, every swatch and circle will use the expected color; an exact boundary will enter the higher band.

### Step 2: Add repeatable checks

Added `verifyChart()` in `script.js`. It inspects actual circle attributes (`cx`, `cy`, `r`, and `fill`), SVG dimensions, axis transforms, legend swatches, numeric values, and the scale domains. Results appear in the page and console. It reports failures without silently removing records.

### Step 3: Run the normal source chart and record evidence

| Requirement / test | Observed evidence | Result |
| --- | --- | --- |
| Circle count equals valid rows | 63 loaded, 63 valid, 63 SVG circles; 0 excluded | PASS |
| No uncaught errors | Browser error log returned no entries | PASS |
| Numeric conversion | Population, GRDP, area and density are finite JavaScript numbers | PASS |
| Minimum and maximum fit | Every circle, including its radius, fits within the 368 × 814 inner area | PASS |
| Conventional y direction | `y(0) = 801`; `y(154.84) = 38.413`, so the larger value is higher | PASS |
| Axes align with plotting area | Bottom axis translated to y=801; left axis to x=13; both meet at zero | PASS |
| Dynamic domains | Population extent 327.9–8598.7 → domain [0, 9000]; GRDP extent 20.7–154.84 → domain [0, 160] after `.nice()` | PASS |
| Density legend matches circles | All four actual swatch colors and all 63 circle fills match the shared mapping | PASS |
| Boundary behavior | Tested just below and exactly at 100, 500 and 1000; exact values enter the higher band | PASS |
| Circle area proportional to land area | Rendered radius² ratios match source land-area ratios for all marks | PASS |
| Readable titles and units | Visually inspected full chart: population in thousand people; GRDP in million VND/person/year; density and area units stated | PASS |

The on-page source view has **11/11 automatic checks passing**, including the size and tooltip checks added for Section 10. Console error inspection and visual label inspection are additional checks, not included in that total.

## Section 9.2 — Test with small data

### Step 4: Define a test dataset using the actual field structure

The test CSV uses `province`, `population`, `GRDP-VND`, `area`, and `density`. GRDP values retain the decimal-comma format so the real conversion path is tested.

| Province | Population (thousand) | GRDP (million VND/year) | Area (km²) | Density (people/km²) |
| --- | ---: | ---: | ---: | ---: |
| Test Low | 100 | 10 | 100 | 99 |
| Test Medium | 500 | 50 | 400 | 100 |
| Test High | 1000 | 100 | 900 | 500 |
| Test Maximum | 1500 | 150 | 1600 | 1000 |

These are synthetic test values, not real provinces. They cover low, medium and high positions, maximum area, and all three exact density boundaries.

### Step 5: Run the small-data view

Clicked **Small test dataset**, which loads `index.html?test=1` through D3 and the same `buildChart()` function as the source data.

Observed results:

1. Four valid rows produced four circles.
2. The points move right and upward in low → medium → high → maximum order.
3. Domains recalculated to x=[0,1600] and y=[0,160], proving they respond to the replacement data.
4. Land areas 100, 400, 900 and 1600 produce radii 3.25, 6.5, 9.75 and 13 pixels.
5. A fourfold land-area increase (100 → 400) produces a fourfold circle-area increase: `(6.5 / 3.25)² = 4`.
6. The maximum area gives the maximum configured radius of 13 pixels.
7. Density 99 is blue; 100 is green; 500 is yellow; 1000 is purple. These match the legend.
8. All circle edges remain inside the adapted plotting area.

Result: **14/14 automatic checks passed**.

## Section 9.3 — Debugging challenge: Bug C

### Step 6: Reproduce the defect deliberately

The existing source chart already used square-root sizing. To test the defect honestly, added a controlled reproduction: `index.html?test=1&bug=area`. This switches only the synthetic test view to `d3.scaleLinear()` for radius. The source view always uses `d3.scaleSqrt()`.

1. **Observed:** Test Medium has four times Test Low's land area, but sixteen times its rendered circle area. The reproduction reports **12/14 checks passed**, with both proportional-area checks failing.
2. **Expected:** Four times the land area should give four times the circle area, hence twice the radius.
3. **Likely cause:** Radius is linear in land area; because circle area is `πr²`, this squares the intended ratio.
4. **Fix:** Use `d3.scaleSqrt().domain([0, maxArea]).range([0, 13])`. A zero origin is necessary for exact proportionality.
5. **Verification:** Reopened **Small test dataset**. Observed circle-area ratio returned from 16 to 4; **14/14 checks passed**. The unchanged maximum-area radius of 13 shows that the failing test detects the relationship between sizes, rather than only checking the largest mark.

### Step 7: Restore the source CSV

Clicked **Source CSV**. Confirmed 63 circles, 0 excluded records, **11/11 checks passed**, and no browser error log entries. The submission view therefore displays actual province data.

## Section 10 — Adapt the chart

### Prediction note

Suggested prediction: “Changing width and height should update the inner dimensions, scale ranges, axes and label positions; adding tooltips should change each circle's hover text without changing its position, size or color.”

This sentence is an AI-assisted draft. The handout asks for a prediction written before using AI; this document does not claim that the students independently wrote it before this session. Add your own original prediction if you recorded one.

### Step 8: Change the canvas from 300 × 600 to 450 × 900

1. Changed the `width` and `height` constants in `script.js` to 450 and 900.
2. Updated the initial SVG attributes in `index.html` to the same dimensions.
3. Updated the SVG flex width in `style.css` to 450 pixels, preserving the simple styling.
4. Retained margins `{ top: 24, right: 18, bottom: 62, left: 64 }`; inner dimensions therefore change from 218 × 514 to 368 × 814.
5. Because the scales already derive their ranges from inner dimensions, x changes from [13,205] to [13,355] and y from [501,13] to [801,13].
6. The bottom axis still uses `yScale(0)` and the left axis still uses `xScale(0)`. Titles and gridlines continue to use inner dimensions, so their positions update automatically.
7. Made the status text use the dimension variables instead of a fixed “300 × 600” message.

### Step 9: Choose additional adaptation B — Tooltip

Expanded each circle's SVG `<title>` from the province name to five fields: province name, population, GRDP per person, land area, and density. Numeric fields include units. The browser displays this native tooltip when a circle is hovered; no extra styling or chart library is required.

### Step 10: Verify the adaptation

- Browser inspection confirmed actual SVG attributes of **450 × 900**.
- Automated geometry inspection confirmed every circle fits inside the **368 × 814** plotting area.
- Visually inspected the complete chart: circles, axes, tick labels and axis titles remain inside the SVG canvas.
- Source and small-data tests still passed, preserving the population, GRDP, land-area and density encodings.
- Inspected every circle's `<title>`: all contain the province name and the four labeled measures. The tooltip content was verified; the browser-controlled test did not capture a native tooltip popup on screen.

## Reflection

1. **What was easiest to adapt?** Changing the two dimension constants, because scale ranges, gridlines, axes and labels already depend on inner dimensions.
2. **What depended on hard-coded assumptions?** Margins, maximum radius of 13 pixels, tick counts, density boundaries and CSS flex width. The expected 450 × 900 size in the verification check is intentional for this task. The data domain maxima are calculated dynamically.
3. **What would improve with more records or larger values?** Larger values already expand the domains. More records could increase overlap; consider highlighting/search and a larger plotting area. Long tick labels may require wider margins. The embedded CSV and external CSV must be kept in sync when updating the dataset.

AI helped implement the adaptation, controlled bug reproduction, checks and this document. The results above are tool-run evidence. Review the code, reproduce the tests and write your own reflection before submission.
