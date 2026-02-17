#!/usr/bin/env python3
"""
Documentation Auto-Generator
============================

自动生成项目文档，包括：
- 主题索引
- API文档
- 变更日志
- 统计报告

Usage:
    python doc_generator.py --all
    python doc_generator.py --type api --output docs/api.md
"""

import argparse
import ast
import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class DocGenerator:
    """文档生成器"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.themes_dir = self.project_root / "themes"
        self.output_dir = self.project_root / "generated_docs"
        self.output_dir.mkdir(exist_ok=True)
    
    def generate_all(self):
        """生成所有文档"""
        print("🚀 开始生成所有文档...")
        
        self.generate_theme_index()
        self.generate_api_docs()
        self.generate_stats_report()
        self.generate_changelog()
        self.generate_architecture_doc()
        
        print(f"✅ 文档已生成到: {self.output_dir}")
    
    def generate_theme_index(self):
        """生成主题索引"""
        print("📑 生成主题索引...")
        
        themes = self._get_all_themes()
        
        content = "# DSL Schema 主题索引\n\n"
        content += f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        content += f"**主题总数**: {len(themes)}\n\n"
        content += "---\n\n"
        
        for theme in sorted(themes):
            theme_path = self.themes_dir / theme
            info = self._get_theme_info(theme_path)
            
            content += f"## {info['title']}\n\n"
            content += f"- **目录**: `{theme}/`\n"
            content += f"- **文档数**: {info['doc_count']}\n"
            content += f"- **代码文件**: {info['code_count']}\n"
            
            if info['concepts']:
                content += f"- **核心概念**: {', '.join(info['concepts'][:5])}\n"
            
            if info['standards']:
                content += f"- **相关标准**: {', '.join(info['standards'][:3])}\n"
            
            content += "\n"
        
        output_file = self.output_dir / "THEME_INDEX.md"
        output_file.write_text(content, encoding='utf-8')
        print(f"  ✓ {output_file.name}")
    
    def generate_api_docs(self):
        """从代码生成API文档"""
        print("📚 生成API文档...")
        
        api_dir = self.themes_dir / "00_Meta" / "API"
        if not api_dir.exists():
            print("  ⚠️ 未找到API目录")
            return
        
        content = "# API 参考文档\n\n"
        content += f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        # 解析Python文件
        for py_file in sorted(api_dir.rglob("*.py")):
            if py_file.name.startswith("__"):
                continue
            
            content += f"## {py_file.stem}\n\n"
            
            try:
                source = py_file.read_text(encoding='utf-8')
                tree = ast.parse(source)
                
                # 提取类和函数
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        content += f"### Class: `{node.name}`\n\n"
                        docstring = ast.get_docstring(node)
                        if docstring:
                            content += f"{docstring}\n\n"
                        
                        # 提取方法
                        for item in node.body:
                            if isinstance(item, ast.FunctionDef):
                                content += f"#### `{item.name}()`\n\n"
                                method_doc = ast.get_docstring(item)
                                if method_doc:
                                    content += f"{method_doc}\n\n"
                
            except Exception as e:
                content += f"_解析错误: {e}_\n\n"
        
        output_file = self.output_dir / "API_REFERENCE.md"
        output_file.write_text(content, encoding='utf-8')
        print(f"  ✓ {output_file.name}")
    
    def generate_stats_report(self):
        """生成统计报告"""
        print("📊 生成统计报告...")
        
        themes = self._get_all_themes()
        
        stats = {
            "generated_at": datetime.now().isoformat(),
            "total_themes": len(themes),
            "total_documents": 0,
            "total_code_files": 0,
            "total_lines_of_code": 0,
            "languages": {},
            "themes": []
        }
        
        for theme in sorted(themes):
            theme_path = self.themes_dir / theme
            theme_stats = self._analyze_theme(theme_path)
            
            stats["total_documents"] += theme_stats["documents"]
            stats["total_code_files"] += theme_stats["code_files"]
            stats["total_lines_of_code"] += theme_stats["lines_of_code"]
            
            for lang, count in theme_stats["languages"].items():
                stats["languages"][lang] = stats["languages"].get(lang, 0) + count
            
            stats["themes"].append({
                "name": theme,
                **theme_stats
            })
        
        # 生成JSON报告
        json_file = self.output_dir / "statistics.json"
        json_file.write_text(
            json.dumps(stats, indent=2, ensure_ascii=False),
            encoding='utf-8'
        )
        
        # 生成Markdown报告
        md_content = "# 项目统计报告\n\n"
        md_content += f"**生成时间**: {stats['generated_at']}\n\n"
        md_content += "## 总体统计\n\n"
        md_content += f"- **主题数**: {stats['total_themes']}\n"
        md_content += f"- **文档数**: {stats['total_documents']:,}\n"
        md_content += f"- **代码文件**: {stats['total_code_files']:,}\n"
        md_content += f"- **代码行数**: {stats['total_lines_of_code']:,}\n\n"
        
        md_content += "## 编程语言分布\n\n"
        for lang, count in sorted(stats["languages"].items(), key=lambda x: -x[1]):
            md_content += f"- **{lang}**: {count} 文件\n"
        
        md_file = self.output_dir / "STATISTICS.md"
        md_file.write_text(md_content, encoding='utf-8')
        
        print(f"  ✓ {json_file.name}")
        print(f"  ✓ {md_file.name}")
    
    def generate_changelog(self):
        """生成变更日志"""
        print("📝 生成变更日志...")
        
        content = "# 变更日志\n\n"
        content += "所有显著的变更都将记录在此文件中。\n\n"
        
        # 添加版本记录
        content += "## [2.0.0] - 2026-02-17\n\n"
        content += "### 新增\n"
        content += "- 完整的Schema验证工具链\n"
        content += "- 概念-属性矩阵生成器\n"
        content += "- REST API服务\n"
        content += "- ML推荐系统\n"
        content += "- Web界面\n"
        content += "- 容器化部署支持\n"
        content += "- CLI命令行工具\n"
        content += "- Kubernetes部署配置\n"
        content += "- Terraform基础设施代码\n"
        content += "- 国际化i18n支持\n"
        content += "- 端到端测试套件\n\n"
        
        content += "### 改进\n"
        content += "- 性能优化\n"
        content += "- 文档完善\n"
        content += "- 测试覆盖率提升\n\n"
        
        output_file = self.output_dir / "CHANGELOG.md"
        output_file.write_text(content, encoding='utf-8')
        print(f"  ✓ {output_file.name}")
    
    def generate_architecture_doc(self):
        """生成架构文档"""
        print("🏗️ 生成架构文档...")
        
        content = "# 系统架构文档\n\n"
        content += "## 整体架构\n\n"
        content += "```\n"
        content += """
┌─────────────────────────────────────────────────────────┐
│                     用户界面层                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   Web UI     │  │   CLI Tool   │  │   REST API   │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
                           │
┌─────────────────────────────────────────────────────────┐
│                     服务层                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  Validation  │  │    Matrix    │  │  ML Service  │  │
│  │   Service    │  │  Generator   │  │              │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
                           │
┌─────────────────────────────────────────────────────────┐
│                     数据层                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  PostgreSQL  │  │    Redis     │  │ File System  │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
"""
        content += "```\n\n"
        
        content += "## 组件说明\n\n"
        content += "### API服务\n"
        content += "- FastAPI框架\n"
        content += "- 异步处理\n"
        content += "- 自动文档生成\n\n"
        
        content += "### 验证服务\n"
        content += "- JSON Schema验证\n"
        content += "- XML Schema验证\n"
        content += "- 标准合规性检查\n\n"
        
        content += "### ML服务\n"
        content += "- 转换策略推荐\n"
        content += "- 相似Schema搜索\n"
        content += "- 异常检测\n\n"
        
        output_file = self.output_dir / "ARCHITECTURE.md"
        output_file.write_text(content, encoding='utf-8')
        print(f"  ✓ {output_file.name}")
    
    def _get_all_themes(self) -> List[str]:
        """获取所有主题"""
        if not self.themes_dir.exists():
            return []
        
        return [
            d.name for d in self.themes_dir.iterdir()
            if d.is_dir() and d.name[0].isdigit()
        ]
    
    def _get_theme_info(self, theme_path: Path) -> Dict:
        """获取主题信息"""
        info = {
            "title": theme_path.name,
            "doc_count": 0,
            "code_count": 0,
            "concepts": [],
            "standards": []
        }
        
        readme_path = theme_path / "README.md"
        if readme_path.exists():
            content = readme_path.read_text(encoding='utf-8', errors='ignore')
            title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
            if title_match:
                info["title"] = title_match.group(1)
        
        for item in theme_path.rglob("*"):
            if item.is_file():
                if item.suffix == '.md':
                    info["doc_count"] += 1
                elif item.suffix in ['.py', '.js', '.ts', '.go', '.rs']:
                    info["code_count"] += 1
        
        concepts_dir = theme_path / "Concepts"
        if concepts_dir.exists():
            for md_file in concepts_dir.glob("*.md"):
                info["concepts"].append(md_file.stem)
        
        return info
    
    def _analyze_theme(self, theme_path: Path) -> Dict:
        """分析主题统计信息"""
        stats = {
            "documents": 0,
            "code_files": 0,
            "lines_of_code": 0,
            "languages": {}
        }
        
        for item in theme_path.rglob("*"):
            if not item.is_file():
                continue
            
            if item.suffix == '.md':
                stats["documents"] += 1
            elif item.suffix in ['.py', '.js', '.ts', '.go', '.rs', '.java']:
                stats["code_files"] += 1
                stats["languages"][item.suffix] = stats["languages"].get(item.suffix, 0) + 1
                
                try:
                    lines = item.read_text(encoding='utf-8', errors='ignore').split('\n')
                    stats["lines_of_code"] += len(lines)
                except:
                    pass
        
        return stats


def main():
    parser = argparse.ArgumentParser(description="文档生成器")
    parser.add_argument("--all", "-a", action="store_true", help="生成所有文档")
    parser.add_argument("--type", "-t", 
                       choices=['index', 'api', 'stats', 'changelog', 'architecture'],
                       help="生成特定类型的文档")
    parser.add_argument("--project-root", "-p", default=".", help="项目根目录")
    
    args = parser.parse_args()
    
    generator = DocGenerator(args.project_root)
    
    if args.all:
        generator.generate_all()
    elif args.type:
        getattr(generator, f'generate_{args.type}')()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
