#!/usr/bin/env python3
"""
项目统计工具

生成项目的详细统计信息
"""

import os
import sys
from pathlib import Path
from typing import Dict, List


class ProjectStats:
    """项目统计器"""
    
    def __init__(self, root_dir: str = "."):
        self.root_dir = Path(root_dir).resolve()
        self.stats: Dict[str, any] = {}
        
    def count_files(self, directory: Path, pattern: str = "*", exclude_dirs: set = None) -> int:
        """统计文件数量"""
        if exclude_dirs is None:
            exclude_dirs = {'.git', 'node_modules', '__pycache__', '.venv', 'venv', '.pytest_cache'}
        
        count = 0
        if not directory.exists():
            return 0
        
        for file_path in directory.rglob(pattern):
            if any(excluded in file_path.parts for excluded in exclude_dirs):
                continue
            if file_path.is_file():
                count += 1
        
        return count
    
    def count_lines(self, file_path: Path) -> int:
        """统计文件行数"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return sum(1 for _ in f)
        except:
            return 0
    
    def get_total_lines(self, directory: Path, pattern: str = "*") -> int:
        """统计总行数"""
        exclude_dirs = {'.git', 'node_modules', '__pycache__', '.venv', 'venv', '.pytest_cache'}
        total = 0
        
        if not directory.exists():
            return 0
        
        for file_path in directory.rglob(pattern):
            if any(excluded in file_path.parts for excluded in exclude_dirs):
                continue
            if file_path.is_file():
                total += self.count_lines(file_path)
        
        return total
    
    def count_schemas(self) -> int:
        """统计Schema数量"""
        themes_dir = self.root_dir / "themes"
        if not themes_dir.exists():
            return 0
        
        count = 0
        for theme_dir in themes_dir.iterdir():
            if not theme_dir.is_dir():
                continue
            for schema_dir in theme_dir.iterdir():
                if schema_dir.is_dir():
                    count += 1
        
        return count
    
    def collect_stats(self):
        """收集统计信息"""
        print("收集项目统计信息...")
        
        # 代码统计
        code_dir = self.root_dir / "code"
        self.stats["code"] = {
            "python_files": self.count_files(code_dir, "*.py"),
            "typescript_files": self.count_files(code_dir, "*.ts"),
            "test_files": self.count_files(code_dir / "tests", "*.py"),
            "total_lines": self.get_total_lines(code_dir, "*.py"),
        }
        
        # 文档统计
        docs_dir = self.root_dir / "docs"
        themes_dir = self.root_dir / "themes"
        view_dir = self.root_dir / "view"
        
        self.stats["docs"] = {
            "guide_files": self.count_files(docs_dir / "guides", "*.md"),
            "report_files": self.count_files(docs_dir / "reports", "*.md"),
            "schema_files": self.count_files(themes_dir, "*.md"),
            "view_files": self.count_files(view_dir, "*.md"),
            "total_docs": (
                self.count_files(docs_dir, "*.md") +
                self.count_files(themes_dir, "*.md") +
                self.count_files(view_dir, "*.md")
            ),
        }
        
        # Schema统计
        self.stats["schemas"] = {
            "total": self.count_schemas(),
            "expected_docs": self.count_schemas() * 5,  # 每个Schema 5个文档
        }
        
        # 服务统计
        docker_dir = self.root_dir / "docker"
        self.stats["services"] = {
            "dockerfiles": self.count_files(docker_dir, "Dockerfile*"),
            "api_services": 9,  # 已知的API服务数量
        }
        
        # 工具统计
        scripts_dir = self.root_dir / "scripts"
        self.stats["tools"] = {
            "scripts": self.count_files(scripts_dir, "*.py"),
        }
    
    def generate_report(self, output_file: str = "project_stats_report.md"):
        """生成统计报告"""
        report_path = self.root_dir / output_file
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("# 项目统计报告\n\n")
            f.write("## 📊 代码统计\n\n")
            f.write("| 类别 | 数量 |\n")
            f.write("|------|------|\n")
            f.write(f"| Python文件 | {self.stats['code']['python_files']} |\n")
            f.write(f"| TypeScript文件 | {self.stats['code']['typescript_files']} |\n")
            f.write(f"| 测试文件 | {self.stats['code']['test_files']} |\n")
            f.write(f"| 总代码行数 | {self.stats['code']['total_lines']:,} |\n")
            
            f.write("\n## 📚 文档统计\n\n")
            f.write("| 类别 | 数量 |\n")
            f.write("|------|------|\n")
            f.write(f"| 指南文档 | {self.stats['docs']['guide_files']} |\n")
            f.write(f"| 报告文档 | {self.stats['docs']['report_files']} |\n")
            f.write(f"| Schema文档 | {self.stats['docs']['schema_files']} |\n")
            f.write(f"| View文档 | {self.stats['docs']['view_files']} |\n")
            f.write(f"| 总文档数 | {self.stats['docs']['total_docs']} |\n")
            
            f.write("\n## 🎨 Schema统计\n\n")
            f.write("| 类别 | 数量 |\n")
            f.write("|------|------|\n")
            f.write(f"| Schema总数 | {self.stats['schemas']['total']} |\n")
            f.write(f"| 预期文档数 | {self.stats['schemas']['expected_docs']} |\n")
            
            f.write("\n## 🐳 服务统计\n\n")
            f.write("| 类别 | 数量 |\n")
            f.write("|------|------|\n")
            f.write(f"| Dockerfile | {self.stats['services']['dockerfiles']} |\n")
            f.write(f"| API服务 | {self.stats['services']['api_services']} |\n")
            
            f.write("\n## 🛠️ 工具统计\n\n")
            f.write("| 类别 | 数量 |\n")
            f.write("|------|------|\n")
            f.write(f"| 脚本工具 | {self.stats['tools']['scripts']} |\n")
        
        print(f"\n报告已生成: {report_path}")
    
    def print_summary(self):
        """打印统计摘要"""
        print("\n" + "="*60)
        print("项目统计摘要")
        print("="*60)
        
        print(f"\n📦 代码:")
        print(f"  Python文件: {self.stats['code']['python_files']}")
        print(f"  TypeScript文件: {self.stats['code']['typescript_files']}")
        print(f"  测试文件: {self.stats['code']['test_files']}")
        print(f"  总代码行数: {self.stats['code']['total_lines']:,}")
        
        print(f"\n📚 文档:")
        print(f"  指南文档: {self.stats['docs']['guide_files']}")
        print(f"  报告文档: {self.stats['docs']['report_files']}")
        print(f"  Schema文档: {self.stats['docs']['schema_files']}")
        print(f"  View文档: {self.stats['docs']['view_files']}")
        print(f"  总文档数: {self.stats['docs']['total_docs']}")
        
        print(f"\n🎨 Schema:")
        print(f"  Schema总数: {self.stats['schemas']['total']}")
        print(f"  预期文档数: {self.stats['schemas']['expected_docs']}")
        
        print(f"\n🐳 服务:")
        print(f"  Dockerfile: {self.stats['services']['dockerfiles']}")
        print(f"  API服务: {self.stats['services']['api_services']}")
        
        print(f"\n🛠️ 工具:")
        print(f"  脚本工具: {self.stats['tools']['scripts']}")


def main():
    """主函数"""
    root_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    
    stats = ProjectStats(root_dir)
    stats.collect_stats()
    stats.print_summary()
    stats.generate_report()
    
    print("\n✅ 统计完成")


if __name__ == "__main__":
    main()
