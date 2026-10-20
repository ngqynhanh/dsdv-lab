// Nguồn: https://tungth.github.io/data/vn-provinces-data.csv
// data.js chứa CSV local, nên mở trực tiếp index.html cũng chạy được.

// 1. Kích thước và vùng vẽ
const duration = 700;
const margin = { top: 72, right: 90, bottom: 24, left: 170 };
const width = 1040;
const chartWidth = width - margin.left - margin.right;
const svg = d3.select("#chart");
const chart = svg.append("g")
  .attr("transform", `translate(${margin.left},${margin.top})`);
const axis = chart.append("g").attr("class", "axis");
const rowsGroup = chart.append("g");
const x = d3.scaleLinear().range([0, chartWidth]);
const y = d3.scaleBand().padding(0.23);

chart.append("text")
  .attr("class", "axis-title")
  .attr("x", chartWidth / 2).attr("y", -45)
  .attr("text-anchor", "middle")
  .text("GRDP-VND (đơn vị chi tiết và năm không được ghi trong CSV)");

// 2. Trạng thái: dữ liệu gốc, các tỉnh đang chọn, tỉnh vừa xóa
let allRecords = [];
let active = [];
let removed = null;
let busy = false;

function updateButtons() {
  d3.select("#add").property("disabled", busy || active.length === allRecords.length);
  d3.select("#remove").property("disabled", busy || active.length <= 1);
  d3.select("#undo").property("disabled", busy || removed === null);
  d3.select("#sort-select").property("disabled", busy || active.length === 0);
  d3.select("#count").text(`${active.length} / ${allRecords.length} tỉnh`);
}

// 3. Vẽ lại khi thêm, xóa, undo hoặc sắp xếp
async function render() {
  busy = true;
  updateButtons();
  d3.select("#status").text("Đang chuyển động…");

  // Chỉ sort bản sao. active luôn giữ thứ tự thêm từ nguồn.
  const data = active.slice();
  const sort = d3.select("#sort-select").property("value");
  if (sort === "name") data.sort((a, b) => a.name.localeCompare(b.name, "vi"));
  if (sort === "grdp") data.sort((a, b) => b.value - a.value);

  const height = data.length * 30;
  x.domain([0, d3.max(data, d => d.value) || 1]).nice();
  y.domain(data.map(d => d.id)).range([0, height]);
  const t = svg.transition().duration(duration);
  const resize = t.attr("height", height + margin.top + margin.bottom);
  const axisMove = axis.transition(t)
    .call(d3.axisTop(x).ticks(7).tickSize(-height).tickPadding(8));

  // Key là mã tỉnh: sort không tạo lại node của tỉnh đó.
  const rows = rowsGroup.selectAll("g.row").data(data, d => d.id);

  // EXIT: thu thanh, làm mờ hàng rồi xóa khỏi DOM.
  const exitBars = rows.exit().select("rect").transition(t).attr("width", 0);
  const exitRows = rows.exit().transition(t).style("opacity", 0).remove();

  // ENTER: mỗi hàng mới chứa thanh, tên tỉnh và nhãn giá trị.
  const enter = rows.enter().append("g")
    .attr("class", "row").attr("data-id", d => d.id)
    .attr("transform", d => `translate(0,${y(d.id)})`)
    .style("opacity", 0);
  enter.append("rect").attr("class", "bar").attr("width", 0);
  enter.append("text").attr("class", "province-label")
    .attr("x", -12).attr("text-anchor", "end")
    .attr("dominant-baseline", "middle").text(d => d.name);
  enter.append("text").attr("class", "value-label")
    .attr("x", 7).attr("dominant-baseline", "middle")
    .text(d => d.value.toFixed(2));

  // UPDATE: dùng chung cho hàng mới và hàng đã có.
  const allRows = enter.merge(rows).order();
  const moveRows = allRows.transition(t).style("opacity", 1)
    .attr("transform", d => `translate(0,${y(d.id)})`);
  const bars = allRows.select("rect").transition(t)
    .attr("width", d => x(d.value)).attr("height", y.bandwidth())
    .on("start", function () { d3.select(this).classed("changing", true); })
    .on("end", function () { d3.select(this).classed("changing", false); });
  const names = allRows.select(".province-label").transition(t)
    .attr("y", y.bandwidth() / 2);
  const values = allRows.select(".value-label").transition(t)
    .attr("x", d => x(d.value) + 7).attr("y", y.bandwidth() / 2);

  // Đợi mọi chuyển động xong mới cho bấm tiếp, tránh lỗi bấm liên tục.
  await Promise.all([resize, axisMove, exitBars, exitRows, moveRows, bars, names, values]
    .map(animation => animation.end()));
  busy = false;
  updateButtons();
  d3.select("#status").text(`Đang hiển thị ${active.length} tỉnh. Thanh màu cam khi chuyển động.`);
}

// 4. Mỗi nút có một handler riêng, dễ theo dõi.
d3.select("#add").on("click", function () {
  if (busy || active.length === allRecords.length) return;
  // active là các tỉnh đầu nguồn; tỉnh tiếp theo nằm ở index active.length.
  active.push(allRecords[active.length]);
  removed = null; // Add đã khôi phục tỉnh vừa xóa, không cho Undo trùng.
  render().catch(showError);
});

d3.select("#remove").on("click", function () {
  if (busy || active.length <= 1) return;
  removed = active.pop(); // Xóa tỉnh thêm gần nhất, không phải thanh dưới cùng.
  render().catch(showError);
});

d3.select("#undo").on("click", function () {
  if (busy || removed === null) return;
  active.push(removed); // Tỉnh bị xóa vốn nằm cuối active.
  removed = null; // Chỉ Undo một lần.
  render().catch(showError);
});

d3.select("#sort-select").on("change", function () {
  if (!busy) render().catch(showError);
});

function showError(error) {
  console.error(error);
  busy = true;
  updateButtons();
  d3.select("#status").text(`Lỗi: ${error.message}`);
}

// 5. Đọc CSV local và kiểm tra dữ liệu trước khi vẽ.
try {
  if (typeof window.LAB4_CSV !== "string") throw new Error("Thiếu file data.js.");
  const raw = d3.csvParse(window.LAB4_CSV);
  console.log("CSV headers:", raw.columns);
  console.table(raw.slice(0, 3));
  for (const field of ["ma", "province", "GRDP-VND"]) {
    if (!raw.columns.includes(field)) throw new Error(`Thiếu cột ${field}`);
  }

  const ids = new Set();
  const excluded = [];
  for (const row of raw) {
    const id = row.ma.trim();
    const name = row.province.trim();
    const number = row["GRDP-VND"].trim().replace(",", ".");
    const value = number === "" ? NaN : Number(number);
    if (id && ids.has(id)) throw new Error(`Trùng mã tỉnh ${id}`);
    if (id) ids.add(id);
    if (!id || !name || !Number.isFinite(value) || value < 0) {
      excluded.push(row);
    } else {
      allRecords.push({ id, name, value });
    }
  }
  console.log("Dòng bị loại:", excluded.length);
  console.table(excluded);
  if (allRecords.length === 0) throw new Error("Không có dữ liệu hợp lệ.");
  active = allRecords.slice(0, 20);
  render().catch(showError);
} catch (error) {
  showError(error);
}
