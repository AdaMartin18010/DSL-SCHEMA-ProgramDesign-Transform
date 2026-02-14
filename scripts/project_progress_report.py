#!/usr/bin/env python3
"""
项目进度报告生成器

生成当前项目完成情况的综合报告
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any


class ProjectProgressReport:
    """项目进度报告生成器"""
    
    def __init__(self, project_root: str = None):
        if project_root is None:
            self.project_root = Path(__file__).parent.parent
        else:
            self.project_root = Path(project_root)
        
        self.report: Dict[str, Any] = {}
    
    def count_code_files(self) -> Dict:
        """统计代码文件"""
        code_dir = self.project_root / "code"
        
        stats = {
            'python_files': 0,
            'typescript_files': 0,
            'test_files': 0,
            'total_lines': 0
        }
        
        if not code_dir.exists():
            return stats
        
        for py_file in code_dir.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue
            
            try:
                lines = len(py_file.read_text(encoding='utf-8').split('\n'))
                stats['total_lines'] += lines
                
                if "test_" in py_file.name or "_test.py" in py_file.name:
                    stats['test_files'] += 1
                else:
                    stats['python_files'] += 1
            except:
                pass
        
        for ts_file in code_dir.rglob("*.ts"):
            try:
                lines = len(ts_file.read_text(encoding='utf-8').split('\n'))
                stats['typescript_files'] += 1
                stats['total_lines'] += lines
            except:
                pass
        
        return stats
    
    def count_schema_docs(self) -> Dict:
        """统计Schema文档"""
        themes_dir = self.project_root / "themes"
        
        stats = {
            'total_themes': 0,
            'total_schemas': 0,
            'total_docs': 0,
            'standard_docs': 0  # 01-05结构的文档
        }
        
        if not themes_dir.exists():
            return stats
        
        for theme_dir in themes_dir.iterdir():
            if theme_dir.is_dir() and theme_dir.name[0].isdigit():
                stats['total_themes'] += 1
                
                for schema_dir in theme_dir.iterdir():
                    if schema_dir.is_dir():
                        stats['total_schemas'] += 1
                        
                        # 检查标准文档
                        standard_files = [
                            "01_Overview.md",
                            "02_Formal_Definition.md",
                            "03_Standards.md",
                            "04_Transformation.md",
                            "05_Case_Studies.md"
                        ]
                        
                        for std_file in standard_files:
                            if (schema_dir / std_file).exists():
                                stats['standard_docs'] += 1
                            stats['total_docs'] += 1
        
        return stats
    
    def run_tests(self) -> Dict:
        """运行测试并统计结果"""
        import subprocess
        
        results = {
            'llm_tests': 0,
            'usl_tests': 0,
            'total_tests': 0,
            'passed': 0,
            'failed': 0
        }
        
        try:
            # 运行LLM测试
            result = subprocess.run(
                ["python", "-m", "pytest", "code/tests/test_llm_reasoning.py", "-v", "--tb=no"],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            for line in result.stdout.split('\n'):
                if 'passed' in line:
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if part == 'passed':
                            try:
                                count = int(parts[i-1])
                                results['llm_tests'] = count
                                results['passed'] += count
                            except:
                                pass
                elif 'failed' in line:
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if part == 'failed':
                            try:
                                count = int(parts[i-1])
                                results['failed'] += count
                            except:
                                pass
            
            # 运行USL测试
            result = subprocess.run(
                ["python", "-m", "pytest", "code/tests/test_usl.py", "-v", "--tb=no"],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            for line in result.stdout.split('\n'):
                if 'passed' in line:
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if part == 'passed':
                            try:
                                count = int(parts[i-1])
                                results['usl_tests'] = count
                                results['passed'] += count
                            except:
                                pass
                elif 'failed' in line:
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if part == 'failed':
                            try:
                                count = int(parts[i-1])
                                results['failed'] += count
                            except:
                                pass
            
            results['total_tests'] = results['llm_tests'] + results['usl_tests']
            
        except Exception as e:
            results['error'] = str(e)
        
        return results
    
    def calculate_progress(self) -> Dict:
        """计算总体进度"""
        # 基于任务清单计算进度
        tasks = {
            'P0': {'total': 2, 'completed': 2},  # P0任务全部完成
            'P1': {'total': 8, 'completed': 7},  # P1任务完成了7个
            'P2': {'total': 11, 'completed': 0},  # P2任务待开始
        }
        
        total_tasks = sum(t['total'] for t in tasks.values())
        completed_tasks = sum(t['completed'] for t in tasks.values())
        
        progress = {
            'overall': round(completed_tasks / total_tasks * 100, 1),
            'by_priority': {}
        }
        
        for priority, counts in tasks.items():
            progress['by_priority'][priority] = {
                'completed': counts['completed'],
                'total': counts['total'],
                'percentage': round(counts['completed'] / counts['total'] * 100, 1)
            }
        
        return progress
    
    def generate_report(self) -> Dict:
        """生成完整报告"""
        print("📊 正在生成项目进度报告...")
        
        code_stats = self.count_code_files()
        print(f"  ✅ 代码统计完成: {code_stats['python_files']} Python文件")
        
        doc_stats = self.count_schema_docs()
        print(f"  ✅ 文档统计完成: {doc_stats['total_schemas']} Schemas")
        
        test_stats = self.run_tests()
        print(f"  ✅ 测试统计完成: {test_stats.get('total_tests', 0)} 测试")
        
        progress = self.calculate_progress()
        
        self.report = {
            'generated_at': datetime.now().isoformat(),
            'code_statistics': code_stats,
            'documentation_statistics': doc_stats,
            'test_statistics': test_stats,
            'progress': progress,
            'summary': {
                'total_code_lines': code_stats['total_lines'],
                'total_schemas': doc_stats['total_schemas'],
                'total_docs': doc_stats['total_docs'],
                'total_tests': test_stats.get('total_tests', 0),
                'tests_passed': test_stats.get('passed', 0),
                'overall_progress': progress['overall']
            }
        }
        
        return self.report
    
    def print_report(self):
        """打印报告到控制台"""
        report = self.report
        summary = report['summary']
        
        print()
        print("=" * 70)
        print("📋 DSL Schema 项目进度报告")
        print("=" * 70)
        print()
        
        print("🎯 总体进度")
        print("-" * 70)
        print(f"  整体完成度: {summary['overall_progress']:.1f}%")
        print()
        
        print("📦 代码统计")
        print("-" * 70)
        code = report['code_statistics']
        print(f"  Python模块: {code['python_files']}")
        print(f"  TypeScript模块: {code['typescript_files']}")
        print(f"  测试文件: {code['test_files']}")
        print(f"  总代码行数: {code['total_lines']:,}")
        print()
        
        print("📚 文档统计")
        print("-" * 70)
        docs = report['documentation_statistics']
        print(f"  主题数: {docs['total_themes']}")
        print(f"  Schema数: {docs['total_schemas']}")
        print(f"  总文档数: {docs['total_docs']}")
        print(f"  标准结构文档: {docs['standard_docs']}")
        print()
        
        print("🧪 测试统计")
        print("-" * 70)
        tests = report['test_statistics']
        print(f"  总测试数: {tests.get('total_tests', 0)}")
        print(f"  LLM推理测试: {tests.get('llm_tests', 0)}")
        print(f"  USL测试: {tests.get('usl_tests', 0)}")
        print(f"  通过: {tests.get('passed', 0)}")
        print(f"  失败: {tests.get('failed', 0)}")
        print()
        
        print("📊 按优先级进度")
        print("-" * 70)
        for priority, stats in report['progress']['by_priority'].items():
            bar_length = 30
            filled = int(bar_length * stats['percentage'] / 100)
            bar = '█' * filled + '░' * (bar_length - filled)
            print(f"  {priority}: [{bar}] {stats['completed']}/{stats['total']} ({stats['percentage']:.1f}%)")
        print()
        
        print("=" * 70)
        print(f"✅ 项目整体完成度: {summary['overall_progress']:.1f}%")
        print("=" * 70)
    
    def save_report(self, filename: str = "project_progress_report.json"):
        """保存报告到文件"""
        output_path = self.project_root / "scripts" / filename
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.report, f, ensure_ascii=False, indent=2)
        print(f"\n💾 报告已保存: {output_path}")


def main():
    """主函数"""
    report_generator = ProjectProgressReport()
    report_generator.generate_report()
    report_generator.print_report()
    report_generator.save_report()


if __name__ == "__main__":
    main()
