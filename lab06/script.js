const URL =
	"https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/" +
	"csse_covid_19_data/csse_covid_19_time_series/" +
	"time_series_covid19_confirmed_global.csv"

const COUNTRIES = ["Vietnam", "US", "France", "Italy"]
const START = new Date(2020, 3, 1) // 1 Apr 2020
const END = new Date(2020, 4, 1) // 1 May 2020 (inclusive)

const parseHeader = d3.timeParse("%m/%d/%y") // "4/1/20" -> Date
const fmtDate = d3.timeFormat("%d %b %Y")
const fmtTick = d3.timeFormat("%d %b")
const fmtInt = d3.format(",")

// Stable colors: tied to the country name, not to array order.
const color = d3
	.scaleOrdinal()
	.domain(COUNTRIES)
	.range(["#c8102e", "#177ca4", "#7a5cc2", "#e28b37"])

d3.csv(URL)
	.then((rows) => {
		// ---- Section 2: inspect the source before plotting --------------------
		console.log("Headers:", rows.columns.slice(0, 7))
		console.log(
			"Both dates?",
			rows.columns.includes("4/1/20"),
			rows.columns.includes("5/1/20"),
		)
		console.table(
			rows.filter((r) => COUNTRIES.includes(r["Country/Region"])).slice(0, 8),
		)

		const data = reshape(rows)
		drawLineChart(data.series)
		drawStackedArea(data.daily, data.negatives)
	})
	.catch((err) => {
		console.error(err)
		d3.select("#readout")
			.classed("error", true)
			.text("Could not load the CSV: " + err.message)
	})

// =========================================================================
// A. Clean and reshape: wide CSV -> { country, date, cases } records
// =========================================================================

// Returns a nonnegative number, or null for blank/invalid text.
// The test runs BEFORE Number(), because Number("") silently becomes 0.
function toCount(raw) {
	const text = (raw ?? "").trim()
	if (!/^\d+(\.\d+)?$/.test(text)) return null
	return Number(text)
}

function reshape(rows) {
	// Date headers are compared as Date objects, never as text
	// ("4/10/20" < "4/2/20" as strings, which would scramble the order).
	const dateCols = rows.columns
		.map((header) => ({ header, date: parseHeader(header) }))
		.filter((c) => c.date !== null)
		.sort((a, b) => a.date - b.date)

	const inRange = dateCols.filter((c) => c.date >= START && c.date <= END)
	// The day before the range is needed only to get daily-new cases on 1 Apr.
	const dayBefore = dateCols.find((c) => +c.date === +d3.timeDay.offset(START, -1))

	const invalid = []
	// Sum every province/region row of one country for one date column.
	const total = (countryRows, col) =>
		d3.sum(countryRows, (r) => {
			const n = toCount(r[col.header])
			if (n === null) {
				invalid.push({ country: r["Country/Region"], province: r["Province/State"], date: col.header, raw: r[col.header] })
				return 0
			}
			return n
		})

	// d3.group (D3 v7) replaces the obsolete d3.nest.
	const byCountry = d3.group(
		rows.filter((r) => COUNTRIES.includes(r["Country/Region"])),
		(r) => r["Country/Region"],
	)

	const tidy = []
	const baseline = new Map() // country -> cumulative cases on 31 Mar
	for (const country of COUNTRIES) {
		const countryRows = byCountry.get(country) ?? []
		console.log(`${country}: ${countryRows.length} source row(s) summed`)
		for (const col of inRange) {
			tidy.push({ country, date: col.date, cases: total(countryRows, col) })
		}
		baseline.set(country, dayBefore ? total(countryRows, dayBefore) : null)
	}

	// Group the tidy records into one series per country, dates ascending.
	const series = Array.from(
		d3.group(tidy, (d) => d.country),
		([name, values]) => ({ name, values: values.sort((a, b) => a.date - b.date) }),
	)

	// Daily new cases = today's cumulative − yesterday's cumulative.
	// A negative difference is a data revision, not "negative cases": clamp to 0
	// for the stacked chart and keep a list so the handling is documented.
	const negatives = []
	const daily = inRange.map((col, i) => {
		const row = { date: col.date }
		for (const s of series) {
			const prev = i === 0 ? baseline.get(s.name) : s.values[i - 1].cases
			const diff = prev === null ? 0 : s.values[i].cases - prev
			if (diff < 0) negatives.push({ country: s.name, date: fmtDate(col.date), change: diff })
			row[s.name] = Math.max(0, diff)
		}
		return row
	})

	// ---- Checks (V1) -------------------------------------------------------
	console.log("Dates kept:", inRange.length, "(expected 31)")
	console.log("Observations:", tidy.length, "(expected 4 × 31 = 124)")
	console.log("Blank/invalid cells:", invalid.length, invalid)
	const first = {},
		last = {}
	for (const s of series) {
		first[s.name] = s.values[0].cases
		last[s.name] = s.values.at(-1).cases
	}
	console.log("First day", fmtDate(inRange[0].date), first)
	console.log("Last day", fmtDate(inRange.at(-1).date), last)
	console.table(tidy.slice(0, 5))
	if (negatives.length) console.table(negatives)

	return { series, daily, negatives }
}

// =========================================================================
// B + C. Four lines, shared-date readout, legend hover + click-to-lock
// =========================================================================
function drawLineChart(series) {
	const width = 900,
		height = 440,
		margin = { top: 24, right: 28, bottom: 54, left: 74 }
	const innerW = width - margin.left - margin.right
	const innerH = height - margin.top - margin.bottom

	const svg = d3
		.select("#chart")
		.append("svg")
		.attr("viewBox", `0 0 ${width} ${height}`)
		.attr("role", "img")
		.attr("aria-label", "Line chart of cumulative confirmed COVID-19 cases for Vietnam, US, France and Italy, 1 April to 1 May 2020")
	const g = svg.append("g").attr("transform", `translate(${margin.left},${margin.top})`)

	const dates = series[0].values.map((d) => d.date) // shared by all series
	const x = d3.scaleTime().domain(d3.extent(dates)).range([0, innerW])
	const y = d3
		.scaleLinear()
		.domain([0, d3.max(series, (s) => d3.max(s.values, (d) => d.cases))])
		.nice()
		.range([innerH, 0])

	g.append("g").attr("class", "grid").call(d3.axisLeft(y).ticks(6).tickSize(-innerW).tickFormat(""))
	g.append("g")
		.attr("class", "axis")
		.attr("transform", `translate(0,${innerH})`)
		.call(d3.axisBottom(x).ticks(d3.timeDay.every(3)).tickFormat(fmtTick))
	g.append("g").attr("class", "axis").call(d3.axisLeft(y).ticks(6).tickFormat(d3.format("~s")))
	g.append("text")
		.attr("class", "axis-label")
		.attr("x", innerW / 2)
		.attr("y", innerH + 44)
		.attr("text-anchor", "middle")
		.text("Date (daily, 2020)")
	g.append("text")
		.attr("class", "axis-label")
		.attr("transform", "rotate(-90)")
		.attr("x", -innerH / 2)
		.attr("y", -54)
		.attr("text-anchor", "middle")
		.text("Cumulative confirmed cases (people)")

	// One <path> per COUNTRY (province rows were already summed).
	const line = d3
		.line()
		.x((d) => x(d.date))
		.y((d) => y(d.cases))
	const paths = g
		.selectAll("path.series")
		.data(series, (d) => d.name)
		.join("path")
		.attr("class", "series")
		.attr("stroke", (d) => color(d.name))
		.attr("d", (d) => line(d.values))
	console.log("Paths drawn:", paths.size(), "(expected 4)")

	// ---- Legend: temporary hover vs. locked selection -----------------------
	// hovered: lasts only while the pointer/keyboard focus is on a legend item.
	// locked:  set by click, survives pointerleave until changed or cleared.
	let hovered = null
	let locked = null

	const legend = d3.select("#legend")
	const items = legend
		.selectAll("button.country")
		.data(series, (d) => d.name)
		.join("button")
		.attr("type", "button")
		.attr("class", "country")
	items.append("span").attr("class", "swatch").style("background", (d) => color(d.name))
	items.append("span").text((d) => d.name)
	items.append("span").attr("class", "lock-state")
	const showAll = legend.append("button").attr("type", "button").attr("class", "show-all").text("Show all")

	const dots = g
		.selectAll("circle.dot")
		.data(series, (d) => d.name)
		.join("circle")
		.attr("class", "dot")
		.attr("r", 4.5)
		.attr("fill", (d) => color(d.name))
		.style("display", "none")

	function applyFocus() {
		const active = hovered ?? locked // hover wins while it lasts
		const isDim = (d) => active !== null && d.name !== active
		// Only classes change — no series is filtered out or removed.
		paths.classed("dim", isDim).classed("focus", (d) => d.name === active)
		dots.classed("dim", isDim)
		items
			.classed("dim", isDim)
			.classed("locked", (d) => d.name === locked)
			.attr("aria-pressed", (d) => d.name === locked)
		items.select(".lock-state").text((d) => (d.name === locked ? "(locked)" : ""))
		showAll.property("disabled", locked === null)
		d3.selectAll("#readout .value").classed("dim", function () {
			return active !== null && this.dataset.country !== active
		})
	}

	items
		.on("pointerenter focus", (event, d) => {
			hovered = d.name
			applyFocus()
		})
		.on("pointerleave blur", () => {
			hovered = null // falls back to the locked country, or to all four
			applyFocus()
		})
		.on("click", (event, d) => {
			locked = locked === d.name ? null : d.name // same again = unlock
			applyFocus()
		})
	showAll.on("click", () => {
		locked = null
		hovered = null
		applyFocus()
	})
	d3.select(window).on("keydown.unlock", (event) => {
		if (event.key === "Escape") {
			locked = null
			applyFocus()
		}
	})

	// ---- Shared-date readout -------------------------------------------------
	const readout = d3.select("#readout")
	const idleText = "Move over the chart to see the four values for one date."
	readout.text(idleText)

	const guide = g.append("line").attr("class", "guide").attr("y1", 0).attr("y2", innerH).style("display", "none")
	dots.raise()
	const bisect = d3.bisector((d) => d).center // nearest date, not "next" date

	g.append("rect")
		.attr("width", innerW)
		.attr("height", innerH)
		.attr("fill", "transparent")
		.style("cursor", "crosshair")
		.on("pointermove", function (event) {
			const [px] = d3.pointer(event, this)
			const pointerDate = x.invert(Math.max(0, Math.min(innerW, px)))
			// ONE index, computed once, is reused for all four countries,
			// so the readout can never mix two different dates.
			const i = bisect(dates, pointerDate)
			const date = dates[i]

			guide.style("display", null).attr("x1", x(date)).attr("x2", x(date))
			dots
				.style("display", null)
				.attr("cx", x(date))
				.attr("cy", (s) => y(s.values[i].cases))

			const parts = series.map(
				(s) =>
					`<span class="value" data-country="${s.name}">` +
					`<span class="swatch" style="background:${color(s.name)}"></span>` +
					`${s.name}: <strong>${fmtInt(s.values[i].cases)}</strong></span>`,
			)
			readout.html(`<strong>${fmtDate(date)}</strong><div class="values">${parts.join("")}</div>`)
			applyFocus()
		})
		.on("pointerleave", () => {
			guide.style("display", "none")
			dots.style("display", "none")
			readout.text(idleText)
		})

	applyFocus()
}

// =========================================================================
// Optional extension: stacked area of DAILY NEW cases
// =========================================================================
function drawStackedArea(daily, negatives) {
	const width = 900,
		height = 380,
		margin = { top: 20, right: 28, bottom: 54, left: 74 }
	const innerW = width - margin.left - margin.right
	const innerH = height - margin.top - margin.bottom

	const svg = d3
		.select("#area-chart")
		.append("svg")
		.attr("viewBox", `0 0 ${width} ${height}`)
		.attr("role", "img")
		.attr("aria-label", "Stacked area chart of daily new confirmed COVID-19 cases for Vietnam, US, France and Italy")
	const g = svg.append("g").attr("transform", `translate(${margin.left},${margin.top})`)

	// Every row has all four keys for the same date, so the layers are aligned.
	const layers = d3.stack().keys(COUNTRIES)(daily)
	const x = d3.scaleTime().domain(d3.extent(daily, (d) => d.date)).range([0, innerW])
	const y = d3
		.scaleLinear()
		.domain([0, d3.max(layers.at(-1), (d) => d[1])])
		.nice()
		.range([innerH, 0])

	g.append("g").attr("class", "grid").call(d3.axisLeft(y).ticks(5).tickSize(-innerW).tickFormat(""))

	const area = d3
		.area()
		.x((d) => x(d.data.date))
		.y0((d) => y(d[0]))
		.y1((d) => y(d[1]))
	g.selectAll("path.layer")
		.data(layers, (d) => d.key)
		.join("path")
		.attr("class", "layer")
		.attr("fill", (d) => color(d.key))
		.attr("d", area)
		.append("title")
		.text((d) => d.key)

	g.append("g")
		.attr("class", "axis")
		.attr("transform", `translate(0,${innerH})`)
		.call(d3.axisBottom(x).ticks(d3.timeDay.every(3)).tickFormat(fmtTick))
	g.append("g").attr("class", "axis").call(d3.axisLeft(y).ticks(5).tickFormat(d3.format("~s")))
	g.append("text")
		.attr("class", "axis-label")
		.attr("x", innerW / 2)
		.attr("y", innerH + 44)
		.attr("text-anchor", "middle")
		.text("Date (daily, 2020)")
	g.append("text")
		.attr("class", "axis-label")
		.attr("transform", "rotate(-90)")
		.attr("x", -innerH / 2)
		.attr("y", -54)
		.attr("text-anchor", "middle")
		.text("Daily new cases (stacked total)")

	d3.select("#area-note").text(
		negatives.length
			? `Negative revisions clamped to 0: ` +
					negatives.map((n) => `${n.country} ${n.date} (${fmtInt(n.change)})`).join("; ") +
					"."
			: "No negative daily changes occurred in this range.",
	)
}
