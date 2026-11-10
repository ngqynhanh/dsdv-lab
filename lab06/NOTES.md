# Lab 06 — D3.js: Multi-line COVID-19 Chart

**Course:** Data Science and Data Visualization — International University

**Students:** Phạm Như Nguyên Trung - ITCSIU24091; Nguyễn Quỳnh Anh - ITCSIU24005

**Run:** Using Open with Live Server

**Data:** JHU CSSE `time_series_covid19_confirmed_global.csv`, loaded from GitHub (no local CSV). Historical data.

## 1. Transformed-data evidence

Wide CSV (one column per date) → tidy records `{ country, date: Date, cases: Number }`.

| Check (console) | Result |
| --- | --- |
| Headers | `Province/State, Country/Region, Lat, Long, 1/22/20, …` |
| `4/1/20` and `5/1/20` both present | true, true |
| Source rows summed per country | Vietnam 1, US 1, **France 12**, Italy 1 |
| Dates kept | 31 (1 Apr → 1 May 2020 inclusive) |
| Observations | 124 = 4 × 31 |
| Blank / invalid cells | 0 |

| Country | 01 Apr 2020 | 01 May 2020 |
| --- | ---: | ---: |
| Vietnam | 218 | 270 |
| US | 227,903 | 1,115,972 |
| France | 57,125 | 169,387 |
| Italy | 110,574 | 207,428 |

All values are computed from the CSV at load time; nothing is hard-coded.

## 2. THINK answers

1. **Why does France appear in several rows?** The file has one row per province/region. France has 12 rows: mainland (blank `Province/State`) plus 11 overseas territories (French Guiana, French Polynesia, Guadeloupe, Martinique, Mayotte, New Caledonia, Reunion, Saint Barthelemy, Saint Pierre and Miquelon, St Martin, Wallis and Futuna). The country total is the sum of all of them for each date.
2. **What breaks if dates are sorted as plain text?** Text compares character by character, so `4/1/20 < 4/10/20 < 4/2/20`. The line would jump back and forth in time, and a text range filter `>= '4/1/20' && <= '5/1/20'` would keep the wrong columns. We parse headers with `d3.timeParse('%m/%d/%y')` and compare `Date` objects.
3. **Cases per day or accumulated?** The CSV stores **cumulative** counts (total confirmed up to that day), so the main Y-axis is "Cumulative confirmed cases". Daily new cases must be derived as today − yesterday (done only in the stacked-area extension).

## 3. Verification (expected → actual)

| Test | Expected | Actual |
| --- | --- | --- |
| V1 — reshape | 4 countries × 31 dates; provinces summed once per day | 124 records; France = 12 rows summed per date (57,125 on 1 Apr vs 56,362 for mainland alone). **Pass** |
| V2 — axes/path | 4 lines, chronological, nonnegative | 4 `path.series`, no province paths; X runs 01 Apr → 01 May left→right; Y starts at 0 and grows upward; line ends match the table above. **Pass** |
| V3 — pointer | Same nearest date; four values match cleaned data | Middle of chart → 16 Apr 2020: Vietnam 268, US 683,351, France 145,166, Italy 168,941. Right edge → 01 May 2020: 270 / 1,115,972 / 169,387 / 207,428 (same as table). Guide and dots hide on leave. **Pass** |
| V4 — legend | Hover isolates visually; leave restores all four | Hover France → only France at full opacity, other three dimmed; leave → all four restored; still 4 paths in the DOM. **Pass** |

## 4. Bug challenge

- **Failure:** France's line was too low — 56,362 on 1 Apr and 167,846 on 1 May instead of 57,125 and 169,387.
- **Cause:** taking a single France row (`rows.find(...)`, the mainland row with blank `Province/State`) instead of aggregating; the 11 overseas-territory rows were ignored.
- **Fix:** group rows with `d3.group(rows, r => r['Country/Region'])` and use `d3.sum` over **all** rows of the country for each date column.
- **Retest:** console logs "France: 12 source row(s) summed"; 1 Apr = 57,125 and 1 May = 169,387; still exactly 124 observations and 4 paths.

## 5. ADAPT — click-to-lock legend focus

Two separate state variables drive the same visual rule (`active = hovered ?? locked`):

- **Temporary hover (`hovered`)** — set on `pointerenter`, cleared on `pointerleave`. It is a preview: nothing is remembered once the pointer leaves the legend.
- **Locked selection (`locked`)** — set on `click`. It persists after the pointer moves away, so the reader can go to the chart and use the date readout while one country stays emphasized. Clicking the same country again unlocks it; clicking another country moves the lock; **Show all** (or `Esc`) restores all four lines.

While a lock is active, hovering a different country temporarily previews it, and leaving returns to the locked one. Both states only toggle CSS classes (`dim`, `focus`); no data is filtered or removed, so the readout always shows all four values. The legend items are `<button>`s, so lock also works from the keyboard and exposes `aria-pressed`.

## 6. Optional extension — stacked area of daily new cases

- Daily new = cumulative(today) − cumulative(yesterday); 31 Mar is read only as the baseline for 1 Apr.
- **Negative revisions:** France has four days where the cumulative count dropped (4 Apr −17,076; 7 Apr −3,489; 23 Apr −1,709; 29 Apr −1,455). These are reporting corrections, not negative cases, and a stack cannot show negative bands, so they are clamped to 0 and listed under the chart.
- Every row holds all four countries for the same date, so `d3.stack()` layers are aligned; drawn with `d3.area()`. Y-axis: "Daily new cases (stacked total)".

## 7. AI-use disclosure

Claude (Anthropic) was used to help write and test `index.html`, `script.js`, `style.css`. We ran the page, checked the console output, write the notes and the V1–V4 results above ourselves, and can explain the grouping and the shared-date readout.
