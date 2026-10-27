from pathlib import Path
import json, html, math
from PIL import Image, ImageDraw, ImageFont
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image as RLImage, Preformatted

ROOT=Path.cwd(); OUT=ROOT/'output'/'DSDV_on_tap'; OUT.mkdir(parents=True,exist_ok=True)
ASSET=ROOT/'tmp'/'dsdv_sources'/'figures'; ASSET.mkdir(exist_ok=True)
FONT=Path('C:/Windows/Fonts')
for name,file in [('Arial','arial.ttf'),('Arial-Bold','arialbd.ttf'),('Arial-Italic','ariali.ttf'),('Consolas','consola.ttf')]:
    pdfmetrics.registerFont(TTFont(name,str(FONT/file)))
pdfmetrics.registerFontFamily('Arial',normal='Arial',bold='Arial-Bold',italic='Arial-Italic',boldItalic='Arial-Bold')
def font(n=25,b=False):return ImageFont.truetype(str(FONT/('arialbd.ttf' if b else 'arial.ttf')),n)
def canvas(name,w=1300,h=600):
    im=Image.new('RGB',(w,h),'white'); return im,ImageDraw.Draw(im),ASSET/name

# Original teaching figures, with explicit numeric data rather than inferred scan colors.
im,d,p=canvas('gestalt.png',1300,390)
for i,title in enumerate(['Proximity','Similarity','Connectedness','Common region']):
    x=20+i*325; d.text((x,15),title,font=font(25,True),fill='black')
    if i==3:d.rounded_rectangle((x+5,90,x+292,280),15,outline='#777777',width=3)
    for r in range(3):
        for c in range(4):
            xx=x+35+c*(48 if c<2 or i!=0 else 60)+(35 if i==0 and c>=2 else 0); yy=120+r*65
            color=('#2166ac' if c<2 else '#d97706') if i==1 else '#444444'
            d.ellipse((xx,yy,xx+22,yy+22),fill=color)
            if i==2 and c in (0,2):d.line((xx+23,yy+11,xx+48,yy+11),fill='#444444',width=4)
d.text((20,330),'Grouping must match the intended data relationships',font=font(27),fill='black'); im.save(p)

im,d,p=canvas('heatmap.png',1300,500)
org=['Liver','Lung','Colon','Breast']; genes=['G1','G2','G3','G4','G5']; vals=[[10,30,70,20,90],[0,50,80,30,10],[60,20,40,90,70],[30,10,20,60,100]]
d.text((35,15),'Redesign example  Percentage by organ and indicator',font=font(30,True),fill='black')
for j,g in enumerate(genes):d.text((260+j*175,75),g,font=font(25),fill='black')
for i,o in enumerate(org):
    d.text((35,125+i*78),o,font=font(25),fill='black')
    for j,v in enumerate(vals[i]):
        col=tuple(int(a+(b-a)*v/100) for a,b in zip((239,246,255),(25,75,130)))
        x=235+j*175;y=115+i*78;d.rectangle((x,y,x+155,y+65),fill=col,outline='white',width=3)
        d.text((x+55,y+18),str(v),font=font(25,True),fill='white' if v>=55 else 'black')
d.text((35,450),'Illustrative data  Color scale 0 to 100 percent  Missing values need a separate symbol',font=font(23),fill='black');im.save(p)

students=[(1,80,'IT',1,2),(2,70,'CS',1,3),(3,90,'CS',1,4),(4,100,'IT',1,12),(5,60,'DS',2,15),(6,70,'DS',2,16),(7,90,'DS',2,25),(8,90,'CS',2,26),(9,50,'CS',3,9),(10,60,'IT',3,10),(11,85,'CS',3,11),(12,90,'DS',4,31),(13,70,'DS',4,32),(14,70,'DS',4,39),(15,80,'CS',5,5),(16,90,'IT',5,6),(17,100,'IT',5,7),(18,70,'DS',6,34),(19,90,'CS',6,35),(20,60,'CS',6,36)]
im,d,p=canvas('classroom.png',1300,760)
d.text((430,10),'CLASSROOM FRONT',font=font(28,True),fill='black');pos={}
for seat in range(1,41):
    r=(seat-1)//8;c=(seat-1)%8; x=75+c*138+(80 if c>=4 else 0); y=80+r*112;pos[seat]=(x+48,y+35)
for gid in range(1,7):
    ss=[s for s in students if s[3]==gid]
    for i,s in enumerate(ss):
        for t in ss[i+1:]:d.line((pos[s[4]],pos[t[4]]),fill='#b8b8b8',width=2)
cols={'IT':'#0072b2','CS':'#d55e00','DS':'#009e73'}
for seat,(cx,cy) in pos.items():
    d.rectangle((cx-49,cy-36,cx+49,cy+40),fill='white',outline='#999999',width=2)
    s=next((s for s in students if s[4]==seat),None)
    d.text((cx-44,cy-33),str(seat),font=font(17),fill='#555555')
    if s:
        idx,gpa,major,gid,_=s; d.rectangle((cx-35,cy+21,cx-35+int(gpa*.7),cy+31),fill=cols[major])
        d.text((cx-27,cy-10),f'{idx} G{gid}',font=font(18,True),fill='black')
d.text((35,680),'Seat position = location   Mini bar length = GPA on 0 to 100 scale',font=font(25),fill='black')
d.text((35,720),'IT blue   CS orange   DS green   G1 to G6 = group ID   Gray lines = all pairwise group links',font=font(22),fill='black');im.save(p)

country=[('Finland',21.3),('Sweden',21.4),('Denmark',21.7),('Estonia',22.7),('France',23.4),('Germany',23.8),('Portugal',29.7),('Italy',30.0),('Croatia',33.4)]
im,d,p=canvas('dotplot.png',1300,640)
d.text((25,10),'Selected countries  Mean age leaving parental household 2022',font=font(28,True),fill='black')
left=250; top=80;scale=55
for v in range(20,35,2):
    xx=left+(v-20)*scale;d.line((xx,top-8,xx,top+460),fill='#dddddd',width=2);d.text((xx-14,top+470),str(v),font=font(23),fill='black')
for i,(n,v) in enumerate(country):
    y=top+i*50;d.text((20,y-14),n,font=font(25),fill='black'); x=left+(v-20)*scale;d.ellipse((x-8,y-8,x+8,y+8),fill='#2166ac');d.text((x+18,y-15),str(v),font=font(23),fill='black')
d.text((580,600),'Age in years',font=font(24),fill='black');im.save(p)

im,d,p=canvas('critique.png',1300,490)
d.text((25,10),'Reported satisfaction by department',font=font(30,True),fill='black')
for v in [70,75,80,85,90]:
    y=390-(v-70)*13;d.line((140,y,1180,y),fill='#dddddd',width=2);d.text((70,y-12),str(v),font=font(23),fill='black')
for i,(n,v,col) in enumerate([('IT',78,'#0072b2'),('CS',82,'#d55e00'),('DS',84,'#009e73')]):
    x=260+i*300;y=390-(v-70)*13;d.rectangle((x,y,x+130,390),fill=col);d.text((x+40,y-35),str(v),font=font(25,True),fill='black');d.text((x+40,410),n,font=font(26),fill='black')
d.text((25,455),'Practice figure  Scores out of 100  Bar baseline is 70',font=font(22),fill='black');im.save(p)

pages=[]
def page(title,*blocks):pages.append((title,list(blocks)))
def P(t):return ('p',t)
def H(t):return ('h',t)
def T(headers,rows,widths=None):return ('table',(headers,rows,widths))
def F(name,caption,width=6.8):return ('figure',(name,caption,width))
def C(t):return ('code',t.strip('\n'))
def B(t):return ('bullet',t)

page('Ôn tập giữa kỳ DSDV',
P('Data Science and Data Visualization  IT138IU'),
P('Tài liệu học và luyện đề bằng tiếng Việt với thuật ngữ tiếng Anh. Mục tiêu là tự phân tích một biểu đồ, giải thích lựa chọn thiết kế và viết được mã D3 cho biểu đồ cột theo yêu cầu đề.'),
H('Cách dùng tài liệu'),
B('Lượt 1: học phần kiến thức nền và cách trả lời ở trang 3 đến 11; tự nói lại mỗi khái niệm bằng một ví dụ.'),
B('Lượt 2: xem bài giải theo ba đề cũ ở trang 12 đến 16; tự vẽ lại hình trước khi đọc phương án gợi ý.'),
B('Lượt 3: viết lại mã ở trang 17 đến 21, sau đó làm bài tập và hai đề mô phỏng ở trang 22 đến 26.'),
B('Lượt 4: chấm theo lời giải ở trang 27 đến 30 và ôn bằng bảng kiểm trang 31.'),
H('Bố cục'),
T(['Phần','Trang'],[['Dạng đề và phạm vi','2'],['Kiến thức C1 đến C5 và cách trả lời','3 đến 11'],['Giải và phân tích đề cũ','12 đến 16'],['D3 và mã mẫu','17 đến 21'],['Bài tập và hai đề luyện','22 đến 26'],['Đáp án và thang tự chấm','27 đến 30'],['Ôn nhanh và nguồn tra cứu','31 đến 32']],[5.5,1.3]),
P('Các câu hỏi luyện tập và thang tự chấm là nội dung biên soạn để tự học. Phần lời giải đề cũ là phương án tham khảo, không phải đáp án chính thức.'))

page('Dạng đề và trọng tâm ôn tập',
T(['Đề theo tên tệp','Cấu trúc quan sát được'],[
['2023 HK1','90 phút, 100 điểm. Phân tích và sửa biểu đồ methylation 35; thiết kế lớp học 35; D3 cột ngang COVID 30.'],
['2026 HK1','90 phút, 100 điểm. Ba giới hạn thị giác 30; phân tích sơ đồ ghế máy bay 40; D3 cột dọc cars 30.'],
['2026 HK2','90 phút, 100 điểm. Ba giới hạn thị giác 30; phân tích tuổi rời gia đình ở châu Âu 40; D3 cột dọc cars 30.']],[1.3,5.5]),
P('Tên tệp được giữ để nhận diện nguồn; không dùng tên tệp để suy ra niên khóa hay ngày thi. Hai đề mang tên 2026 dùng cùng dạng D3: lấy 10 xe có Horsepower lớn nhất rồi vẽ Acceleration.'),
H('Nội dung cần làm được'),
B('Phân loại dataset, items, links, attributes; phân biệt nominal, ordinal, interval, ratio theo ý nghĩa của dữ liệu.'),
B('Viết ánh xạ rõ ràng thuộc tính nào được mã hóa bằng channel nào trên mark nào.'),
B('Giải thích giới hạn tri giác bằng cấu trúc định nghĩa, ví dụ, hệ quả thiết kế.'),
B('Phê bình có căn cứ rồi vẽ phương án mới, có trục, thang, đơn vị, nhãn và chú giải.'),
B('D3: nạp, chuyển kiểu, lọc, sắp xếp, lấy top k, scales, axes, bars, text labels.'),
P('Đề cũ cho biết dạng kỹ năng cần luyện, không bảo đảm nội dung hay tỷ trọng của kỳ thi sắp tới. Các slide được cung cấp có tên thư mục outdated; dùng chúng cùng thông báo phạm vi hiện tại của giảng viên.'))

page('C1 Mục đích của trực quan hóa',
H('Visualization và insight'),
P('Trực quan hóa biến dữ liệu thành biểu diễn đồ họa, thường có tương tác, để khám phá, kiểm chứng hoặc trình bày. Insight là hiểu được cấu trúc, xu hướng, cụm, ngoại lệ hoặc một quan hệ có ý nghĩa để đặt câu hỏi hay hành động tiếp.'),
T(['Mục đích','Câu hỏi','Ví dụ'],[['Exploration','Có điều gì đáng chú ý?','Khám phá cụm khách hàng trên scatterplot.'],['Confirmation','Giả thuyết có phù hợp dữ liệu?','So sánh phân phối điểm của hai lớp.'],['Presentation','Người xem cần hiểu điều gì?','Làm nổi bật mức thay đổi doanh thu.']],[1.4,2.1,3.3]),
H('Vì sao cần cả thống kê và biểu đồ'),
P('Hai bộ dữ liệu có thể có mean, variance và correlation gần giống nhau nhưng hình dạng rất khác: quan hệ cong, outlier hay cụm. Anscombe’s quartet minh họa vì sao chỉ nhìn số tóm tắt là chưa đủ. Biểu đồ cũng không tự chứng minh quan hệ nhân quả.'),
H('Vai trò của người và máy'),
P('Máy xử lý, tính toán, lọc và vẽ chính xác trên lượng dữ liệu lớn. Con người nhận dạng pattern, dùng kiến thức bối cảnh để giải thích và quyết định câu hỏi tiếp theo. Thiết kế phải tính đến giới hạn chú ý, trí nhớ và khả năng so sánh thị giác.'),
H('Khi một con số hoặc tự động hóa phù hợp hơn'),
P('Nếu câu hỏi xác định rõ và chỉ cần một giá trị như tổng số sinh viên, con số trực tiếp có thể đủ. Nếu phải phản ứng tức thì ở tần suất rất cao, hệ thống tự động có thể xử lý trước; biểu đồ vẫn hữu ích cho giám sát và kiểm tra.'),
P('Nguồn học: C1, trang PDF 4 đến 7, 13 đến 21 và 31.'))

page('C3 Phân loại thuộc tính dữ liệu',
P('Kiểu dữ liệu trong visualization nói về ý nghĩa và phép so sánh hợp lệ. Nó khác với string, int hay float trong lập trình. Số áo 10 và 20 là nhãn; không thể kết luận người mang áo 20 có giá trị gấp đôi.'),
T(['Loại','Phép hiểu hợp lệ','Ví dụ và lưu ý'],[
['Nominal N','Giống hay khác','Ngành học, quốc gia, mã nhóm, seat ID. Nhãn có chữ số vẫn có thể là nominal.'],
['Ordinal O','Có thứ tự','Kém, trung bình, tốt; hạng A B C. Không giả định khoảng cách bằng nhau.'],
['Interval Q','Khoảng chênh lệch có nghĩa','Nhiệt độ Celsius, năm lịch. Mốc 0 tùy quy ước nên không so tỷ lệ trực tiếp.'],
['Ratio Q','Khoảng cách và tỷ lệ có nghĩa','Khối lượng, độ dài, số ca, tuổi, thời gian chạy. Mốc 0 thể hiện không có đại lượng.']],[1.25,1.7,3.85]),
H('Các trường hợp dễ mất điểm'),
B('GPA: quantitative; có thứ tự và chênh lệch điểm. Trong bối cảnh bài này không diễn giải GPA 80 là năng lực gấp đôi GPA 40. Nếu phải chọn thang đo, nêu giả định interval-like cho điểm số.'),
B('Seat number: nominal nếu chỉ là mã ghế. Hàng và cột suy ra từ sơ đồ là vị trí không gian, không phải điểm số của ghế.'),
B('Rating 1 đến 5 sao: thường ordinal; giả định khoảng cách bằng nhau cần được nói rõ nếu tính trung bình.'),
B('Ngày lịch: temporal và interval khi xét chênh lệch thời gian. Khoảng thời gian đã trôi qua là ratio. Giờ trong ngày còn có tính cyclic.'),
P('Nguồn học: C3, trang PDF 5 đến 8 và 27 đến 36. Khi đề chỉ hỏi categorical, ordinal, quantitative, trả lời ở mức này trước rồi mới bổ sung interval hoặc ratio.'))

page('C3 Cấu trúc dataset và ngữ nghĩa',
T(['Dataset','Đơn vị và quan hệ','Ví dụ'],[['Table','Mỗi hàng là item; cột là attribute','Sinh viên, GPA, ngành và ghế.'],['Network','Nodes là items; edges là links','Sinh viên và quan hệ cùng nhóm.'],['Tree','Cấu trúc phân cấp không có chu trình','Trường rồi khoa rồi lớp. Với cây vô hướng thường yêu cầu liên thông.'],['Field','Giá trị lấy mẫu trên miền liên tục','Nhiệt độ tại các vị trí không gian.'],['Geometry','Hình học và vị trí đã có ý nghĩa','Đường biên, mặt, khối hay sơ đồ ghế.']],[1.15,2.95,2.7]),
H('Đơn vị quan sát phải được nói rõ'),
P('Ở ma trận cơ quan × chỉ thị, một quan sát là một cặp cơ quan và chỉ thị với một tỷ lệ methylation. Có thể trình bày dưới dạng bảng dài Organ, Indicator, Percentage hoặc ma trận; nêu rõ cách hiểu mình chọn.'),
H('Khóa không đồng nghĩa với đại lượng'),
P('Mã sinh viên dùng để nhận diện item. Một bản ghi COVID trong đề 2023 cần nhãn Province/State cùng Country/Region để phân biệt. Nếu chuyển sang tổng theo quốc gia thì phải aggregate các bản ghi và nói rõ đơn vị đã đổi.'),
H('Các cấu trúc bổ sung'),
P('Set không có thứ tự và không lặp; list có thứ tự và có thể lặp; cluster nhóm các item tương tự. Dữ liệu sequential đi từ nhỏ đến lớn; diverging có mốc giữa có nghĩa như độ lệch so với 0; cyclic có điểm đầu và cuối nối nhau như giờ trong ngày.'),
P('Ngữ nghĩa quyết định thiết kế: 20 là nhiệt độ, số người hay mã phòng sẽ dẫn tới thang đo và channel khác nhau. Cần metadata gồm đơn vị, thời điểm, định nghĩa và cách thu thập.'),
P('Nguồn học: C3, trang PDF 9 đến 22, 26 và 32 đến 36.'))

page('C2 Thị giác chú ý và trí nhớ',
T(['Giới hạn hoặc hiện tượng','Ví dụ','Hệ quả thiết kế'],[
['Change blindness','Khó nhận ra một điểm đã đổi khi hai khung hình bị ngắt quãng.','Đặt hai trạng thái cạnh nhau hoặc đánh dấu vùng thay đổi.'],
['Inattentional blindness','Chăm chú đếm một nhóm nên bỏ qua đối tượng khác đang hiện diện.','Hạn chế cạnh tranh chú ý; làm nổi bật cảnh báo quan trọng.'],
['Màu phụ thuộc nền','Hai ô cùng RGB có thể trông sáng tối khác nhau.','Dùng nền nhất quán và thang màu có thứ tự rõ.'],
['Ước lượng tuyệt đối yếu','Khó nói một vòng tròn lớn hơn chính xác bao nhiêu lần.','Ưu tiên vị trí trên trục chung hoặc chiều dài căn thẳng.'],
['Phân biệt màu hạn chế','Một số người khó phân biệt đỏ với xanh lá.','Dùng thêm shape, nhãn hoặc kiểu nét cho cùng thông tin.']],[1.45,2.65,2.7]),
H('Popout và preattentive processing'),
P('Một phần tử có thuộc tính đơn lẻ khác biệt như màu hoặc hướng có thể được phát hiện rất nhanh, trước khi tập trung chú ý. Ví dụ một chấm cam giữa nhiều chấm xám. Nếu mục tiêu là hình tròn đỏ giữa các hình tròn xanh và hình vuông đỏ, không có thuộc tính đơn lẻ duy nhất; phải tìm tổ hợp và việc tìm kiếm thường chậm hơn.'),
H('Perception và cognition'),
P('Perception tiếp nhận và diễn giải tín hiệu cảm giác; cognition áp dụng tri thức để suy luận, giải quyết vấn đề và ra quyết định. Tri giác chịu ảnh hưởng của kinh nghiệm, kỳ vọng và mục tiêu. Mắt không ghi lại toàn cảnh như máy ảnh: ta nhìn qua fixation và saccade.'),
P('Mẫu câu thi: Change blindness is difficulty detecting changes across separate views. For example, a point changes after a blank frame. Therefore, I would show the states side by side and highlight the changed point.'),
P('Nguồn học: C2 Color, trang PDF 3 đến 4, 20 đến 21, 41 đến 49; C2 Popout, trang PDF 2, 11, 17 đến 28.'))

page('C2 Màu sắc và thang màu',
T(['Thành phần','Ý nghĩa','Ứng dụng'],[['Hue','Sắc màu như xanh, cam, tím','Phân biệt nhóm nominal.'],['Saturation','Mức bão hòa của màu','Có thể biểu đạt độ lớn khi có thứ tự dễ nhận.'],['Value và lightness','Độ sáng tối trong mô hình tương ứng','Dãy sáng đến tối cho dữ liệu ordered.']],[1.4,2.65,2.75]),
P('HSV Value, perceptual lightness và luminance không hoàn toàn đồng nhất. Trong trả lời thiết kế, hãy nói rõ channel định dùng thay vì gọi mọi thay đổi màu là hue.'),
T(['Colormap','Dùng khi','Ví dụ'],[['Categorical','Các nhóm không có thứ tự','Ngành IT CS DS; dùng sắc màu khác nhau.'],['Sequential','Một chiều từ thấp đến cao','Số ca từ 0 đến lớn; sáng đến tối.'],['Diverging','Có mốc trung tâm quan trọng','Sai lệch so với 0; hai phía khác sắc và giữa trung tính.'],['Cyclic','Giá trị có vòng lặp','Giờ trong ngày; tránh bước nhảy giả ở điểm nối.']],[1.35,2.65,2.8]),
H('Những lỗi thường gặp'),
B('Rainbow tạo thứ tự và ranh giới cảm nhận không đều; không phải lựa chọn mặc định tốt để đọc độ lớn liên tục.'),
B('Quá nhiều màu cạnh tranh làm mất highlight. Với ít nhóm, dùng ít màu phân biệt rõ; nếu nhiều nhóm, cân nhắc nhãn trực tiếp hoặc chia panels.'),
B('Không dùng riêng đỏ và xanh lá cho hai trạng thái quan trọng. Thêm shape, text hoặc line style để truyền đạt dự phòng.'),
B('Dùng thang diverging khi không có mốc giữa có ý nghĩa có thể gợi ra phân chia giả.'),
P('RGB là trộn ánh sáng theo mô hình cộng; CMY/CMYK là trộn mực theo mô hình trừ. Không nhầm mô hình tạo màu với quy tắc chọn colormap cho dữ liệu.'),
P('Nguồn học: C2 Color, trang PDF 28 đến 40, 41 đến 55.'))

page('C2 Gestalt và cách thể hiện nhóm',
F('gestalt.png','Hình minh họa tự vẽ về bốn cách tạo nhóm thị giác.'),
T(['Nguyên lý','Cách hiểu và cách dùng'],[['Proximity','Phần tử gần nhau được xem là cùng nhóm. Dùng khoảng cách để chia nhóm cột hoặc panels.'],['Similarity','Phần tử cùng màu hoặc hình dạng được xem là liên quan. Dùng hue nhất quán cho cùng ngành.'],['Connectedness','Đường nối tạo liên hệ trực tiếp. Thích hợp thể hiện quan hệ trong network.'],['Common region','Được bao trong cùng vùng gợi cùng nhóm. Dùng enclosure cho một cụm có ý nghĩa.'],['Continuity','Mắt có xu hướng tiếp tục theo đường liên tục. Hỗ trợ đọc line chart; tránh giao cắt khó theo dõi.'],['Closure','Mắt hoàn thiện đường biên còn thiếu để nhận hình. Không đồng nhất closure với việc bao nhóm bằng một khung kín.'],['Symmetry và figure ground','Cân xứng hỗ trợ nhận dạng; tương phản tách chủ thể khỏi nền. Dùng nền nhẹ để dữ liệu nổi rõ.']],[1.55,5.25]),
P('Các tín hiệu nhóm có thể xung đột. Ví dụ đặt hai ngành sát nhau nhưng cùng một màu cho hai nhóm khác sẽ tạo cách hiểu mâu thuẫn. Nêu quan hệ cần truyền đạt trước rồi chọn proximity, similarity hoặc connection phù hợp.'),
P('Nguồn học: C2 Popout, trang PDF 29 đến 58.'))

page('C4 Marks channels và nguyên lý mã hóa',
P('Mark là phần tử hình học dùng biểu diễn item hoặc link: point, line, area và đôi khi volume. Channel là thuộc tính thị giác thay đổi theo dữ liệu: position, length, area, hue, lightness, shape, orientation. Đừng chỉ viết mark là màu: màu là channel.'),
T(['Biểu đồ','Marks','Ánh xạ điển hình'],[['Bar chart','Thanh hình chữ nhật hoặc mark dạng line theo mô hình đơn giản','Danh mục sang vị trí; giá trị sang chiều dài và vị trí đầu thanh.'],['Scatterplot','Point','Hai đại lượng sang x và y; nhóm sang hue hoặc shape.'],['Heatmap','Ô chữ nhật','Hai thuộc tính danh mục sang hàng và cột; giá trị sang lightness.'],['Node link','Point và line','Item sang node; quan hệ sang connection.'],['Bubble chart','Point dạng hình tròn','Giá trị sang diện tích, không phải bán kính tuyến tính.']],[1.25,2.0,3.55]),
H('Expressiveness'),
P('Mã hóa phải biểu đạt đúng thông tin có trong dữ liệu. Nominal không có thứ tự, nên kích thước tăng dần theo mã ngành dễ ngụ ý ngành này lớn hơn ngành kia. Với điểm số, hue rời rạc không có thứ tự sẽ không diễn đạt rõ độ lớn.'),
H('Effectiveness'),
P('Thuộc tính quan trọng nên dùng channel dễ đọc và nổi bật. Với so sánh định lượng, ưu tiên position trên thang chung, rồi các vị trí không căn thẳng, length, angle, area; depth, luminance và volume thường kém chính xác hơn cho nhiệm vụ này. Thứ hạng phụ thuộc nhiệm vụ, không phải luật tuyệt đối cho mọi loại dữ liệu.'),
P('Redundant encoding: mã hóa một thuộc tính bằng nhiều channel, ví dụ ngành bằng hue và shape. Separability: người xem có thể đọc riêng từng channel; tránh phối hợp nhiều biến gây nhiễu hoặc che lấp nhau.'),
P('Nguồn học: C4, trang PDF 3 đến 15, 19 đến 29 và 43 đến 48.'))

page('C5 Đánh giá và thiết kế lại biểu đồ',
T(['Vấn đề','Hệ quả','Cách sửa phù hợp'],[['Trục cắt trên bar chart','Chiều dài thanh phóng đại chênh lệch','Cho baseline 0; nếu cần zoom, dùng dotplot có trục rõ.'],['3D không cần thiết','Che khuất và sai lệch do phối cảnh','Chuyển sang 2D hoặc small multiples.'],['Nhiều pie tương tự','Khó so các góc và phần không chung baseline','Dùng bar chart căn thẳng hoặc dotplot.'],['Thiếu đơn vị và nhãn','Không biết giá trị biểu đạt gì','Ghi tên trục, đơn vị, thời gian và nguồn.'],['Chỉ có mean','Ẩn độ phân tán, outlier và đa đỉnh','Thêm raw points, boxplot hoặc violin theo mục tiêu.'],['Animation để so trạng thái','Buộc nhớ khung hình trước','Small multiples cùng thang và cùng thứ tự.']],[1.6,2.3,2.9]),
H('Graphical integrity và lie factor'),
P('Độ lớn thể hiện phải phù hợp độ lớn dữ liệu. Theo cách tính biến thiên tương đối thường dùng: lie factor bằng phần trăm thay đổi thể hiện trên hình chia cho phần trăm thay đổi trong dữ liệu. Luôn ghi rõ baseline và cách đo hiệu ứng.'),
P('Ví dụ giá trị 100 lên 110 tăng 10%. Nếu trục thanh bắt đầu ở 90, chiều dài thấy được 10 lên 20 tăng 100%; lie factor là 10. Nếu dữ liệu không đổi, phép chia này không dùng được. Không trộn tỷ số kích thước với phần trăm tăng.'),
H('Quy tắc cần hiểu theo ngữ cảnh'),
P('Bar chart thường cần baseline 0 vì length mã hóa độ lớn. Line chart và dotplot có thể dùng miền hẹp được ghi rõ để quan sát biến thiên. Giảm chart junk và tăng data ink không có nghĩa xóa trục, nhãn hoặc ngữ cảnh cần thiết.'),
P('Lưu ý khi học C5 trang 31: median không chỉ dành cho phân phối chuẩn. CI cho mean biểu đạt bất định của ước lượng, không phải vùng chứa phần lớn điểm dữ liệu. Muốn thấy phân phối, cần biểu diễn phân phối hoặc dữ liệu gốc. Xem nguồn thống kê ở trang 32.'),
P('Nguồn học: C5, trang PDF 9 đến 31, 34 đến 43, 49 đến 73.'))

page('Cách viết câu trả lời phân tích biểu đồ',
H('Bước 1 Nêu mục tiêu'),
P('Viết một câu có đối tượng và phép so sánh: mục tiêu là so sánh tỷ lệ methylation giữa các cơ quan và chỉ thị để tìm các cặp có tỷ lệ cao. Tránh câu chung như để trực quan hóa dữ liệu.'),
H('Bước 2 Xác định dữ liệu'),
P('Nêu item hoặc đơn vị quan sát; liệt kê thuộc tính và loại của từng thuộc tính; ghi đơn vị và thời điểm. Với sơ đồ có vị trí thực, phân biệt identifier với spatial position.'),
H('Bước 3 Mô tả encoding đang có'),
P('Dùng mẫu: mỗi mark ... biểu diễn ...; channel ... mã hóa thuộc tính ... . Ví dụ mỗi hình tròn biểu diễn một quốc gia; text ghi tên và tuổi; hue biểu diễn nhóm tuổi. Vị trí theo bố cục bản đồ chỉ gần đúng, không dùng để xếp hạng tuổi.'),
H('Bước 4 Nêu lỗi và tác động'),
P('Mỗi nhận xét phải gắn với nhiệm vụ: chiều sâu gây che khuất nên khó so sánh các cột phía sau; dùng các sắc màu không có thứ tự khiến khó suy ra quốc gia nào có tuổi trung bình cao hơn.'),
H('Bước 5 Vẽ và giải thích phương án mới'),
P('Vẽ đủ marks, axes, ticks, labels, đơn vị và legend nếu cần. Ghi mapping mới; giải thích vì sao nó hỗ trợ nhiệm vụ; nêu đánh đổi. Dotplot xếp hạng tuổi so sánh tốt hơn nhưng giảm thông tin địa lý; có thể thêm bản đồ nhỏ nếu nhiệm vụ cần vị trí.'),
H('Khung tiếng Anh có thể tái sử dụng'),
P('The goal is to compare ... . Each item represents ... . The attributes are ... . The author uses ... marks and maps ... to ... . This makes ... difficult because ... . I would redesign it as ... . In the new design, ... encodes ... . This improves ... because ... .'),
P('Tự kiểm: mô tả bản gốc trước, đề xuất bản mới sau. Nếu chỉ nói biểu đồ xấu hoặc dùng bar chart tốt hơn mà không chỉ ra mapping và lý do, câu trả lời còn thiếu.'))

page('Đề 2023 Câu phân tích methylation',
P('Đề gốc: trang PDF 2, câu 1, tổng 35 điểm gồm data 10, encoding 5, problems 10 và redesign 10. Hình dùng nhiều cột 3D để thể hiện tỷ lệ methylation theo cơ quan và chỉ thị.'),
H('Phương án trả lời'),
B('Data: bảng đa chiều cơ quan × chỉ thị. Mỗi cặp là một quan sát. Organ và indicator là nominal; methylation percentage là quantitative ratio với miền 0 đến 100%.'),
B('Marks và channels: các cột/khối trụ; hai vị trí trên mặt phẳng nền mã hóa cơ quan và chỉ thị; chiều cao mã hóa phần trăm. Không suy đoán ý nghĩa màu từ bản scan nếu không có legend đọc được.'),
B('Problems: cột trước che cột sau; phối cảnh làm chiều cao khó so; nhãn nhỏ và nghiêng; lưới dày; nhiều nhóm khó tra cặp; không có baseline so sánh dễ đọc cho mọi cột.'),
B('Redesign: heatmap để tìm pattern của toàn ma trận. Hàng là cơ quan, cột là chỉ thị, lightness theo tỷ lệ 0 đến 100%; ghi giá trị khi số ô vừa phải. Nếu cần so thật chính xác một chỉ thị, thêm bar/dotplot riêng.'),
F('heatmap.png','Minh họa cách vẽ lại bằng số liệu tự tạo, không chép số từ hình scan.'),
P('Vì sao hợp lý: heatmap bỏ che khuất và cho phép quét hàng/cột. Đánh đổi: đọc chênh lệch nhỏ qua màu kém chính xác hơn position; nhãn số hoặc một view phụ khắc phục phần này. Ô thiếu dữ liệu cần ký hiệu riêng để không nhầm với 0%.'))

page('Đề 2023 Câu thiết kế lớp học',
P('Đề gốc: trang PDF 2 đến 3, câu 2, tổng 35 điểm. Cần thể hiện GPA, major, group ID, seat number và các liên kết giữa mọi thành viên cùng nhóm theo sơ đồ lớp.'),
T(['Thuộc tính','Loại','Encoding đề xuất'],[['Seat','ID nominal và vị trí suy ra','Position x y giữ đúng sơ đồ ghế.'],['GPA','Quantitative','Mini bar có length theo thang 0 đến 100.'],['Major','Nominal','Hue; thêm ký hiệu IT CS DS nếu cần in xám.'],['Group ID','Nominal','Nhãn G1 đến G6 và đường nối cặp cùng nhóm.'],['Student index','Identifier nominal','Nhãn index trong ghế để đối chiếu item.']],[1.15,1.7,3.95]),
F('classroom.png','Minh họa dùng 20 sinh viên và vị trí ghế theo bảng đề 2023. Số nhỏ góc trái là ghế; số trước G là index.'),
P('Sơ đồ có 5 hàng, mỗi hàng 8 ghế chia hai dãy 4 ghế. Không dùng force layout vì sẽ mất vị trí ghế thật. Tạo links cho mọi cặp cùng group: nhóm 4 người cần 6 cạnh, nhóm 3 người cần 3 cạnh; dữ liệu đề có tổng 24 cạnh.'),
P('Đường nối có thể giao nhau: vẽ dưới node, dùng nét mảnh và ghi group ID trên node; bản tương tác có thể highlight một nhóm. Nếu đề đòi mọi liên kết thì chỉ vẽ cây nối hoặc nối qua một group hub chưa thể hiện đủ quan hệ cặp trực tiếp.'))

page('Đề 2026 HK1 Giới hạn thị giác và ghế máy bay',
H('Câu 1 Ba giới hạn thị giác 30 điểm'),
P('Chọn ba ý khác nhau, mỗi ý có giải thích, ví dụ và hệ quả thiết kế. Một bộ trả lời đủ là change blindness, khó phân biệt một số màu và khó ước lượng diện tích chính xác. Dùng mẫu ở trang 6, không chỉ liệt kê tên hiện tượng.'),
H('Câu 2 Phân tích sơ đồ ghế 40 điểm'),
P('Đề gốc trang PDF 2: mục tiêu 5, data và types 15, marks và channels 10, redesign 10. Mục tiêu của hình là thể hiện xác suất tiếp xúc gần người bệnh theo ghế và vai trò của một số người trên máy bay.'),
B('Items: ghế hoặc người tại ghế nếu dữ liệu một người một ghế; cần nói rõ. Attributes: row và seat ID; spatial position; probability quantitative ratio 0 đến 100%; role nominal như người bệnh hoặc tiếp viên khi legend có mã hóa.'),
B('Marks: hình chữ nhật cho ghế, glyph/text cho trạng thái hoặc vai trò. Position giữ hàng và phía lối đi; màu/thang sáng tối có legend theo xác suất. Bản scan không cho phép khẳng định chính xác từng sắc màu.'),
B('Problems: ghế và chữ nhỏ; khó tra legend; dễ lẫn ô trống, xác suất thấp và trạng thái đặc biệt; màu không có thứ tự rõ sẽ làm sai việc so độ lớn. Chỉ kết luận lỗi nào có bằng chứng từ hình hoặc nêu điều kiện nếu bản màu không đọc được.'),
H('Phương án vẽ lại'),
P('Giữ sơ đồ ghế vì vị trí gần người bệnh là ngữ nghĩa quan trọng. Dùng sequential lightness cho xác suất; dấu X cho người bệnh; chữ C hoặc ký hiệu khác cho tiếp viên và giải thích bằng legend riêng. Ghi hàng, cột ghế, lối đi và mũi hướng đầu máy bay. Ô không có dữ liệu dùng họa tiết hoặc ký hiệu khác 0%.'),
P('Nên vẽ legend 0%, 25%, 50%, 75%, 100% và một hàng ghế mẫu để chứng minh mapping. Đây là phương án giữ spatial context; bar chart xếp theo xác suất có thể là view phụ nếu cần tra thứ hạng.'))

page('Đề 2026 HK2 Tuổi rời gia đình',
P('Đề gốc trang PDF 2: data 15, marks/channels 10, redesign có hình và giải thích 15. Dữ liệu là tuổi trung bình rời gia đình cha mẹ năm 2022 theo quốc gia; có mục EU 27 là tổng hợp, không phải một quốc gia riêng.'),
T(['Thành phần','Phân tích'],[['Items','Các quốc gia; nếu có EU 27, coi là bản ghi tổng hợp và phân biệt rõ.'],['Attributes','Country nominal; mean age quantitative ratio, đơn vị năm; age band là ordinal được suy ra từ tuổi; năm 2022 là metadata thời gian.'],['Marks/channels','Hình tròn kích thước gần như cố định; text cho tên và tuổi; hue/lightness theo các dải tuổi; vị trí gợi bố cục địa lý.'],['Vấn đề','Màu theo bin làm mất chi tiết so sánh; thứ tự không theo tuổi; chữ trên nền có thể khó đọc; kích thước tròn không giúp đọc tuổi.']],[1.4,5.4]),
F('dotplot.png','Một phần số đọc được từ đề dùng minh họa dotplot đã sắp theo tuổi. Không phải toàn bộ dataset.'),
P('Redesign: dotplot ngang, quốc gia trên y và mean age trên x, cùng một trục; sắp tăng dần, thêm nhãn 1 chữ số thập phân. Tách EU 27 thành đường tham chiếu 26.4 năm nếu dùng toàn bộ dữ liệu; không tính trung bình EU bằng cách lấy trung bình đơn giản các quốc gia.'),
P('Justification: position trên thang chung giúp đọc chênh lệch tốt hơn hue. Có thể giữ màu để đánh dấu một nhóm cụ thể, nhưng không cần mỗi quốc gia một màu. Trục x thu hẹp được nếu miền và ticks rõ vì dotplot mã hóa bằng vị trí.'))

page('Đề cũ Phần lập trình và những điểm cần sửa',
H('Cars ở hai đề mang tên 2026'),
P('Phải xếp giảm dần Horsepower, lấy 10 bản ghi, nhưng chiều cao cột biểu diễn Acceleration. Dùng Name làm nhãn x theo yêu cầu đề. Không sắp theo Acceleration và không lấy Horsepower làm chiều cao.'),
P('Đề có 5 điểm cho visualization và R1 đến R5 mỗi mục 5 điểm: fixed SVG và margins/scales, hai axes và title, nhãn Name, xử lý top 10, value labels. Học cách kiểm từng yêu cầu thay vì chỉ vẽ ra hình.'),
H('CSV COVID ở đề 2023'),
P('Mỗi hàng giữ Province/State và Country/Region làm key/label. Chọn đúng cột ngày, lọc số ca khác 0, vẽ cột ngang với thang x tuyến tính và y band, có trục và giá trị trên thanh. Tổng theo quốc gia là bài khác nếu không được yêu cầu.'),
H('Hai bẫy trong gợi ý cũ'),
B('d3.csv có row converter; d3.json không có tham số row converter tương tự. Với JSON, nạp xong rồi dùng map(convertRow). Gợi ý mẫu ở trang 4 của các đề cars cũng minh họa cách map này.'),
B('Tên cột ngày phải khớp chính xác header. Ngày 03/03/2023 thường có thể là 3/3/23 trong dạng CSV minh họa; dòng hint cuối đề còn ghi 03/03/2022. Chọn theo yêu cầu ngày trong câu hỏi và kiểm tra header, không sao chép hint mâu thuẫn.'),
H('Một lưu ý về ngữ nghĩa cars'),
P('Trong dataset cars kiểu Vega, Acceleration được mô tả bằng thời gian tăng tốc tính bằng giây, dù tên trường là Acceleration. Giữ tên trường theo đề và ghi đơn vị khi đã xác nhận metadata; không tự đổi sang m/s². Name cũng có thể lặp trong dữ liệu thực, nên dùng key nội bộ riêng; trục vẫn hiển thị Name.'),
P('Phần mã sau dùng D3 v7. Các bộ dữ liệu dùng để luyện có thể giản lược; điều quan trọng khi thi là trình bày đúng chuỗi xử lý và mapping.'))

page('D3 Quy trình và hình học cần nhớ',
T(['Bước','Ý nghĩa','Hàm hoặc cú pháp'],[['Load','Nạp dữ liệu bất đồng bộ','await d3.json hoặc d3.csv'],['Parse','Đổi số; bảo toàn null','map, row converter, Number'],['Filter','Bỏ hàng thiếu trường cần dùng','filter, Number.isFinite'],['Sort và slice','Chọn top k theo trường đề yêu cầu','sort rồi slice'],['Layout','SVG cố định và vùng vẽ bên trong','margins, translate'],['Scales','Dữ liệu sang tọa độ','scaleBand, scaleLinear'],['Draw','Nối dữ liệu với marks','data, join, attr'],['Annotate','Trục và nhãn đủ nghĩa','axisBottom, axisLeft, text']],[1.1,2.6,3.1]),
H('Cột dọc'),
P('x là scaleBand cho danh mục; y là scaleLinear từ 0 đến max. Trong SVG, y tăng theo hướng xuống nên range của y là [innerHeight, 0]. Đầu cột ở y(value); height là innerHeight trừ y(value); width là x.bandwidth().'),
H('Cột ngang'),
P('x là scaleLinear từ 0 đến max với range [0, innerWidth]; y là scaleBand. x của thanh bằng 0; width là x(value); y là y(key); height là y.bandwidth().'),
H('Kiểm tra trước khi bind data'),
B('Không biến null hay chuỗi rỗng thành số 0 bằng ép kiểu thiếu kiểm soát. Loại hoặc xử lý missing theo ý nghĩa dữ liệu.'),
B('Sort số cần comparator, ví dụ (a,b) => b.Horsepower - a.Horsepower. Sort chuỗi mặc định có thể cho thứ tự sai.'),
B('Nếu không có dữ liệu hợp lệ, hiện thông báo và kết thúc; không tạo scale có domain undefined.'),
P('Mã mẫu tiếp theo được chia theo trang để dễ viết tay. Khi chạy, nối nguyên các đoạn theo thứ tự vào cùng một file HTML.'))

cars1='''<!doctype html>
<html lang="en"><meta charset="utf-8">
<title>Midterm Challenge</title>
<script src="https://cdn.jsdelivr.net/npm/d3@7"></script>
<body><h1>Acceleration of top 10 horsepower cars</h1>
<div id="chart"></div>
<script>
async function main() {
  const raw = await d3.json("cars.json");
  const numberOrNaN = v =>
    v == null || String(v).trim() === "" ? NaN : +v;
  const data = raw.map((d, i) => ({
    ...d, key: String(i),
    Horsepower: numberOrNaN(d.Horsepower),
    Acceleration: numberOrNaN(d.Acceleration)
  })).filter(d => d.Name &&
    Number.isFinite(d.Horsepower) &&
    Number.isFinite(d.Acceleration) &&
    d.Horsepower >= 0 && d.Acceleration >= 0)
    .sort((a, b) => b.Horsepower - a.Horsepower)
    .slice(0, 10);
  if (!data.length) {
    d3.select("#chart").text("No valid data");
    return;
  }
  const W = 800, H = 500;
  const m = {top: 45, right: 25, bottom: 180, left: 65};
  const w = W - m.left - m.right;
  const h = H - m.top - m.bottom;
  const svg = d3.select("#chart").append("svg")
    .attr("width", W).attr("height", H);
  const g = svg.append("g")
    .attr("transform", `translate(${m.left},${m.top})`);
  const names = new Map(data.map(d => [d.key, d.Name]));
  const x = d3.scaleBand().domain(data.map(d => d.key))
    .range([0, w]).padding(0.2);
  const maxY = d3.max(data, d => d.Acceleration) || 1;
  const y = d3.scaleLinear().domain([0, maxY]).nice()
    .range([h, 0]);'''
cars2='''  g.append("g").attr("transform", `translate(0,${h})`)
    .call(d3.axisBottom(x).tickFormat(k => names.get(k)))
    .selectAll("text").attr("transform", "rotate(-55)")
    .attr("text-anchor", "end").attr("dx", "-.6em")
    .attr("dy", ".2em");
  g.append("g").call(d3.axisLeft(y));
  g.append("text").attr("x", 0).attr("y", -15)
    .text("Acceleration (seconds)");
  svg.append("text").attr("x", m.left + w / 2)
    .attr("y", H - 12).attr("text-anchor", "middle")
    .text("Car name - ordered by Horsepower");
  g.selectAll("rect.bar").data(data, d => d.key)
    .join("rect").attr("class", "bar")
    .attr("x", d => x(d.key))
    .attr("y", d => y(d.Acceleration))
    .attr("width", x.bandwidth())
    .attr("height", d => h - y(d.Acceleration))
    .attr("fill", "#2166ac");
  g.selectAll("text.value").data(data, d => d.key)
    .join("text").attr("class", "value")
    .attr("x", d => x(d.key) + x.bandwidth() / 2)
    .attr("y", d => y(d.Acceleration) - 6)
    .attr("text-anchor", "middle")
    .text(d => d.Acceleration);
}
main().catch(error => {
  console.error(error);
  d3.select("#chart").text("Cannot load cars.json");
});
</script></body></html>'''
page('D3 Cars Mã mẫu phần một',C(cars1),P('Mỗi key là chỉ số bản ghi trước khi sort, giúp tránh gộp các Name trùng. Các giá trị Acceleration thiếu được loại trước khi chọn top 10; nếu đề quy định cách xử lý missing khác thì phải ghi rõ.'))
page('D3 Cars Mã mẫu phần hai',C(cars2),
H('Đối chiếu yêu cầu'),P('SVG 800 × 500 và translate theo margin; x band và y linear; đủ hai axes; Name hiển thị ở ticks; top 10 theo Horsepower; chiều cao và nhãn số theo Acceleration. Margin dưới lớn để chứa tên xe dài.'),
P('Khi thi, bản dùng Name trực tiếp làm domain có thể ngắn hơn nếu đề giả định Name duy nhất. Trong dữ liệu thật, dùng key riêng vẫn giữ nguyên yêu cầu hiển thị Name.'))

covid1='''<!doctype html>
<html lang="en"><meta charset="utf-8">
<title>Midterm</title>
<script src="https://cdn.jsdelivr.net/npm/d3@7"></script>
<body><h1>Confirmed cases on 3 March 2023</h1>
<div id="chart"></div><script>
async function main() {
  const raw = await d3.csv("covid_global.csv");
  const parse = d3.timeParse("%m/%d/%y");
  const target = new Date(2023, 2, 3);
  const dateKey = raw.columns.find(k => {
    const dt = parse(k);
    return dt && +dt === +target;
  });
  if (!dateKey) throw new Error("Date column missing");
  const data = raw.map((d, i) => ({
    key: String(i),
    label: [d["Province/State"], d["Country/Region"]]
      .filter(Boolean).join(" / "),
    value: d[dateKey]?.trim() ? +d[dateKey] : NaN
  })).filter(d => Number.isFinite(d.value) && d.value > 0);
  if (!data.length) throw new Error("No non-zero rows");
  const W = 1000, H = 650;
  const m = {top: 40, right: 95, bottom: 55, left: 260};
  const w = W - m.left - m.right;
  const h = H - m.top - m.bottom;
  const svg = d3.select("#chart").append("svg")
    .attr("width", W).attr("height", H);
  const g = svg.append("g")
    .attr("transform", `translate(${m.left},${m.top})`);
  const label = new Map(data.map(d => [d.key, d.label]));
  const x = d3.scaleLinear()
    .domain([0, d3.max(data, d => d.value)]).nice()
    .range([0, w]);
  const y = d3.scaleBand().domain(data.map(d => d.key))
    .range([0, h]).padding(0.15);'''
covid2='''  g.append("g").attr("transform", `translate(0,${h})`)
    .call(d3.axisBottom(x).ticks(6));
  g.append("g")
    .call(d3.axisLeft(y).tickFormat(k => label.get(k)));
  svg.append("text").attr("x", m.left + w / 2)
    .attr("y", H - 10).attr("text-anchor", "middle")
    .text("Confirmed cases");
  g.selectAll("rect.bar").data(data, d => d.key)
    .join("rect").attr("class", "bar")
    .attr("x", 0).attr("y", d => y(d.key))
    .attr("width", d => x(d.value))
    .attr("height", y.bandwidth())
    .attr("fill", "#2166ac");
  g.selectAll("text.value").data(data, d => d.key)
    .join("text").attr("class", "value")
    .attr("x", d => Math.max(0, x(d.value) - 4))
    .attr("y", d => y(d.key) + y.bandwidth() / 2)
    .attr("dy", ".35em").attr("text-anchor", "end")
    .attr("fill", "white").attr("font-size", 10)
    .text(d => d3.format(",")(d.value));
}
main().catch(error => {
  console.error(error);
  d3.select("#chart").text(error.message);
});
</script></body></html>'''
page('D3 COVID Mã mẫu phần một',C(covid1),P('Mã tìm cột theo ngày đã parse, không mặc định một chuỗi header. Không cộng các tỉnh thành về quốc gia vì đề gốc cần nhãn của từng hàng.'))
page('D3 COVID Mã mẫu phần hai',C(covid2),
H('Giới hạn khi chạy toàn bộ dataset'),
P('Đây là khung đáp ứng dạng viết mã của đề: SVG cố định, scale, trục, nhãn, filter và số trên thanh. Với hàng trăm dòng và giá trị chênh lệch lớn, fixed height khiến nhãn quá dày và một số số không vừa trong thanh. Không tự bỏ bớt hàng hoặc lấy top 10 nếu đề không cho phép.'),
P('Trong sản phẩm thực, cần thống nhất thêm yêu cầu phân trang, vùng cuộn, chọn nhóm hoặc chiều cao theo số dòng. Với thanh quá ngắn, chuyển số ra ngoài và đổi màu chữ; nếu đề bắt buộc số nằm trong thanh, nêu rõ xung đột đọc được này.'),
P('Chạy các file mã bằng HTTP server tại thư mục có HTML và dữ liệu. Mở bằng file:// có thể làm fetch bị chặn. Thư viện D3 nạp từ CDN nên cần mạng; đặt bản D3 cục bộ nếu muốn dùng hoàn toàn offline.'))

page('Bài tập tự luyện phân loại và giải thích',
H('Bài 1 Phân loại thuộc tính'),
P('Với mỗi mục, ghi N, O, interval hoặc ratio và một câu giải thích. a Mã sinh viên; b ngành; c hạng nhất nhì ba; d nhiệt độ Celsius; e tuổi; f thời gian chạy 100 m; g số ca; h năm lịch; i rating 1 đến 5; j số ghế; k nhóm máu; l khoảng cách di chuyển.'),
H('Bài 2 Chọn channel'),
P('a So sánh chính xác điểm của 12 lớp. b Phân biệt 3 ngành trên scatterplot. c Tìm vùng nhiệt cao trên ma trận. d Thể hiện độ lệch âm dương so với mục tiêu. Nêu mark, channel và lý do.'),
H('Bài 3 Giới hạn thị giác'),
P('Viết ba đoạn ngắn theo cấu trúc hiện tượng, ví dụ, implication. Chọn trong change blindness, color vision deficiency, area judgment, inattentional blindness. Không dùng cùng một ví dụ cho ba ý.'),
H('Bài 4 Kiểm tra hiểu đúng'),
P('Đánh dấu đúng/sai rồi sửa câu sai. a Mọi số nguyên đều quantitative. b Hue có thứ tự tự nhiên để đọc chính xác độ lớn. c D3 y tăng xuống dưới. d Cột dọc có height bằng y(value). e JSON có thể chuyển kiểu bằng map sau khi nạp. f Top 10 Horsepower thì chiều cao bắt buộc là Horsepower. g Mọi biểu đồ đều phải có trục từ 0. h CI cho mean chứa 95% các quan sát.'),
H('Bài 5 Suy luận hình học'),
P('a Giá trị 4 và 16 được mã hóa bằng diện tích hình tròn. Tỷ lệ bán kính phải là bao nhiêu? b y có domain [0,100], range [300,0]. Với value 40, tìm y, height của thanh và vị trí y của nhãn trên cột 6 px. c Giá trị 50 lên 60 nhưng cột có baseline 40. Tính lie factor theo phần trăm thay đổi.'),
P('Làm trước khi đọc đáp án trang 27. Dành khoảng 30 phút, ưu tiên giải thích ngắn gọn hơn là chỉ ghi đáp số.'))

page('Bài tập tự luyện phê bình và D3',
H('Bài 6 Phân tích hình'),
F('critique.png','Hình luyện tập dùng số liệu tự tạo; trục cột bắt đầu ở 70.'),
P('a Nêu mục tiêu, items và types. b Chỉ ra marks/channels. c Tính mức tăng thật từ IT đến DS và mức tăng chiều dài thấy được. d Vẽ hai phương án sửa phù hợp. e Cho biết không thể suy ra điều gì về phân phối điểm từ ba mean này.'),
H('Bài 7 Sửa mã'),
C('''const data = raw.slice(0, 10)
  .sort((a, b) => a.Horsepower - b.Horsepower);
const y = d3.scaleLinear().domain([0, max]).range([0, h]);
bars.attr("y", d => y(d.Acceleration))
  .attr("height", d => y(d.Acceleration));'''),
P('Nêu ít nhất bốn lỗi hoặc chỗ chưa đúng yêu cầu top 10 Horsepower rồi vẽ Acceleration. Sửa bằng 5 đến 10 dòng. Giả định số đã parse và max là Acceleration lớn nhất.'),
H('Bài 8 Thiết kế dữ liệu nhiều thuộc tính'),
P('Có 15 sinh viên với ID, GPA, ngành, nhóm và vị trí bàn thực. Vẽ một mẫu cho 6 người để thể hiện tất cả thuộc tính và mọi quan hệ cùng nhóm. Ghi mapping và một cách giảm clutter mà vẫn giữ vị trí bàn.'),
P('Đáp án ở trang 28.'))

page('Đề mô phỏng A Phần lý thuyết và phân tích',
P('90 phút  100 điểm  Làm cả ba câu ở trang 24 và 25. Gợi ý phân bổ 20 phút, 35 phút, 30 phút và 5 phút kiểm tra.'),
H('Câu 1 Giới hạn thị giác 30 điểm'),
P('List three limitations of the human visual system. For each limitation, explain it, give one example, and describe its implication for visualization design. Có thể trả lời bằng tiếng Việt và giữ thuật ngữ chính bằng tiếng Anh.'),
H('Câu 2 Phân tích và thiết kế lại 40 điểm'),
P('Một báo cáo so sánh thời gian trung bình hoàn thành bài thực hành của 4 lớp. Biểu đồ gốc là 3D pie chart, một miếng cho mỗi lớp, kích thước/góc theo thời gian; mỗi lớp một màu và có nhãn số.'),
T(['Lớp','Thời gian trung bình phút'],[['A','42'],['B','38'],['C','47'],['D','40']],[2.0,4.8]),
P('a Nêu mục tiêu của visualization 5 điểm. b Xác định items, attributes và types 15 điểm. c Phân tích marks/channels của bản gốc 10 điểm. d Chỉ ra vấn đề rồi vẽ redesign có mapping và justification 10 điểm.'),
H('Yêu cầu với hình vẽ'),
P('Hình phải có tên lớp, đơn vị phút, thang đo và đủ bốn giá trị. Lựa chọn biểu đồ cần hỗ trợ so sánh lớp nhanh nhất và chênh lệch giữa hai lớp. Nếu dùng dotplot với trục hẹp, ghi miền và ticks rõ.'),
P('Không đọc lời giải trước khi làm. Thang điểm tự chấm cho phần này ở trang 29.'))

page('Đề mô phỏng A Phần D3',
H('Câu 3 D3 Cars 30 điểm'),
P('Create an HTML page titled Midterm Challenge. Load cars.json. Each row has Name, Horsepower, Acceleration and Origin. Draw a vertical bar chart of Acceleration for the ten cars with the highest Horsepower.'),
T(['Yêu cầu','Điểm'],[['Đúng bar chart và đúng biến được vẽ','5'],['SVG 800 × 500, margins, scaleBand và scaleLinear','5'],['Hai axes, ticks và title trục y','5'],['Name làm nhãn các cột','5'],['Parse số, bỏ missing cần thiết, sort giảm Horsepower rồi lấy 10','5'],['Giá trị Acceleration ở phía trên từng cột','5']],[5.9,.9]),
H('Dữ liệu nhỏ để kiểm tra logic'),
T(['Name','Horsepower','Acceleration'],[['A','90','14'],['B','150','11'],['C','120','13'],['D','200','10'],['E','null','12'],['F','180','15']],[2.8,2,2]),
P('Nếu thử với bảng nhỏ này, yêu cầu top 10 trả về tất cả 5 bản ghi hợp lệ, theo thứ tự D, F, B, C, A. Chiều cao lần lượt 10, 15, 11, 13, 14. Đây là bảng kiểm logic, không thay thế dữ liệu cars.json trong đề.'),
H('Tự kiểm trước khi nộp'),
B('Sort và slice đúng thứ tự; so số thay vì chuỗi; giá trị null không biến thành 0.'),
B('y range đảo chiều; height là h trừ y(value); nhãn text không bị join với phần tử trục.'),
B('Mỗi cột có Name ở x, giá trị ở trên và số thuộc Acceleration.'),
P('Mã lời giải đầy đủ ở trang 18 đến 19. Hướng dẫn tự chấm ở trang 29.'))

page('Đề mô phỏng B Thiết kế và cột ngang',
P('90 phút  100 điểm  Phân bổ gợi ý 30 phút, 30 phút, 25 phút và 5 phút kiểm tra.'),
H('Câu 1 Phân tích biểu đồ 35 điểm'),
P('Một bảng gồm Region, Month, Revenue được vẽ thành cột trụ 3D trên hai trục nền Region và Month; chiều cao là Revenue, mỗi tháng một màu.'),
T(['Region','Jan','Feb','Mar'],[['North','120','150','130'],['Central','80','90','100'],['South','160','140','180']],[2.3,1.5,1.5,1.5]),
P('Đơn vị triệu đồng. a Data/types 10 điểm. b Marks/channels 5 điểm. c Problems 10 điểm. d Vẽ và giải thích redesign 10 điểm. Nêu rõ chọn ưu tiên so sánh độ lớn hay theo dõi xu hướng.'),
H('Câu 2 Thiết kế lớp học 35 điểm'),
T(['ID','GPA','Major','Group','Seat'],[['S1','80','IT','G1','1'],['S2','65','CS','G1','2'],['S3','90','DS','G2','3'],['S4','75','IT','G2','4'],['S5','85','CS','G2','5'],['S6','70','DS','G1','6']],[1.2,1.1,1.5,1.5,1.5]),
P('Sơ đồ gồm hai hàng: hàng trước 1 2 3 và hàng sau 4 5 6. Giữ đúng vị trí ghế, thể hiện GPA, ngành và group ID, nối mọi cặp cùng group. Chấm: vị trí 5; GPA 10; major 10; nhóm và links 10.'),
H('Câu 3 D3 cột ngang 30 điểm'),
P('Load cases.csv có Province, Country, Cases. Viết HTML title Midterm; parse Cases, giữ hàng Cases > 0; dùng nhãn Province / Country; SVG 900 × 600 và margins; x linear, y band; có axes, title và giá trị ở cuối thanh. Mỗi yêu cầu chính: load/parse/filter, SVG/scales, axes/title, nhãn, bars, values được 5 điểm.'),
P('Lời giải và mapping ở trang 30.'))

page('Đáp án bài tập từ một đến năm',
H('Bài 1'),
P('a N; b N; c O; d interval; e ratio; f ratio; g ratio; h interval; i O; j N; k N; l ratio. Lý do chung: identifier chỉ xác định danh tính; rank chỉ có thứ tự; mốc 0 Celsius và năm lịch tùy quy ước; tuổi, số lượng, khoảng cách và duration có mốc 0 mang nghĩa không có đại lượng.'),
H('Bài 2'),
P('a Bar chart hoặc dotplot, position/length trên cùng thang giúp so sánh. b Point với hue hoặc shape cho nominal, có legend. c Ô heatmap với lightness tăng theo nhiệt; giữ trục không gian hoặc hàng/cột đúng ngữ nghĩa. d Diverging scale với 0 ở màu trung tính và hai phía đối lập; không dùng categorical hue ngẫu nhiên.'),
H('Bài 3'),
P('Ví dụ đáp án: change blindness khiến khó so hai khung animation, dùng small multiples; khó phân biệt đỏ xanh khiến trạng thái tốt/xấu bị nhầm, thêm icon và label; diện tích khó ước lượng khiến bubble 40 và 60 khó so, đổi sang dotplot chung trục. Mỗi ý cần đủ hiện tượng, ví dụ cụ thể, quyết định thiết kế.'),
H('Bài 4'),
P('a Sai, số áo và mã ghế là nominal. b Sai, hue chủ yếu phân biệt identity. c Đúng. d Sai, height bằng h trừ y(value). e Đúng. f Sai, biến xếp hạng khác biến được vẽ; trong đề chiều cao là Acceleration. g Sai, phụ thuộc mark và nhiệm vụ; bar length thường cần 0. h Sai, CI cho mean thể hiện bất định của mean, không phải khoảng chứa 95% quan sát.'),
H('Bài 5'),
P('a Diện tích gấp 4 thì bán kính gấp 2. Lấy bán kính tỷ lệ trực tiếp với giá trị sẽ khiến diện tích tăng theo bình phương và làm sai encoding.'),
P('b y(40) là 180 px; height là 120 px; nhãn nằm ở y bằng 174 px. Đây là tọa độ trong vùng g đã translate, chưa cộng margin của SVG.'),
P('c Dữ liệu tăng 20%; chiều dài thấy được từ 10 lên 20 tăng 100%; lie factor bằng 5. Phải ghi rõ đang dùng biến thiên tương đối so với mốc ban đầu.'))

page('Đáp án bài tập từ sáu đến tám',
H('Bài 6'),
P('Items là ba ngành/khoa IT CS DS; department nominal; mean satisfaction quantitative theo thang điểm 0 đến 100, không mặc định tỷ lệ năng lực hay cảm xúc. Marks là rect; x position theo department; bar length từ baseline 70 theo score trừ 70; hue cũng theo department; text ghi số.'),
P('IT đến DS tăng 6 điểm, tương đương 6/78 xấp xỉ 7.69%. Thanh thấy được từ 8 đến 14 tăng 75%; lie factor xấp xỉ 9.75. Sửa 1: bar chart với y từ 0 đến 100. Sửa 2: dotplot cùng trục 70 đến 90 với ticks rõ, sắp 78, 82, 84. Không kết luận độ phân tán, cỡ mẫu hay khác biệt có ý nghĩa thống kê khi chỉ có mean.'),
H('Bài 7'),
C('''const data = raw
  .sort((a, b) => b.Horsepower - a.Horsepower)
  .slice(0, 10);
const y = d3.scaleLinear()
  .domain([0, max]).range([h, 0]);
bars.attr("y", d => y(d.Acceleration))
  .attr("height", d => h - y(d.Acceleration));'''),
P('Bốn lỗi chính: slice quá sớm; sort tăng thay vì giảm; y range chưa đảo; height sai. Nếu cần giữ raw nguyên vẹn, dùng [...raw].sort(...). Dữ liệu thực còn phải parse và loại missing trước đoạn này.'),
H('Bài 8'),
P('Giữ tọa độ bàn; node theo student ID; GPA bằng mini bar, ngành bằng hue cộng chữ ngành, nhóm bằng nhãn và links. Với n người trong nhóm cần n nhân (n trừ 1) chia 2 links nếu mọi cặp được nối. Nét mảnh dưới node và highlight theo nhóm giúp giảm clutter mà không đổi sơ đồ bàn.'),
P('Phương án khác vẫn đúng nếu đủ thuộc tính, không tạo thứ tự giả cho nominal và giải thích được tradeoff. Không nhất thiết phải dùng nhiều màu hoặc nhiều kích thước đồng thời.'))

page('Lời giải đề mô phỏng A',
H('Câu 1 Tự chấm 30 điểm'),
P('Mỗi giới hạn tối đa 10 điểm: giải thích hiện tượng 3, ví dụ đúng 3, hệ quả thiết kế có liên hệ 4. Ví dụ bộ ba change blindness, color vision deficiency và area judgment ở trang 6. Ba tên không có diễn giải chưa đủ điểm của một câu hoàn chỉnh.'),
H('Câu 2 Tự chấm 40 điểm'),
P('Mục tiêu 5: so sánh thời gian trung bình của bốn lớp và tìm lớp nhanh nhất. Data 15: item là lớp; class N; duration Q ratio, đơn vị phút; mean là thống kê tổng hợp, không phải thời gian của mỗi sinh viên.'),
P('Encoding 10: các miếng pie dạng area, angle/area theo duration, hue theo class, text theo class và số; chiều sâu tạo phối cảnh nhưng không mã hóa biến dữ liệu hữu ích.'),
P('Redesign 10: bar ngang sắp B 38, D 40, A 42, C 47, trục x từ 0 có đơn vị phút; hoặc dotplot cùng thang. Giải thích: các thời gian trung bình không phải các phần của một tổng có ngữ nghĩa; 3D còn làm lệch cảm nhận, trong khi vị trí/length chung trục hỗ trợ so trực tiếp. B nhanh nhất, chậm hơn B nhiều nhất là C với 9 phút.'),
H('Câu 3 Tự chấm 30 điểm'),
P('Dùng mã mẫu trang 18 và 19. Đánh dấu sáu tiêu chí trang 25, mỗi tiêu chí 5. Với phần code chưa hoàn chỉnh, chấm dựa trên phần thể hiện đúng; đừng tự cho đủ chỉ vì có gọi tên một hàm.'),
T(['Lỗi cần nhận ra','Cách kiểm'],[['Nhầm trường','Chiều cao và value label đều là Acceleration.'],['Sai top k','Thứ tự bảng nhỏ phải D F B C A.'],['Sai hình học','y giảm khi value tăng; height tăng khi value tăng.'],['Nhãn mất hoặc trùng','Domain key riêng, tickFormat hiển thị Name.']],[2.0,4.8]),
P('Đây là thang tự chấm đề mô phỏng. Khi học nhóm, nhờ người khác đọc hình redesign mà không nghe giải thích trước để kiểm khả năng truyền đạt.'))

page('Lời giải đề mô phỏng B',
H('Câu 1 35 điểm'),
P('Data 10: mỗi cặp Region và Month là một observation; Region nominal; Month temporal/ordinal trong ba tháng đã cho; Revenue quantitative ratio, triệu đồng. Encoding 5: cột trụ; x và depth position cho Region/Month; height cho Revenue; hue theo Month.'),
P('Problems 10: occlusion, perspective, khó căn thẳng giữa các dãy, màu lặp cho thời gian không giúp đọc trend nhiều bằng thứ tự trục. Redesign 10: grouped bars chung baseline 0 nếu so các mức; x là Region, các bar trong nhóm theo Month, height là Revenue. Hoặc line chart theo Jan Feb Mar, một line mỗi Region, y cùng thang để so xu hướng. Cần hình và legend đủ ba region nếu chọn line.'),
H('Câu 2 35 điểm'),
P('Vẽ hai hàng đúng 1 2 3 và 4 5 6 được 5. GPA qua length trên thang cố định được 10. Major qua hue kèm label được 10. Group qua nhãn G1 G2 và đủ links được 10. G1: S1 S2 S6; G2: S3 S4 S5. Mỗi nhóm ba người có ba cạnh; tổng sáu cạnh.'),
H('Câu 3 30 điểm'),
P('Áp dụng khung COVID trang 20 đến 21, thay W 900 và H 600; bỏ đoạn tìm ngày; dùng loader dưới đây. Nên đặt nhãn số bên ngoài cuối thanh để không mất chữ trên thanh nhỏ.'),
C('''const raw = await d3.csv("cases.csv");
const data = raw.map((d, i) => ({
  key: String(i),
  label: [d.Province, d.Country].filter(Boolean).join(" / "),
  value: d.Cases?.trim() ? +d.Cases : NaN
})).filter(d => Number.isFinite(d.value) && d.value > 0);
// In the value-label selection:
// x: d => x(d.value) + 5
// text-anchor: start; fill: black
// Reserve enough right margin for the largest label.'''),
P('Chấm sáu mục × 5 như đề. Công thức bar ngang: x 0, y y(key), width x(value), height y.bandwidth(). Nếu data rỗng cần thông báo; label trên trục phải giữ cả Province và Country.'))

page('Ôn nhanh trước khi làm bài',
H('Mười câu hỏi tự kiểm'),
B('Item là gì, một hàng hoặc mark đại diện cho đơn vị nào?'),
B('Nominal, ordinal và quantitative đã phân biệt theo nghĩa thay vì kiểu số/chữ chưa?'),
B('Mỗi attribute có một mapping cụ thể sang channel nào?'),
B('Thiết kế có expressiveness và effectiveness phù hợp nhiệm vụ không?'),
B('Giới hạn thị giác đã có ví dụ và implication chưa?'),
B('Redesign có hình, scale, units, labels, legend và justification chưa?'),
B('Dữ liệu thiếu, số 0 và trạng thái đặc biệt có bị trộn lẫn không?'),
B('D3 đã parse trước khi sort và filter chưa?'),
B('Sort theo trường nào và vẽ trường nào; có bị tráo không?'),
B('Bar dọc có y đảo chiều và height bằng h trừ y(value) không?'),
H('Kế hoạch học gợi ý trong ba buổi'),
T(['Buổi','Nội dung','Kết quả cần tự làm'],[['1','Trang 3 đến 11 và bài 1 đến 5','Phân loại và giải thích không nhìn tài liệu.'],['2','Trang 12 đến 21 và bài 6 đến 8','Vẽ lại một hình và viết code bar dọc/ngang.'],['3','Hai đề mô phỏng, mỗi đề 90 phút','Chấm lỗi rồi viết lại phần yếu nhất.']],[.8,2.8,3.2]),
H('Từ vựng dễ cần dùng trong bài thi'),
P('Items = đối tượng; attributes = thuộc tính; encoding = mã hóa; marks = phần tử hình học; channels = kênh thị giác; common scale = thang chung; occlusion = che khuất; baseline = mốc gốc; salience = độ nổi bật; clutter = rối; small multiples = nhiều biểu đồ nhỏ; justification = giải thích căn cứ lựa chọn.'))

page('Nguồn học và đối chiếu',
P('Số trang dưới đây là trang PDF đếm từ 1, không phải số in trên slide. Riêng tập C2 Popout có số in bắt đầu khoảng 60 nên hai hệ đánh số khác nhau.'),
T(['Nguồn do người học cung cấp','Vị trí sử dụng chính'],[['C1-Data Science and Visualization.pdf','Khái niệm 4 đến 7; lựa chọn visualization 13 đến 21; human 31.'],['C2-Perception-Color.pdf','Perception 3 đến 4; thị giác 20 đến 21; HSV 28; colormap 35 đến 40; màu tương đối 49.'],['C2-Perception-Popout-Change blindness-gestalt.pdf','Popout 2 và 11; change blindness 19 đến 28; Gestalt 29 đến 58.'],['C3-Data.pdf','Data và dataset types 5 đến 22; attribute scales 27 đến 36.'],['C4-Marks-Channels.pdf','Marks và channels 3 đến 15; channel accuracy 19 đến 48.'],['C5-Design guideline.pdf','Integrity 9 đến 31; alternatives 34 đến 43; design 49 đến 73.'],['it138iu_2023_HK1_midterm.pdf','Câu 1 và 2 trang 2 đến 3; D3 trang 3 đến 4.'],['it138iu_2026_HK1_midterm.pdf','Giới hạn và phân tích trang 2; cars trang 2 đến 4.'],['it138iu_2026_HK2_midterm.pdf','Giới hạn và phân tích trang 2; cars trang 2 đến 4.']],[3.5,3.3]),
H('Tài liệu kỹ thuật và thống kê bổ sung'),
P('D3 fetch và parsing: https://d3js.org/d3-fetch'),
P('Band scales: https://d3js.org/d3-scale/band'),
P('Data join: https://d3js.org/d3-selection/joining'),
P('CI cho mean: NIST Engineering Statistics Handbook, mục 1.3.5.2, https://www.itl.nist.gov/div898/handbook/eda/section3/eda352.htm'),
P('Các hình Gestalt, heatmap và bài tập điểm số được tự vẽ. Hình lớp học lấy vị trí và dữ liệu từ đề 2023; dotplot chỉ trích các giá trị đọc rõ trong đề HK2. Các phương án thiết kế là lời giải tham khảo để luyện tư duy.'))

# Save runnable reference solutions too; the document remains the main deliverable.
(OUT/'cars_solution.html').write_text(cars1+'\n'+cars2,encoding='utf-8')
(OUT/'covid_solution.html').write_text(covid1+'\n'+covid2,encoding='utf-8')
(ROOT/'tmp'/'dsdv_sources'/'pages.json').write_text(json.dumps(pages,ensure_ascii=False,indent=2),encoding='utf-8')

styles={
 'p':ParagraphStyle('p',fontName='Arial',fontSize=10.8,leading=15.2,spaceAfter=7),
 'bullet':ParagraphStyle('bullet',fontName='Arial',fontSize=10.8,leading=15.2,spaceAfter=7,leftIndent=12,firstLineIndent=-9),
 'h':ParagraphStyle('h',fontName='Arial-Bold',fontSize=12.3,leading=16,spaceBefore=9,spaceAfter=6,keepWithNext=True),
 'title':ParagraphStyle('title',fontName='Arial-Bold',fontSize=21,leading=26,spaceAfter=15),
 'cell':ParagraphStyle('cell',fontName='Arial',fontSize=9.7,leading=13),
 'cellhead':ParagraphStyle('cellhead',fontName='Arial-Bold',fontSize=9.7,leading=13,textColor=colors.white),
 'caption':ParagraphStyle('caption',fontName='Arial-Italic',fontSize=9.2,leading=12,spaceAfter=8),
 'code':ParagraphStyle('code',fontName='Consolas',fontSize=8.7,leading=11.2,spaceAfter=9),
}
def para(text,style):return Paragraph(html.escape(text),styles[style])
story=[]
for idx,(title,blocks) in enumerate(pages):
 if idx:story.append(PageBreak())
 story.append(para(title,'title'))
 for kind,v in blocks:
  if kind in ['p','h','bullet']:
   story.append(para(('• ' if kind=='bullet' else '')+v,kind))
  elif kind=='code':story.append(Preformatted(v,styles['code']))
  elif kind=='figure':
   name,cap,w=v;im=Image.open(ASSET/name); height=w*72*im.height/im.width
   story.extend([RLImage(str(ASSET/name),width=w*72,height=height),Spacer(1,5),para(cap,'caption')])
  elif kind=='table':
   headers,rows,widths=v; cells=[[para(x,'cellhead') for x in headers]]+[[para(str(x),'cell') for x in row] for row in rows]
   tb=Table(cells,colWidths=[w*72 for w in widths] if widths else None,repeatRows=1,hAlign='LEFT')
   tb.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#24445f')),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#f2f6f9')]),('GRID',(0,0),(-1,-1),.45,colors.HexColor('#d9d9d9')),('VALIGN',(0,0),(-1,-1),'MIDDLE'),('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7),('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6)]))
   story.extend([tb,Spacer(1,9)])
def footer(c,doc):
 c.setFont('Arial',8.5);c.setFillColor(colors.HexColor('#555555'));c.drawString(48,25,'DSDV  IT138IU  Ôn tập và luyện đề');c.drawRightString(564,25,str(doc.page))
pdfpath=OUT/'DSDV_On_tap_va_luyen_de.pdf'
SimpleDocTemplate(str(pdfpath),pagesize=(612,792),rightMargin=48,leftMargin=48,topMargin=42,bottomMargin=43,title='Ôn tập giữa kỳ DSDV',author='Tài liệu tự học').build(story,onFirstPage=footer,onLaterPages=footer)

doc=Document();sec=doc.sections[0];sec.page_width=Inches(8.5);sec.page_height=Inches(11)
for st in doc.styles:
 for border in list(st.element.iter(qn('w:pBdr'))):border.getparent().remove(border)
sec.left_margin=sec.right_margin=Inches(.67);sec.top_margin=Inches(.59);sec.bottom_margin=Inches(.6)
normal=doc.styles['Normal'];normal.font.name='Arial';normal.font.size=Pt(10.8);normal.paragraph_format.line_spacing=1.05;normal.paragraph_format.space_after=Pt(7)
for name,size in [('Title',21),('Heading 1',12.3)]:
 st=doc.styles[name];st.font.name='Arial';st.font.size=Pt(size);st.font.color.rgb=RGBColor(0,0,0);st.font.bold=True
 st.paragraph_format.space_after=Pt(12 if name=='Title' else 6)
 st.paragraph_format.space_before=Pt(0 if name=='Title' else 8)
for idx,(title,blocks) in enumerate(pages):
 if idx:doc.add_page_break()
 doc.add_paragraph(title,'Title' if idx==0 else 'Title')
 for kind,v in blocks:
  if kind in ['p','bullet','h']:
   pp=doc.add_paragraph(('• ' if kind=='bullet' else '')+v,'Heading 1' if kind=='h' else 'Normal')
   if kind=='bullet':pp.paragraph_format.left_indent=Inches(.13);pp.paragraph_format.first_line_indent=Inches(-.13)
  elif kind=='code':
   pp=doc.add_paragraph();pp.paragraph_format.line_spacing=1;pp.paragraph_format.space_after=Pt(9)
   rr=pp.add_run(v);rr.font.name='Consolas';rr.font.size=Pt(8.7)
  elif kind=='figure':
   name,cap,w=v;doc.add_picture(str(ASSET/name),width=Inches(w));pp=doc.add_paragraph(cap);pp.runs[0].italic=True;pp.runs[0].font.size=Pt(9.2)
  elif kind=='table':
   headers,rows,widths=v;tb=doc.add_table(rows=1,cols=len(headers));tb.alignment=WD_TABLE_ALIGNMENT.LEFT;tb.autofit=False
   for j,w in enumerate(widths):tb.columns[j].width=Inches(w)
   for ri,row in enumerate([headers]+rows):
    cells=tb.rows[0].cells if ri==0 else tb.add_row().cells
    for j,txt in enumerate(row):
     cell=cells[j];cell.width=Inches(widths[j]);cell.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
     tcPr=cell._tc.get_or_add_tcPr();borders=OxmlElement('w:tcBorders')
     for edge in ['top','left','bottom','right']:
      el=OxmlElement('w:'+edge);el.set(qn('w:val'),'single');el.set(qn('w:sz'),'4');el.set(qn('w:color'),'D9D9D9');borders.append(el)
     tcPr.append(borders);sh=OxmlElement('w:shd');sh.set(qn('w:fill'),'24445F' if ri==0 else ('F2F6F9' if ri%2==0 else 'FFFFFF'));tcPr.append(sh)
     margins=OxmlElement('w:tcMar')
     for edge in ['top','left','bottom','right']:
      el=OxmlElement('w:'+edge);el.set(qn('w:w'),'80');el.set(qn('w:type'),'dxa');margins.append(el)
     tcPr.append(margins)
     pp=cell.paragraphs[0];pp.paragraph_format.space_after=Pt(2);pp.paragraph_format.space_before=Pt(2)
     rr=pp.add_run(str(txt));rr.font.size=Pt(9.7)
     if ri==0:rr.bold=True;rr.font.color.rgb=RGBColor(255,255,255)
    trpr=tb.rows[ri]._tr.get_or_add_trPr();cant=OxmlElement('w:cantSplit');trpr.append(cant)
    if ri==0:repeat=OxmlElement('w:tblHeader');trpr.append(repeat)
   doc.add_paragraph().paragraph_format.space_after=Pt(0)
footerp=sec.footer.paragraphs[0];footerp.alignment=WD_ALIGN_PARAGRAPH.RIGHT
rr=footerp.add_run('DSDV  IT138IU  |  ');rr.font.name='Arial';rr.font.size=Pt(8)
fld=OxmlElement('w:fldSimple');fld.set(qn('w:instr'),'PAGE');footerp._p.append(fld)
doc.core_properties.title='Ôn tập giữa kỳ DSDV';doc.core_properties.author='';doc.core_properties.subject='Lý thuyết và bài tập giữa kỳ IT138IU'
docxpath=OUT/'DSDV_On_tap_va_luyen_de.docx';doc.save(docxpath)
print(json.dumps({'pages_planned':len(pages),'pdf':str(pdfpath),'docx':str(docxpath)},ensure_ascii=True))
