# Section 14 — Separate density-highlighting example

This is a standalone learning example. Your existing `lab03-d3` files were not edited.

## Run it

Double-click `index.html`. Keep all files in this folder together. No installation, internet connection or server is required. The local D3 library is included. `data.js` contains a copy of the CSV so D3 can parse it when the HTML is opened directly; browsers normally block fetching another local file from `file://`.

When served over HTTP, the page uses `d3.csv("vn-provinces-data.csv")`. When opened directly, it uses `d3.csvParse(window.PROVINCE_CSV)`. If you change the dataset, update both the CSV and its copy in `data.js`.

## Learn the implementation step by step

Read the numbered comments in `script.js` in this order:

1. **Define density bands once.** Thresholds `[100, 500, 1000]` produce four categories: <100, 100–<500, 500–<1000 and ≥1000 people/km². These are explicit chart-design categories. `densityBand()` uses `d3.bisectRight()` to return the category index. Exactly 500 returns index 2, putting it in the higher band.
2. **Load and convert data.** Inspect headers and two records in the console. Convert population, GRDP, area and density to numbers. Replace the GRDP decimal comma before conversion. Invalid rows are logged and excluded.
3. **Draw the original encodings.** Population uses a linear x-scale; GRDP uses a linear, reversed y-scale; land area uses a square-root radius scale; density determines the fill color. Axes use zero baselines and data-derived upper limits. The canvas remains 450 × 900 from Section 10.
4. **Create the control and legend.** Both use the shared `categories` array. The selector starts with “All provinces” and then lists the four density bands. The option values `0`, `1`, `2`, `3` are category indexes, not density values.
5. **React to a selection.** The change event calls `highlightCategory()`. `matches(d)` checks whether a province's category equals the selected category. `Number(selected)` converts the HTML option's string into a number before comparing indexes.
6. **Apply highlighting.** Matches get opacity 0.8 and a dark outline. Other circles get opacity 0.12 and a faint outline. The update never changes `cx`, `cy`, `r` or `fill`, and never removes a circle. It updates the count in the status paragraph.

The core new logic is:

```js
const selected = selector.value;
const matches = d => selected === "all" ||
  densityBand(d.density) === Number(selected);

circles.attr("fill-opacity", d => matches(d) ? 0.8 : 0.12);
```

The full function also changes outlines and displays the matching count. To understand the feature, follow one row (for example Đồng Tháp with density 500) through `densityBand()`, `matches()` and the opacity assignment.

## Tests performed on 17 October 2026

Expected counts were calculated from the supplied CSV separately from the browser interactions. The selector was changed through the browser UI, and the actual SVG attributes were inspected after each change.

| Case | Expected | Observed | Result |
| --- | --- | --- | --- |
| Select <100 | 9 provinces highlighted | 9 highlighted, 63 circles retained | PASS |
| Select 100–<500 | 33 highlighted; Đồng Tháp excluded | 33 highlighted; Đồng Tháp faded | PASS |
| Select 500–<1000 — boundary case | 13 highlighted; Đồng Tháp at exactly 500 included | 13 highlighted; Đồng Tháp emphasized | PASS |
| Select ≥1000 | 8 highlighted | 8 highlighted | PASS |
| Reset to All provinces | All 63 emphasized again | 63 highlighted | PASS |

For every selection, all 63 circles' province identifiers, `cx`, `cy`, `r` and fill colors were compared against the initial state: every comparison matched. Therefore the highlighting preserves the original data-to-position, size and color encodings. Browser error logs were empty, and the JavaScript syntax check passed.

Browser testing used a temporary localhost server. Direct `file://` navigation is not supported by the browser testing tool; the local data copy and CSV parsing were checked separately. The example itself does not require that server.

## Limitation

Overlapping provinces can remain difficult to distinguish, especially within the selected category. Fading other categories improves attention but does not separate coincident circles. No province is removed to make the chart look cleaner. Density colors also appear paler on faded marks; the dark outline distinguishes the active group while the legend preserves the original category hues.

## AI assistance and independent group verification

AI helped create this separate example, explain the category and event-handler code, and execute the tests reported above.

Your group's independent verification has not yet been reported. Use this checklist and record actual results rather than copying the AI test results as your own:

- [ ] Open `index.html` directly and confirm 63 circles are loaded.
- [ ] Select <100 and confirm 9 provinces are highlighted.
- [ ] Select 500–<1000 and confirm 13 provinces are highlighted.
- [ ] Find Đồng Tháp's CSV row, confirm density is exactly 500, and explain why it belongs in that band.
- [ ] Reset All provinces and confirm the count returns to 63.
- [ ] Explain why highlighting does not change the population, GRDP, area or density encodings.

Verified by: __________  Date: __________

What our group independently checked and observed: __________

After performing the checks, replace the pending-verification note in the page with a short factual description of what your group verified.
