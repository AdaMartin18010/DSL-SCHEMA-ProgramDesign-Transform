#!/usr/bin/env python3
"""
验证文档格式和结构

检查所有Schema文档是否符合标准结构（01-05文档）
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Tuple


class DocValidator:
    """文档验证器"""
    
    REQUIRED_FILES = [
        "01_Overview.md",
        "02_Formal_Definition.md",
        "03_Standards.md",
        "04_Transformation.md",
        "05_Case_Studies.md"
    ]
    
    def __init__(self, themes_dir: str = "themes"):
        self.themes_dir = Path(themes_dir)
        self.schemas: Dict[str, Dict[str, bool]] = {}
        self.missing_files: List[Tuple[str, str]] = []
        
    def find_schemas(self):
        """查找所有Schema目录"""
        if not self.themes_dir.exists():
            print(f"错误：目录不存在 {self.themes_dir}")
            return
        
        for theme_dir in self.themes_dir.iterdir():
            if not theme_dir.is_dir():
                continue
            
            # 查找Schema目录
            for schema_dir in theme_dir.iterdir():
                if not schema_dir.is_dir():
                    continue
                
                schema_name = f"{theme_dir.name}/{schema_dir.name}"
                self.schemas[schema_name] = {}
                
                # 检查必需文件
                for required_file in self.REQUIRED_FILES:
                    file_path = schema_dir / required_file
                    exists = file_path.exists()
                    self.schemas[schema_name][required_file] = exists
                    
                    if not exists:
                        self.missing_files.append((schema_name, required_file))
    
    def generate_report(self, output_file: str = "doc_validation_report.md"):
        """生成验证报告"""
        report_path = Path(output_file)
        
        total_schemas = len(self.schemas)
        complete_schemas = sum(
            1 for files in self.schemas.values()
            if all(files.values())
        )
        incomplete_schemas = total_schemas - complete_schemas
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("# 文档验证报告\n\n")
            f.write(f"**总Schema数**: {total_schemas}\n\n")
            f.write(f"**完整Schema数**: {complete_schemas}\n\n")
            f.write(f"**不完整Schema数**: {incomplete_schemas}\n\n")
            f.write(f"**缺失文件数**: {len(self.missing_files)}\n\n")
            
            if self.missing_files:
                f.write("## 缺失文件列表\n\n")
                f.write("| Schema | 缺失文件 |\n")
                f.write("|--------|----------|\n")
                
                for schema_name, missing_file in self.missing_files:
                    f.write(f"| {schema_name} | {missing_file} |\n")
            else:
                f.write("## ✅ 所有Schema文档完整\n\n")
            
            f.write("\n## Schema状态详情\n\n")
            f.write("| Schema | 01 | 02 | 03 | 04 | 05 | 状态 |\n")
            f.write("|--------|----|----|----|----|----|------|\n")
            
            for schema_name, files in sorted(self.schemas.items()):
                status = "✅" if all(files.values()) else "❌"
                f.write(f"| {schema_name} | ")
                f.write("✅" if files["01_Overview.md"] else "❌")
                f.write(" | ")
                f.write("✅" if files["02_Formal_Definition.md"] else "❌")
                f.write(" | ")
                f.write("✅" if files["03_Standards.md"] else "❌")
                f.write(" | ")
                f.write("✅" if files["04_Transformation.md"] else "❌")
                f.write(" | ")
                f.write("✅" if files["05_Case_Studies.md"] else "❌")
                f.write(f" | {status} |\n")
        
        print(f"\n报告已生成: {report_path}")
        print(f"完整Schema: {complete_schemas}/{total_schemas}")
        print(f"缺失文件: {len(self.missing_files)}")
    
    def validate(self):
        """执行验证"""
        print("开始验证文档...")
        self.find_schemas()
        self.generate_report()
        
        if self.missing_files:
            print(f"\n⚠️  发现 {len(self.missing_files)} 个缺失文件")
            return False
        else:
            print("\n✅ 所有文档完整")
            return True


def main():
    """主函数"""
    themes_dir = sys.argv[1] if len(sys.argv) > 1 else "themes"
    
    validator = DocValidator(themes_dir)
    is_valid = validator.validate()
    
    sys.exit(0 if is_valid else 1)


if __name__ == "__main__":
    main()
