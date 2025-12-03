#!/usr/bin/env python3
"""
项目健康检查

检查项目的整体健康状况，包括：
- 代码结构
- 文档完整性
- 配置文件
- 测试覆盖
"""

import os
import sys
from pathlib import Path
from typing import Dict, List


class HealthChecker:
    """健康检查器"""
    
    def __init__(self, root_dir: str = "."):
        self.root_dir = Path(root_dir).resolve()
        self.checks: Dict[str, bool] = {}
        self.issues: List[str] = []
        
    def check_directory_structure(self):
        """检查目录结构"""
        required_dirs = [
            "code",
            "docs",
            "themes",
            "view",
            "docker",
            "examples"
        ]
        
        missing_dirs = []
        for dir_name in required_dirs:
            dir_path = self.root_dir / dir_name
            if not dir_path.exists():
                missing_dirs.append(dir_name)
        
        if missing_dirs:
            self.checks["目录结构"] = False
            self.issues.append(f"缺失目录: {', '.join(missing_dirs)}")
        else:
            self.checks["目录结构"] = True
    
    def check_code_modules(self):
        """检查代码模块"""
        code_dir = self.root_dir / "code"
        if not code_dir.exists():
            self.checks["代码模块"] = False
            self.issues.append("code目录不存在")
            return
        
        required_modules = [
            "api_gateway",
            "multimodal_kg",
            "temporal_kg",
            "llm_reasoning",
            "usl",
            "hierarchical_kg",
            "knowledge_chain",
            "explainable_reasoning",
            "schema_versioning"
        ]
        
        missing_modules = []
        for module in required_modules:
            module_path = code_dir / module
            if not module_path.exists():
                missing_modules.append(module)
        
        if missing_modules:
            self.checks["代码模块"] = False
            self.issues.append(f"缺失模块: {', '.join(missing_modules)}")
        else:
            self.checks["代码模块"] = True
    
    def check_documentation(self):
        """检查文档"""
        docs_dir = self.root_dir / "docs"
        if not docs_dir.exists():
            self.checks["文档"] = False
            self.issues.append("docs目录不存在")
            return
        
        required_guides = [
            "guides/QUICK_START_GUIDE.md",
            "guides/DEPLOYMENT_GUIDE.md",
            "guides/DEVELOPMENT_GUIDE.md",
            "guides/API_REFERENCE.md"
        ]
        
        missing_guides = []
        for guide in required_guides:
            guide_path = docs_dir / guide
            if not guide_path.exists():
                missing_guides.append(guide)
        
        if missing_guides:
            self.checks["文档"] = False
            self.issues.append(f"缺失指南: {', '.join(missing_guides)}")
        else:
            self.checks["文档"] = True
    
    def check_config_files(self):
        """检查配置文件"""
        required_files = [
            "README.md",
            "LICENSE",
            "CONTRIBUTING.md",
            "docker/docker-compose.yml",
            "code/requirements.txt"
        ]
        
        missing_files = []
        for file_path in required_files:
            full_path = self.root_dir / file_path
            if not full_path.exists():
                missing_files.append(file_path)
        
        if missing_files:
            self.checks["配置文件"] = False
            self.issues.append(f"缺失文件: {', '.join(missing_files)}")
        else:
            self.checks["配置文件"] = True
    
    def check_tests(self):
        """检查测试"""
        tests_dir = self.root_dir / "code" / "tests"
        if not tests_dir.exists():
            self.checks["测试"] = False
            self.issues.append("tests目录不存在")
            return
        
        test_files = list(tests_dir.glob("test_*.py"))
        if len(test_files) < 5:
            self.checks["测试"] = False
            self.issues.append(f"测试文件不足: {len(test_files)} 个")
        else:
            self.checks["测试"] = True
    
    def run_all_checks(self):
        """运行所有检查"""
        print("开始项目健康检查...\n")
        
        self.check_directory_structure()
        self.check_code_modules()
        self.check_documentation()
        self.check_config_files()
        self.check_tests()
        
        print("检查结果:")
        print("-" * 50)
        
        for check_name, status in self.checks.items():
            status_icon = "✅" if status else "❌"
            print(f"{status_icon} {check_name}")
        
        if self.issues:
            print("\n发现的问题:")
            for issue in self.issues:
                print(f"  - {issue}")
        
        print("-" * 50)
        
        all_passed = all(self.checks.values())
        if all_passed:
            print("\n✅ 项目健康状况良好")
        else:
            print(f"\n⚠️  发现 {len(self.issues)} 个问题")
        
        return all_passed
    
    def generate_report(self, output_file: str = "health_check_report.md"):
        """生成健康检查报告"""
        report_path = self.root_dir / output_file
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("# 项目健康检查报告\n\n")
            
            f.write("## 检查结果\n\n")
            f.write("| 检查项 | 状态 |\n")
            f.write("|--------|------|\n")
            
            for check_name, status in self.checks.items():
                status_text = "✅ 通过" if status else "❌ 失败"
                f.write(f"| {check_name} | {status_text} |\n")
            
            if self.issues:
                f.write("\n## 发现的问题\n\n")
                for issue in self.issues:
                    f.write(f"- {issue}\n")
            else:
                f.write("\n## ✅ 未发现问题\n\n")
        
        print(f"\n报告已生成: {report_path}")


def main():
    """主函数"""
    root_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    
    checker = HealthChecker(root_dir)
    all_passed = checker.run_all_checks()
    checker.generate_report()
    
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
