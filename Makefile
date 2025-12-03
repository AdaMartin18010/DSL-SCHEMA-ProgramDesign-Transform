# DSL Schema项目Makefile

.PHONY: help install test lint format check health validate links stats clean

# 默认目标
help:
	@echo "DSL Schema项目 - 可用命令:"
	@echo ""
	@echo "  安装和设置:"
	@echo "    make install          - 安装Python依赖"
	@echo "    make install-ts       - 安装TypeScript依赖"
	@echo ""
	@echo "  开发:"
	@echo "    make test             - 运行测试"
	@echo "    make lint             - 代码检查"
	@echo "    make format           - 代码格式化"
	@echo ""
	@echo "  检查:"
	@echo "    make check            - 运行所有检查"
	@echo "    make health           - 项目健康检查"
	@echo "    make validate         - 文档验证"
	@echo "    make links            - 链接检查"
	@echo "    make stats            - 项目统计"
	@echo ""
	@echo "  数据库:"
	@echo "    make init-db          - 初始化数据库"
	@echo ""
	@echo "  服务:"
	@echo "    make start            - 启动所有API服务"
	@echo ""
	@echo "  清理:"
	@echo "    make clean            - 清理临时文件"

# 安装Python依赖
install:
	pip install -r code/requirements.txt

# 安装TypeScript依赖
install-ts:
	cd code && npm install

# 运行测试
test:
	pytest code/tests/ -v

# 代码检查
lint:
	flake8 code/ --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 code/ --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
	mypy code/ --ignore-missing-imports

# 代码格式化
format:
	black code/
	isort code/

# 运行所有检查
check:
	python scripts/run_all_checks.py

# 项目健康检查
health:
	python scripts/project_health_check.py

# 文档验证
validate:
	python scripts/validate_docs.py

# 链接检查
links:
	python scripts/check_links.py

# 项目统计
stats:
	python scripts/project_stats.py

# View目录检查
check-view:
	python scripts/check_view_directory.py

# 初始化数据库
init-db:
	python code/scripts/init_databases.py

# 启动所有API服务
start:
	python code/scripts/run_all_apis.py

# 清理临时文件
clean:
	find . -type d -name "__pycache__" -exec rm -r {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -r {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name "htmlcov" -exec rm -r {} + 2>/dev/null || true
	find . -type f -name "*.log" -delete
