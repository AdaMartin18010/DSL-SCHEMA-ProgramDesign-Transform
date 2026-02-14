#!/usr/bin/env python3
"""
文档验证脚本

执行以下检查：
1. 文档交叉引用检查
2. 代码示例验证
3. 思维导图完整性检查
"""

import re
import json
from pathlib import Path
from typing import Dict, List, Tuple, Set
from dataclasses import dataclass, field, asdict


@dataclass
class VerificationResult:
    """验证结果"""
    check_type: str
    status: str  # 'passed', 'warning', 'error'
    message: str
    details: List[str] = field(default_factory=list)


class DocumentationVerifier:
    """文档验证器"""
    
    def __init__(self, project_root: str = None):
        if project_root is None:
            self.project_root = Path(__file__).parent.parent
        else:
            self.project_root = Path(project_root)
        
        self.results: List[VerificationResult] = []
    
    def check_cross_references(self) -> VerificationResult:
        """检查文档交叉引用"""
        print("🔗 检查文档交叉引用...")
        
        issues = []
        warnings = []
        checked = 0
        
        # 检查所有markdown文件中的链接
        md_files = list(self.project_root.rglob("*.md"))
        
        link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        
        for md_file in md_files:
            if '.git' in str(md_file):
                continue
                
            try:
                content = md_file.read_text(encoding='utf-8')
                links = re.findall(link_pattern, content)
                
                for text, link in links:
                    checked += 1
                    
                    # 跳过外部链接
                    if link.startswith('http://') or link.startswith('https://'):
                        continue
                    
                    # 跳过锚点链接
                    if link.startswith('#'):
                        continue
                    
                    # 解析相对路径
                    if link.startswith('/'):
                        target = self.project_root / link[1:]
                    else:
                        target = md_file.parent / link
                    
                    # 移除锚点部分
                    target = Path(str(target).split('#')[0])
                    
                    if not target.exists():
                        rel_path = md_file.relative_to(self.project_root)
                        issues.append(f"{rel_path}: 链接指向不存在的文件 '{link}'")
            except Exception as e:
                warnings.append(f"无法读取 {md_file}: {e}")
        
        if issues:
            return VerificationResult(
                check_type='交叉引用',
                status='warning',
                message=f'发现 {len(issues)} 个损坏的链接 (检查了 {checked} 个)',
                details=issues[:20]  # 最多显示20个
            )
        else:
            return VerificationResult(
                check_type='交叉引用',
                status='passed',
                message=f'所有 {checked} 个链接有效',
                details=[]
            )
    
    def verify_code_examples(self) -> VerificationResult:
        """验证代码示例"""
        print("💻 验证代码示例...")
        
        issues = []
        checked = 0
        valid = 0
        
        # 检查Python代码块
        md_files = list(self.project_root.rglob("*.md"))
        
        python_code_pattern = r'```python\s*\n(.*?)```'
        
        for md_file in md_files:
            if '.git' in str(md_file):
                continue
            
            try:
                content = md_file.read_text(encoding='utf-8')
                python_blocks = re.findall(python_code_pattern, content, re.DOTALL)
                
                for block in python_blocks:
                    checked += 1
                    code = block.strip()
                    
                    if not code:
                        continue
                    
                    # 尝试编译Python代码
                    try:
                        compile(code, '<string>', 'exec')
                        valid += 1
                    except SyntaxError as e:
                        rel_path = md_file.relative_to(self.project_root)
                        issues.append(f"{rel_path}: Python语法错误 - {e.msg}")
            except Exception as e:
                pass
        
        if issues:
            return VerificationResult(
                check_type='代码示例',
                status='warning',
                message=f'{valid}/{checked} 个Python代码块语法正确',
                details=issues[:10]
            )
        else:
            return VerificationResult(
                check_type='代码示例',
                status='passed',
                message=f'所有 {checked} 个Python代码块语法正确',
                details=[]
            )
    
    def check_mindmaps(self) -> VerificationResult:
        """检查思维导图完整性"""
        print("🗺️  检查思维导图...")
        
        themes_dir = self.project_root / "themes"
        
        missing_mindmap = []
        total_overview = 0
        
        if themes_dir.exists():
            for theme_dir in themes_dir.iterdir():
                if theme_dir.is_dir() and theme_dir.name[0].isdigit():
                    for schema_dir in theme_dir.iterdir():
                        if schema_dir.is_dir():
                            overview_file = schema_dir / "01_Overview.md"
                            
                            if overview_file.exists():
                                total_overview += 1
                                
                                try:
                                    content = overview_file.read_text(encoding='utf-8')
                                    
                                    # 检查是否包含思维导图
                                    has_mindmap = bool(re.search(
                                        r'##?\s*思维导图|mindmap|graph\s+TD|graph\s+LR|flowchart',
                                        content,
                                        re.IGNORECASE
                                    ))
                                    
                                    if not has_mindmap:
                                        rel_path = overview_file.relative_to(self.project_root)
                                        missing_mindmap.append(str(rel_path))
                                except:
                                    pass
        
        if missing_mindmap:
            return VerificationResult(
                check_type='思维导图',
                status='warning',
                message=f'{len(missing_mindmap)}/{total_overview} 个Overview文档缺少思维导图',
                details=missing_mindmap[:15]
            )
        else:
            return VerificationResult(
                check_type='思维导图',
                status='passed',
                message=f'所有 {total_overview} 个Overview文档包含思维导图',
                details=[]
            )
    
    def run_all_checks(self) -> List[VerificationResult]:
        """运行所有检查"""
        print("=" * 70)
        print("📋 文档验证开始")
        print("=" * 70)
        print()
        
        self.results = [
            self.check_cross_references(),
            self.verify_code_examples(),
            self.check_mindmaps(),
        ]
        
        return self.results
    
    def print_report(self):
        """打印验证报告"""
        print()
        print("=" * 70)
        print("📊 文档验证报告")
        print("=" * 70)
        print()
        
        for result in self.results:
            status_icon = {
                'passed': '✅',
                'warning': '⚠️',
                'error': '❌'
            }.get(result.status, '❓')
            
            print(f"{status_icon} {result.check_type}")
            print(f"   状态: {result.status.upper()}")
            print(f"   结果: {result.message}")
            
            if result.details:
                print(f"   详情 (显示前{len(result.details)}个):")
                for detail in result.details:
                    print(f"      - {detail}")
            print()
        
        # 统计
        passed = sum(1 for r in self.results if r.status == 'passed')
        warnings = sum(1 for r in self.results if r.status == 'warning')
        errors = sum(1 for r in self.results if r.status == 'error')
        
        print("=" * 70)
        print(f"📈 统计: {passed} 通过, {warnings} 警告, {errors} 错误")
        print("=" * 70)
    
    def save_report(self, filename: str = "documentation_verification_report.json"):
        """保存报告到文件"""
        output_path = self.project_root / "scripts" / filename
        
        report = {
            'results': [asdict(r) for r in self.results],
            'summary': {
                'passed': sum(1 for r in self.results if r.status == 'passed'),
                'warnings': sum(1 for r in self.results if r.status == 'warning'),
                'errors': sum(1 for r in self.results if r.status == 'error'),
            }
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 报告已保存: {output_path}")


def main():
    """主函数"""
    verifier = DocumentationVerifier()
    verifier.run_all_checks()
    verifier.print_report()
    verifier.save_report()


if __name__ == "__main__":
    main()
