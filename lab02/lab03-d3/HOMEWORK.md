# Section 14 — Tooltip and interpretation

## 1. Chosen feature

Used the second homework option: a tooltip plus a short interpretation of two interesting data points. The five-field native SVG tooltip introduced in Section 10 is reused. Hover over a circle to read its name, population, GRDP per person, area and density with units.

## 2. Implementation steps

1. Read the supplied CSV and selected Hồ Chí Minh (largest population) and Quảng Bình (highest GRDP per person) for interpretation.
2. Retained the existing D3 circle tooltips, linear population and GRDP scales, reversed y range, square-root area scale and discrete density colors.
3. Added a Homework section below the chart. `renderHomework()` reads the converted records and generates the two interpretation paragraphs. The numbers therefore come from the plotted records.
4. Added three checks against expected values independently transcribed from the CSV. Each compares all five fields in the actual rendered `<title>` and the circle's density color.
5. Added a limitation and a note separating AI assistance from independent group verification.
6. Restored the missing embedded CSV so opening the HTML directly can still use the existing data-URL loading path. The embedded copy matches the external CSV.
7. Opened the page in a browser over localhost, inspected the displayed test results and browser errors, checked the synthetic-data view, and restored the source-data view.

## 3. Interpretation of two data points

**Hồ Chí Minh:** Population is 8,598.7 thousand people, the largest in this CSV, so its circle appears farthest right. Density is 4,171 people/km², placing it in the purple ≥1,000 category. GRDP per person is 43.6 million VND/year. Its land area is 2,061.4 km², so its circle is smaller than Quảng Bình's despite its larger population.

**Quảng Bình:** GRDP per person is 154.84 million VND/year, the highest in this CSV, so its circle appears highest. Population is 887.6 thousand people, placing it far to the left of Hồ Chí Minh. Its land area is 8,000 km², giving it about 3.88 times Hồ Chí Minh's circle area. Density is 111 people/km², in the green 100–<500 category.

Together these points show that the highest population does not necessarily coincide with the highest GRDP per person in this dataset. This is a description of the supplied records, not a causal conclusion or a claim about current provincial rankings.

## 4. Tests and recorded results

Tests run by the AI assistant on 13 October 2026:

| Case | Expected tooltip values: population / GRDP / area / density | Other expectation | Observed result |
| --- | --- | --- | --- |
| Hồ Chí Minh | 8,598.7 / 43.6 / 2,061.4 / 4,171 | Province name correct; purple circle; decimal comma correctly converted | PASS: all five fields and color match |
| Quảng Bình | 887.6 / 154.84 / 8,000 / 111 | Province name correct; green circle; largest GRDP fits near the top | PASS: all five fields and color match; chart bounds check passes |
| Đồng Tháp — edge case | 1,693.3 / 41.1 / 3,383.8 / 500 | Exactly 500 enters yellow 500–<1,000 band, rather than green 100–<500 | PASS: all five fields and boundary color match |

Units: population = thousand people; GRDP = million VND/person/year; area = km²; density = people/km².

Additional regression evidence:

- Source view: 63 valid records, 63 circles, 0 exclusions; 11/11 existing checks pass.
- Synthetic view: 14/14 existing checks pass. Source-province interpretations are replaced by an explicit synthetic-data notice, preventing misleading interpretation of test points.
- Returned to the source view after testing; it displays all 63 provinces.
- Browser error log: no error entries.
- JavaScript syntax check: passes.

The tests inspect actual rendered SVG tooltip text and circle attributes. A native tooltip popup was not captured through simulated hovering. The group should perform the hover checks below. Browser automation used HTTP because it does not permit direct `file://` navigation.

## 5. Limitation

Overlapping circles can hide smaller marks and make their hover tooltips difficult to reach. Transparency and drawing smaller circles last reduce this problem but do not eliminate it. Circle areas are also difficult to compare exactly by eye; the tooltip supplies exact values without changing the original visual encodings.

## 6. AI assistance and independent verification

AI helped implement the tooltip in Section 10, add the homework interpretations and checks, restore the embedded CSV, and run the tests recorded above.

**Independent group verification: not yet reported.** The following is a worksheet for the group, not a claim that these actions have already been performed.

1. Open `index.html` directly. Confirm that the chart loads and shows 63 provinces.
2. Hover over the farthest-right circle (Hồ Chí Minh), wait for the native tooltip, and compare all five fields with its CSV row.
3. Hover over the highest circle (Quảng Bình) and compare all five fields with its CSV row.
4. Locate Đồng Tháp using the tooltip. Compare density 500 with the legend and confirm that its circle is yellow.
5. Review the two interpretation paragraphs against the CSV and explain why larger population does not imply a larger circle.
6. Record what you actually observed below, then update the short group-verification note on the page.

| Group check | Verified by | Date | Actual observation / issue |
| --- | --- | --- | --- |
| Direct opening and 63 circles | To complete | To complete | To complete |
| Hồ Chí Minh hover and CSV comparison | To complete | To complete | To complete |
| Quảng Bình hover and CSV comparison | To complete | To complete | To complete |
| Đồng Tháp density boundary | To complete | To complete | To complete |
| Interpretation and original encodings | To complete | To complete | To complete |
