# 脚本工具目录

## 📋 脚本列表

本目录包含用于项目维护和验证的实用脚本工具。

### 1. 链接检查工具

**文件**: `check_links.py`

**功能**: 检查Markdown文档中的链接有效性

**使用方法**:
```bash
python scripts/check_links.py [项目根目录]
```

**输出**: 生成 `link_check_report.md` 报告文件

### 2. 文档验证工具

**文件**: `validate_docs.py`

**功能**: 验证所有Schema文档是否符合标准结构（01-05文档）

**使用方法**:
```bash
python scripts/validate_docs.py [themes目录路径]
```

**输出**: 生成 `doc_validation_report.md` 报告文件

### 3. 项目健康检查工具

**文件**: `project_health_check.py`

**功能**: 检查项目的整体健康状况

**检查项**:
- 目录结构
- 代码模块
- 文档完整性
- 配置文件
- 测试覆盖

**使用方法**:
```bash
python scripts/project_health_check.py [项目根目录]
```

**输出**: 生成 `health_check_report.md` 报告文件

### 4. 运行所有检查工具

**文件**: `run_all_checks.py`

**功能**: 一键运行所有检查工具

**使用方法**:
```bash
python scripts/run_all_checks.py
```

**输出**: 运行所有检查并生成汇总报告

### 5. 项目统计工具

**文件**: `project_stats.py`

**功能**: 生成项目的详细统计信息

**统计项**:
- 代码统计（文件数、行数）
- 文档统计（各类文档数量）
- Schema统计（Schema数量、文档数量）
- 服务统计（Dockerfile、API服务）
- 工具统计（脚本数量）

**使用方法**:
```bash
python scripts/project_stats.py [项目根目录]
```

**输出**: 生成 `project_stats_report.md` 报告文件

### 6. 开发环境设置脚本

**文件**:
- `setup_dev_env.sh` (Linux/Mac)
- `setup_dev_env.bat` (Windows)

**功能**: 自动设置开发环境

**功能**:
- 创建虚拟环境
- 安装Python依赖
- 安装TypeScript依赖
- 检查PostgreSQL和pgvector

**使用方法**:
```bash
# Linux/Mac
bash scripts/setup_dev_env.sh

# Windows
scripts\setup_dev_env.bat
```

### 7. View目录检查工具

**文件**: `check_view_directory.py`

**功能**: 检查view目录的完整性

**检查项**:
- 核心Schema文档完整性
- 主题分析文档完整性
- 理论分析文档完整性
- 导航文档完整性
- 内部链接有效性
- 文档统计

**使用方法**:
```bash
python scripts/check_view_directory.py [view目录路径]
```

**输出**: 生成 `view_directory_check_report.md` 报告文件

---

## 🚀 快速使用

### 使用Makefile（推荐）

```bash
# 运行所有检查
make check

# 项目健康检查
make health

# 文档验证
make validate

# 链接检查
make links

# 项目统计
make stats
```

### 直接运行脚本

```bash
# 运行所有检查
python scripts/run_all_checks.py

# 单独运行
python scripts/project_health_check.py
python scripts/validate_docs.py
python scripts/check_links.py
python scripts/project_stats.py
```

### 设置开发环境

```bash
# Linux/Mac
bash scripts/setup_dev_env.sh

# Windows
scripts\setup_dev_env.bat
```

### 集成到CI/CD

这些脚本可以集成到CI/CD流程中，在每次提交时自动检查项目健康状况。

---

**创建时间**：2025-01-21
**维护者**：DSL Schema研究团队
