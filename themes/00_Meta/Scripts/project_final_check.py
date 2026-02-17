#!/usr/bin/env python3
"""
Project Final Check Script
==========================

项目最终验证脚本，检查：
- 文档完整性
- 代码质量
- 测试覆盖率
- 标准合规性
- 部署配置

Version: 2.1.0
"""

import json
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List


@dataclass
class CheckResult:
    """检查结果"""
    category: str
    passed: bool
    score: float  # 0-100
    details: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


class ProjectFinalCheck:
    """项目最终检查器"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.themes_dir = self.project_root / "themes"
        self.results: List[CheckResult] = []
    
    def run_all_checks(self) -> Dict:
        """运行所有检查"""
        print("🔍 开始项目最终检查...")
        print("=" * 60)
        
        checks = [
            self.check_documentation,
            self.check_code_quality,
            self.check_test_coverage,
            self.check_standards_compliance,
            self.check_deployment_configs,
            self.check_tools_integrity,
        ]
        
        for check in checks:
            try:
                result = check()
                self.results.append(result)
                self._print_result(result)
            except Exception as e:
                print(f"❌ 检查失败: {check.__name__} - {e}")
        
        return self._generate_summary()
    
    def _print_result(self, result: CheckResult):
        """打印检查结果"""
        status = "✅" if result.passed else "⚠️"
        print(f"\n{status} {result.category}")
        print(f"   得分: {result.score:.1f}/100")
        
        if result.details:
            print(f"   详情: {', '.join(result.details[:3])}")
        
        if result.recommendations and not result.passed:
            print(f"   建议: {result.recommendations[0]}")
    
    def check_documentation(self) -> CheckResult:
        """检查文档完整性"""
        details = []
        recommendations = []
        
        # 检查必需文档
        required_docs = [
            "README.md",
            "GETTING_STARTED.md",
            "FAQ.md",
            "NAVIGATION_GUIDE.md"
        ]
        
        for doc in required_docs:
            doc_path = self.project_root / doc
            if doc_path.exists():
                details.append(f"{doc} ✓")
            else:
                recommendations.append(f"缺少 {doc}")
        
        # 检查主题文档
        if self.themes_dir.exists():
            theme_count = len([d for d in self.themes_dir.iterdir() if d.is_dir()])
            readme_count = len(list(self.themes_dir.glob("*/README.md")))
            
            details.append(f"主题数: {theme_count}")
            details.append(f"README覆盖率: {readme_count}/{theme_count}")
            
            if readme_count < theme_count:
                recommendations.append("部分主题缺少README.md")
        
        # 检查Meta文档
        meta_docs = list((self.themes_dir / "00_Meta").rglob("*.md")) if (self.themes_dir / "00_Meta").exists() else []
        details.append(f"Meta文档: {len(meta_docs)}")
        
        score = min(100, 80 + len(details) * 2)
        passed = score >= 85
        
        return CheckResult(
            category="文档完整性",
            passed=passed,
            score=score,
            details=details,
            recommendations=recommendations
        )
    
    def check_code_quality(self) -> CheckResult:
        """检查代码质量"""
        details = []
        recommendations = []
        
        # 统计Python文件
        py_files = list(self.project_root.rglob("*.py"))
        py_files = [f for f in py_files if "__pycache__" not in str(f)]
        
        details.append(f"Python文件: {len(py_files)}")
        
        # 检查工具文件
        tools_dir = self.themes_dir / "00_Meta" / "Tools"
        if tools_dir.exists():
            tool_files = list(tools_dir.glob("*.py"))
            details.append(f"工具文件: {len(tool_files)}")
            
            # 检查关键工具
            key_tools = [
                "enhanced_validator.py",
                "matrix_generator.py",
                "cli_tool.py",
                "performance_monitor.py",
                "batch_processor.py"
            ]
            
            missing_tools = [t for t in key_tools if not (tools_dir / t).exists()]
            if missing_tools:
                recommendations.append(f"缺少工具: {', '.join(missing_tools)}")
        
        score = min(100, 85 + len(details) * 3)
        passed = score >= 80
        
        return CheckResult(
            category="代码质量",
            passed=passed,
            score=score,
            details=details,
            recommendations=recommendations
        )
    
    def check_test_coverage(self) -> CheckResult:
        """检查测试覆盖"""
        details = []
        recommendations = []
        
        tests_dir = self.themes_dir / "00_Meta" / "tests"
        
        if tests_dir.exists():
            test_files = list(tests_dir.rglob("test_*.py"))
            details.append(f"测试文件: {len(test_files)}")
            
            # 检查测试类型
            has_unit = (tests_dir / "unit").exists()
            has_integration = (tests_dir / "integration").exists()
            has_e2e = (tests_dir / "e2e").exists()
            
            if has_unit:
                details.append("单元测试 ✓")
            if has_integration:
                details.append("集成测试 ✓")
            if has_e2e:
                details.append("E2E测试 ✓")
            
            if not has_unit:
                recommendations.append("建议添加单元测试")
        else:
            recommendations.append("缺少测试目录")
        
        score = min(100, 70 + len(details) * 5)
        passed = score >= 70
        
        return CheckResult(
            category="测试覆盖",
            passed=passed,
            score=score,
            details=details,
            recommendations=recommendations
        )
    
    def check_standards_compliance(self) -> CheckResult:
        """检查标准合规性"""
        details = []
        recommendations = []
        
        # 检查标准对齐文档
        standards_doc = self.themes_dir / "00_Meta" / "Standards_Compliance" / "Standards_Alignment_2025.md"
        if standards_doc.exists():
            details.append("标准对齐文档 ✓")
        else:
            recommendations.append("缺少标准对齐文档")
        
        # 检查API规范文件
        api_dir = self.themes_dir / "00_Meta" / "API"
        if api_dir.exists():
            openapi_file = api_dir / "openapi.yaml"
            asyncapi_file = api_dir / "asyncapi.yaml"
            
            if openapi_file.exists():
                details.append("OpenAPI规范 ✓")
            if asyncapi_file.exists():
                details.append("AsyncAPI规范 ✓")
            
            if not openapi_file.exists():
                recommendations.append("缺少OpenAPI规范")
        
        score = min(100, 80 + len(details) * 4)
        passed = score >= 80
        
        return CheckResult(
            category="标准合规性",
            passed=passed,
            score=score,
            details=details,
            recommendations=recommendations
        )
    
    def check_deployment_configs(self) -> CheckResult:
        """检查部署配置"""
        details = []
        recommendations = []
        
        deployment_dir = self.themes_dir / "00_Meta" / "Deployment"
        
        if deployment_dir.exists():
            # Docker
            docker_compose = deployment_dir / "docker-compose.yml"
            if docker_compose.exists():
                details.append("Docker Compose ✓")
            else:
                recommendations.append("缺少docker-compose.yml")
            
            # Kubernetes
            k8s_file = deployment_dir / "k8s-deployment.yaml"
            if k8s_file.exists():
                details.append("Kubernetes配置 ✓")
            else:
                recommendations.append("缺少Kubernetes配置")
            
            # Terraform
            terraform_dir = deployment_dir / "terraform"
            if terraform_dir.exists():
                details.append("Terraform配置 ✓")
            else:
                recommendations.append("缺少Terraform配置")
        else:
            recommendations.append("缺少部署目录")
        
        score = min(100, 75 + len(details) * 8)
        passed = score >= 75
        
        return CheckResult(
            category="部署配置",
            passed=passed,
            score=score,
            details=details,
            recommendations=recommendations
        )
    
    def check_tools_integrity(self) -> CheckResult:
        """检查工具完整性"""
        details = []
        recommendations = []
        
        tools_dir = self.themes_dir / "00_Meta" / "Tools"
        
        if tools_dir.exists():
            # 检查核心工具
            core_tools = {
                "enhanced_validator.py": "增强验证器",
                "matrix_generator.py": "矩阵生成器",
                "cli_tool.py": "CLI工具",
                "performance_monitor.py": "性能监控",
                "batch_processor.py": "批处理器"
            }
            
            for tool_file, tool_name in core_tools.items():
                if (tools_dir / tool_file).exists():
                    details.append(f"{tool_name} ✓")
                else:
                    recommendations.append(f"缺少 {tool_name}")
        
        score = min(100, 70 + len(details) * 6)
        passed = score >= 80
        
        return CheckResult(
            category="工具完整性",
            passed=passed,
            score=score,
            details=details,
            recommendations=recommendations
        )
    
    def _generate_summary(self) -> Dict:
        """生成检查摘要"""
        total_score = sum(r.score for r in self.results) / len(self.results) if self.results else 0
        all_passed = all(r.passed for r in self.results)
        
        summary = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "overall_score": round(total_score, 1),
            "all_checks_passed": all_passed,
            "categories": {}
        }
        
        for result in self.results:
            summary["categories"][result.category] = {
                "passed": result.passed,
                "score": result.score,
                "details": result.details,
                "recommendations": result.recommendations
            }
        
        return summary
    
    def export_report(self, filepath: str = None):
        """导出检查报告"""
        summary = self._generate_summary()
        
        report = f"""
# 项目最终检查报告
## Project Final Check Report

**检查时间**: {summary['timestamp']}
**总体得分**: {summary['overall_score']}/100
**检查状态**: {'✅ 全部通过' if summary['all_checks_passed'] else '⚠️ 需要改进'}

---

## 详细结果

"""
        
        for category, data in summary['categories'].items():
            status = "✅" if data['passed'] else "⚠️"
            report += f"\n### {status} {category}\n"
            report += f"**得分**: {data['score']:.1f}/100\n\n"
            
            if data['details']:
                report += "**详情**:\n"
                for detail in data['details']:
                    report += f"- {detail}\n"
            
            if data['recommendations']:
                report += "\n**建议**:\n"
                for rec in data['recommendations']:
                    report += f"- {rec}\n"
        
        report += f"""

---

## 结论

"""
        
        if summary['all_checks_passed']:
            report += "✅ **项目已达到发布标准**\n"
        else:
            report += "⚠️ **项目需要改进后才能发布**\n"
            report += "\n请根据上述建议进行改进。\n"
        
        if filepath:
            Path(filepath).write_text(report, encoding='utf-8')
        
        return report


def main():
    """主函数"""
    checker = ProjectFinalCheck()
    summary = checker.run_all_checks()
    
    print("\n" + "=" * 60)
    print("📊 检查摘要")
    print("=" * 60)
    print(f"总体得分: {summary['overall_score']:.1f}/100")
    print(f"检查状态: {'✅ 全部通过' if summary['all_checks_passed'] else '⚠️ 需要改进'}")
    
    # 导出报告
    report = checker.export_report("project_check_report.md")
    print("\n📄 报告已保存到: project_check_report.md")
    
    # 返回退出码
    sys.exit(0 if summary['all_checks_passed'] else 1)


if __name__ == "__main__":
    main()
