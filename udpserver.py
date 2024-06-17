import socket
import random
import struct
import time

# 常量定义
SERVER_IP = 'localhost'  # 服务器 IP 地址，根据实际情况修改
SERVER_PORT = 12345       # 服务器端口号，根据实际情况修改
DROP_RATE = 0.2           # 丢包率 (20% 的丢包率)
TIME_FORMAT = '%H-%M-%S'  # 服务器时间的格式化字符串

# 创建 UDP 套接字
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((SERVER_IP, SERVER_PORT))

# 模拟丢包的函数
def simulate_packet_drop():
    return random.random() < DROP_RATE

# 获取当前服务器时间的函数
def get_server_time():
    return time.time()

# 主循环，监听来自客户端的请求
print("UDP 服务器正在监听...")
while True:
    # 接收来自客户端的消息
    message, client_address = server_socket.recvfrom(2048)

    # 模拟丢包
    if simulate_packet_drop():
        print(f"丢弃来自 {client_address} 的数据包")
        continue

    # 解析消息
    seq_no = int.from_bytes(message[0:2], byteorder='big')
    ver = int.from_bytes(message[2:3], byteorder='big')
    other_data = message[3:]

    # 准备服务器响应
    response_seq_no = seq_no
    server_time = get_server_time()
    response = (response_seq_no).to_bytes(2, byteorder='big') + struct.pack('d', server_time)

    # 将响应发送回客户端
    server_socket.sendto(response, client_address)
    print(f"向客户端发送序号为 {seq_no} 的响应至 {client_address}")

# 关闭套接字
server_socket.close()
