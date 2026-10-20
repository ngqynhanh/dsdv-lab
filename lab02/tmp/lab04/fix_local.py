from pathlib import Path
import json
root=Path(r'D:\Documents\# Documents\# UNI\Year 3 -  Sem 1\Data Science and Data Visualization\Lab\lab04\lab04-d3')
csv=(root/'vn-provinces-data.csv').read_text(encoding='utf-8-sig')
(root/'data.js').write_text('// Local copy of vn-provinces-data.csv; original source: https://tungth.github.io/data/vn-provinces-data.csv\nwindow.LAB4_CSV = '+json.dumps(csv,ensure_ascii=False)+';\n',encoding='utf-8')
p=root/'index.html'
s=p.read_text(encoding='utf-8')
if 'src="data.js"' not in s:
 s=s.replace('<script defer src="chart.js"></script>','<script defer src="data.js"></script>\n\t\t<script defer src="chart.js"></script>')
p.write_text(s,encoding='utf-8')
p=root/'chart.js';s=p.read_text(encoding='utf-8')
s=s.replace('d3.csv("vn-provinces-data.csv")','Promise.resolve().then(() => {\n\tif (typeof window.LAB4_CSV !== "string") throw new Error("Không tìm thấy data.js. Đặt data.js cùng thư mục index.html.");\n\treturn d3.csvParse(window.LAB4_CSV);\n})')
p.write_text(s,encoding='utf-8')
p=root/'NOTES.md';s=p.read_text(encoding='utf-8')
s=s.replace('Không mở HTML bằng `file://` vì trình duyệt có thể chặn đọc CSV.', 'Có thể mở trực tiếp `index.html` bằng `file://`: `data.js` chứa nguyên nội dung CSV local, được phân tích bằng `d3.csvParse`, không dùng fetch. Local web server vẫn là cách chạy theo hướng dẫn của đề.')
s+='\n\n## Cập nhật đọc dữ liệu local\n\n`index.html` nạp `d3.v7.min.js` → `data.js` → `chart.js`. `data.js` chứa nguyên nội dung `vn-provinces-data.csv`; không gọi mạng để lấy dữ liệu. Nếu chỉnh CSV, cần cập nhật chuỗi `window.LAB4_CSV` trong `data.js` tương ứng. Mở bản HTML trong thư mục `lab04-d3`.\n'
p.write_text(s,encoding='utf-8')
print(root)
