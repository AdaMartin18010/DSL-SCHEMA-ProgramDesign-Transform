#!/usr/bin/env python3
"""
环境配置脚本

自动化开发环境配置，包括：
- 依赖安装
- 数据库初始化
- 环境变量检查
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from typing import List, Dict, Tuple, Optional


class EnvironmentSetup:
    """环境配置类"""
    
    def __init__(self, project_root: str = None):
        """
        初始化环境配置
        
        Args:
            project_root: 项目根目录，默认为当前脚本所在目录的父目录
        """
        if project_root is None:
            self.project_root = Path(__file__).parent.parent
        else:
            self.project_root = Path(project_root)
        
        self.check_results: Dict[str, bool] = {}
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def check_python_version(self) -> bool:
        """检查Python版本"""
        print("🔍 检查Python版本...")
        
        version = sys.version_info
        required = (3, 9)
        
        if version >= required:
            print(f"  ✅ Python {version.major}.{version.minor}.{version.micro}")
            self.check_results['python_version'] = True
            return True
        else:
            print(f"  ❌ Python版本过低: {version.major}.{version.minor}")
            print(f"     需要: {required[0]}.{required[1]}+")
            self.check_results['python_version'] = False
            self.errors.append(f"Python版本过低: {version.major}.{version.minor}")
            return False
    
    def check_dependencies(self) -> bool:
        """检查Python依赖"""
        print("🔍 检查Python依赖...")
        
        required_packages = [
            'fastapi',
            'pydantic',
            'numpy',
            'pytest',
            'lark',
        ]
        
        missing = []
        
        for package in required_packages:
            try:
                __import__(package)
                print(f"  ✅ {package}")
            except ImportError:
                print(f"  ❌ {package} (未安装)")
                missing.append(package)
        
        if missing:
            self.check_results['dependencies'] = False
            self.errors.append(f"缺少依赖: {', '.join(missing)}")
            print(f"\n  💡 运行: pip install {' '.join(missing)}")
            return False
        else:
            self.check_results['dependencies'] = True
            print(f"  ✅ 所有依赖已安装")
            return True
    
    def check_environment_variables(self) -> bool:
        """检查环境变量"""
        print("🔍 检查环境变量...")
        
        optional_vars = [
            'OPENAI_API_KEY',
            'ANTHROPIC_API_KEY',
            'DATABASE_URL',
        ]
        
        missing = []
        for var in optional_vars:
            value = os.getenv(var)
            if value:
                # 隐藏API密钥的大部分内容
                if 'KEY' in var:
                    display = value[:10] + "..." if len(value) > 10 else "***"
                else:
                    display = value
                print(f"  ✅ {var}={display}")
            else:
                print(f"  ⚠️  {var} (未设置)")
                missing.append(var)
        
        if missing:
            self.warnings.append(f"可选环境变量未设置: {', '.join(missing)}")
            print(f"\n  💡 提示: 设置这些环境变量可以启用更多功能")
        
        self.check_results['env_vars'] = True
        return True
    
    def check_project_structure(self) -> bool:
        """检查项目结构"""
        print("🔍 检查项目结构...")
        
        required_dirs = [
            'code',
            'themes',
            'docs',
            'examples',
        ]
        
        all_exist = True
        for dir_name in required_dirs:
            dir_path = self.project_root / dir_name
            if dir_path.exists():
                print(f"  ✅ {dir_name}/")
            else:
                print(f"  ❌ {dir_name}/ (不存在)")
                all_exist = False
        
        self.check_results['project_structure'] = all_exist
        return all_exist
    
    def install_dependencies(self) -> bool:
        """安装依赖"""
        print("📦 安装依赖...")
        
        requirements_file = self.project_root / "requirements.txt"
        
        if not requirements_file.exists():
            print("  ⚠️ requirements.txt 不存在，创建默认依赖文件")
            self._create_requirements_file()
        
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "-r", str(requirements_file)],
                check=True,
                capture_output=True
            )
            print("  ✅ 依赖安装完成")
            return True
        except subprocess.CalledProcessError as e:
            print(f"  ❌ 依赖安装失败: {e}")
            self.errors.append("依赖安装失败")
            return False
    
    def _create_requirements_file(self):
        """创建requirements.txt文件"""
        requirements = """# 核心依赖
fastapi>=0.100.0
pydantic>=2.0.0
uvicorn>=0.23.0

# 数据处理
numpy>=1.24.0

# 数据库
psycopg2-binary>=2.9.0

# USL解析
lark>=1.1.0

# 测试
pytest>=7.4.0
pytest-asyncio>=0.21.0

# 可选: LLM API
openai>=1.0.0
anthropic>=0.8.0

# 工具
python-dotenv>=1.0.0
pyyaml>=6.0
"""
        
        requirements_file = self.project_root / "requirements.txt"
        requirements_file.write_text(requirements, encoding='utf-8')
        print(f"  ✅ 创建 {requirements_file}")
    
    def setup_database(self) -> bool:
        """设置数据库"""
        print("🗄️  设置数据库...")
        
        # 检查PostgreSQL是否可用
        try:
            import psycopg2
            print("  ✅ psycopg2 已安装")
        except ImportError:
            print("  ⚠️  psycopg2 未安装，跳过数据库设置")
            self.warnings.append("PostgreSQL支持未安装")
            return True
        
        # 检查数据库连接
        database_url = os.getenv('DATABASE_URL', 'postgresql://localhost:5432/schema_db')
        
        try:
            conn = psycopg2.connect(database_url)
            conn.close()
            print(f"  ✅ 数据库连接成功: {database_url}")
            self.check_results['database'] = True
            return True
        except Exception as e:
            print(f"  ⚠️  数据库连接失败: {e}")
            print(f"     数据库URL: {database_url}")
            self.warnings.append(f"数据库连接失败: {e}")
            return True  # 数据库是可选的
    
    def run_tests(self) -> bool:
        """运行测试验证环境"""
        print("🧪 运行测试...")
        
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pytest", "code/tests/", "-v", "--tb=short"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                print("  ✅ 所有测试通过")
                self.check_results['tests'] = True
                return True
            else:
                print(f"  ⚠️  部分测试失败")
                print(f"     运行 'pytest code/tests/' 查看详情")
                self.warnings.append("部分测试失败")
                self.check_results['tests'] = False
                return False
        except Exception as e:
            print(f"  ⚠️  测试运行失败: {e}")
            self.warnings.append(f"测试运行失败: {e}")
            return True
    
    def generate_report(self) -> Dict:
        """生成配置报告"""
        return {
            'status': 'success' if not self.errors else 'failed',
            'checks': self.check_results,
            'errors': self.errors,
            'warnings': self.warnings,
            'summary': {
                'total_checks': len(self.check_results),
                'passed': sum(1 for v in self.check_results.values() if v),
                'failed': sum(1 for v in self.check_results.values() if not v),
            }
        }
    
    def setup(self, auto_install: bool = False) -> bool:
        """
        运行完整的环境配置
        
        Args:
            auto_install: 是否自动安装缺失的依赖
            
        Returns:
            配置是否成功
        """
        print("=" * 60)
        print("🚀 DSL Schema 项目环境配置")
        print("=" * 60)
        print()
        
        # 1. 检查Python版本
        self.check_python_version()
        print()
        
        # 2. 检查项目结构
        self.check_project_structure()
        print()
        
        # 3. 检查环境变量
        self.check_environment_variables()
        print()
        
        # 4. 检查依赖
        deps_ok = self.check_dependencies()
        if not deps_ok and auto_install:
            self.install_dependencies()
            # 重新检查
            deps_ok = self.check_dependencies()
        print()
        
        # 5. 设置数据库
        self.setup_database()
        print()
        
        # 6. 运行测试
        self.run_tests()
        print()
        
        # 生成报告
        report = self.generate_report()
        
        print("=" * 60)
        print("📊 配置报告")
        print("=" * 60)
        print(f"总检查项: {report['summary']['total_checks']}")
        print(f"通过: {report['summary']['passed']}")
        print(f"失败: {report['summary']['failed']}")
        
        if self.errors:
            print("\n❌ 错误:")
            for error in self.errors:
                print(f"  - {error}")
        
        if self.warnings:
            print("\n⚠️  警告:")
            for warning in self.warnings:
                print(f"  - {warning}")
        
        print()
        if report['status'] == 'success':
            print("✅ 环境配置完成！")
        else:
            print("❌ 环境配置失败，请修复上述错误")
        
        return report['status'] == 'success'


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='DSL Schema 项目环境配置')
    parser.add_argument('--install', action='store_true', help='自动安装缺失的依赖')
    parser.add_argument('--check-only', action='store_true', help='仅检查，不安装')
    
    args = parser.parse_args()
    
    setup = EnvironmentSetup()
    
    if args.check_only:
        # 仅检查
        setup.check_python_version()
        setup.check_project_structure()
        setup.check_environment_variables()
        setup.check_dependencies()
        setup.setup_database()
    else:
        # 完整配置
        success = setup.setup(auto_install=args.install)
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
