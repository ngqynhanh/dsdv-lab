# Mở rộng trực tiếp từ script.js

Mở `index.html` để chạy bản tích hợp. `homework.html` vẫn là ví dụ độc lập cũ.

## Luồng chạy

1. D3 tải CSV một lần (hoặc đọc bản dữ liệu cục bộ khi mở HTML trực tiếp).
2. `buildChart(rows)` chuyển kiểu dữ liệu, tạo scales, vẽ circles và axes như trước.
3. Trong `buildChart()`, gọi `setupHomework(data, plot, thresholds)` để thêm tương tác vào các circles đã vẽ.
4. `setupHomework()` lấy `plot.selectAll(".provinces circle")`. Không cần viết lại hàm `draw()` hay tải CSV lần nữa.
5. Khi dropdown thay đổi, hàm `highlight()` đổi opacity và viền. Tọa độ, bán kính, màu phân loại và dữ liệu vẫn giữ nguyên.
6. Khi chuột đi vào circle, `pointerenter` nhận `(event, d)`. `d.province` chính là tên tỉnh/thành của circle đó. Tooltip hiện tên và bốn số liệu.
7. `pointermove` cập nhật vị trí tooltip; `pointerleave` ẩn tooltip. Có thể dùng Tab để focus circle và Escape để ẩn.

## Những lỗi trong phần code đang nối dở

- `start()` tải lại CSV rồi gọi `draw()` chưa được định nghĩa.
- Selector dùng `#density-selector`, trong HTML lại là `#density-category`.
- HTML có hai phần tử cùng id `status`.

Đã thay phần nối dở bằng `setupHomework()` dùng lại dữ liệu và circles từ `buildChart()`. Bản script trước khi tích hợp nằm trong `script-before-integration.js.txt` để đối chiếu.

## Cách hover đơn giản nhất

Code gốc đã có `circle.append("title").text(...)`: trình duyệt hiện tooltip mặc định khi giữ chuột trên circle. Bản tích hợp còn thêm một div tooltip để thông tin hiện ngay, dễ đọc hơn. Nội dung được gán bằng `.text()`.

## Kiểm tra đã chạy

- Biểu đồ gốc: 11/11 checks passed.
- Chọn 500–<1000: 13/63 provinces highlighted.
- Tương tác với circle Hồ Chí Minh: tooltip hiện tên, dân số 8598.7, GRDP 43.6, diện tích 2061.4, mật độ 4171 và đơn vị.
- Escape ẩn tooltip.
- Không có lỗi JavaScript trong browser log.

AI thực hiện các kiểm tra trên qua localhost. Nhóm cần tự hover và ghi lại kết quả độc lập khi nộp bài.
