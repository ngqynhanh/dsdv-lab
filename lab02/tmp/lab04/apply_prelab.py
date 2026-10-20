from pathlib import Path
root=Path(r'D:\Documents\# Documents\# UNI\Year 3 -  Sem 1\Data Science and Data Visualization\Lab\lab04\lab04-d3')
(root/'chart.js').write_text(Path('tmp/lab04/chart-prelab.js').read_text(encoding='utf-8'),encoding='utf-8')
p=root/'index.html';s=p.read_text(encoding='utf-8');s=s.replace('\t\t<script defer src="data.js"></script>\n','');p.write_text(s,encoding='utf-8')
p=root/'data.js'
if p.exists(): p.unlink()
p=root/'NOTES.md';s=p.read_text(encoding='utf-8')
a=s.index('Có thể mở trực tiếp');b=s.index('\n',a)
s=s[:a]+'Phải chạy qua local web server hoặc VS Code Live Server. Không mở bằng `file://`: `d3.csv("vn-provinces-data.csv")` đọc trực tiếp file CSV qua HTTP. D3 lưu local nên không cần Internet.'+s[b:]
s=s.replace('Mỗi `g.row` chứa thanh, nhãn tỉnh và nhãn số; stable key của nhóm bảo toàn danh tính cho cả ba thành phần.', 'Thanh, tên và giá trị dùng ba keyed join riêng theo mẫu Pre-lab Demo 2/3; mỗi join đều dùng `d => d.id`.')
s=s.replace('quan sát `.row` trong Elements','quan sát `rect.bar` trong Elements')
a=s.find('\n\n## Cập nhật đọc dữ liệu local')
if a>=0:s=s[:a]
s+='''

## Phiên bản theo Pre-lab Demo 2/3

`render()` dùng `selectAll(...).data(data, d => d.id).join(enter, update, exit).transition(t)` như demo. Thanh, tên tỉnh và giá trị có join riêng. Các nút sửa active rồi gọi render; sort dùng bản sao. Phần chờ transition chỉ để khóa thao tác nhanh khi cả trục, nhãn và thanh đang chạy.

Đọc trực tiếp `vn-provinces-data.csv` bằng `d3.csv(...).then(...)`; đã bỏ data.js và không dùng biến CSV trên window. Khi sửa CSV rồi tải lại trang, biểu đồ đọc dữ liệu mới.

Chạy: mở thư mục lab04-d3 trong VS Code, bấm phải index.html → Open with Live Server; hoặc chạy `python -m http.server 8000` tại thư mục này rồi vào http://localhost:8000. Tên file CSV không tự trở thành biến trong window; d3.csvParse chỉ phân tích nội dung chuỗi, còn d3.csv mới đọc file qua URL.

Các bằng chứng trong evidence thuộc phiên bản đầu. Phiên bản theo prelab được kiểm thử lại qua HTTP: đọc CSV thật, 20→21→20, sort giữ cùng node thanh, Undo, Remove→Add, bấm nhanh, giới hạn 1–63 và vị trí nhãn/scale.
'''
p.write_text(s,encoding='utf-8')
