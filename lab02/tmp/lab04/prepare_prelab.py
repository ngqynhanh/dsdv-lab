from pathlib import Path
root=Path(r'D:\Documents\# Documents\# UNI\Year 3 -  Sem 1\Data Science and Data Visualization\Lab\lab04\lab04-d3')
s=(root/'chart.js').read_text(encoding='utf-8-sig')
s=s.replace('// data.js chứa CSV local, nên mở trực tiếp index.html cũng chạy được.', '// Đọc CSV local bằng d3.csv(); mở index.html qua Live Server.\n// Cách join(enter, update, exit) theo Pre-lab Demo 2 và Demo 3.')
a=s.index('  // Key là mã tỉnh:')
b=s.index('  busy = false;',a)
s=s[:a]+'''  // Giống Demo 2 và 3: bind dữ liệu theo mã tỉnh, rồi join 3 nhánh.
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
''' +s[b:]
s=s.replace('try {\n  const raw = "vn-provinces-data.csv" in window ? d3.csvParse(window["vn-provinces-data.csv"]) : d3.csvParse(window.LAB4_CSV);', 'd3.csv("vn-provinces-data.csv").then(raw => {')
s=s.replace('} catch (error) {\n  showError(error);\n}', '}).catch(showError);')
s=s.replace('`Lỗi: ${error.message}`', '`Lỗi: ${error.message}. Mở index.html bằng Live Server; không mở bằng file://.`')
Path('tmp/lab04/chart-prelab.js').write_text(s,encoding='utf-8')
