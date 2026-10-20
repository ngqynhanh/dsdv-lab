// Nguồn: https://tungth.github.io/data/vn-provinces-data.csv
// Đọc CSV local bằng d3.csv(); mở index.html qua Live Server.
// Cách join(enter, update, exit) theo Pre-lab Demo 2 và Demo 3.

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

  // Giống Demo 2 và 3: bind dữ liệu theo mã tỉnh, rồi join 3 nhánh.
  let exitBars;
  const bars = rowsGroup.selectAll("rect.bar")
    .data(data, d => d.id)
    .join(
      enter => enter.append("rect")
        .attr("class", "bar").attr("data-id", d => d.id)
        .attr("x", 0).attr("y", d => y(d.id)).attr("width", 0),
      update => update,
      exit => {
        exitBars = exit.transition(t).attr("width", 0).style("opacity", 0).remove();
      }
    )
    .transition(t)
    .attr("y", d => y(d.id))
    .attr("width", d => x(d.value))
    .attr("height", y.bandwidth())
    .on("start", function () { d3.select(this).classed("changing", true); })
    .on("end", function () { d3.select(this).classed("changing", false); });

  // Tên tỉnh bên trái, cũng dùng key để di chuyển đúng tỉnh khi sort.
  let exitNames;
  const names = rowsGroup.selectAll("text.province-label")
    .data(data, d => d.id)
    .join(
      enter => enter.append("text")
        .attr("class", "province-label")
        .attr("x", -12).attr("y", d => y(d.id) + y.bandwidth() / 2)
        .attr("text-anchor", "end").attr("dominant-baseline", "middle"),
      update => update,
      exit => { exitNames = exit.transition(t).style("opacity", 0).remove(); }
    )
    .text(d => d.name)
    .transition(t)
    .attr("y", d => y(d.id) + y.bandwidth() / 2);

  // Giá trị bên phải đầu thanh.
  let exitValues;
  const values = rowsGroup.selectAll("text.value-label")
    .data(data, d => d.id)
    .join(
      enter => enter.append("text")
        .attr("class", "value-label").attr("x", 7)
        .attr("y", d => y(d.id) + y.bandwidth() / 2)
        .attr("dominant-baseline", "middle"),
      update => update,
      exit => { exitValues = exit.transition(t).style("opacity", 0).remove(); }
    )
    .text(d => d.value.toFixed(2))
    .transition(t)
    .attr("x", d => x(d.value) + 7)
    .attr("y", d => y(d.id) + y.bandwidth() / 2);

  // Lab có nhiều thành phần hơn demo: đợi tất cả xong mới mở lại nút.
  await Promise.all([resize, axisMove, bars, names, values, exitBars, exitNames, exitValues]
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
  d3.select("#status").text(`Lỗi: ${error.message}. Mở index.html bằng Live Server; không mở bằng file://.`);
}

// 5. Đọc CSV local và kiểm tra dữ liệu trước khi vẽ.
d3.csv("vn-provinces-data.csv").then(raw => {
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
}).catch(showError);
