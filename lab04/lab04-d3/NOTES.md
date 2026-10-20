# Lab 04 — Data Join, Transitions, Enter & Exit

**Pham Nhu Nguyen Trung — ITCSIU24091**  
**Nguyen Quynh Anh — ITCSIU24005**  
Data Science and Data Visualization — International University

Phạm vi: các phần thực hành Lab 4, bao gồm Undo Remove; không làm optional homework Top 10.

## Chạy bài

Mở terminal trong thư mục này:

```powershell
python -m http.server 8000
```

Truy cập http://localhost:8000 . Phải chạy qua local web server hoặc VS Code Live Server. Không mở bằng `file://`: `d3.csv("vn-provinces-data.csv")` đọc trực tiếp file CSV qua HTTP. D3 lưu local nên không cần Internet.

## THINK — lời giải tham khảo có AI hỗ trợ

**Các câu dưới đây được soạn sau khi dùng AI, không phải bằng chứng nhóm đã thực hiện THINK “AI OFF”.** Nhóm cần tự trả lời/đối chiếu và giải thích trước khi nộp; không ghi nhận hoạt động trên lớp hoặc đổi vai nếu chưa thực hiện.

**T1.** Với `[A,B,C] -> [C,A,D]`, D enter, B exit, A và C update. Đổi thứ tự không đổi danh tính. Key theo index gắn phần tử với vị trí: node của A có thể bị gán dữ liệu C, làm chuyển động thể hiện sai đối tượng. Dùng `d => d.id` với `id` từ cột `ma`.

**T2.** Mô hình trạng thái:

```text
raw CSV rows
  -> kiểm tra cột, chuẩn hóa số, kiểm tra mã trùng
  -> allRecords (thứ tự nguồn, bất biến)
  -> active (tập được thêm, giữ thứ tự thành viên)
  -> data = active.slice() (bản sao được sort trong render)
  -> keyed join -> hàng, thanh, tên, giá trị; cập nhật scales/axis

removed = tỉnh vừa xóa hoặc null
sort = giá trị dropdown: source | name | grdp
busy = khóa thao tác trong transition
```

Không sort `allRecords`: Add phải tìm tỉnh chưa có đầu tiên theo nguồn. Không sort `active`: Remove phải lấy thành viên cuối cùng, không lấy thanh cuối trên màn hình.

**T3.** Sau 20 tỉnh đầu và 3 lần Add, Remove xóa bản ghi hợp lệ thứ 23 theo nguồn, bất kể sort cao–thấp. Code sử dụng `active.pop()`, còn sort chỉ tác động một bản sao.

**T4.** Các rủi ro và cách xử lý:

- Key trùng hoặc key theo vị trí: dùng `ma` và dừng tải nếu gặp mã trùng.
- Dấu phẩy thập phân: chuyển `"34,33"` thành `34.33`; không dùng `parseFloat("34,33")`.
- Chuỗi rỗng thành 0: kiểm tra định dạng trước khi gọi Number.
- Axis cũ khi cực đại thay đổi: tính lại domain ở mỗi render.
- Nhãn không đi cùng thanh: nhóm `g.row` theo key; chuyển động vị trí hàng và cập nhật x của nhãn giá trị.
- Bấm liên tục: khóa cả nút và handler bằng `busy` đến khi mọi transition kết thúc.
- CSV lỗi: hiện lỗi rõ trên trang và Console; không thay bằng số liệu tự tạo.

**T5.** Y là danh mục tỉnh, dùng band scale. X là giá trị `GRDP-VND`, dùng linear scale bắt đầu từ 0; CSV không đủ metadata để xác nhận đơn vị chi tiết/năm. Nhãn giá trị ở `x(value)+7`, giữa thanh theo chiều dọc. Chiều rộng SVG cố định 1040 px, mỗi tỉnh chiếm 30 px; chiều cao bằng `n*30 + 72 + 24`. Cắt phần đầu trục số sẽ phóng đại chênh lệch chiều dài thanh.

## BUILD — dữ liệu và triển khai

Nguồn gốc: https://tungth.github.io/data/vn-provinces-data.csv

Bản CSV trong bài được tải trực tiếp từ URL trên ngày 20/10/2026. SHA-256:

```text
1864A8BC9BF60808541DBC5CDF32F04940C8A2DD65D77EB7FDCA9DBD6401E3AE
```

Headers thật: `ma, province, area, population, density, GRDP-VND, GRDP-USD`.

- ID: `ma`; tên hiển thị: `province`; giá trị: `GRDP-VND`.
- Có 63 bản ghi hợp lệ, không có mã trùng, không có dòng bị loại.
- Hà Nội: `ma=1`, `GRDP-VND="34,33"` -> 34.33; Hà Giang: `ma=2`, `"134,40"` -> 134.40.
- Console in headers, ba dòng đầu và bảng dòng bị loại.
- CSV không ghi năm tham chiếu, không có metadata xác định đơn vị chi tiết. Tên cột gợi ý tiền tệ VND nhưng chưa đủ để kết luận tổng GRDP, triệu/tỷ VND hay bình quân đầu người. Bài giữ tên trường gốc và thông báo giới hạn này, không dùng nhãn “năm hiện tại” hoặc khẳng định ranh giới hành chính hiện hành.
- Giữ nguyên giá trị nguồn, kể cả các giá trị có vẻ bất thường; không tự sửa xếp hạng.

Khối try/catch cuối file đọc và kiểm tra dữ liệu. Mỗi nút có handler riêng; `render()` tạo bản sao để sort rồi cập nhật chart. Thanh, tên và giá trị dùng ba keyed join riêng theo mẫu Pre-lab Demo 2/3; mỗi join đều dùng `d => d.id`.

Transition 700 ms dùng cubic easing. Enter tăng chiều rộng từ 0 và hiện dần; update di chuyển hàng và đổi kích thước; exit thu chiều rộng về 0, mờ dần rồi xóa node. `.on('start')` tô cam, `.on('end')` trả lại màu xanh. Axis, nhãn và chiều cao cùng chuyển động.

## VERIFY — bằng chứng chạy thật

Kiểm thử tự động bằng Chromium/Playwright ngày 20/10/2026, kiểm tra DOM và trạng thái sau khi transition hoàn tất. Đây là kiểm thử do AI chạy, không phải ghi nhận nhóm tự thao tác. Ảnh `evidence/chart.png` được chụp từ ứng dụng thật; log đầy đủ ở `evidence/results.json`.

| Test | Kỳ vọng | Quan sát thực tế | Kết quả |
|---|---|---|---|
| V1 Initial | 20 tỉnh, thanh và nhãn tương ứng | 20 `g.row`, 20 ID duy nhất, 20 tên, 20 nhãn số | PASS |
| V2 Add/Remove | 20→21→20, tập ban đầu được khôi phục | Đếm đúng; mảng ID trước/sau giống nhau; node exit đã bị xóa | PASS |
| V3 Sort | Đổi thứ tự, giữ danh tính | GRDP giảm dần; A–Z theo locale vi; mọi node sau sort là cùng object DOM trước sort; active không đổi | PASS |
| V4 Boundary | 1 ≤ số tỉnh ≤ 63 | Gọi Add 70 lần đạt 63, nút Add khóa; Remove 70 lần còn 1, nút Remove khóa; không sinh node trùng | PASS |
| V5 Axis/values | Trục, chiều rộng, nhãn đúng theo tập active | Domain khi có đủ tỉnh `[0,160]`, khi còn Hà Nội `[0,35]`; thanh 765.069 px = 34.33/35×780; nhãn 34.33 | PASS |

Các thao tác thường và Undo dùng đúng duration 700 ms của bài. Riêng vòng lặp biên và phiên tạo lỗi giảm duration xuống 1 ms bằng thay response trong trình duyệt kiểm thử; file nộp vẫn là 700 ms. Không suy diễn kiểm thử timing cho 140 thao tác ở tốc độ thật từ vòng lặp này.

Bổ sung: gọi Add, Add, Remove cùng lúc chỉ chấp nhận Add đầu tiên, số tỉnh thành 21. Không có JavaScript page error trong các kiểm thử. Đã xem ảnh toàn trang: tên tỉnh, nhãn và trục không chồng/cắt; màn hình hẹp có cuộn ngang để giữ chart width cố định.

### Lỗi chủ động D4 — nhãn giá trị không cập nhật vị trí

1. **Kỳ vọng:** `label.x = x(value)+7`, nhãn nằm ngoài đầu thanh.
2. **Tạo lỗi:** trong bản response dùng riêng cho kiểm thử, thay vị trí nhãn bằng hằng số `x=7`; giữ nguyên cập nhật thanh.
3. **Quan sát:** nhãn Hà Nội nằm ở x=7, trong khi đầu thanh + khoảng cách phải là 174.35875. Nhãn bị đặt trong thanh, không đi theo độ dài thanh.
4. **Nguyên nhân:** code cập nhật bar width nhưng không cập nhật tọa độ của value label theo cùng scale.
5. **Sửa:** phục hồi `.attr("x", d => x(d.value) + 7)` trong transition nhãn.
6. **Retest:** kiểm tra tất cả hàng có `label.x == bar.width + 7` với sai số dưới 0.001 px: PASS.

Bản nộp không chứa lỗi chủ động. Có thể tái hiện bằng thay dòng tương ứng trong `values`, tải lại, quan sát, rồi hoàn tác.

## ADAPT — Undo Remove

Biến `removed` nhớ tỉnh vừa bị xóa. Vì active luôn là các tỉnh đầu nguồn và Remove chỉ xóa cuối mảng, Undo dùng `active.push(removed)` để khôi phục đúng vị trí cuối cũ, sau đó đặt removed = null. Add cũng xóa lịch sử Undo vì nó đã thêm lại tỉnh đó; sort chỉ dùng bản sao nên không ảnh hưởng quy tắc này.

| Chuỗi | Quan sát thực tế | Kết quả |
|---|---|---|
| Remove→Undo | Mảng active trước và sau giống hoàn toàn, kể cả vị trí | PASS |
| Remove→Undo→Undo | Undo thứ hai không thay đổi state; nút bị khóa | PASS |
| Sort→Remove→Undo | Xóa thành viên cuối của active; Undo khôi phục đúng vị trí; vẫn hiển thị theo sort | PASS |

## AI collaboration record

Đây là bản ghi các bước hỗ trợ thực tế trong phiên làm bài, không phải ba prompt riêng do sinh viên đã gửi.

| Yêu cầu / bước | Đề xuất và quyết định | Kiểm tra |
|---|---|---|
| Người dùng: “làm lab 4, bỏ phần homework ra” | Triển khai BUILD và ADAPT; bỏ Top 10; ghi THINK là tham khảo có AI | Đối chiếu phạm vi với PDF |
| AI tự review keyed update và bấm nhanh | Giữ allRecords/active/visible riêng; chọn khóa controls đến khi cả labels và exit hoàn tất | So sánh object DOM trước/sau sort; ba action đồng thời chỉ nhận một |
| AI lập kiểm thử và tạo lỗi nhãn | Chấp nhận test biên, công thức width, thử D4; không dùng ảnh đẹp làm bằng chứng duy nhất | V1–V5, Undo và retest D4 đạt; xem log/ảnh kèm |

## Chuẩn bị GROUP CHECK

Đây là hướng dẫn ôn tập, không khẳng định đã hoàn thành kiểm tra trực tiếp với giảng viên.

1. Chỉ ra `.data(records, d => d.id)` và giải thích key `ma`.
2. Demo Add (enter), sort (update), Remove (exit); quan sát `rect.bar` trong Elements.
3. Giải thích V5: khi chỉ còn Hà Nội, domain thay đổi; bar và nhãn phải cùng dùng x-scale mới.
4. Đổi `duration = 700` thành `300`, tải lại và demo.
5. Cả hai thành viên cần tự giải thích `active.pop()`, `active.slice()` và `removed`. Tự xác nhận THINK, vai trò nhóm và yêu cầu giảng viên trước khi nộp.


## Phiên bản theo Pre-lab Demo 2/3

`render()` dùng `selectAll(...).data(data, d => d.id).join(enter, update, exit).transition(t)` như demo. Thanh, tên tỉnh và giá trị có join riêng. Các nút sửa active rồi gọi render; sort dùng bản sao. Phần chờ transition chỉ để khóa thao tác nhanh khi cả trục, nhãn và thanh đang chạy.

Đọc trực tiếp `vn-provinces-data.csv` bằng `d3.csv(...).then(...)`; đã bỏ data.js và không dùng biến CSV trên window. Khi sửa CSV rồi tải lại trang, biểu đồ đọc dữ liệu mới.

Chạy: mở thư mục lab04-d3 trong VS Code, bấm phải index.html → Open with Live Server; hoặc chạy `python -m http.server 8000` tại thư mục này rồi vào http://localhost:8000. Tên file CSV không tự trở thành biến trong window; d3.csvParse chỉ phân tích nội dung chuỗi, còn d3.csv mới đọc file qua URL.

Các bằng chứng trong evidence thuộc phiên bản đầu. Phiên bản theo prelab được kiểm thử lại qua HTTP: đọc CSV thật, 20→21→20, sort giữ cùng node thanh, Undo, Remove→Add, bấm nhanh, giới hạn 1–63 và vị trí nhãn/scale.
