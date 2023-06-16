import socket
import sqlite3
import json
import ast
import ssl
import threading


def send_get_request(url, headers=None):
    # Phân tích URL để lấy thông tin về host và đường dẫn
    host, path = parse_url(url)
    
    # Tạo ngữ cảnh SSL
    context = ssl.create_default_context()
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Bọc socket với SSL
    client_socket = context.wrap_socket(client_socket, server_hostname=host)
    client_socket.connect((host, 443))

    # Gửi yêu cầu GET
    request = build_get_request(host, path, headers)
    client_socket.sendall(request.encode())
    
    # Nhận và trả về phản hồi từ máy chủ
    header, content = receive_response(client_socket)

    substring = b',{"id":1958,'
    content = content.split(substring)[0]
    content += b']}}'

    client_socket.close()
    return header, content

def parse_url(url):
    # Tách host và path từ URL
    url_parts = url.split('/')
    host = url_parts[2]
    path = '/' + '/'.join(url_parts[3:])
    return host, path

def build_get_request(host, path, headers):
    request = f"GET {path} HTTP/1.1\r\n"
    request += f"Host: {host}\r\n"
    
    if headers:
        for key, value in headers.items():
            request += f"{key}: {value}\r\n"
    
    request += "\r\n"
    return request

def receive_response(client_socket):
    response = b""
    while True:
        data = client_socket.recv(4096)
        response += data
        if b"\r\n0\r\n\r\n" in response:
            break

    # Chia phản hồi thành phần tiêu đề và nội dung
    header_end = response.find(b"\r\n\r\n")
    header = response[:header_end]
    content_start = header_end + 4
    content_end = response.rfind(b"\r\n0\r\n\r\n")
    content = response[content_start:content_end]
    content = content[content.index(b'{'):]

    return header, content

def get_status_code(header):
    # Tách mã trạng thái từ phản hồi HTTP
    status_line = header.split('\r\n')[0]
    status_code = int(status_line.split(' ')[1])
    return status_code

def response_to_json(data):
    data = data.decode('utf8')
    data_start = data.find('"data":[') + 8
    data_section = data[data_start:-5]

    values = []
    start_index = 0
    while True:
        id_start = data_section.find('"id":', start_index)
        if id_start == -1:
            break

        id_end = data_section.find(',', id_start)
        id_value = data_section[id_start + 5:id_end]

        name_start = data_section.find('"name":', id_end)
        name_end = data_section.find(',', name_start)
        name_value = data_section[name_start + 8:name_end]

        symbol_start = data_section.find('"symbol":', name_end)
        symbol_end = data_section.find(',', symbol_start)
        symbol_value = data_section[symbol_start + 10:symbol_end]

        price_start = data_section.find('"price":', symbol_end)
        price_end = data_section.find(',', price_start)
        price_value = data_section[price_start + 8:price_end]

        values.append({"id": id_value, "name": name_value, "symbol": symbol_value, "price": price_value})

        start_index = price_end

    return values
def get_all_coins():
    # Lấy danh sách các đồng tiền và giá của chúng
    conn = sqlite3.connect('coin.db')
    cursor = conn.cursor()

    cursor.execute('SELECT coin_name, coin_price FROM coin')
    result = cursor.fetchall()

    conn.close()

    coins_dict = dict(result)
    return coins_dict


def get_coin_price(coin_symbol):
    # Lấy giá của một đồng tiền cụ thể
    conn = sqlite3.connect('coin.db')
    cursor = conn.cursor()

    cursor.execute( 'SELECT coin_price FROM coin WHERE coin_symbol = ?', (coin_symbol,))
    result = cursor.fetchone()

    conn.close()

    return float(result[0])


def handle_client(client_socket):
    # Xử lý yêu cầu từ một client
    while True:
        # Nhận yêu cầu từ client
        request_str = client_socket.recv(4096).decode()
        if not request_str:
            break
        request = json.loads(request_str)['data']
        print('Client: ' + request)
        # Xử lý yêu cầu
        if request == 'MARKET ALL':
            response_data = get_all_coins()
        elif 'MARKET' in request:
            coin_symbol = request.split()[1]
            response_data = get_coin_price(coin_symbol)
        else:
            response_data = 'Invalid request'

        # Gửi kết quả trả về cho client
        response = {'status': 'OK', 'data': response_data}
        response_str = json.dumps(response)
        client_socket.send(response_str.encode())


if __name__ == '__main__':
    HOST = '127.0.0.1'
    PORT = 8000
    # Sử dụng hàm send_get_request() với headers
    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
    headers = {'Accepts': 'application/json',
           'X-CMC_PRO_API_KEY': '83a2a200-4303-4bf8-b9e1-801b84ac7c31'}
    header, content = send_get_request(url, headers)

    status_code = get_status_code(header.decode())

    json_data = response_to_json(content)
    conn = sqlite3.connect('coin.db')
    cursor = conn.cursor()
    cursor.execute(
        'CREATE TABLE IF NOT EXISTS coin (coin_id INTEGER PRIMARY KEY, coin_name TEXT, coin_symbol TEXT, coin_price REAL)')
    for coin in json_data:
        if coin['name'] in ['Bitcoin', 'Ethereum', 'Binance Coin', 'Cardano', 'XRP', 'Dogecoin', 'Polkadot', 'Solana', 'USD Coin', 'Terra']:
            coin_id = coin['id']
            coin_name = coin['name']
            coin_symbol = coin['symbol']
            coin_price = coin['price']
            cursor.execute('UPDATE coin SET coin_price = ? WHERE coin_symbol = ?', (coin_price, coin_symbol))
    conn.commit()
    conn.close()


    # Thiết lập server
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(1)

    print('Server is running on {}:{}'.format(HOST, PORT))

    while True:
        client_socket, address = server_socket.accept()
        print('Client is connected from', address)

        # Tạo một luồng mới để xử lý yêu cầu từ client
        client_thread = threading.Thread(target=handle_client, args=(client_socket,))
        client_thread.start()
