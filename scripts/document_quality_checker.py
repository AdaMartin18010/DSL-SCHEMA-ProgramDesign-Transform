#!/usr/bin/env python3
"""
文档质量检查脚本
检查所有Schema文档的完整性和质量
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass, asdict


@dataclass
class DocumentCheckResult:
    """文档检查结果"""
    file_path: str
    doc_type: str  # 01_Overview, 02_Formal_Definition, etc.
    exists: bool
    has_toc: bool = False
    has_required_sections: bool = False
    missing_sections: List[str] = None
    issues: List[str] = None
    
    def __post_init__(self):
        if self.missing_sections is None:
            self.missing_sections = []
        if self.issues is None:
            self.issues = []


class DocumentQualityChecker:
    """文档质量检查器"""
    
    # 标准文档结构（使用更灵活的关键词匹配）
    DOC_TYPES = {
        '01_Overview.md': {
            'name': '概览文档',
            'required_sections': [
                ('核心结论', ['核心结论', '结论', '概述']),
                ('概念定义', ['概念定义', '定义', 'Schema定义']),
                ('Schema结构', ['Schema元素', '三层结构', '分层', '架构']),
                ('标准对标', ['标准对标', '标准', 'ISO', '规范']),
                ('应用场景', ['应用场景', '应用', '案例']),
                ('思维导图', ['思维导图', '导图', '知识图谱'])
            ]
        },
        '02_Formal_Definition.md': {
            'name': '形式化定义',
            'required_sections': [
                ('形式化模型', ['形式化模型', '形式化', '模型']),
                ('DSL定义', ['DSL定义', 'DSL', '语法']),
                ('类型系统', ['类型系统', '类型', '数据类型']),
                ('约束规则', ['约束规则', '约束', '规则']),
                ('转换函数', ['转换函数', '转换', '映射'])
            ]
        },
        '03_Standards.md': {
            'name': '标准文档',
            'required_sections': [
                ('标准体系', ['标准体系', '标准', '规范体系']),
                ('主要标准', ['主要标准', '核心标准', 'ISO', 'IEC']),
                ('标准对比', ['标准对比', '对比', '比较']),
                ('发展趋势', ['发展趋势', '趋势', '发展', '展望'])
            ]
        },
        '04_Transformation.md': {
            'name': '转换文档',
            'required_sections': [
                ('转换体系', ['转换体系', '转换概述', '转换方向']),
                ('转换规则', ['转换规则', '规则', '映射规则']),
                ('转换验证', ['转换验证', '验证', '测试']),
                ('数据存储', ['数据库存储', '存储', 'PostgreSQL', '数据分析'])
            ]
        },
        '05_Case_Studies.md': {
            'name': '案例文档',
            'required_sections': [
                ('案例', ['案例', '实践', '应用实例']),
                ('业务背景', ['业务背景', '背景', '业务']),
                ('技术挑战', ['技术挑战', '挑战', '问题']),
                ('解决方案', ['解决方案', '方案', '解决']),
                ('代码实现', ['代码实现', '代码', '实现']),
                ('效果评估', ['效果评估', '评估', '效果', '结果'])
            ]
        }
    }
    
    def __init__(self, themes_dir: str = 'themes'):
        self.themes_dir = Path(themes_dir)
        self.results: List[DocumentCheckResult] = []
        self.summary = {
            'total_schemas': 0,
            'total_docs': 0,
            'complete_docs': 0,
            'incomplete_docs': 0,
            'missing_docs': 0,
            'issues_by_type': {}
        }
    
    def get_all_schema_dirs(self) -> List[Path]:
        """获取所有Schema目录"""
        schema_dirs = []
        for theme_dir in self.themes_dir.iterdir():
            if theme_dir.is_dir() and not theme_dir.name.startswith('.'):
                for schema_dir in theme_dir.iterdir():
                    if schema_dir.is_dir() and not schema_dir.name.startswith('.'):
                        schema_dirs.append(schema_dir)
        return schema_dirs
    
    def check_document(self, doc_path: Path, doc_type: str) -> DocumentCheckResult:
        """检查单个文档"""
        result = DocumentCheckResult(
            file_path=str(doc_path),
            doc_type=doc_type,
            exists=doc_path.exists()
        )
        
        if not result.exists:
            result.issues.append(f"文件不存在: {doc_path}")
            return result
        
        try:
            content = doc_path.read_text(encoding='utf-8')
        except Exception as e:
            result.issues.append(f"读取文件失败: {e}")
            return result
        
        # 检查目录结构
        result.has_toc = '## ' in content or '### ' in content
        
        # 检查必需章节（使用灵活匹配）
        required = self.DOC_TYPES.get(doc_type, {}).get('required_sections', [])
        for section_name, keywords in required:
            found = False
            for keyword in keywords:
                # 支持多种章节标题格式
                patterns = [
                    rf'##\s*\d*\.?\s*{re.escape(keyword)}',
                    rf'###\s*\d*\.?\s*{re.escape(keyword)}',
                    rf'##\s*{re.escape(keyword)}',
                    rf'###\s*{re.escape(keyword)}'
                ]
                if any(re.search(p, content, re.IGNORECASE) for p in patterns):
                    found = True
                    break
            if not found:
                result.missing_sections.append(section_name)
        
        result.has_required_sections = len(result.missing_sections) == 0
        
        if result.missing_sections:
            result.issues.append(f"缺少章节: {', '.join(result.missing_sections)}")
        
        return result
    
    def check_schema(self, schema_dir: Path) -> List[DocumentCheckResult]:
        """检查一个Schema的所有文档"""
        results = []
        for doc_type in self.DOC_TYPES.keys():
            doc_path = schema_dir / doc_type
            result = self.check_document(doc_path, doc_type)
            results.append(result)
        return results
    
    def run_full_check(self) -> Dict[str, Any]:
        """运行完整检查"""
        print("🔍 开始文档质量全面检查...\n")
        
        schema_dirs = self.get_all_schema_dirs()
        self.summary['total_schemas'] = len(schema_dirs)
        
        print(f"发现 {len(schema_dirs)} 个Schema目录")
        
        for i, schema_dir in enumerate(schema_dirs, 1):
            print(f"  检查 [{i}/{len(schema_dirs)}] {schema_dir.name}...", end=' ')
            results = self.check_schema(schema_dir)
            self.results.extend(results)
            
            # 统计
            complete = sum(1 for r in results if r.exists and r.has_required_sections)
            incomplete = sum(1 for r in results if r.exists and not r.has_required_sections)
            missing = sum(1 for r in results if not r.exists)
            
            print(f"✓完整:{complete} ⚠不完整:{incomplete} ✗缺失:{missing}")
        
        # 生成汇总
        self._generate_summary()
        
        return self.summary
    
    def _generate_summary(self):
        """生成汇总统计"""
        self.summary['total_docs'] = len(self.results)
        self.summary['complete_docs'] = sum(
            1 for r in self.results if r.exists and r.has_required_sections
        )
        self.summary['incomplete_docs'] = sum(
            1 for r in self.results if r.exists and not r.has_required_sections
        )
        self.summary['missing_docs'] = sum(
            1 for r in self.results if not r.exists
        )
        
        # 按文档类型统计问题
        for doc_type in self.DOC_TYPES.keys():
            type_results = [r for r in self.results if r.doc_type == doc_type]
            self.summary['issues_by_type'][doc_type] = {
                'total': len(type_results),
                'complete': sum(1 for r in type_results if r.exists and r.has_required_sections),
                'incomplete': sum(1 for r in type_results if r.exists and not r.has_required_sections),
                'missing': sum(1 for r in type_results if not r.exists)
            }
    
    def generate_report(self, output_path: str = 'document_quality_report.json'):
        """生成检查报告"""
        report = {
            'summary': self.summary,
            'results': [
                {
                    'file_path': r.file_path,
                    'doc_type': r.doc_type,
                    'exists': r.exists,
                    'has_toc': r.has_toc,
                    'has_required_sections': r.has_required_sections,
                    'missing_sections': r.missing_sections,
                    'issues': r.issues
                }
                for r in self.results
            ]
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"\n📄 详细报告已保存: {output_path}")
        return report
    
    def print_summary(self):
        """打印汇总信息"""
        print("\n" + "=" * 60)
        print("📊 文档质量检查汇总")
        print("=" * 60)
        print(f"总Schema数: {self.summary['total_schemas']}")
        print(f"总文档数: {self.summary['total_docs']}")
        print(f"完整文档: {self.summary['complete_docs']} ({self.summary['complete_docs']/max(self.summary['total_docs'],1)*100:.1f}%)")
        print(f"不完整文档: {self.summary['incomplete_docs']} ({self.summary['incomplete_docs']/max(self.summary['total_docs'],1)*100:.1f}%)")
        print(f"缺失文档: {self.summary['missing_docs']} ({self.summary['missing_docs']/max(self.summary['total_docs'],1)*100:.1f}%)")
        
        print("\n📋 按文档类型统计:")
        print("-" * 60)
        for doc_type, stats in self.summary['issues_by_type'].items():
            print(f"{doc_type:25s} 完整:{stats['complete']:3d}  不完整:{stats['incomplete']:3d}  缺失:{stats['missing']:3d}")


def main():
    checker = DocumentQualityChecker()
    checker.run_full_check()
    checker.print_summary()
    checker.generate_report()
    
    # 生成Markdown报告
    print("\n" + "=" * 60)
    print("🔍 问题文档列表 (前20个)")
    print("=" * 60)
    
    problem_docs = [r for r in checker.results if r.issues]
    for r in problem_docs[:20]:
        print(f"\n📄 {r.file_path}")
        for issue in r.issues:
            print(f"   ⚠️  {issue}")


if __name__ == '__main__':
    main()
