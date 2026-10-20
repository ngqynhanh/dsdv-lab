### 1. Data join

For `[A, B, C] → [C, A, D]` keyed by ID, D enters, B exits, and A and C update.

Order doesn’t change identity. With a key function, matching goes by key, so A’s element stays A’s and C’s stays C’s. Only the data order changes. The DOM isn’t reordered unless you call `.order()` or `.sort()`.

`(d, i) => i` is risky because it matches by position. C binds to A’s old element, A to B’s, and D to C’s. Every datum counts as an update, with no enter or exit, so element state and transitions end up on the wrong records. Use a stable unique key like `d => d.id`.

### 2. Data pipeline

- **(a) Raw rows:** the unprocessed strings from `csv()`.
- **(b) `allRecords`:** the validated, typed records.
- **(c) `activeRecords`:** (b) filtered down to the active keys.
- **(d) `sortedRecords`:** a sorted copy of (c), used only for drawing.

`sort()` changes the array in place. If you sort `allRecords`, the original order is gone, later filters depend on earlier sorts, and every other view reading that array changes without warning. Sort a copy (`[...activeRecords].sort(...)`) so `allRecords` stays as loaded and any redraw can start from it.

### 3. Remove behavior

Remove deletes the last province added, whatever the current sort is.

Say the user adds Da Nang, then HCMC, then Hanoi, and sorts by GRDP descending. Remove deletes Hanoi, even though it isn’t the bottom row.

### 4. Edge cases

| #   | Edge case                    | What goes wrong                                                                                                                                                           | Fix                                                                                                                                                            |
| --- | ---------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | **Wrong key**                | With `(d, i) => i`, bars bind to the wrong stuff, so transitions and state attach to the wrong record. Names with inconsistent spelling or diacritics also fail to match. | Key by a stable unique ID (`d => d.id`), not by index or display name.                                                                                         |
| 2   | **Changing chart height**    | The number of bars changes, so the SVG resizes, bars stretch or get cut off, and the layout jumps.                                                                        | Compute height from the bar count (`n * barHeight + margins`), then update the y-scale range and SVG height in `render()`.                                     |
| 3   | **Stale axis**               | The x-domain still uses the old max after add or remove, so bars overflow or the axis shows outdated ticks.                                                               | Recompute domains and call the axis inside `render()` every time. Decide whether the domain follows the active data or stays fixed across all of `allRecords`. |
| 4   | **Missing labels**           | Rects are joined but text is not, so labels are orphaned after removal. Long province names can also be clipped by the left margin.                                       | Join one `<g>` per record containing both rect and text. Size the margin to the longest name.                                                                  |
| 5   | **Decimal commas**           | Vietnamese-format numbers like `1.234,5` parse as `NaN` or as `1.234`, which is off by a factor of 1000.                                                                  | Normalize the string explicitly before converting, and check `Number.isFinite`. Reject or flag bad rows at validation.                                         |
| 6   | **Rapid repeated clicks**    | Remove on an empty list, the same province added twice, or overlapping transitions that leave stale elements.                                                             | Disable the buttons when not applicable and guard against duplicates in `activeKeys`. Make `render()` fully state-driven, and interrupt or name transitions.   |
| 7   | **Duplicate records**        | Two rows with the same ID (for example, multiple years) break the join. Duplicate data go to enter, and duplicate elements go to exit.                                    | Dedupe or filter by year during validation, and assert that IDs are unique.                                                                                    |
| 8   | **Zero or unavailable GRDP** | A zero value draws an invisible bar that looks like missing data. A log scale fails on zero. Missing values become `NaN`, which makes the sort order unpredictable.       | Treat `null` and `0` differently. Show a “No data” label, sort nulls last, and avoid a log scale.                                                              |

### 5. Chart encoding

It’s a horizontal bar chart with one bar per province.

- **y axis:** province name on a band scale keyed by ID, in the current sort order.
- **x axis:** GRDP on a linear scale that starts at 0. The axis title gives the unit (trillion VND) and the year.
- **Labels:** names are right-aligned in the left margin, and values sit just past the end of each bar. Missing data shows “No data” instead of an empty row.
- **Height:** `margins + n × step` (for example, 32px per bar). Bars keep a constant thickness, and the chart grows or shrinks as provinces come and go.

A non-zero baseline misleads because readers take bar length as a proportion of the value. Truncating the axis cuts off the part every bar shares, so the length ratio stops matching the data ratio. 900 vs 1000 is an 11% gap, but with the axis starting at 850 the bars measure 50 and 150, and the larger one looks three times as big.