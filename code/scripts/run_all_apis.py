"""
启动所有API服务

使用multiprocessing启动所有API服务
"""

import multiprocessing
import subprocess
import time
import sys
import os
# 添加code目录到Python路径
code_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, code_dir)


def run_api(module_name, port):
    """运行API服务"""
    cmd = ["uvicorn", f"{module_name}.api:app", "--host", "0.0.0.0", "--port", str(port)]
    subprocess.run(cmd)


def main():
    """主函数"""
    apis = [
        ("multimodal_kg", 8000),
        ("temporal_kg", 8001),
        ("llm_reasoning", 8002),
        ("usl", 8003),
    ]
    
    processes = []
    
    print("启动所有API服务...")
    for module_name, port in apis:
        print(f"启动 {module_name} API (端口 {port})...")
        p = multiprocessing.Process(target=run_api, args=(module_name, port))
        p.start()
        processes.append(p)
        time.sleep(2)  # 等待服务启动
    
    print("\n✅ 所有API服务已启动")
    print("按 Ctrl+C 停止所有服务")
    
    try:
        for p in processes:
            p.join()
    except KeyboardInterrupt:
        print("\n正在停止所有服务...")
        for p in processes:
            p.terminate()
        print("✅ 所有服务已停止")


if __name__ == "__main__":
    main()
