#!/usr/bin/env python3
"""
运行所有检查工具

一键运行所有项目检查工具
"""

import sys
import subprocess
from pathlib import Path


def run_script(script_name: str, description: str) -> bool:
    """运行脚本"""
    print(f"\n{'='*60}")
    print(f"运行: {description}")
    print(f"{'='*60}")
    
    script_path = Path(__file__).parent / script_name
    
    if not script_path.exists():
        print(f"❌ 脚本不存在: {script_path}")
        return False
    
    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=Path(__file__).parent.parent,
            capture_output=False
        )
        return result.returncode == 0
    except Exception as e:
        print(f"❌ 运行失败: {e}")
        return False


def main():
    """主函数"""
    print("="*60)
    print("项目全面检查")
    print("="*60)
    
    checks = [
        ("project_health_check.py", "项目健康检查"),
        ("validate_docs.py", "文档验证"),
        ("check_links.py", "链接检查"),
    ]
    
    results = {}
    
    for script_name, description in checks:
        success = run_script(script_name, description)
        results[description] = success
    
    # 汇总结果
    print("\n" + "="*60)
    print("检查结果汇总")
    print("="*60)
    
    for description, success in results.items():
        status = "✅ 通过" if success else "❌ 失败"
        print(f"{status} - {description}")
    
    all_passed = all(results.values())
    
    if all_passed:
        print("\n🎉 所有检查通过！")
        sys.exit(0)
    else:
        failed_count = sum(1 for v in results.values() if not v)
        print(f"\n⚠️  {failed_count} 个检查失败")
        sys.exit(1)


if __name__ == "__main__":
    main()
