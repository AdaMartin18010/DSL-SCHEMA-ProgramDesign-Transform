#!/usr/bin/env python3
"""
文档质量检查脚本
检查所有Schema文档的内容完整性和质量
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass, field, asdict


@dataclass
class CheckResult:
    """检查结果"""
    file_path: str
    checks: Dict[str, bool] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            'file_path': self.file_path,
            'checks': self.checks,
            'errors': self.errors,
            'warnings': self.warnings
        }


class DocumentQualityChecker:
    """文档质量检查器"""
    
    def __init__(self, themes_dir: str = "themes"):
        self.themes_dir = Path(themes_dir)
        self.results: List[CheckResult] = []
        
    def get_all_schema_dirs(self) -> List[Path]:
        """获取所有Schema目录"""
        schema_dirs = []
        if not self.themes_dir.exists():
            return schema_dirs
            
        for theme_dir in self.themes_dir.iterdir():
            if theme_dir.is_dir() and theme_dir.name.startswith(('0', '1', '2', '3', '4', '5', '6', '7', '8', '9')):
                for schema_dir in theme_dir.iterdir():
                    if schema_dir.is_dir():
                        schema_dirs.append(schema_dir)
        return schema_dirs
    
    def check_file_structure(self, schema_dir: Path) -> CheckResult:
        """检查文件结构"""
        result = CheckResult(file_path=str(schema_dir))
        expected_files = [
            "01_Overview.md",
            "02_Formal_Definition.md", 
            "03_Standards.md",
            "04_Transformation.md",
            "05_Case_Studies.md"
        ]
        
        for expected in expected_files:
            file_path = schema_dir / expected
            result.checks[f"has_{expected}"] = file_path.exists()
            if not file_path.exists():
                result.errors.append(f"缺少文件: {expected}")
        
        return result
    
    def check_overview_content(self, file_path: Path) -> CheckResult:
        """检查01_Overview.md内容"""
        result = CheckResult(file_path=str(file_path))
        
        if not file_path.exists():
            result.errors.append("文件不存在")
            return result
            
        content = file_path.read_text(encoding='utf-8')
        
        # 检查必要章节
        required_sections = [
            ("目录", r"##?\s*目录"),
            ("核心结论", r"##?\s*核心结论"),
            ("概念定义", r"##?\s*概念定义"),
            ("Schema元素", r"##?\s*.*Schema.*元素"),
            ("标准对标", r"##?\s*.*标准.*对标"),
            ("应用场景", r"##?\s*应用场景"),
        ]
        
        for section_name, pattern in required_sections:
            found = bool(re.search(pattern, content, re.IGNORECASE))
            result.checks[f"has_{section_name}"] = found
            if not found:
                result.warnings.append(f"可能缺少章节: {section_name}")
        
        # 检查思维导图
        has_mindmap = bool(re.search(r"##?\s*思维导图|mindmap|graph\s+TD|graph\s+LR", content, re.IGNORECASE))
        result.checks["has_mindmap"] = has_mindmap
        
        return result
    
    def check_formal_definition_content(self, file_path: Path) -> CheckResult:
        """检查02_Formal_Definition.md内容"""
        result = CheckResult(file_path=str(file_path))
        
        if not file_path.exists():
            result.errors.append("文件不存在")
            return result
            
        content = file_path.read_text(encoding='utf-8')
        
        required_sections = [
            ("目录", r"##?\s*目录"),
            ("形式化模型", r"##?\s*形式化模型"),
            ("DSL定义", r"##?\s*.*DSL.*定义"),
            ("类型系统", r"##?\s*类型系统"),
            ("约束规则", r"##?\s*约束规则"),
            ("转换函数", r"##?\s*转换函数"),
        ]
        
        for section_name, pattern in required_sections:
            found = bool(re.search(pattern, content, re.IGNORECASE))
            result.checks[f"has_{section_name}"] = found
            if not found:
                result.warnings.append(f"可能缺少章节: {section_name}")
        
        return result
    
    def check_standards_content(self, file_path: Path) -> CheckResult:
        """检查03_Standards.md内容"""
        result = CheckResult(file_path=str(file_path))
        
        if not file_path.exists():
            result.errors.append("文件不存在")
            return result
            
        content = file_path.read_text(encoding='utf-8')
        
        required_sections = [
            ("目录", r"##?\s*目录"),
            ("标准体系", r"##?\s*标准体系"),
            ("主要标准", r"##?\s*主要标准"),
            ("标准对比", r"##?\s*标准对比"),
            ("发展趋势", r"##?\s*.*发展趋势|2024.*2025|2025.*2026"),
        ]
        
        for section_name, pattern in required_sections:
            found = bool(re.search(pattern, content, re.IGNORECASE))
            result.checks[f"has_{section_name}"] = found
            if not found:
                result.warnings.append(f"可能缺少章节: {section_name}")
        
        return result
    
    def check_transformation_content(self, file_path: Path) -> CheckResult:
        """检查04_Transformation.md内容"""
        result = CheckResult(file_path=str(file_path))
        
        if not file_path.exists():
            result.errors.append("文件不存在")
            return result
            
        content = file_path.read_text(encoding='utf-8')
        
        required_sections = [
            ("目录", r"##?\s*目录"),
            ("转换体系", r"##?\s*转换体系"),
            ("转换规则", r"##?\s*转换规则"),
            ("转换验证", r"##?\s*转换验证"),
        ]
        
        for section_name, pattern in required_sections:
            found = bool(re.search(pattern, content, re.IGNORECASE))
            result.checks[f"has_{section_name}"] = found
            if not found:
                result.warnings.append(f"可能缺少章节: {section_name}")
        
        # 检查数据库存储章节
        has_db_section = bool(re.search(r"##?\s*6\.?\s*数据库存储|##?\s*.*数据库存储.*分析", content, re.IGNORECASE))
        result.checks["has_database_section"] = has_db_section
        
        # 检查PostgreSQL
        has_postgres = "postgresql" in content.lower() or "postgres" in content.lower()
        result.checks["has_postgresql"] = has_postgres
        
        # 检查Python代码
        has_python = "```python" in content
        result.checks["has_python_code"] = has_python
        
        return result
    
    def check_case_studies_content(self, file_path: Path) -> CheckResult:
        """检查05_Case_Studies.md内容"""
        result = CheckResult(file_path=str(file_path))
        
        if not file_path.exists():
            result.errors.append("文件不存在")
            return result
            
        content = file_path.read_text(encoding='utf-8')
        
        # 检查章节
        required_sections = [
            ("目录", r"##?\s*目录"),
            ("案例概述", r"##?\s*案例概述"),
            ("实践案例", r"##?\s*实践案例|案例\s*[:：]"),
        ]
        
        for section_name, pattern in required_sections:
            found = bool(re.search(pattern, content, re.IGNORECASE))
            result.checks[f"has_{section_name}"] = found
            if not found:
                result.warnings.append(f"可能缺少章节: {section_name}")
        
        # 统计案例数量（二级标题数量）
        case_pattern = r"##\s+\d+\.?\s*"
        cases = re.findall(case_pattern, content)
        result.checks["case_count"] = len(cases)
        
        if len(cases) < 5:
            result.warnings.append(f"案例数量可能不足: 发现{len(cases)}个案例，建议至少5个")
        
        # 检查代码
        has_code = "```" in content
        result.checks["has_code_examples"] = has_code
        
        return result
    
    def run_full_check(self) -> Dict[str, Any]:
        """运行完整检查"""
        print("🔍 开始文档质量全面检查...")
        
        schema_dirs = self.get_all_schema_dirs()
        print(f"📁 发现 {len(schema_dirs)} 个Schema目录")
        
        all_results = []
        
        for i, schema_dir in enumerate(schema_dirs, 1):
            print(f"\n[{i}/{len(schema_dirs)}] 检查: {schema_dir.name}")
            
            # 检查文件结构
            structure_result = self.check_file_structure(schema_dir)
            all_results.append(structure_result)
            
            # 检查每个文档
            checks = [
                ("01_Overview.md", self.check_overview_content),
                ("02_Formal_Definition.md", self.check_formal_definition_content),
                ("03_Standards.md", self.check_standards_content),
                ("04_Transformation.md", self.check_transformation_content),
                ("05_Case_Studies.md", self.check_case_studies_content),
            ]
            
            for filename, check_func in checks:
                file_path = schema_dir / filename
                result = check_func(file_path)
                all_results.append(result)
                
                # 显示进度
                status = "✅" if not result.errors else "❌"
                print(f"  {status} {filename}")
        
        # 生成报告
        return self.generate_report(all_results)
    
    def generate_report(self, results: List[CheckResult]) -> Dict[str, Any]:
        """生成检查报告"""
        total_files = len(results)
        error_count = sum(1 for r in results if r.errors)
        warning_count = sum(1 for r in results if r.warnings)
        
        # 按类型统计
        structure_issues = [r for r in results if "has_01_Overview.md" in r.checks and not r.checks.get("has_01_Overview.md", True)]
        db_section_missing = []
        trends_section_missing = []
        
        for r in results:
            if "04_Transformation.md" in r.file_path:
                if not r.checks.get("has_database_section", True):
                    db_section_missing.append(r)
            if "03_Standards.md" in r.file_path:
                if not r.checks.get("has_发展趋势", True):
                    trends_section_missing.append(r)
        
        report = {
            "summary": {
                "total_files_checked": total_files,
                "files_with_errors": error_count,
                "files_with_warnings": warning_count,
                "schema_dirs_checked": len([r for r in results if "has_01_Overview.md" in r.checks]),
                "missing_db_section_count": len(db_section_missing),
                "missing_trends_section_count": len(trends_section_missing),
            },
            "issues": {
                "structure_issues": [r.to_dict() for r in structure_issues],
                "missing_db_section": [r.file_path for r in db_section_missing],
                "missing_trends_section": [r.file_path for r in trends_section_missing],
            },
            "all_results": [r.to_dict() for r in results],
        }
        
        return report


def main():
    """主函数"""
    checker = DocumentQualityChecker()
    report = checker.run_full_check()
    
    # 保存报告
    report_path = Path("scripts/document_quality_report.json")
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    # 打印摘要
    summary = report["summary"]
    print("\n" + "="*60)
    print("📊 文档质量检查报告摘要")
    print("="*60)
    print(f"总检查文件数: {summary['total_files_checked']}")
    print(f"错误文件数: {summary['files_with_errors']}")
    print(f"警告文件数: {summary['files_with_warnings']}")
    print(f"Schema目录数: {summary['schema_dirs_checked']}")
    print(f"缺少数据库存储章节: {summary['missing_db_section_count']}")
    print(f"缺少标准发展趋势章节: {summary['missing_trends_section_count']}")
    print(f"\n详细报告已保存: {report_path}")
    
    return report


if __name__ == "__main__":
    main()
