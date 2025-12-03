#!/usr/bin/env python3
"""
View目录完整性检查工具

检查view目录的文档完整性、导航链接、交叉引用等
"""

import os
import sys
import re
from pathlib import Path
from typing import Dict, List, Tuple, Set


class ViewDirectoryChecker:
    """View目录检查器"""
    
    def __init__(self, view_dir: str = "view"):
        self.view_dir = Path(view_dir)
        self.issues: List[Tuple[str, str]] = []  # (file, issue)
        self.stats: Dict[str, any] = {}
        
    def check_core_schemas(self):
        """检查核心Schema文档"""
        required_schemas = [
            "program.md",
            "iot_schema.md",
            "can_schema.md",
            "plc_schema.md",
            "physics_schema.md"
        ]
        
        missing = []
        for schema in required_schemas:
            if not (self.view_dir / schema).exists():
                missing.append(schema)
                self.issues.append((f"view/{schema}", "核心Schema文档缺失"))
        
        self.stats["core_schemas"] = {
            "required": len(required_schemas),
            "found": len(required_schemas) - len(missing),
            "missing": missing
        }
    
    def check_theme_docs(self):
        """检查主题分析文档"""
        themes_dir = self.view_dir / "analysis" / "themes"
        required_themes = [
            "01-领域语言转换与AI时代适配方案.md",
            "02-DSL分类与典型示例.md",
            "03-DSL转换方案与技术分析.md",
            "04-IOT-Schema深度分析.md",
            "05-行业Schema分析与转换.md",
            "06-多维模型转换论证.md",
            "07-编程语言类型系统与控制逻辑.md",
            "08-二进制转换与TCP协议.md",
            "09-跨行业转换体系扩展论证.md"
        ]
        
        missing = []
        for theme in required_themes:
            if not (themes_dir / theme).exists():
                missing.append(theme)
                self.issues.append((f"view/analysis/themes/{theme}", "主题分析文档缺失"))
        
        self.stats["theme_docs"] = {
            "required": len(required_themes),
            "found": len(required_themes) - len(missing),
            "missing": missing
        }
    
    def check_theory_docs(self):
        """检查理论分析文档"""
        theory_dir = self.view_dir / "theory"
        required_theories = [
            "00-理论文档导航总览.md",
            "06_Formal_Verification_Proofs.md",
            "06_Tree_Model_AI_ML_Application.md",
            "06_Tree_Model_AI_ML_Case_Studies.md",
            "07_Knowledge_Graph_Mapping.md",
            "08_Multidimensional_Knowledge_Matrix.md",
            "09_Information_Theory_Analysis.md",
            "10_Formal_Language_Theory_Analysis.md"
        ]
        
        missing = []
        for theory in required_theories:
            if not (theory_dir / theory).exists():
                missing.append(theory)
                self.issues.append((f"view/theory/{theory}", "理论分析文档缺失"))
        
        self.stats["theory_docs"] = {
            "required": len(required_theories),
            "found": len(required_theories) - len(missing),
            "missing": missing
        }
    
    def check_navigation_docs(self):
        """检查导航文档"""
        required_nav = [
            "README.md",
            "NAVIGATION.md",
            "00-项目总览.md"
        ]
        
        missing = []
        for nav in required_nav:
            if not (self.view_dir / nav).exists():
                missing.append(nav)
                self.issues.append((f"view/{nav}", "导航文档缺失"))
        
        self.stats["navigation_docs"] = {
            "required": len(required_nav),
            "found": len(required_nav) - len(missing),
            "missing": missing
        }
    
    def check_internal_links(self, file_path: Path):
        """检查文件内部链接"""
        link_pattern = r'\[([^\]]+)\]\(([^\)]+)\)'
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                links = re.findall(link_pattern, content)
                
                for link_text, link_url in links:
                    # 跳过外部链接
                    if link_url.startswith('http') or link_url.startswith('mailto'):
                        continue
                    
                    # 跳过锚点链接
                    if link_url.startswith('#'):
                        continue
                    
                    # 检查相对路径链接
                    if '/' in link_url or link_url.endswith('.md'):
                        target = (file_path.parent / link_url).resolve()
                        if not target.exists():
                            self.issues.append((
                                str(file_path.relative_to(self.view_dir)),
                                f"无效链接: {link_url}"
                            ))
        except Exception as e:
            self.issues.append((
                str(file_path.relative_to(self.view_dir)),
                f"无法读取文件: {e}"
            ))
    
    def check_all_links(self):
        """检查所有文件的链接"""
        md_files = list(self.view_dir.rglob("*.md"))
        
        for md_file in md_files:
            self.check_internal_links(md_file)
        
        self.stats["link_check"] = {
            "files_checked": len(md_files),
            "issues_found": len([i for i in self.issues if "无效链接" in i[1]])
        }
    
    def count_documents(self):
        """统计文档数量"""
        core_schemas = len(list((self.view_dir).glob("*.md"))) - 3  # 排除导航文档
        theme_docs = len(list((self.view_dir / "analysis" / "themes").glob("*.md")))
        theory_docs = len(list((self.view_dir / "theory").glob("*.md")))
        practice_docs = len(list((self.view_dir / "practices").glob("*.md")))
        diagram_docs = len(list((self.view_dir / "diagrams").glob("*.md")))
        analysis_docs = len(list((self.view_dir / "analysis").glob("*.md")))
        
        self.stats["document_count"] = {
            "core_schemas": core_schemas,
            "theme_docs": theme_docs,
            "theory_docs": theory_docs,
            "practice_docs": practice_docs,
            "diagram_docs": diagram_docs,
            "analysis_docs": analysis_docs,
            "total": core_schemas + theme_docs + theory_docs + practice_docs + diagram_docs + analysis_docs
        }
    
    def run_all_checks(self):
        """运行所有检查"""
        print("开始检查view目录...\n")
        
        self.check_core_schemas()
        self.check_theme_docs()
        self.check_theory_docs()
        self.check_navigation_docs()
        self.count_documents()
        self.check_all_links()
        
        print("检查完成\n")
    
    def generate_report(self, output_file: str = "view_directory_check_report.md"):
        """生成检查报告"""
        report_path = Path(output_file)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("# View目录完整性检查报告\n\n")
            
            f.write("## 📊 文档统计\n\n")
            f.write("| 类别 | 数量 |\n")
            f.write("|------|------|\n")
            f.write(f"| 核心Schema文档 | {self.stats['document_count']['core_schemas']} |\n")
            f.write(f"| 主题分析文档 | {self.stats['document_count']['theme_docs']} |\n")
            f.write(f"| 理论分析文档 | {self.stats['document_count']['theory_docs']} |\n")
            f.write(f"| 实践指南文档 | {self.stats['document_count']['practice_docs']} |\n")
            f.write(f"| 图表文档 | {self.stats['document_count']['diagram_docs']} |\n")
            f.write(f"| 分析文档 | {self.stats['document_count']['analysis_docs']} |\n")
            f.write(f"| **总计** | **{self.stats['document_count']['total']}** |\n")
            
            f.write("\n## ✅ 完整性检查\n\n")
            f.write("| 检查项 | 状态 |\n")
            f.write("|--------|------|\n")
            
            f.write(f"| 核心Schema文档 | ")
            if self.stats['core_schemas']['found'] == self.stats['core_schemas']['required']:
                f.write("✅ 完整 |\n")
            else:
                f.write(f"❌ 缺失 {len(self.stats['core_schemas']['missing'])} 个 |\n")
            
            f.write(f"| 主题分析文档 | ")
            if self.stats['theme_docs']['found'] == self.stats['theme_docs']['required']:
                f.write("✅ 完整 |\n")
            else:
                f.write(f"❌ 缺失 {len(self.stats['theme_docs']['missing'])} 个 |\n")
            
            f.write(f"| 理论分析文档 | ")
            if self.stats['theory_docs']['found'] == self.stats['theory_docs']['required']:
                f.write("✅ 完整 |\n")
            else:
                f.write(f"❌ 缺失 {len(self.stats['theory_docs']['missing'])} 个 |\n")
            
            f.write(f"| 导航文档 | ")
            if self.stats['navigation_docs']['found'] == self.stats['navigation_docs']['required']:
                f.write("✅ 完整 |\n")
            else:
                f.write(f"❌ 缺失 {len(self.stats['navigation_docs']['missing'])} 个 |\n")
            
            if self.issues:
                f.write("\n## ⚠️ 发现的问题\n\n")
                f.write("| 文件 | 问题 |\n")
                f.write("|------|------|\n")
                
                for file_path, issue in self.issues[:50]:  # 限制显示前50个问题
                    f.write(f"| {file_path} | {issue} |\n")
            else:
                f.write("\n## ✅ 未发现问题\n\n")
        
        print(f"报告已生成: {report_path}")
    
    def print_summary(self):
        """打印检查摘要"""
        print("="*60)
        print("View目录检查摘要")
        print("="*60)
        
        print(f"\n📊 文档统计:")
        print(f"  核心Schema文档: {self.stats['document_count']['core_schemas']}")
        print(f"  主题分析文档: {self.stats['document_count']['theme_docs']}")
        print(f"  理论分析文档: {self.stats['document_count']['theory_docs']}")
        print(f"  实践指南文档: {self.stats['document_count']['practice_docs']}")
        print(f"  图表文档: {self.stats['document_count']['diagram_docs']}")
        print(f"  分析文档: {self.stats['document_count']['analysis_docs']}")
        print(f"  总计: {self.stats['document_count']['total']}")
        
        print(f"\n✅ 完整性检查:")
        print(f"  核心Schema文档: {self.stats['core_schemas']['found']}/{self.stats['core_schemas']['required']}")
        print(f"  主题分析文档: {self.stats['theme_docs']['found']}/{self.stats['theme_docs']['required']}")
        print(f"  理论分析文档: {self.stats['theory_docs']['found']}/{self.stats['theory_docs']['required']}")
        print(f"  导航文档: {self.stats['navigation_docs']['found']}/{self.stats['navigation_docs']['required']}")
        
        if self.issues:
            print(f"\n⚠️  发现 {len(self.issues)} 个问题")
        else:
            print("\n✅ 未发现问题")


def main():
    """主函数"""
    view_dir = sys.argv[1] if len(sys.argv) > 1 else "view"
    
    checker = ViewDirectoryChecker(view_dir)
    checker.run_all_checks()
    checker.print_summary()
    checker.generate_report()
    
    if checker.issues:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
