import socket
import json

def connect_to_server():
    # Kết nối đến server
    HOST = '127.0.0.1'
    PORT = 8000
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, PORT))
    return client_socket

def display_menu():
    # Hiển thị menu cho người dùng và lấy yêu cầu tra cứu
    print('1. Tra cứu danh sách các đồng tiền và giá qui đổi của đồng tiền tương ứng.')
    print('2. Tra cứu 1 đồng tiền và giá qui đổi của đồng tiền đó.')
    print('3. Hủy kết nối.')
    choice = input('Vui lòng chọn tính năng (1,2 hoặc 3): ')

    if choice == '1':
        request = {'status': 'OK', 'data': 'MARKET ALL'}
    elif choice == '2':
        coin_symbol = input('Nhập mã của đồng tiền (VD: BTC): ')
        request_data = 'MARKET ' + coin_symbol.upper()
        request = {'status': 'OK', 'data': request_data}
    elif choice == '3':
        request = {'status': 'CLOSE', 'data': ''}
    else:
        print('Bạn đã nhập lựa chọn không hợp lệ!')
        request = None

    return request

def send_request(client_socket, request):
    # Gửi yêu cầu đến server và nhận kết quả trả về
    print("CLient: Sending request " + request['data'])
    request_str = json.dumps(request) # Chuyển đổi từ dict sang chuỗi JSON
    client_socket.send(request_str.encode())
    response_str = client_socket.recv(1024).decode()
    response = json.loads(response_str)
    return response

def display_result(result):
    # Hiển thị kết quả tra cứu cho người dùng
    result = result['data']
    if isinstance(result, dict):
        print('Server: ')
        for coin_name, coin_price in result.items():
            print(coin_name, ':', coin_price)
    elif isinstance(result, float):
        print('Server: Giá của đồng tiền là', result)
    else:
        print(result)

if __name__ == '__main__':
    client_socket = connect_to_server()

    while True:
        request = display_menu()

        if request['status'] == 'OK':
            result = send_request(client_socket, request)
            display_result(result)
        elif request['status'] == 'CLOSE':
            print('Đóng kết nối')
            break
    client_socket.close()