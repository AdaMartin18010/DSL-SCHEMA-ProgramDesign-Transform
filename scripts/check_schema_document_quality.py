#!/usr/bin/env python3
"""
检查Schema文档质量

重点关注数据模型转换、数据处理相关的Schema
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Tuple, Set
from dataclasses import dataclass
from enum import Enum


class DocumentType(Enum):
    """文档类型"""
    OVERVIEW = "01_Overview.md"
    FORMAL_DEFINITION = "02_Formal_Definition.md"
    STANDARDS = "03_Standards.md"
    TRANSFORMATION = "04_Transformation.md"
    CASE_STUDIES = "05_Case_Studies.md"


@dataclass
class DocumentCheckResult:
    """文档检查结果"""
    schema_name: str
    doc_type: DocumentType
    file_path: Path
    has_content: bool
    missing_sections: List[str]
    quality_score: float
    issues: List[str]


class SchemaDocumentQualityChecker:
    """Schema文档质量检查器"""
    
    def __init__(self, themes_dir: str = "themes"):
        self.themes_dir = Path(themes_dir)
        self.check_results: List[DocumentCheckResult] = []
        
        # 定义各文档类型的必需章节
        self.required_sections = {
            DocumentType.OVERVIEW: [
                r'核心结论',
                r'概念定义',
                r'Schema元素',
                r'标准对标',
                r'应用场景'
            ],
            DocumentType.FORMAL_DEFINITION: [
                r'形式化模型',
                r'DSL定义',
                r'类型系统',
                r'约束规则',
                r'转换函数'
            ],
            DocumentType.STANDARDS: [
                r'标准体系概述',
                r'主要标准',
                r'标准对比矩阵',
                r'标准发展趋势'
            ],
            DocumentType.TRANSFORMATION: [
                r'转换体系概述',
                r'转换规则',
                r'数据库存储',
                r'数据分析查询'
            ],
            DocumentType.CASE_STUDIES: [
                r'案例概述',
                r'业务背景',
                r'技术挑战',
                r'解决方案',
                r'完整代码实现',
                r'效果评估'
            ]
        }
    
    def check_all_schemas(self, focus_themes: List[str] = None) -> List[DocumentCheckResult]:
        """
        检查所有Schema文档
        
        Args:
            focus_themes: 重点关注的主题列表（如['27_Enterprise_Data_Analytics']）
            
        Returns:
            检查结果列表
        """
        if focus_themes:
            # 只检查指定的主题
            for theme_name in focus_themes:
                theme_path = self.themes_dir / theme_name
                if theme_path.exists():
                    self._check_theme(theme_path)
        else:
            # 检查所有主题
            for theme_path in self.themes_dir.iterdir():
                if theme_path.is_dir() and not theme_path.name.startswith('.'):
                    self._check_theme(theme_path)
        
        return self.check_results
    
    def _check_theme(self, theme_path: Path):
        """检查主题下的所有Schema"""
        for schema_path in theme_path.iterdir():
            if schema_path.is_dir() and not schema_path.name.startswith('.'):
                self._check_schema(schema_path)
    
    def _check_schema(self, schema_path: Path):
        """检查单个Schema的所有文档"""
        schema_name = schema_path.name
        
        for doc_type in DocumentType:
            doc_path = schema_path / doc_type.value
            result = self._check_document(schema_name, doc_type, doc_path)
            self.check_results.append(result)
    
    def _check_document(self, schema_name: str, doc_type: DocumentType, 
                       doc_path: Path) -> DocumentCheckResult:
        """
        检查单个文档
        
        Args:
            schema_name: Schema名称
            doc_type: 文档类型
            doc_path: 文档路径
            
        Returns:
            检查结果
        """
        missing_sections = []
        issues = []
        quality_score = 0.0
        
        if not doc_path.exists():
            return DocumentCheckResult(
                schema_name=schema_name,
                doc_type=doc_type,
                file_path=doc_path,
                has_content=False,
                missing_sections=[],
                quality_score=0.0,
                issues=[f"文档不存在: {doc_path}"]
            )
        
        # 读取文档内容
        try:
            with open(doc_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            return DocumentCheckResult(
                schema_name=schema_name,
                doc_type=doc_type,
                file_path=doc_path,
                has_content=False,
                missing_sections=[],
                quality_score=0.0,
                issues=[f"读取文档失败: {str(e)}"]
            )
        
        if not content.strip():
            return DocumentCheckResult(
                schema_name=schema_name,
                doc_type=doc_type,
                file_path=doc_path,
                has_content=False,
                missing_sections=[],
                quality_score=0.0,
                issues=["文档内容为空"]
            )
        
        # 检查必需章节
        required = self.required_sections.get(doc_type, [])
        found_sections = []
        
        for section_pattern in required:
            pattern = re.compile(section_pattern, re.IGNORECASE)
            if pattern.search(content):
                found_sections.append(section_pattern)
            else:
                missing_sections.append(section_pattern)
        
        # 计算质量分数
        if required:
            quality_score = len(found_sections) / len(required) * 100
        
        # 特殊检查
        if doc_type == DocumentType.TRANSFORMATION:
            # 检查数据库存储章节
            if not re.search(r'数据库存储|PostgreSQL.*存储|数据存储与分析', content, re.IGNORECASE):
                issues.append("缺少数据库存储章节")
            
            # 检查Python代码
            if not re.search(r'```python|def\s+\w+|class\s+\w+', content):
                issues.append("缺少Python代码示例")
        
        if doc_type == DocumentType.CASE_STUDIES:
            # 检查案例数量
            case_count = len(re.findall(r'##\s+\d+\.|###\s+\d+\.\d+', content))
            if case_count < 5:
                issues.append(f"案例数量不足（当前{case_count}个，需要至少5个）")
        
        if doc_type == DocumentType.STANDARDS:
            # 检查标准发展趋势
            if not re.search(r'标准发展趋势|发展趋势|2024-2025|2025-2026', content, re.IGNORECASE):
                issues.append("缺少标准发展趋势章节")
        
        return DocumentCheckResult(
            schema_name=schema_name,
            doc_type=doc_type,
            file_path=doc_path,
            has_content=True,
            missing_sections=missing_sections,
            quality_score=quality_score,
            issues=issues
        )
    
    def generate_report(self, output_path: Path = None) -> str:
        """
        生成检查报告
        
        Args:
            output_path: 输出文件路径
            
        Returns:
            报告内容
        """
        if output_path is None:
            output_path = Path("docs/reports/SCHEMA_DOCUMENT_QUALITY_CHECK_REPORT.md")
        
        # 按Schema分组
        schema_results: Dict[str, List[DocumentCheckResult]] = {}
        for result in self.check_results:
            if result.schema_name not in schema_results:
                schema_results[result.schema_name] = []
            schema_results[result.schema_name].append(result)
        
        # 计算统计信息
        total_schemas = len(schema_results)
        total_docs = len(self.check_results)
        complete_docs = sum(1 for r in self.check_results if r.has_content and r.quality_score >= 80)
        incomplete_docs = total_docs - complete_docs
        
        # 生成报告
        report_lines = [
            "# Schema文档质量检查报告",
            "",
            "## 📋 文档信息",
            "",
            f"**检查时间**：{Path(__file__).stat().st_mtime}",
            f"**检查范围**：{total_schemas}个Schema，{total_docs}个文档",
            f"**完整文档**：{complete_docs}个（质量分数≥80）",
            f"**不完整文档**：{incomplete_docs}个",
            "",
            "---",
            "",
            "## 📊 总体统计",
            "",
            f"- **检查的Schema数量**：{total_schemas}个",
            f"- **检查的文档数量**：{total_docs}个",
            f"- **完整文档数量**：{complete_docs}个",
            f"- **不完整文档数量**：{incomplete_docs}个",
            f"- **总体完成率**：{complete_docs/total_docs*100:.1f}%",
            "",
            "---",
            "",
            "## 📋 详细检查结果",
            ""
        ]
        
        # 按质量分数排序
        sorted_schemas = sorted(
            schema_results.items(),
            key=lambda x: sum(r.quality_score for r in x[1]) / len(x[1])
        )
        
        for schema_name, results in sorted_schemas:
            avg_score = sum(r.quality_score for r in results) / len(results)
            
            report_lines.extend([
                f"### {schema_name}",
                "",
                f"**平均质量分数**：{avg_score:.1f}%",
                "",
                "| 文档类型 | 质量分数 | 状态 | 缺失章节 | 问题 |",
                "|---------|---------|------|---------|------|"
            ])
            
            for result in sorted(results, key=lambda r: r.doc_type.value):
                status = "✅ 完整" if result.quality_score >= 80 else "⚠️ 不完整"
                missing = ", ".join(result.missing_sections[:3]) if result.missing_sections else "-"
                issues = ", ".join(result.issues[:2]) if result.issues else "-"
                
                report_lines.append(
                    f"| {result.doc_type.value} | {result.quality_score:.1f}% | {status} | {missing} | {issues} |"
                )
            
            report_lines.append("")
        
        # 问题汇总
        report_lines.extend([
            "---",
            "",
            "## ⚠️ 问题汇总",
            ""
        ])
        
        # 按问题类型分组
        issue_types: Dict[str, List[DocumentCheckResult]] = {}
        for result in self.check_results:
            for issue in result.issues:
                if issue not in issue_types:
                    issue_types[issue] = []
                issue_types[issue].append(result)
        
        for issue_type, results in sorted(issue_types.items(), key=lambda x: len(x[1]), reverse=True):
            report_lines.extend([
                f"### {issue_type}",
                "",
                f"**影响文档数量**：{len(results)}个",
                "",
                "受影响的Schema："
            ])
            
            affected_schemas = set(r.schema_name for r in results)
            for schema_name in sorted(affected_schemas):
                report_lines.append(f"- {schema_name}")
            
            report_lines.append("")
        
        report_content = "\n".join(report_lines)
        
        # 保存报告
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        return report_content


def main():
    """主函数"""
    print("=" * 80)
    print("Schema文档质量检查")
    print("=" * 80)
    print()
    
    checker = SchemaDocumentQualityChecker()
    
    # 重点关注数据相关的Schema
    focus_themes = [
        '27_Enterprise_Data_Analytics',  # 数据相关Schema
        '26_Enterprise_Finance',  # 企业财务Schema
        '28_Enterprise_Performance_Management'  # 企业绩效管理Schema
    ]
    
    print(f"检查范围：{', '.join(focus_themes)}")
    print()
    
    results = checker.check_all_schemas(focus_themes=focus_themes)
    
    print(f"检查完成：{len(results)}个文档")
    print()
    
    # 生成报告
    report_path = Path("docs/reports/SCHEMA_DOCUMENT_QUALITY_CHECK_REPORT.md")
    report_content = checker.generate_report(report_path)
    
    print(f"✅ 报告已生成：{report_path}")
    print()
    
    # 输出摘要
    complete_count = sum(1 for r in results if r.quality_score >= 80)
    incomplete_count = len(results) - complete_count
    
    print(f"完整文档：{complete_count}个")
    print(f"不完整文档：{incomplete_count}个")
    print(f"完成率：{complete_count/len(results)*100:.1f}%")


if __name__ == "__main__":
    main()
