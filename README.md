# Socket_API_sv_client
1.	Đề tài nhóm: Socket – Server – Client - API
Viết ứng dụng cho phép tra cứu thông tin giá cryptocurrency, theo mô hình client-server, sử dụng Socket với các chức năng như sau: 
•	Tra cứu danh sách các đồng tiền và giá qui đổi của đồng tiền tương ứng.
•	Tra cứu 1 đồng tiền và giá qui đổi của đồng tiền đó.
2.	Kịch bản giao tiếp của chương trình:
Chương trình này sử dụng giao thức trao đổi thông điệp giữa client và server thông qua kết nối socket. Dữ liệu được mã hóa bằng định dạng JSON để dễ dàng phân tích.
Khi client kết nối đến server, nó có thể yêu cầu danh sách tất cả các đồng tiền có sẵn hoặc yêu cầu giá của một đồng tiền cụ thể.
Thông điệp được gửi từ client đến server và ngược lại có cấu trúc như sau:
•	Để yêu cầu danh sách các đồng tiền có sẵn, client gửi một thông điệp yêu cầu có cấu trúc như sau: request = {'status': 'OK', 'data': 'MARKET ALL'}
•	Để yêu cầu giá của một đồng tiền cụ thể, client gửi một thông điệp yêu cầu có cấu trúc như sau: request_data = 'MARKET ' + coin_symbol.upper()
o	        			request = {'status': 'OK', 'data': request_data}
Server sẽ trả về kết quả dưới dạng một thông điệp với cấu trúc như sau: {'status': 'OK', 'data': response_data}
Cơ sở dữ liệu trong chương trình này được tổ chức dưới dạng một từ điển (dictionary) trong mã nguồn của server, server dùng thư viện thứ 3 lấy dữ liệu kết hợp cả API và CSDL bằng cách lấy dữ liệu từ API và lưu vào CSDL. Dùng thư viện bên thứ 3 ở phía ứng dụng server để tải dữ liệu từ API về, cụ thể là thư viện HTTP client để giao tiếp với API. Nó lưu trữ thông tin về tên và giá của 10 đồng tiền phổ biến.
3.	Môi trường lập trình: Python
Thư viện cài đặt:
-	Socket
-	Sqlite3
-	json
-	ssl
-	threading
4.	Hướng dẫn sử dụng:
Chạy chương trình:
-	Đầu tiên ta chạy server trước để để lắng nghe những request từ client
Kết nối tới server:
-	Chạy file client.py tại server sẽ xuất hiện thông báo:  
-	Tại client sẽ có 1 menu để chúng ta lựa chọn:
Khi chọn chức năng 1:
- Đưa ra danh sách các đồng tiền
Khi chọn chức năng 2:
-	Chương trình sẽ yêu cầu ta nhập mã loại tiền cần tra cứu VD: BTC
- Server sẽ trả về thông tin loại tiền tương ứng cho client
Đa luồng:

 
 

