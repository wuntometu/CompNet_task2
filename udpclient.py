import socket
import time
import struct
import statistics

TIMEOUT = 0.1             # 超时时间
NUM_REQUESTS = 12         # 发送12个request数据包

# 命令行方式下指定serverIp serverPort.
SERVER_IP = input("请输入服务器IP地址：")
SERVER_PORT = int(input("请输入服务器端口号："))

received_packets = 0    # 接收到的 UDP 包数量
timed_out_packets = 0   # 超时的 UDP 包数量
rtt_values = []         # 用于存储 RTT 值的列表
start_time = 0
end_time = 0

# 创建 UDP 套接字，IPv4地址，数据包套接字（两个参数）
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# 计算 RTT 的函数，单位毫秒
def calculate_rtt(send_time):
    return (time.time() * 1000) - send_time

# 发送和接收数据的函数
def send_and_receive(seq_no):
    global received_packets, timed_out_packets, start_time, end_time

    # 数据包内容
    ver = 2
    seq_bytes = seq_no.to_bytes(2, byteorder='big')     # 2字节seq no. 大端序适合网络传输
    ver_byte = ver.to_bytes(1, byteorder='big')         # 1字节ver.
    other_data = b'X' * 200                             # 无意义的字母序列
    message = seq_bytes + ver_byte + other_data

    # 发送消息
    send_time = time.time() * 1000
    client_socket.sendto(message, (SERVER_IP, SERVER_PORT))
    print(f"发送序号为 {seq_no} 的数据包")

    # 接收响应或处理超时
    client_socket.settimeout(TIMEOUT)
    try:
        response, server_address = client_socket.recvfrom(2048)
        if len(response) >= 3:  # 假设响应至少包含 3 个字节
            recv_seq_no = int.from_bytes(response[0:2], byteorder='big')
            end_time = struct.unpack('I', response[2:6])[0]
            if start_time == 0:
                start_time = end_time
            rtt = calculate_rtt(send_time)
            rtt_values.append(rtt)
            received_packets += 1
            print(f"{recv_seq_no}, {server_address[0]}, {rtt}")
        else:
            raise ValueError("响应格式错误")
    except socket.timeout:
        timed_out_packets += 1
        print(f"{seq_no}, request time out")



# 主循环发送请求
for i in range(1, NUM_REQUESTS + 1):
    send_and_receive(i)

# 计算丢包率
total_packets = received_packets + timed_out_packets
packet_loss = (timed_out_packets / total_packets) * 100 if total_packets > 0 else 0

# 计算 RTT 统计信息
max_rtt = max(rtt_values) if rtt_values else 0
min_rtt = min(rtt_values) if rtt_values else 0
avg_rtt = statistics.mean(rtt_values) if rtt_values else 0
rtt_stdev = statistics.stdev(rtt_values) if len(rtt_values) > 1 else 0
sys_time = end_time - start_time

# 打印汇总信息
print("\n--- 汇总信息 ---")
print(f"接收到的 UDP 包数量: {received_packets}")
print(f"丢包率: {packet_loss:.2f}%")
print(f"最大 RTT: {max_rtt:.2f} 毫秒")
print(f"最小 RTT: {min_rtt:.2f} 毫秒")
print(f"平均 RTT: {avg_rtt:.2f} 毫秒")
print(f"RTT 标准差: {rtt_stdev:.2f} 毫秒")
print(f"server整体响应时间: {sys_time:.2f} 毫秒")

# 关闭套接字
client_socket.close()
