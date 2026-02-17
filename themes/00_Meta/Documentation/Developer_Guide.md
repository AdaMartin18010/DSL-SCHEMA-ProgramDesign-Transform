# DSL Schema 开发者指南
## Developer Guide

**版本**: 2.1.0  
**日期**: 2026-02-17

---

## 目录

1. [环境设置](#环境设置)
2. [项目结构](#项目结构)
3. [开发工作流](#开发工作流)
4. [API开发](#api开发)
5. [测试指南](#测试指南)
6. [性能优化](#性能优化)
7. [贡献指南](#贡献指南)

---

## 环境设置

### 系统要求

- Python 3.9+
- Docker 24+ (可选)
- PostgreSQL 14+ (可选)
- Redis 7+ (可选)

### 本地开发环境

```bash
# 克隆仓库
git clone https://github.com/dsl-schema/themes.git
cd themes

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 验证安装
python -m pytest themes/00_Meta/tests/ -v
```

---

## 项目结构

```
themes/
├── 00_Meta/
│   ├── API/                    # API服务
│   ├── Tools/                  # 工具集合
│   ├── Tests/                  # 测试套件
│   ├── Deployment/             # 部署配置
│   └── Documentation/          # 技术文档
├── 01_Industrial_Automation/   # 主题目录
├── 04_Financial_Services/
└── ...
```

---

## 开发工作流

### 分支策略

```
main → develop → feature/xxx
```

### 提交规范

```
<type>(<scope>): <subject>

feat(validator): 添加JSON Schema 2025-01支持
```

**类型**: feat, fix, docs, refactor, test, chore

---

## API开发

### 添加新端点

```python
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

@router.post("/endpoint")
async def endpoint(request: Request):
    return {"result": "success"}
```

---

## 测试指南

### 运行测试

```bash
pytest                          # 所有测试
pytest tests/unit/ -v          # 单元测试
pytest --cov=. --cov-report=html  # 覆盖率
```

---

## 性能优化

```python
from performance_monitor import track_performance

@track_performance("validate")
def validate(schema):
    pass
```

---

**维护者**: DSL Schema团队
