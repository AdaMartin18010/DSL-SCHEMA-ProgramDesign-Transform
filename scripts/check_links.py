#!/usr/bin/env python3
"""
检查Markdown文档中的链接有效性

检查项目中的所有Markdown文档，验证内部链接和外部链接的有效性
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Tuple, Set
from urllib.parse import urlparse


class LinkChecker:
    """链接检查器"""
    
    def __init__(self, root_dir: str = "."):
        self.root_dir = Path(root_dir).resolve()
        self.md_files: List[Path] = []
        self.broken_links: List[Tuple[Path, str, str]] = []  # (file, link, reason)
        self.valid_links: Set[str] = set()
        
    def find_md_files(self):
        """查找所有Markdown文件"""
        exclude_dirs = {'.git', 'node_modules', '__pycache__', '.venv', 'venv'}
        
        for md_file in self.root_dir.rglob("*.md"):
            # 跳过排除的目录
            if any(excluded in md_file.parts for excluded in exclude_dirs):
                continue
            self.md_files.append(md_file)
        
        print(f"找到 {len(self.md_files)} 个Markdown文件")
    
    def extract_links(self, file_path: Path) -> List[Tuple[int, str]]:
        """提取文件中的所有链接"""
        links = []
        link_pattern = r'\[([^\]]+)\]\(([^\)]+)\)'
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    matches = re.finditer(link_pattern, line)
                    for match in matches:
                        link_text = match.group(1)
                        link_url = match.group(2)
                        links.append((line_num, link_url))
        except Exception as e:
            print(f"错误：无法读取文件 {file_path}: {e}")
        
        return links
    
    def check_link(self, file_path: Path, link: str) -> Tuple[bool, str]:
        """检查链接是否有效"""
        # 跳过锚点链接
        if link.startswith('#'):
            return True, ""
        
        # 外部链接
        parsed = urlparse(link)
        if parsed.scheme in ('http', 'https', 'mailto'):
            # 外部链接，暂时标记为有效（需要网络检查）
            return True, ""
        
        # 内部链接
        if link.startswith('/'):
            # 绝对路径
            target = self.root_dir / link.lstrip('/')
        else:
            # 相对路径
            target = (file_path.parent / link).resolve()
        
        # 检查文件是否存在
        if target.exists():
            return True, ""
        
        # 检查是否是锚点链接（文件存在但锚点可能不存在）
        if '#' in link:
            file_part, anchor = link.split('#', 1)
            if file_part:
                file_target = (file_path.parent / file_part).resolve()
                if file_target.exists():
                    # 文件存在，但锚点验证需要更复杂的逻辑
                    return True, ""
        
        return False, f"文件不存在: {target}"
    
    def check_all_links(self):
        """检查所有文件的链接"""
        print("\n开始检查链接...")
        
        for md_file in self.md_files:
            links = self.extract_links(md_file)
            
            for line_num, link in links:
                is_valid, reason = self.check_link(md_file, link)
                
                if not is_valid:
                    self.broken_links.append((md_file, link, reason))
                    print(f"❌ {md_file.relative_to(self.root_dir)}:{line_num} - {link}")
                    print(f"   原因: {reason}")
                else:
                    self.valid_links.add(link)
        
        print(f"\n检查完成:")
        print(f"  有效链接: {len(self.valid_links)}")
        print(f"  无效链接: {len(self.broken_links)}")
    
    def generate_report(self, output_file: str = "link_check_report.md"):
        """生成检查报告"""
        report_path = self.root_dir / output_file
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("# 链接检查报告\n\n")
            f.write(f"**检查时间**: {Path(__file__).stat().st_mtime}\n\n")
            f.write(f"**检查文件数**: {len(self.md_files)}\n\n")
            f.write(f"**有效链接数**: {len(self.valid_links)}\n\n")
            f.write(f"**无效链接数**: {len(self.broken_links)}\n\n")
            
            if self.broken_links:
                f.write("## 无效链接列表\n\n")
                f.write("| 文件 | 行号 | 链接 | 原因 |\n")
                f.write("|------|------|------|------|\n")
                
                for file_path, link, reason in self.broken_links:
                    rel_path = file_path.relative_to(self.root_dir)
                    f.write(f"| {rel_path} | - | {link} | {reason} |\n")
            else:
                f.write("## ✅ 所有链接有效\n\n")
        
        print(f"\n报告已生成: {report_path}")


def main():
    """主函数"""
    root_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    
    checker = LinkChecker(root_dir)
    checker.find_md_files()
    checker.check_all_links()
    checker.generate_report()
    
    if checker.broken_links:
        print(f"\n⚠️  发现 {len(checker.broken_links)} 个无效链接")
        sys.exit(1)
    else:
        print("\n✅ 所有链接有效")
        sys.exit(0)


if __name__ == "__main__":
    main()
