// ==========================================
// Part A: Dynamic Bar Chart (H1 & H2)
// ==========================================
function drawBarChart(data) {
  const svg = d3.select("#bar-chart");
  svg.selectAll("*").remove(); // Clear previous DOM elements

  if (!data || data.length === 0) return;

  const width = 640, height = 300;
  const margin = { top: 25, right: 20, bottom: 30, left: 40 };
  const chartWidth = width - margin.left - margin.right;
  const chartHeight = height - margin.top - margin.bottom;

  svg.attr("width", width).attr("height", height);

  const g = svg.append("g")
               .attr("transform", `translate(${margin.left},${margin.top})`);

  // Scales
  const xScale = d3.scaleBand()
                   .domain(d3.range(data.length))
                   .range([0, chartWidth])
                   .padding(0.15);

  const maxVal = d3.max(data) || 100;
  const yScale = d3.scaleLinear()
                   .domain([0, maxVal])
                   .range([chartHeight, 0]);

  const avg = d3.mean(data) || 0;

  // H2: Opacity scale mapping data value to visual intensity
  const opacityScale = d3.scaleLinear()
                         .domain([0, maxVal])
                         .range([0.45, 1.0]);

  // Bars
  g.selectAll(".bar")
   .data(data)
   .enter()
   .append("rect")
   .attr("class", "bar")
   .attr("x", (d, i) => xScale(i))
   .attr("y", d => yScale(d))
   .attr("width", xScale.bandwidth())
   .attr("height", d => Math.max(0, chartHeight - yScale(d)))
   // Primary encoding: Color distinguishes above vs below average
   .attr("fill", d => d > avg ? "#e74c3c" : "#3498db")
   // H2: Second visual encoding (Opacity reflects value magnitude)
   .attr("opacity", d => opacityScale(d))
   // H2: Border highlights elements above average
   .attr("stroke", d => d > avg ? "#900c3f" : "#1b4f72")
   .attr("stroke-width", d => d > avg ? 2 : 0.5);

  // Labels
  g.selectAll(".label")
   .data(data)
   .enter()
   .append("text")
   .attr("class", "label")
   .attr("x", (d, i) => xScale(i) + xScale.bandwidth() / 2)
   .attr("y", d => Math.max(12, yScale(d) - 5))
   .attr("text-anchor", "middle")
   .attr("font-size", xScale.bandwidth() < 18 ? "9px" : "11px")
   .text(d => d);
}

// Initial dataset
const initialDataset = [
  7, 21, 3, 45, 12, 90, 4, 18, 63, 27,
  84, 36, 55, 9, 72, 41, 96, 14, 68, 30
];
drawBarChart(initialDataset);

// H1: Interactive Controls
document.getElementById("btn-randomize")?.addEventListener("click", () => {
  const count = Math.floor(Math.random() * 15) + 10;
  const randData = Array.from({ length: count }, () => Math.floor(Math.random() * 95) + 5);
  drawBarChart(randData);
});

document.getElementById("btn-small")?.addEventListener("click", () => {
  drawBarChart([7, 21, 3, 45, 12, 90, 4]);
});

document.getElementById("btn-large")?.addEventListener("click", () => {
  const largeData = Array.from({ length: 40 }, () => Math.floor(Math.random() * 100));
  drawBarChart(largeData);
});

// ==========================================
// Part B: Scatterplot (H3)
// ==========================================
const csvUrl = "vis-lab2-data.csv";

// CSV loading with strict zero check (fixing || bug)
d3.csv(csvUrl, d => ({
  id: d.Student_ID || d.Name || "unknown",
  midterm: d.Midterm !== undefined ? +d.Midterm : 0,
  final: d.Final !== undefined ? +d.Final : 0
})).then(data => {
  const validData = data.filter(d => !isNaN(d.midterm) && !isNaN(d.final));
  drawScatterplot(validData, 50);
}).catch(err => {
  console.error("Failed to load CSV:", err);
});

function drawScatterplot(data, failThreshold) {
  const svg = d3.select("#scatterplot");
  svg.selectAll("*").remove();

  const width = 520, height = 400;
  const margin = { top: 30, right: 30, bottom: 50, left: 50 };
  const innerW = width - margin.left - margin.right;
  const innerH = height - margin.top - margin.bottom;

  svg.attr("width", width).attr("height", height);
  const g = svg.append("g").attr("transform", `translate(${margin.left},${margin.top})`);

  const xScale = d3.scaleLinear().domain([0, 100]).range([0, innerW]);
  const yScale = d3.scaleLinear().domain([0, 100]).range([innerH, 0]);

  // H3: Radius scale mapping courseScore to circle size
  const rScale = d3.scaleLinear().domain([0, 100]).range([3.5, 9.5]);

  // Axes
  g.append("g").attr("transform", `translate(0, ${innerH})`).call(d3.axisBottom(xScale));
  g.append("g").call(d3.axisLeft(yScale));

  // Points
  g.selectAll("circle")
   .data(data)
   .enter()
   .append("circle")
   .attr("cx", d => xScale(d.midterm))
   .attr("cy", d => yScale(d.final))
   // H3: Circle radius represents course score
   .attr("r", d => {
     const score = 0.4 * d.midterm + 0.6 * d.final;
     return rScale(score);
   })
   // Fill color denotes pass/fail status
   .attr("fill", d => {
     const score = 0.4 * d.midterm + 0.6 * d.final;
     return score < failThreshold ? "#e74c3c" : "#2ecc71";
   })
   .attr("stroke", "#2c3e50")
   .attr("stroke-width", 0.7)
   .attr("opacity", 0.85);
}

// ==========================================
// Part C: Histogram (Clean Dimensions)
// ==========================================
function drawHistogram(data) {
  const svg = d3.select("#histogram");
  svg.selectAll("*").remove();

  const width = 640, height = 250;
  const margin = { top: 20, right: 20, bottom: 30, left: 40 };
  const innerW = width - margin.left - margin.right;
  const innerH = height - margin.top - margin.bottom;

  svg.attr("width", width).attr("height", height);
  const g = svg.append("g").attr("transform", `translate(${margin.left},${margin.top})`);

  const xScale = d3.scaleLinear().domain([0, 100]).range([0, innerW]);

  const histogramGen = d3.bin()
                         .domain(xScale.domain())
                         .thresholds(d3.range(0, 101, 10));

  const bins = histogramGen(data);

  const yScale = d3.scaleLinear()
                   .domain([0, d3.max(bins, d => d.length) || 1])
                   .nice()
                   .range([innerH, 0]);

  g.selectAll(".bin-rect")
   .data(bins)
   .enter()
   .append("rect")
   .attr("class", "bin-rect")
   .attr("x", d => xScale(d.x0) + 1)
   .attr("width", d => Math.max(0, xScale(d.x1) - xScale(d.x0) - 2))
   .attr("y", d => yScale(d.length))
   .attr("height", d => innerH - yScale(d.length))
   .attr("fill", "#9b59b6");

  g.append("g").attr("transform", `translate(0, ${innerH})`).call(d3.axisBottom(xScale));
  g.append("g").call(d3.axisLeft(yScale).ticks(5));
}

drawHistogram(initialDataset);