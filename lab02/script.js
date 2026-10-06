function drawBarChart(data) {
    const svg = d3.select("#bar-chart");
    svg.selectAll("*").remove(); // Xóa sạch khi vẽ lại dataset mới

    const width = 600, height = 300, margin = { top: 20, right: 20, bottom: 30, left: 40 };
    const chartWidth = width - margin.left - margin.right;
    const chartHeight = height - margin.top - margin.bottom;

    svg.attr("width", width).attr("height", height);

    const g = svg.append("g")
                .attr("transform", `translate(${margin.left},${margin.top})`);

    // Scales
    const xScale = d3.scaleBand()
                    .domain(d3.range(data.length))
                    .range([0, chartWidth])
                    .padding(0.1);

    const yScale = d3.scaleLinear()
                    .domain([0, d3.max(data) || 100])
                    .range([chartHeight, 0]);

    // Vẽ Bar
    g.selectAll(".bar")
    .data(data)
    .enter()
    .append("rect")
    .attr("class", "bar")
    .attr("x", (d, i) => xScale(i))
    .attr("y", d => yScale(d))
    .attr("width", xScale.bandwidth())
    .attr("height", d => chartHeight - yScale(d))
    .attr("fill", d => d > 50 ? "#e74c3c" : "#3498db");

    // Nhãn giá trị
    g.selectAll(".label")
        .data(data)
        .enter()
        .append("text")
        .attr("class", "label")
        .attr("x", (d, i) => xScale(i) + xScale.bandwidth() / 2)
        .attr("y", d => yScale(d) - 5)
        .attr("text-anchor", "middle")
        .attr("font-size", "11px")
        .text(d => d);
    }
const dataset = [
    7, 21, 3, 45, 12, 90, 4, 18, 63, 27,
    84, 36, 55, 9, 72, 41, 96, 14, 68, 30,
    51, 6, 77, 23, 88, 39, 11, 59, 34, 75
];
drawBarChart(dataset);

const csvUrl = "vis-lab2-data.csv";

d3.csv(csvUrl, d => ({
  name: d.Name || d.name,
  midterm: +d.Midterm || +d.midterm,
  final: +d.Final || +d.final
})).then(data => {
  drawScatterplot(data, 50);
});

function drawScatterplot(data, failThreshold) {
  const svg = d3.select("#scatterplot");
  svg.selectAll("*").remove();

  const width = 500, height = 400, margin = { top: 30, right: 30, bottom: 50, left: 50 };
  const innerW = width - margin.left - margin.right;
  const innerH = height - margin.top - margin.bottom;

  svg.attr("width", width).attr("height", height);
  const g = svg.append("g").attr("transform", `translate(${margin.left},${margin.top})`);

  const xScale = d3.scaleLinear().domain([0, 100]).range([0, innerW]);
  const yScale = d3.scaleLinear().domain([0, 100]).range([innerH, 0]);

  // Trục toạ độ
  g.append("g").attr("transform", `translate(0, ${innerH})`).call(d3.axisBottom(xScale));
  g.append("g").call(d3.axisLeft(yScale));

  // Vẽ các điểm
  g.selectAll("circle")
   .data(data)
   .enter()
   .append("circle")
   .attr("cx", d => xScale(d.midterm))
   .attr("cy", d => yScale(d.final))
   .attr("r", 5)
   .attr("fill", d => {
     const courseScore = 0.4 * d.midterm + 0.6 * d.final;
     return courseScore < failThreshold ? "#e74c3c" : "#2ecc71"; // Đỏ nếu trượt, xanh nếu đỗ
   })
   .attr("opacity", 0.8);
}


function drawHistogram(data) {
  const svg = d3.select("#histogram");
  svg.selectAll("*").remove();

  const width = 2000, height = 250, margin = { top: 20, right: 20, bottom: 30, left: 40 };
  const innerW = 300
  const innerH = 200;

  svg.attr("width", width).attr("height", height);
  const g = svg.append("g").attr("transform", `translate(${margin.left},${margin.top})`);

  const xScale = d3.scaleLinear()
                   .domain([0, 100])
                   .range([0, innerW]);

  const histogramGen = d3.bin()
                         .domain(xScale.domain())
                         .thresholds(d3.range(0, 101, 10));

  const bins = histogramGen(data);

  const yScale = d3.scaleLinear()
                   .domain([0, d3.max(bins, d => d.length)])
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
const dataset2 = [
    7, 21, 3, 45, 12, 90, 4, 18, 63, 27,
    84, 36, 55, 9, 72, 41, 96, 14, 68, 30,
    51, 6, 77, 23, 88, 39, 11, 59, 34, 75
];
drawHistogram(dataset2);