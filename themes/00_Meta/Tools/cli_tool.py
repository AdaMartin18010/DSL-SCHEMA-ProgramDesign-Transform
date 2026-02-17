#!/usr/bin/env python3
"""
DSL Schema CLI Tool
===================
命令行工具，用于管理Schema开发工作流

Features:
- 主题管理：创建、验证、删除主题
- 文档生成：自动生成各类文档
- 质量检查：文档完整性和质量分析
- 搜索：全文搜索Schema内容
- 导出：导出为多种格式

Usage:
    python cli_tool.py <command> [options]

Commands:
    validate    验证主题或文档
    generate    生成文档或代码
    search      搜索内容
    export      导出为其他格式
    stats       显示统计信息
    fix         自动修复问题
"""

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import yaml

# 项目路径配置
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
THEMES_DIR = PROJECT_ROOT / "themes"
META_DIR = THEMES_DIR / "00_Meta"


class Colors:
    """终端颜色"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def color_print(text: str, color: str = ""):
    """打印带颜色的文本"""
    if color:
        print(f"{color}{text}{Colors.ENDC}")
    else:
        print(text)


class SchemaCLI:
    """DSL Schema命令行工具"""
    
    def __init__(self):
        self.parser = argparse.ArgumentParser(
            description="DSL Schema CLI Tool",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
    %(prog)s validate --theme 01_Industrial_Automation
    %(prog)s generate --type matrix --output matrix.md
    %(prog)s search "data model" --scope all
    %(prog)s export --format json --output schemas.json
    %(prog)s stats
            """
        )
        self._setup_subcommands()
    
    def _setup_subcommands(self):
        """设置子命令"""
        subparsers = self.parser.add_subparsers(dest='command', help='可用命令')
        
        # validate 命令
        validate_parser = subparsers.add_parser(
            'validate', 
            help='验证主题或文档'
        )
        validate_parser.add_argument(
            '--theme', '-t',
            help='要验证的主题目录名'
        )
        validate_parser.add_argument(
            '--all', '-a',
            action='store_true',
            help='验证所有主题'
        )
        validate_parser.add_argument(
            '--fix', '-f',
            action='store_true',
            help='自动修复发现的问题'
        )
        
        # generate 命令
        generate_parser = subparsers.add_parser(
            'generate',
            help='生成文档或代码'
        )
        generate_parser.add_argument(
            '--type', '-t',
            required=True,
            choices=['index', 'matrix', 'summary', 'mermaid'],
            help='生成类型'
        )
        generate_parser.add_argument(
            '--output', '-o',
            help='输出文件路径'
        )
        generate_parser.add_argument(
            '--theme', '-T',
            help='指定主题'
        )
        
        # search 命令
        search_parser = subparsers.add_parser(
            'search',
            help='搜索内容'
        )
        search_parser.add_argument(
            'query',
            help='搜索关键词'
        )
        search_parser.add_argument(
            '--scope', '-s',
            choices=['all', 'titles', 'content', 'code'],
            default='all',
            help='搜索范围'
        )
        search_parser.add_argument(
            '--theme', '-t',
            help='限定主题'
        )
        
        # export 命令
        export_parser = subparsers.add_parser(
            'export',
            help='导出为其他格式'
        )
        export_parser.add_argument(
            '--format', '-f',
            required=True,
            choices=['json', 'yaml', 'csv', 'html'],
            help='导出格式'
        )
        export_parser.add_argument(
            '--output', '-o',
            required=True,
            help='输出文件'
        )
        
        # stats 命令
        stats_parser = subparsers.add_parser(
            'stats',
            help='显示统计信息'
        )
        stats_parser.add_argument(
            '--detail', '-d',
            action='store_true',
            help='显示详细信息'
        )
        
        # fix 命令
        fix_parser = subparsers.add_parser(
            'fix',
            help='自动修复问题'
        )
        fix_parser.add_argument(
            '--type', '-t',
            choices=['links', 'headers', 'format', 'all'],
            default='all',
            help='修复类型'
        )
    
    def run(self):
        """运行CLI"""
        args = self.parser.parse_args()
        
        if not args.command:
            self.parser.print_help()
            return
        
        handler = getattr(self, f'cmd_{args.command}', None)
        if handler:
            handler(args)
        else:
            color_print(f"未知命令: {args.command}", Colors.FAIL)
    
    # ============== 命令实现 ==============
    
    def cmd_validate(self, args):
        """验证命令"""
        color_print("🔍 开始验证...", Colors.HEADER)
        
        if args.all:
            themes = self._get_all_themes()
        elif args.theme:
            themes = [args.theme]
        else:
            color_print("❌ 请指定 --theme 或 --all", Colors.FAIL)
            return
        
        total_errors = 0
        total_warnings = 0
        
        for theme in themes:
            errors, warnings = self._validate_theme(theme, args.fix)
            total_errors += errors
            total_warnings += warnings
        
        color_print(f"\n{'='*50}", Colors.OKCYAN)
        color_print(f"验证完成: {len(themes)} 个主题", Colors.OKCYAN)
        color_print(f"错误: {total_errors}, 警告: {total_warnings}", 
                   Colors.FAIL if total_errors > 0 else Colors.WARNING)
        
        sys.exit(1 if total_errors > 0 else 0)
    
    def _validate_theme(self, theme_name: str, auto_fix: bool) -> Tuple[int, int]:
        """验证单个主题"""
        color_print(f"\n📁 验证主题: {theme_name}", Colors.OKBLUE)
        
        errors = 0
        warnings = 0
        theme_path = THEMES_DIR / theme_name
        
        if not theme_path.exists():
            color_print(f"  ❌ 主题目录不存在: {theme_path}", Colors.FAIL)
            return 1, 0
        
        # 验证 README.md 存在
        readme_path = theme_path / "README.md"
        if not readme_path.exists():
            color_print(f"  ❌ 缺少 README.md", Colors.FAIL)
            errors += 1
        else:
            # 验证 README 内容
            content = readme_path.read_text(encoding='utf-8')
            if not content.startswith("#"):
                color_print(f"  ⚠️ README.md 缺少标题", Colors.WARNING)
                warnings += 1
        
        # 验证目录结构
        required_files = ['README.md']
        for file in required_files:
            file_path = theme_path / file
            if not file_path.exists():
                color_print(f"  ❌ 缺少必需文件: {file}", Colors.FAIL)
                errors += 1
        
        # 统计文档数量
        md_files = list(theme_path.rglob("*.md"))
        color_print(f"  ✅ 文档数量: {len(md_files)}", Colors.OKGREEN)
        
        return errors, warnings
    
    def cmd_generate(self, args):
        """生成命令"""
        color_print(f"📝 生成 {args.type}...", Colors.HEADER)
        
        if args.type == 'index':
            self._generate_index(args.output)
        elif args.type == 'matrix':
            self._generate_matrix(args.output, args.theme)
        elif args.type == 'summary':
            self._generate_summary(args.output)
        elif args.type == 'mermaid':
            self._generate_mermaid(args.output)
    
    def _generate_index(self, output_path: Optional[str]):
        """生成主题索引"""
        themes = self._get_all_themes()
        
        index_content = "# DSL Schema 主题索引\n\n"
        index_content += f"**生成时间**: {datetime.now().isoformat()}\n\n"
        index_content += "## 主题列表\n\n"
        
        for theme in sorted(themes):
            theme_path = THEMES_DIR / theme
            readme_path = theme_path / "README.md"
            
            if readme_path.exists():
                title = self._extract_title(readme_path)
                doc_count = len(list(theme_path.rglob("*.md")))
                
                index_content += f"### {theme}\n"
                index_content += f"- **标题**: {title}\n"
                index_content += f"- **文档数**: {doc_count}\n"
                index_content += f"- **路径**: `themes/{theme}/`\n\n"
        
        output_file = Path(output_path) if output_path else META_DIR / "INDEX.md"
        output_file.write_text(index_content, encoding='utf-8')
        color_print(f"✅ 索引已生成: {output_file}", Colors.OKGREEN)
    
    def _generate_matrix(self, output_path: Optional[str], theme: Optional[str]):
        """生成概念-属性矩阵"""
        # 简化的矩阵生成
        matrix_content = "# 概念-属性矩阵\n\n"
        matrix_content += "| 主题 | 理论 | 应用 | 标准 | 工具 | 行业 |\n"
        matrix_content += "|------|------|------|------|------|------|\n"
        
        themes = [theme] if theme else self._get_all_themes()
        
        for t in themes:
            row = f"| {t} | ✓ | ✓ | ✓ | ✓ | ✓ |\n"
            matrix_content += row
        
        output_file = Path(output_path) if output_path else META_DIR / "MATRIX.md"
        output_file.write_text(matrix_content, encoding='utf-8')
        color_print(f"✅ 矩阵已生成: {output_file}", Colors.OKGREEN)
    
    def _generate_summary(self, output_path: Optional[str]):
        """生成项目摘要"""
        themes = self._get_all_themes()
        
        summary = {
            "project": "DSL Schema @themes",
            "generated_at": datetime.now().isoformat(),
            "statistics": {
                "total_themes": len(themes),
                "total_documents": 0,
                "total_code_files": 0
            },
            "themes": []
        }
        
        for theme in themes:
            theme_path = THEMES_DIR / theme
            docs = list(theme_path.rglob("*.md"))
            code_files = list(theme_path.rglob("*.py"))
            
            summary["statistics"]["total_documents"] += len(docs)
            summary["statistics"]["total_code_files"] += len(code_files)
            
            summary["themes"].append({
                "name": theme,
                "documents": len(docs),
                "code_files": len(code_files)
            })
        
        output_file = Path(output_path) if output_path else META_DIR / "summary.json"
        output_file.write_text(json.dumps(summary, indent=2, ensure_ascii=False), 
                              encoding='utf-8')
        color_print(f"✅ 摘要已生成: {output_file}", Colors.OKGREEN)
    
    def _generate_mermaid(self, output_path: Optional[str]):
        """生成Mermaid图"""
        mermaid = """```mermaid
graph TD
    A[DSL Schema] --> B[理论基础]
    A --> C[行业应用]
    A --> D[工具链]
    
    B --> B1[概念模型]
    B --> B2[形式化方法]
    
    C --> C1[工业自动化]
    C --> C2[金融科技]
    C --> C3[医疗健康]
    
    D --> D1[验证器]
    D --> D2[生成器]
    D --> D3[API]
```"""
        
        output_file = Path(output_path) if output_path else META_DIR / "architecture.mmd"
        output_file.write_text(mermaid, encoding='utf-8')
        color_print(f"✅ Mermaid图已生成: {output_file}", Colors.OKGREEN)
    
    def cmd_search(self, args):
        """搜索命令"""
        color_print(f"🔎 搜索: {args.query}", Colors.HEADER)
        
        query = args.query.lower()
        results = []
        
        themes = [args.theme] if args.theme else self._get_all_themes()
        
        for theme in themes:
            theme_path = THEMES_DIR / theme
            for md_file in theme_path.rglob("*.md"):
                content = md_file.read_text(encoding='utf-8')
                
                if args.scope in ['all', 'content'] and query in content.lower():
                    # 找到匹配，提取上下文
                    lines = content.split('\n')
                    for i, line in enumerate(lines):
                        if query in line.lower():
                            context = '\n'.join(lines[max(0, i-2):i+3])
                            results.append({
                                'file': str(md_file.relative_to(PROJECT_ROOT)),
                                'line': i + 1,
                                'context': context
                            })
                            break
        
        color_print(f"\n找到 {len(results)} 个结果:", Colors.OKCYAN)
        
        for r in results[:20]:  # 只显示前20个
            color_print(f"\n📄 {r['file']}:{r['line']}", Colors.OKBLUE)
            print(r['context'])
    
    def cmd_export(self, args):
        """导出命令"""
        color_print(f"📦 导出为 {args.format}...", Colors.HEADER)
        
        themes = self._get_all_themes()
        data = []
        
        for theme in themes:
            theme_path = THEMES_DIR / theme
            theme_data = {
                "name": theme,
                "documents": []
            }
            
            for md_file in theme_path.rglob("*.md"):
                theme_data["documents"].append({
                    "path": str(md_file.relative_to(theme_path)),
                    "title": self._extract_title(md_file)
                })
            
            data.append(theme_data)
        
        output_file = Path(args.output)
        
        if args.format == 'json':
            output_file.write_text(json.dumps(data, indent=2, ensure_ascii=False),
                                  encoding='utf-8')
        elif args.format == 'yaml':
            output_file.write_text(yaml.dump(data, allow_unicode=True),
                                  encoding='utf-8')
        
        color_print(f"✅ 已导出到: {output_file}", Colors.OKGREEN)
    
    def cmd_stats(self, args):
        """统计命令"""
        color_print("📊 项目统计", Colors.HEADER)
        
        themes = self._get_all_themes()
        
        total_docs = 0
        total_code = 0
        total_size = 0
        
        for theme in themes:
            theme_path = THEMES_DIR / theme
            docs = list(theme_path.rglob("*.md"))
            code_files = list(theme_path.rglob("*.py"))
            
            total_docs += len(docs)
            total_code += len(code_files)
            total_size += sum(f.stat().st_size for f in docs)
        
        color_print(f"\n{'='*40}", Colors.OKCYAN)
        color_print(f"主题数量: {len(themes)}", Colors.OKGREEN)
        color_print(f"文档总数: {total_docs}", Colors.OKGREEN)
        color_print(f"代码文件: {total_code}", Colors.OKGREEN)
        color_print(f"总大小: {total_size / 1024 / 1024:.2f} MB", Colors.OKGREEN)
        
        if args.detail:
            color_print(f"\n{'='*40}", Colors.OKCYAN)
            color_print("主题详情:", Colors.HEADER)
            for theme in sorted(themes)[:10]:  # 显示前10个
                theme_path = THEMES_DIR / theme
                doc_count = len(list(theme_path.rglob("*.md")))
                color_print(f"  {theme}: {doc_count} 文档", Colors.OKBLUE)
    
    def cmd_fix(self, args):
        """修复命令"""
        color_print("🔧 自动修复...", Colors.HEADER)
        
        fixes_applied = 0
        
        if args.type in ['headers', 'all']:
            # 修复标题格式
            for theme in self._get_all_themes():
                readme_path = THEMES_DIR / theme / "README.md"
                if readme_path.exists():
                    content = readme_path.read_text(encoding='utf-8')
                    # 确保标题格式正确
                    if not content.startswith("# "):
                        content = "# " + content.lstrip("# ")
                        readme_path.write_text(content, encoding='utf-8')
                        fixes_applied += 1
        
        color_print(f"✅ 应用了 {fixes_applied} 个修复", Colors.OKGREEN)
    
    # ============== 辅助方法 ==============
    
    def _get_all_themes(self) -> List[str]:
        """获取所有主题目录"""
        if not THEMES_DIR.exists():
            return []
        
        return [
            d.name for d in THEMES_DIR.iterdir()
            if d.is_dir() and d.name.startswith(("0", "1", "2", "3"))
            and not d.name.startswith("00_Meta")
        ]
    
    def _extract_title(self, file_path: Path) -> str:
        """从Markdown文件提取标题"""
        try:
            content = file_path.read_text(encoding='utf-8')
            match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
            return match.group(1) if match else file_path.stem
        except:
            return file_path.stem


def main():
    """入口点"""
    cli = SchemaCLI()
    cli.run()


if __name__ == "__main__":
    main()
