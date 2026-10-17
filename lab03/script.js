"use strict"

// 1. Load the CSV file using D3. Serve this folder over HTTP when testing locally.
const CSV_URL = "vn-provinces-data.csv"
const settings = new URLSearchParams(location.search)
const testMode = settings.get("test") === "1"
// Controlled reproduction of Section 9 Bug C; never applied to the source chart.
const reproduceAreaBug = testMode && settings.get("bug") === "area"
const TEST_CSV = `province,population,GRDP-VND,area,density
Test Low,100,"10,00",100,99
Test Medium,500,"50,00",400,100
Test High,1000,"100,00",900,500
Test Maximum,1500,"150,00",1600,1000`
const statusElement = document.querySelector("#status")
if (typeof d3 === "undefined") {
	showError(new Error("D3 could not load. Check that d3.v7.min.js is present."))
} else {
	const csvUrl = testMode
		? "data:text/csv;charset=utf-8," + encodeURIComponent(TEST_CSV)
		: location.protocol === "file:"
			? "data:text/csv;charset=utf-8," + encodeURIComponent(window.PROVINCE_CSV)
			: CSV_URL
	d3.csv(csvUrl).then(buildChart).catch(showError)
}

function showError(error) {
	console.error("Lab 3 loading/rendering error:", error)
	statusElement.classList.add("error")
	statusElement.textContent = `Unable to draw chart: ${error.message} Check that the data and D3 library are present.`
}

function buildChart(rows) {
	// 2. Inspect actual headers and raw records before numeric conversion.
	console.log("CSV headers:", rows.columns)
	console.table(rows.slice(0, 2))
	const required = ["province", "population", "area", "density", "GRDP-VND"]
	const missing = required.filter((column) => !rows.columns.includes(column))
	if (missing.length)
		throw new Error(`Missing CSV columns: ${missing.join(", ")}`)

	// Empty strings must not turn into zero. GRDP-VND uses a decimal comma.
	const number = (value) =>
		value == null || value.trim() === "" ? NaN : Number(value)
	const converted = rows.map((row, i) => ({
		row: i + 2,
		province: row.province.trim(),
		population: number(row.population), // thousand people, as supplied
		grdp: number(row["GRDP-VND"].replace(",", ".")), // million VND/person/year
		area: number(row.area), // km²
		density: number(row.density), // people/km²
	}))
	const isValid = (d) =>
		d.province &&
		[d.population, d.grdp, d.area, d.density].every(
			(value) => Number.isFinite(value) && value >= 0,
		) &&
		d.area > 0
	const data = converted.filter(isValid)
	const invalid = converted.filter((d) => !isValid(d))
	if (invalid.length)
		console.warn("Excluded invalid rows (CSV row numbers included):", invalid)
	console.table(data.slice(0, 2))
	if (!data.length)
		throw new Error("The CSV contains no valid province records.")

	// 3. Section 10: dimensions changed from 300 × 600 to 450 × 900.
	const width = 450,
		height = 900
	const margin = { top: 24, right: 18, bottom: 62, left: 64 }
	const innerWidth = width - margin.left - margin.right
	const innerHeight = height - margin.top - margin.bottom
	const maxRadius = 13
	const svg = d3
		.select("#scatterplot")
		.attr("width", width)
		.attr("height", height)
	svg.selectAll("g").remove()
	const plot = svg
		.append("g")
		.attr("transform", `translate(${margin.left},${margin.top})`)

	// 4. Zero is meaningful for both axes; maxima are derived from the data.
	// The fallback 1 only handles an all-zero dataset. Radius padding keeps edges inside.
	const xScale = d3
		.scaleLinear()
		.domain([0, d3.max(data, (d) => d.population) || 1])
		.nice()
		.range([maxRadius, innerWidth - maxRadius])
	// SVG y increases downward: reverse the range to place larger GRDP higher.
	const yScale = d3
		.scaleLinear()
		.domain([0, d3.max(data, (d) => d.grdp) || 1])
		.nice()
		.range([innerHeight - maxRadius, maxRadius])
	// r = 13 * sqrt(area / maxArea), so pi*r² is proportional to province area.
	const areaScale = (reproduceAreaBug ? d3.scaleLinear() : d3.scaleSqrt())
		.domain([0, d3.max(data, (d) => d.area)])
		.range([0, maxRadius])
	const thresholds = [100, 500, 1000] // explicit descriptive rule, people/km²
	const colors = ["#4477AA", "#228833", "#EEAA33", "#AA3377"]
	const densityColor = d3.scaleThreshold().domain(thresholds).range(colors)

	plot
		.append("g")
		.attr("class", "grid")
		.attr("transform", `translate(${maxRadius},0)`)
		.call(
			d3
				.axisLeft(yScale)
				.ticks(6)
				.tickSize(-(innerWidth - 2 * maxRadius))
				.tickFormat(""),
		)

	// 5. One circle for every valid row; draw small circles last to reduce occlusion.
	plot
		.append("g")
		.attr("class", "provinces")
		.selectAll("circle")
		.data([...data].sort((a, b) => b.area - a.area))
		.join("circle")
		.attr("cx", (d) => xScale(d.population))
		.attr("cy", (d) => yScale(d.grdp))
		.attr("r", (d) => areaScale(d.area))
		.attr("fill", (d) => densityColor(d.density))
		.attr("fill-opacity", 0.65)
		.attr("stroke", "#334155")
		.attr("stroke-width", 0.65)
		.append("title")
		.text(
			(d) =>
				`${d.province}\nPopulation: ${d.population.toLocaleString("en-US")} thousand people\nGRDP per person: ${d.grdp} million VND/year\nArea: ${d.area.toLocaleString("en-US")} km²\nDensity: ${d.density.toLocaleString("en-US")} people/km²`,
		)

	// 6. Axes meet at the zero baselines; tick values retain the CSV units.
	plot
		.append("g")
		.attr("class", "axis x-axis")
		.attr("transform", `translate(0,${yScale(0)})`)
		.call(
			d3
				.axisBottom(xScale)
				.ticks(4)
				.tickFormat(d3.format(",.0f"))
				.tickSizeOuter(0),
		)
	plot
		.append("g")
		.attr("class", "axis y-axis")
		.attr("transform", `translate(${xScale(0)},0)`)
		.call(d3.axisLeft(yScale).ticks(6).tickSizeOuter(0))
	plot
		.append("text")
		.attr("class", "axis-title")
		.attr("text-anchor", "middle")
		.attr("x", innerWidth / 2)
		.attr("y", innerHeight + 35)
		.text("Population (thousand people)")
	plot
		.append("text")
		.attr("class", "axis-title")
		.attr("text-anchor", "middle")
		.attr("transform", "rotate(-90)")
		.attr("x", -innerHeight / 2)
		.attr("y", -44)
		.text("GRDP per person (million VND / year)")

	// 7. Generate legend boundaries from the same threshold array used by the scale.
	const labels = colors.map((color, i) => ({
		color,
		label:
			i === 0
				? `< ${thresholds[0]}`
				: i === thresholds.length
					? `≥ ${thresholds[i - 1].toLocaleString("en-US")}`
					: `${thresholds[i - 1].toLocaleString("en-US")} to < ${thresholds[i].toLocaleString("en-US")}`,
	}))
	const legend = d3
		.select("#density-legend")
		.selectAll("li")
		.data(labels)
		.join("li")
	legend.selectAll("*").remove()
	legend
		.append("span")
		.attr("class", "swatch")
		.style("background-color", (d) => d.color)
		.style("opacity", 0.65)
	legend.append("span").text((d) => d.label)
	statusElement.textContent = `${data.length} provinces plotted · ${invalid.length} invalid rows excluded · ${width} × ${height} px canvas${testMode ? " · SYNTHETIC TEST DATA" : ""}${reproduceAreaBug ? " · BUG C REPRODUCTION" : ""}`
	console.log("Record count:", {
		loaded: rows.length,
		valid: data.length,
		circles: plot.selectAll("circle").size(),
	})
	setup(data, plot, thresholds)
	render(data, plot)
	verifyChart({
		data,
		plot,
		svg,
		xScale,
		yScale,
		areaScale,
		densityColor,
		thresholds,
		colors,
		innerWidth,
		innerHeight,
		width,
		height,
	})
}

// Homework extension: reuse the circles and converted data from buildChart().
// No second CSV request, second drawing function or duplicated scales needed.
function setup(data, plot, thresholds) {
	const circles = plot.selectAll(".provinces circle")
	const selector = d3.select("#density-category")
	const labels = ["All provinces", "< 100", "100 to < 500", "500 to < 1,000", "≥ 1,000"]
	selector.selectAll("option").data(labels).join("option")
		.attr("value", (d, i) => i === 0 ? "all" : String(i - 1)).text(d => d)
	selector.property("disabled", false)
	const count = d3.select("#status").select(function () { return this.parentNode })
		.selectAll("#highlight-count").data([null]).join("p").attr("id", "highlight-count")
	function highlight() {
		const selected = selector.empty() ? "all" : selector.property("value")
		const matches = d => selected === "all" || d3.bisectRight(thresholds, d.density) === Number(selected)
		circles.attr("data-highlighted", d => String(matches(d)))
			.attr("fill-opacity", d => matches(d) ? 0.8 : 0.12)
			.attr("stroke-width", d => selected !== "all" && matches(d) ? 2 : 0.65)
		count.text(`${data.filter(matches).length} / ${data.length} provinces highlighted`)
	}
	selector.on("change.homework", highlight)
	highlight()

	// Keep the existing SVG <title> as a fallback; show an immediate HTML tooltip too.
	const tooltip = d3.select("body").selectAll("#province-tooltip").data([null])
		.join("div").attr("id", "province-tooltip").attr("role", "tooltip").property("hidden", true)
	const fmt = n => n.toLocaleString("en-US")
	function show(d) {
		tooltip.text(`${d.province}\nDân số: ${fmt(d.population)} nghìn người\nGRDP/người: ${fmt(d.grdp)} triệu VND/năm\nDiện tích: ${fmt(d.area)} km²\nMật độ: ${fmt(d.density)} người/km²`).property("hidden", false)
	}
	function position(x, y) {
		const box = tooltip.node().getBoundingClientRect()
		tooltip.style("left", `${Math.max(8, Math.min(x + 12, window.innerWidth - box.width - 8))}px`)
			.style("top", `${Math.max(8, Math.min(y + 12, window.innerHeight - box.height - 8))}px`)
	}
	function hide() { tooltip.property("hidden", true) }
	circles.attr("data-province", d => d.province).attr("tabindex", 0)
		.attr("aria-label", d => d.province).attr("aria-describedby", "province-tooltip")
		.on("pointerenter.homework", (event, d) => { show(d); position(event.clientX, event.clientY) })
		.on("pointermove.homework", event => position(event.clientX, event.clientY))
		.on("pointerleave.homework", hide)
		.on("focus.homework", function (event, d) {
			show(d)
			const box = this.getBoundingClientRect()
			position(box.right, box.top)
		})
		.on("blur.homework", hide)
		.on("keydown.homework", event => { if (event.key === "Escape") hide() })
}

// Section 14: interpret two source records and check three tooltip cases.
function render(data, plot) {
	const container = d3.select("#homework-interpretations")
	const list = d3.select("#homework-tests")
	container.selectAll("*").remove()
	list.selectAll("*").remove()
	if (testMode) {
		container.append("p").text("Synthetic test view: return to Source CSV to read the province interpretations and run the homework cases.")
		return
	}
	const fmt = value => value.toLocaleString("en-US", { maximumFractionDigits: 2 })
	const hcm = data.find(d => d.province === "Hồ Chí Minh")
	const qb = data.find(d => d.province === "Quảng Bình")
	if (hcm && qb) {
		container.append("p").text(`Hồ Chí Minh has ${fmt(hcm.population)} thousand people, the largest population in the supplied CSV, placing it farthest right. Its density of ${fmt(hcm.density)} people/km² puts it in the purple ≥1,000 band. Its GRDP is ${fmt(hcm.grdp)} million VND/person/year. Although it has the most people, its land area of ${fmt(hcm.area)} km² gives it a smaller circle than Quảng Bình.`)
		container.append("p").text(`Quảng Bình has the highest GRDP per person in this CSV, ${fmt(qb.grdp)} million VND/year, so it appears highest. Its population of ${fmt(qb.population)} thousand places it much farther left than Hồ Chí Minh. Its ${fmt(qb.area)} km² area produces about ${fmt(qb.area / hcm.area)} times Hồ Chí Minh's circle area, while its density of ${fmt(qb.density)} people/km² puts it in the green 100–<500 band. These two records show that the most populous province does not necessarily have the highest GRDP per person in this dataset.`)
		container.append("p").text("Interpretations describe the supplied CSV only; they do not establish current provincial rankings or a causal relationship between population and GRDP.")
	}
	// Expected values are independently transcribed from the supplied CSV.
	const cases = [
		{ name: "Hồ Chí Minh", population: 8598.7, grdp: 43.6, area: 2061.4, density: 4171, color: "#AA3377", reason: "largest population; decimal conversion" },
		{ name: "Quảng Bình", population: 887.6, grdp: 154.84, area: 8000, density: 111, color: "#228833", reason: "highest GRDP; upper chart edge" },
		{ name: "Đồng Tháp", population: 1693.3, grdp: 41.1, area: 3383.8, density: 500, color: "#EEAA33", reason: "edge case: density exactly 500 enters the higher band" }
	]
	const nodes = plot.selectAll(".provinces circle").nodes()
	for (const test of cases) {
		const node = nodes.find(n => n.__data__.province === test.name)
		const expected = `${test.name}\nPopulation: ${test.population.toLocaleString("en-US")} thousand people\nGRDP per person: ${test.grdp} million VND/year\nArea: ${test.area.toLocaleString("en-US")} km²\nDensity: ${test.density.toLocaleString("en-US")} people/km²`
		const passed = Boolean(node && node.querySelector("title").textContent === expected && node.getAttribute("fill") === test.color)
		list.append("li").text(`${passed ? "PASS" : "FAIL"} — ${test.name}: all five tooltip fields and density color match the CSV (${test.reason}).`).style("color", passed ? "#245b2a" : "#b00020")
	}
}

// Section 9: checks inspect actual SVG marks as well as the scale calculations.
function verifyChart({
	data,
	plot,
	svg,
	xScale,
	yScale,
	areaScale,
	densityColor,
	thresholds,
	colors,
	innerWidth,
	innerHeight,
	width,
	height,
}) {
	const results = []
	const check = (test, passed, evidence) =>
		results.push({ test, passed: Boolean(passed), evidence })
	const near = (a, b) => Math.abs(a - b) < 1e-6
	const circles = plot.selectAll(".provinces circle").nodes()
	check(
		"One circle per valid record",
		circles.length === data.length,
		`${circles.length} circles / ${data.length} valid records`,
	)
	check(
		"Numeric fields",
		data.every((d) =>
			[d.population, d.grdp, d.area, d.density].every(
				(v) => typeof v === "number" && Number.isFinite(v),
			),
		),
		"Population, GRDP, area and density are finite numbers",
	)
	check(
		"Circles fit inside plotting area",
		circles.every((node) => {
			const x = +node.getAttribute("cx"),
				y = +node.getAttribute("cy"),
				r = +node.getAttribute("r")
			return (
				x - r >= -1e-6 &&
				x + r <= innerWidth + 1e-6 &&
				y - r >= -1e-6 &&
				y + r <= innerHeight + 1e-6
			)
		}),
		`Plot dimensions: ${innerWidth} × ${innerHeight}; includes circle radii`,
	)
	check(
		"Y increases upward",
		yScale(d3.max(data, (d) => d.grdp)) < yScale(0),
		`y(0)=${yScale(0)}; y(max)=${yScale(d3.max(data, (d) => d.grdp))}`,
	)
	check(
		"Axes meet at zero baselines",
		plot.select(".x-axis").attr("transform") === `translate(0,${yScale(0)})` &&
			plot.select(".y-axis").attr("transform") === `translate(${xScale(0)},0)`,
		`x-axis y=${yScale(0)}; y-axis x=${xScale(0)}`,
	)
	check(
		"Dynamic domains cover data",
		xScale.domain()[1] >= d3.max(data, (d) => d.population) &&
			yScale.domain()[1] >= d3.max(data, (d) => d.grdp),
		`x domain [${xScale.domain()}]; y domain [${yScale.domain()}]`,
	)
	const reference = data[0]
	check(
		"Circle area is proportional to province area",
		circles.every((node) => {
			const d = node.__data__,
				r = +node.getAttribute("r")
			return near(
				(r * r) / areaScale(reference.area) ** 2,
				d.area / reference.area,
			)
		}),
		"Compared rendered radius² ratios against province area ratios",
	)
	const swatches = d3.selectAll("#density-legend .swatch").nodes()
	check(
		"Legend colors match marks",
		swatches.length === colors.length &&
			swatches.every(
				(n, i) =>
					d3.color(n.style.backgroundColor).formatHex() ===
					d3.color(colors[i]).formatHex(),
			) &&
			circles.every(
				(n) => n.getAttribute("fill") === densityColor(n.__data__.density),
			),
		"All four swatches and every circle use the same color mapping",
	)
	check(
		"Density boundary enters higher band",
		thresholds.every(
			(t, i) =>
				densityColor(t) === colors[i + 1] &&
				densityColor(t - 0.001) === colors[i],
		),
		"Checked just below and exactly at 100, 500, 1000",
	)
	check(
		"Adapted SVG size",
		+svg.attr("width") === 450 && +svg.attr("height") === 900,
		`${width} × ${height}`,
	)
	check(
		"Tooltip includes all five fields",
		circles.every((n) => {
			const text = n.querySelector("title").textContent
			return (
				text.includes(n.__data__.province) &&
				["Population:", "GRDP per person:", "Area:", "Density:"].every(
					(label) => text.includes(label),
				)
			)
		}),
		"Every circle has a native SVG hover tooltip with name and four measures",
	)
	if (testMode) {
		const low = data.find((d) => d.province === "Test Low"),
			medium = data.find((d) => d.province === "Test Medium")
		check(
			"Small-data order",
			data.every(
				(d, i) =>
					i === 0 ||
					(xScale(d.population) > xScale(data[i - 1].population) &&
						yScale(d.grdp) < yScale(data[i - 1].grdp)),
			),
			"Low → medium → high → maximum move right and upward",
		)
		check(
			"4× land area gives 4× circle area",
			near((areaScale(medium.area) / areaScale(low.area)) ** 2, 4),
			`Observed circle area ratio: ${(areaScale(medium.area) / areaScale(low.area)) ** 2}`,
		)
		check(
			"Maximum area gets maximum radius",
			near(areaScale(1600), 13),
			`r(1600)=${areaScale(1600)}`,
		)
	}
	console.table(results)
	const list = d3
		.select("#verification-results")
		.selectAll("li")
		.data(results)
		.join("li")
	list
		.text((d) => `${d.passed ? "PASS" : "FAIL"} — ${d.test}: ${d.evidence}`)
		.style("color", (d) => (d.passed ? "#245b2a" : "#b00020"))
	document.querySelector("#verification-summary").textContent =
		`${results.filter((d) => d.passed).length}/${results.length} checks passed.`
}
