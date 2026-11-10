"use strict"

// STEP 1: Density bands control the selector and highlighting.
const thresholds = [100, 500, 1000]
const categories = [
	{ label: "< 100" },
	{ label: "100 to < 500" },
	{ label: "500 to < 1,000" },
	{ label: "≥ 1,000" },
]
// bisectRight counts thresholds <= density: 499 -> band 1, 500 -> band 2.
function densityBand(density) {
	return d3.bisectRight(thresholds, density)
}

const status = document.querySelector("#status")
const selector = document.querySelector("#density-category")

// STEP 2: Parse the same CSV in either direct-file or HTTP mode.
async function start() {
	try {
		if (typeof d3 === "undefined")
			throw new Error("Local D3 library is missing.")
		const rows =
			location.protocol === "file:"
				? d3.csvParse(window.PROVINCE_CSV)
				: await d3.csv("vn-provinces-data.csv")
		console.log("CSV headers:", rows.columns)
		console.table(rows.slice(0, 2))
		const required = ["province", "population", "GRDP-VND", "area", "density"]
		if (required.some((key) => !rows.columns.includes(key)))
			throw new Error("Missing required CSV columns.")
		const number = (value) => (value.trim() === "" ? NaN : Number(value))
		const converted = rows.map((row) => ({
			province: row.province.trim(),
			population: number(row.population),
			grdp: number(row["GRDP-VND"].replace(",", ".")),
			area: number(row.area),
			density: number(row.density),
		}))
		const valid = (d) =>
			d.province &&
			d.area > 0 &&
			[d.population, d.grdp, d.area, d.density].every(
				(n) => Number.isFinite(n) && n >= 0,
			)
		const data = converted.filter(valid)
		const rejected = converted.filter((d) => !valid(d))
		if (rejected.length) console.warn("Invalid rows excluded:", rejected)
		if (!data.length) throw new Error("No valid province records.")
		console.table(data.slice(0, 2))
		draw(data, rejected.length)
	} catch (error) {
		status.classList.add("error")
		status.textContent = `Unable to draw chart: ${error.message}`
		console.error(error)
	}
}

function draw(data, rejectedCount) {
	// STEP 3: Calculate the unweighted mean GRDP of the valid provinces.
	const meanGRDP = d3.mean(data, (d) => d.grdp)
	const meanCategories = [
		{ label: "Above mean GRDP", color: "#4477AA" },
		{ label: "Below mean GRDP", color: "#EEAA33" },
		{ label: "Equal to mean GRDP", color: "#777777" },
	]
	const meanCategory = (grdp) =>
		grdp > meanGRDP ? 0 : grdp < meanGRDP ? 1 : 2
	// Preserve position, area encodings and the Section 10 dimensions.
	const width = 450,
		height = 900
	const margin = { top: 24, right: 18, bottom: 62, left: 64 }
	const innerWidth = width - margin.left - margin.right
	const innerHeight = height - margin.top - margin.bottom
	const maxRadius = 13
	const xScale = d3
		.scaleLinear()
		.domain([0, d3.max(data, (d) => d.population) || 1])
		.nice()
		.range([maxRadius, innerWidth - maxRadius])
	const yScale = d3
		.scaleLinear()
		.domain([0, d3.max(data, (d) => d.grdp) || 1])
		.nice()
		.range([innerHeight - maxRadius, maxRadius])
	const areaScale = d3
		.scaleSqrt()
		.domain([0, d3.max(data, (d) => d.area)])
		.range([0, maxRadius])
	// Zero provides meaningful baselines; radius² remains proportional to area.
	const svg = d3.select("#chart").attr("width", width).attr("height", height)
	const plot = svg
		.append("g")
		.attr("transform", `translate(${margin.left},${margin.top})`)
	const circles = plot
		.append("g")
		.attr("class", "provinces")
		.selectAll("circle")
		.data([...data].sort((a, b) => b.area - a.area))
		.join("circle")
		.attr("data-province", (d) => d.province)
		.attr("cx", (d) => xScale(d.population))
		.attr("cy", (d) => yScale(d.grdp))
		.attr("r", (d) => areaScale(d.area))
		.attr("fill", (d) => meanCategories[meanCategory(d.grdp)].color)

	// Use the same y-scale as the circles to locate the mean reference line.
	const meanY = yScale(meanGRDP)
	plot
		.append("line")
		.attr("class", "mean-line")
		.attr("x1", xScale(0))
		.attr("x2", innerWidth)
		.attr("y1", meanY)
		.attr("y2", meanY)
		.attr("stroke", "#333")
		.attr("stroke-width", 1.5)
		.attr("stroke-dasharray", "6,4")
	plot
		.append("text")
		.attr("class", "mean-label")
		.attr("x", innerWidth - 4)
		.attr("y", meanY - 8)
		.attr("text-anchor", "end")
		.attr("font-size", 12)
		.attr("fill", "#333")
		.attr("stroke", "white")
		.attr("stroke-width", 3)
		.attr("paint-order", "stroke")
		.text(`Mean GRDP: ${d3.format(",.2f")(meanGRDP)}`)

	plot
		.append("g")
		.attr("class", "x-axis")
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
		.attr("class", "y-axis")
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

	// STEP 4: Explain the GRDP colors and build the density selector.
	const legend = d3
		.select("#legend")
		.selectAll("li")
		.data(meanCategories)
		.join("li")
	legend
		.append("span")
		.attr("class", "swatch")
		.style("background", (d) => d.color)
	legend.append("span").text((d) => d.label)
	d3.select(selector)
		.append("option")
		.attr("value", "all")
		.text("All provinces")
	categories.forEach((category, index) => {
		d3.select(selector)
			.append("option")
			.attr("value", index)
			.text(category.label)
	})

	// STEP 5 — THE NEW FEATURE: only opacity and outline change on selection.
	// We never filter the data or change cx, cy, radius, fill hue or scale domains.
	function highlightCategory() {
		const selected = selector.value
		const matches = (d) =>
			selected === "all" || densityBand(d.density) === Number(selected)
		circles
			.attr("data-highlighted", (d) => String(matches(d)))
			.attr("fill-opacity", (d) => (matches(d) ? 0.8 : 0.12))
			.attr("stroke", (d) => (matches(d) ? "#111" : "#888"))
			.attr("stroke-opacity", (d) => (matches(d) ? 1 : 0.25))
			.attr("stroke-width", (d) =>
				selected !== "all" && matches(d) ? 2 : 0.65,
			)
		const count = data.filter(matches).length
		status.textContent = `${count} of ${data.length} provinces highlighted · ${rejectedCount} invalid rows excluded`
	}
	selector.disabled = false
	selector.addEventListener("change", highlightCategory)
	highlightCategory()
}

start()
