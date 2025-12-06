#!/usr/bin/env python3
"""
检查所有Schema的04_Transformation.md文件是否包含数据库存储章节
"""

import os
import re
from pathlib import Path
from typing import List, Tuple

def check_database_storage_section(file_path: Path) -> Tuple[bool, str]:
    """
    检查文件是否包含数据库存储章节
    
    返回: (是否包含, 章节标题)
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查多种可能的章节标题格式
        patterns = [
            r'^##?\s*[68]\.?\s*.*[存储数据库]',
            r'^##?\s*数据库存储',
            r'^##?\s*PostgreSQL.*存储',
            r'^##?\s*数据存储与分析',
            r'^##?\s*.*数据存储',
        ]
        
        lines = content.split('\n')
        for i, line in enumerate(lines):
            for pattern in patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    # 检查后续内容是否包含PostgreSQL或表结构相关内容
                    next_lines = '\n'.join(lines[i:min(i+50, len(lines))])
                    if any(keyword in next_lines for keyword in ['PostgreSQL', 'CREATE TABLE', '表结构', 'pgvector']):
                        return True, line.strip()
        
        return False, ""
    except Exception as e:
        return False, f"Error: {str(e)}"

def find_all_transformation_files(base_dir: str = "themes") -> List[Path]:
    """查找所有04_Transformation.md文件"""
    transformation_files = []
    base_path = Path(base_dir)
    
    for file_path in base_path.rglob("04_Transformation.md"):
        transformation_files.append(file_path)
    
    return sorted(transformation_files)

def main():
    """主函数"""
    print("=" * 80)
    print("检查Schema数据库存储章节")
    print("=" * 80)
    print()
    
    transformation_files = find_all_transformation_files()
    print(f"找到 {len(transformation_files)} 个04_Transformation.md文件\n")
    
    missing_sections = []
    has_sections = []
    
    for file_path in transformation_files:
        has_section, section_title = check_database_storage_section(file_path)
        
        # 提取Schema名称
        parts = file_path.parts
        schema_name = parts[-2] if len(parts) >= 2 else file_path.stem
        
        if has_section:
            has_sections.append((schema_name, file_path, section_title))
        else:
            missing_sections.append((schema_name, file_path))
    
    # 输出结果
    print(f"✅ 包含数据库存储章节: {len(has_sections)} 个")
    print(f"❌ 缺少数据库存储章节: {len(missing_sections)} 个")
    print()
    
    if missing_sections:
        print("=" * 80)
        print("缺少数据库存储章节的Schema列表:")
        print("=" * 80)
        for schema_name, file_path in missing_sections:
            print(f"  - {schema_name}")
            print(f"    路径: {file_path}")
        print()
    
    # 生成报告文件
    report_path = Path("docs/reports/DATABASE_STORAGE_SECTION_CHECK_REPORT.md")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("# 数据库存储章节检查报告\n\n")
        f.write(f"**检查时间**: {Path(__file__).stat().st_mtime}\n\n")
        f.write(f"**总文件数**: {len(transformation_files)}\n\n")
        f.write(f"**包含章节**: {len(has_sections)} 个\n\n")
        f.write(f"**缺少章节**: {len(missing_sections)} 个\n\n")
        f.write("---\n\n")
        
        f.write("## 缺少数据库存储章节的Schema\n\n")
        for schema_name, file_path in missing_sections:
            f.write(f"- **{schema_name}**\n")
            f.write(f"  - 路径: `{file_path}`\n\n")
        
        f.write("---\n\n")
        f.write("## 包含数据库存储章节的Schema\n\n")
        for schema_name, file_path, section_title in has_sections:
            f.write(f"- **{schema_name}**\n")
            f.write(f"  - 章节: `{section_title}`\n")
            f.write(f"  - 路径: `{file_path}`\n\n")
    
    print(f"✅ 报告已生成: {report_path}")
    print(f"\n需要补充的Schema数量: {len(missing_sections)}")

if __name__ == "__main__":
    main()
