const URL =
    "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/" +
    "csse_covid_19_data/csse_covid_19_time_series/" +
    "time_series_covid19_confirmed_global.csv";

const DATE = "4/5/20";

const width = 800;
const height = 700;
const margin = { top: 40, right: 40, bottom: 60, left: 70 };

const innerW = width - margin.left - margin.right;
const innerH = height - margin.top - margin.bottom;

const svg = d3.select("#chart")
    .attr("viewBox", `0 0 ${width} ${height}`);

const g = svg.append("g")
    .attr("transform", `translate(${margin.left}, ${margin.top})`);

const tooltip = d3.select("#tooltip")
const status = d3.select("#status")
function content(d) {
    return `<strong>${d.country}</strong>
        ${d.province ? `<br>${d.province}` : ""}
        <br>Latitude: ${d.lat}
        <br>Longitude: ${d.long}
        <br>Confirmed cases (5 April 2020): ${d.value.toLocaleString()}`;
}
// why do we need all three functions? answer: showTooltip displays the tooltip and highlights the circle, moveTooltip updates the position of the tooltip as the pointer moves, and hideTooltip hides the tooltip and resets the circle's appearance when the pointer leaves.
function showTooltip(event, d) {
    tooltip.html(content(d)).style("display", "block")
    status.text(`${d.country}: ${d.value} confirmed cases`)
    d3.select(event.currentTarget)
        .attr("stroke", "#eea638")
        .attr("stroke-width", 4)
    moveTooltip(event)
}
function moveTooltip(event) {
    // Page-based coordinates for a position:fixed tooltip (clientX, clientY).
    tooltip
        .style(
            "left",
            `${Math.min(event.clientX + 15, window.innerWidth - 240)}px`,
        )
        .style("top", `${Math.max(10, event.clientY - 50)}px`)
}
function hideTooltip(event) {
    tooltip.style("display", "none")
    d3.select(event.currentTarget)
        .attr("stroke", "#fff")
        .attr("stroke-width", 2)
    status.text("Move over a circle.")
}

function rowConverter(d) {
    // Check blanks before Number(), because Number("") is 0.
    const required = [d.Lat, d.Long, d[DATE]];

    if (required.some(value =>
        value == null || value.trim() === ""
    )) {
        return null;
    }

    const lat = Number(d.Lat);
    const long = Number(d.Long);
    const value = Number(d[DATE]);

    if (
        !Number.isFinite(lat) ||
        !Number.isFinite(long) ||
        !Number.isFinite(value) ||
        lat < -90 || lat > 90 ||
        long < -180 || long > 180 ||
        value < 0
    ) {
        return null;
    }

    return {
        country: d["Country/Region"],
        province: d["Province/State"],
        lat,
        long,
        value
    };
}

d3.csv(URL).then(function (rows) {
    if (!rows.columns.includes(DATE)) {
        throw new Error(`Missing date column: ${DATE}`);
    }

    const data = rows.map(rowConverter).filter(d => d !== null);

    console.log({
        loaded: rows.length,
        valid: data.length,
        excluded: rows.length - data.length
    });
    console.table(data.slice(0, 3));

    // Longitude controls horizontal position.
    const x = d3.scaleLinear()
        .domain([-180, 180])
        .range([0, innerW]);

    // Reverse the range so north appears above south.
    const y = d3.scaleLinear()
        .domain([-90, 90])
        .range([innerH, 0]);

    // Cases control radius through a square-root scale.
    const radius = d3.scaleSqrt()
        .domain([0, d3.max(data, d => d.value) || 1])
        .range([0, 60]);

    g.append("g")
        .attr("transform", `translate(0, ${innerH})`)
        .call(d3.axisBottom(x).ticks(9));

    g.append("g")
        .call(d3.axisLeft(y).ticks(7));

    g.selectAll("circle")
        .data(data)
        .join("circle")
        .attr("cx", d => x(d.long))
        .attr("cy", d => y(d.lat))
        .attr("r", d => radius(d.value))
        .attr("fill", "steelblue")
        .attr("fill-opacity", 0.5)
        .attr("stroke", "white")
        .on("pointerenter", showTooltip)
        .on("pointermove", moveTooltip)
        .on("pointerleave", hideTooltip)
        .on("focus", function (event, d) {
            status.text(`${d.name}: ${d.visitors} visitors (keyboard)`)
            d3.select(this).attr("stroke", "#eea638")
        })
        .on("blur", function () {
            status.text("Move over a circle.")
            d3.select(this).attr("stroke", "#fff")
        });

    svg.append("text")
        .attr("x", width / 2)
        .attr("y", 22)
        .attr("text-anchor", "middle")
        .text("Confirmed COVID-19 cases — 5 April 2020");

    svg.append("text")
        .attr("x", margin.left + innerW / 2)
        .attr("y", height - 15)
        .attr("text-anchor", "middle")
        .text("Longitude (degrees)");

    svg.append("text")
        .attr("transform", "rotate(-90)")
        .attr("x", -(margin.top + innerH / 2))
        .attr("y", 20)
        .attr("text-anchor", "middle")
        .text("Latitude (degrees)");

    
}).catch(function (error) {
    console.error("CSV/chart failed:", error);
});

