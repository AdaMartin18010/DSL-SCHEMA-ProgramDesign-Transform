#!/usr/bin/env python3
"""
Schema文档质量检查脚本
检查所有Schema文档是否符合标准结构
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class CheckStatus(Enum):
    PASS = "✅"
    FAIL = "❌"
    WARNING = "⚠️"
    SKIP = "⏭️"


@dataclass
class CheckResult:
    file_path: str
    check_name: str
    status: CheckStatus
    message: str


class SchemaDocumentValidator:
    """Schema文档验证器"""
    
    STANDARD_FILES = [
        "01_Overview.md",
        "02_Formal_Definition.md",
        "03_Standards.md",
        "04_Transformation.md",
        "05_Case_Studies.md"
    ]
    
    def __init__(self, themes_dir: str = "themes"):
        self.themes_dir = Path(themes_dir)
        self.results: List[CheckResult] = []
        self.stats = {
            "total_schemas": 0,
            "complete_schemas": 0,
            "incomplete_schemas": 0,
            "total_checks": 0,
            "passed_checks": 0,
            "failed_checks": 0
        }
    
    def validate_all(self) -> None:
        """验证所有Schema文档"""
        print("=" * 80)
        print("Schema文档质量全面检查")
        print("=" * 80)
        
        # 遍历所有主题
        for theme_dir in sorted(self.themes_dir.iterdir()):
            if not theme_dir.is_dir():
                continue
            
            # 遍历主题下的所有Schema
            for schema_dir in sorted(theme_dir.iterdir()):
                if not schema_dir.is_dir():
                    continue
                
                self.stats["total_schemas"] += 1
                self._validate_schema(schema_dir)
        
        self._print_summary()
    
    def _validate_schema(self, schema_dir: Path) -> None:
        """验证单个Schema目录"""
        schema_name = schema_dir.name
        theme_name = schema_dir.parent.name
        
        print(f"\n检查: {theme_name}/{schema_name}")
        print("-" * 60)
        
        # 检查标准文件是否存在
        all_exist = True
        for std_file in self.STANDARD_FILES:
            file_path = schema_dir / std_file
            exists = file_path.exists()
            status = CheckStatus.PASS if exists else CheckStatus.FAIL
            self.results.append(CheckResult(
                file_path=str(file_path),
                check_name=f"文件存在性检查: {std_file}",
                status=status,
                message=f"{'文件存在' if exists else '文件缺失'}"
            ))
            print(f"  {status.value} {std_file}: {'存在' if exists else '缺失'}")
            if not exists:
                all_exist = False
        
        if all_exist:
            self.stats["complete_schemas"] += 1
            # 检查每个文件的内容
            for std_file in self.STANDARD_FILES:
                file_path = schema_dir / std_file
                self._validate_file_content(file_path)
        else:
            self.stats["incomplete_schemas"] += 1
    
    def _validate_file_content(self, file_path: Path) -> None:
        """验证文件内容"""
        try:
            content = file_path.read_text(encoding='utf-8')
        except Exception as e:
            self.results.append(CheckResult(
                file_path=str(file_path),
                check_name="文件读取",
                status=CheckStatus.FAIL,
                message=f"无法读取文件: {e}"
            ))
            return
        
        file_name = file_path.name
        
        # 根据文件类型进行不同的检查
        if file_name == "01_Overview.md":
            self._check_overview(content, file_path)
        elif file_name == "02_Formal_Definition.md":
            self._check_formal_definition(content, file_path)
        elif file_name == "03_Standards.md":
            self._check_standards(content, file_path)
        elif file_name == "04_Transformation.md":
            self._check_transformation(content, file_path)
        elif file_name == "05_Case_Studies.md":
            self._check_case_studies(content, file_path)
    
    def _check_overview(self, content: str, file_path: Path) -> None:
        """检查01_Overview.md内容"""
        checks = [
            ("目录结构", "## 📑 目录" in content or "## 目录" in content),
            ("核心结论", "核心结论" in content),
            ("概念定义", "概念定义" in content or "## 2. 概念定义" in content),
            ("Schema元素", "Schema元素" in content or "## 3. Schema元素" in content),
            ("标准对标", "标准对标" in content or "## 4. 标准对标" in content),
            ("应用场景", "应用场景" in content or "## 5. 应用场景" in content),
            ("思维导图", "思维导图" in content or "```mermaid" in content),
        ]
        
        for check_name, condition in checks:
            self.stats["total_checks"] += 1
            status = CheckStatus.PASS if condition else CheckStatus.WARNING
            if condition:
                self.stats["passed_checks"] += 1
            else:
                self.stats["failed_checks"] += 1
            
            self.results.append(CheckResult(
                file_path=str(file_path),
                check_name=f"Overview.{check_name}",
                status=status,
                message=f"{'包含' if condition else '缺失'} {check_name}"
            ))
            print(f"    {status.value} {check_name}")
    
    def _check_formal_definition(self, content: str, file_path: Path) -> None:
        """检查02_Formal_Definition.md内容"""
        checks = [
            ("形式化模型", "形式化模型" in content or "## 2. 形式化模型" in content),
            ("类型系统", "类型系统" in content or "## 4. 类型系统" in content),
            ("约束规则", "约束规则" in content or "## 5. 约束规则" in content),
        ]
        
        for check_name, condition in checks:
            self.stats["total_checks"] += 1
            status = CheckStatus.PASS if condition else CheckStatus.WARNING
            if condition:
                self.stats["passed_checks"] += 1
            else:
                self.stats["failed_checks"] += 1
            
            self.results.append(CheckResult(
                file_path=str(file_path),
                check_name=f"FormalDefinition.{check_name}",
                status=status,
                message=f"{'包含' if condition else '缺失'} {check_name}"
            ))
            print(f"    {status.value} {check_name}")
    
    def _check_standards(self, content: str, file_path: Path) -> None:
        """检查03_Standards.md内容"""
        checks = [
            ("标准体系", "标准体系" in content or "## 2. 标准体系" in content),
            ("主要标准", "主要标准" in content or "## 3. 主要标准" in content),
            ("标准对比", "标准对比" in content or "## 5. 标准对比" in content or "对比矩阵" in content),
            ("发展趋势", "发展趋势" in content or "## 6. 标准发展趋势" in content),
        ]
        
        for check_name, condition in checks:
            self.stats["total_checks"] += 1
            status = CheckStatus.PASS if condition else CheckStatus.WARNING
            if condition:
                self.stats["passed_checks"] += 1
            else:
                self.stats["failed_checks"] += 1
            
            self.results.append(CheckResult(
                file_path=str(file_path),
                check_name=f"Standards.{check_name}",
                status=status,
                message=f"{'包含' if condition else '缺失'} {check_name}"
            ))
            print(f"    {status.value} {check_name}")
    
    def _check_transformation(self, content: str, file_path: Path) -> None:
        """检查04_Transformation.md内容"""
        checks = [
            ("转换体系", "转换体系" in content or "## 2. 转换体系" in content),
            ("转换规则", "转换规则" in content or "## 3. 转换规则" in content),
            ("代码示例", "```python" in content or "```" in content),
            ("数据库存储", "数据库存储" in content or "## 6. 数据库存储" in content or "PostgreSQL" in content),
        ]
        
        for check_name, condition in checks:
            self.stats["total_checks"] += 1
            status = CheckStatus.PASS if condition else CheckStatus.WARNING
            if condition:
                self.stats["passed_checks"] += 1
            else:
                self.stats["failed_checks"] += 1
            
            self.results.append(CheckResult(
                file_path=str(file_path),
                check_name=f"Transformation.{check_name}",
                status=status,
                message=f"{'包含' if condition else '缺失'} {check_name}"
            ))
            print(f"    {status.value} {check_name}")
    
    def _check_case_studies(self, content: str, file_path: Path) -> None:
        """检查05_Case_Studies.md内容"""
        checks = [
            ("案例概述", "案例" in content),
            ("业务背景", "业务背景" in content),
            ("技术挑战", "技术挑战" in content),
            ("解决方案", "解决方案" in content),
            ("效果评估", "效果评估" in content),
        ]
        
        for check_name, condition in checks:
            self.stats["total_checks"] += 1
            status = CheckStatus.PASS if condition else CheckStatus.WARNING
            if condition:
                self.stats["passed_checks"] += 1
            else:
                self.stats["failed_checks"] += 1
            
            self.results.append(CheckResult(
                file_path=str(file_path),
                check_name=f"CaseStudies.{check_name}",
                status=status,
                message=f"{'包含' if condition else '缺失'} {check_name}"
            ))
            print(f"    {status.value} {check_name}")
    
    def _print_summary(self) -> None:
        """打印总结"""
        print("\n" + "=" * 80)
        print("检查总结")
        print("=" * 80)
        print(f"总Schema数: {self.stats['total_schemas']}")
        print(f"完整Schema数: {self.stats['complete_schemas']} ({self.stats['complete_schemas']/max(1,self.stats['total_schemas'])*100:.1f}%)")
        print(f"不完整Schema数: {self.stats['incomplete_schemas']}")
        print(f"总检查项: {self.stats['total_checks']}")
        print(f"通过: {self.stats['passed_checks']} ({self.stats['passed_checks']/max(1,self.stats['total_checks'])*100:.1f}%)")
        print(f"失败: {self.stats['failed_checks']}")
        
        # 输出失败项
        failed_results = [r for r in self.results if r.status == CheckStatus.FAIL]
        warning_results = [r for r in self.results if r.status == CheckStatus.WARNING]
        
        if failed_results:
            print("\n" + "=" * 80)
            print("❌ 失败项列表")
            print("=" * 80)
            for r in failed_results:
                print(f"{r.file_path}")
                print(f"  检查: {r.check_name}")
                print(f"  消息: {r.message}")
                print()
        
        if warning_results:
            print("\n" + "=" * 80)
            print("⚠️ 警告项列表（前20个）")
            print("=" * 80)
            for r in warning_results[:20]:
                print(f"{r.file_path}")
                print(f"  检查: {r.check_name}")
                print(f"  消息: {r.message}")
                print()
    
    def generate_report(self, output_file: str = "schema_validation_report.md") -> None:
        """生成Markdown报告"""
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# Schema文档质量检查报告\n\n")
            f.write(f"**生成时间**: {os.popen('date').read().strip()}\n\n")
            
            f.write("## 📊 检查统计\n\n")
            f.write(f"- 总Schema数: {self.stats['total_schemas']}\n")
            f.write(f"- 完整Schema数: {self.stats['complete_schemas']}\n")
            f.write(f"- 不完整Schema数: {self.stats['incomplete_schemas']}\n")
            f.write(f"- 总检查项: {self.stats['total_checks']}\n")
            f.write(f"- 通过: {self.stats['passed_checks']}\n")
            f.write(f"- 失败: {self.stats['failed_checks']}\n\n")
            
            # 按状态分组
            failed_results = [r for r in self.results if r.status == CheckStatus.FAIL]
            warning_results = [r for r in self.results if r.status == CheckStatus.WARNING]
            
            if failed_results:
                f.write("## ❌ 失败项\n\n")
                for r in failed_results:
                    f.write(f"### {r.file_path}\n\n")
                    f.write(f"- **检查**: {r.check_name}\n")
                    f.write(f"- **消息**: {r.message}\n\n")
            
            if warning_results:
                f.write("## ⚠️ 警告项\n\n")
                for r in warning_results[:50]:  # 限制数量
                    f.write(f"- `{r.file_path}`: {r.check_name} - {r.message}\n")
        
        print(f"\n报告已生成: {output_file}")


def main():
    """主函数"""
    validator = SchemaDocumentValidator()
    validator.validate_all()
    validator.generate_report()


if __name__ == "__main__":
    main()
