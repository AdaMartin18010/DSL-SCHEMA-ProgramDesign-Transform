# 部署指南

## 📋 文档信息

**创建时间**：2025-01-21
**最后更新**：2025-01-21
**文档版本**：v1.0
**维护者**：DSL Schema研究团队

---

## 🚀 快速开始

### 1. 环境要求

- Python 3.10+
- PostgreSQL 16+（带pgvector扩展）
- Docker和Docker Compose（可选）

### 2. 安装依赖

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# 安装依赖
pip install -r code/requirements.txt
```

### 3. 配置环境变量

```bash
# 复制示例配置文件
cp .env.example .env

# 编辑配置文件
# 设置数据库连接、API密钥等
```

### 4. 初始化数据库

```bash
# 安装PostgreSQL和pgvector扩展
# 创建数据库
createdb multimodal_kg
createdb temporal_kg

# 运行初始化脚本
python code/scripts/init_databases.py
```

### 5. 启动服务

#### 方式1：单独启动

```bash
# 注意：需要将code目录添加到Python路径
export PYTHONPATH="${PYTHONPATH}:$(pwd)/code"

# 多模态知识图谱API
cd code && uvicorn multimodal_kg.api:app --host 0.0.0.0 --port 8000

# 时序知识图谱API
cd code && uvicorn temporal_kg.api:app --host 0.0.0.0 --port 8001

# LLM推理引擎API
cd code && uvicorn llm_reasoning.api:app --host 0.0.0.0 --port 8002

# USL API
cd code && uvicorn usl.api:app --host 0.0.0.0 --port 8003
```

#### 方式2：使用脚本启动所有服务

```bash
python code/scripts/run_all_apis.py
```

#### 方式3：使用Docker Compose

```bash
# 进入docker目录
cd docker

# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

---

## 🐳 Docker部署

### 构建镜像

```bash
# 构建多模态KG镜像
docker build -f docker/Dockerfile.multimodal -t multimodal-kg:latest .

# 构建时序KG镜像
docker build -f Dockerfile.temporal -t temporal-kg:latest .

# 构建LLM推理镜像
docker build -f Dockerfile.llm -t llm-reasoning:latest .

# 构建USL镜像
docker build -f Dockerfile.usl -t usl:latest .
```

### 使用Docker Compose

```bash
# 进入docker目录
cd docker

# 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f [service_name]

# 停止服务
docker-compose down

# 停止并删除数据卷
docker-compose down -v
```

---

## 📊 服务端口

| 服务 | 端口 | 说明 |
|------|------|------|
| **统一API网关** | **8080** | **统一访问入口（推荐）** |
| 多模态知识图谱API | 8000 | REST API |
| 时序知识图谱API | 8001 | REST API |
| LLM推理引擎API | 8002 | REST API |
| USL API | 8003 | REST API |
| 层次化知识表示API | 8004 | REST API |
| 知识链方法API | 8005 | REST API |
| 可解释性推理API | 8006 | REST API |
| Schema版本管理API | 8007 | REST API |
| 多模态数据库 | 5432 | PostgreSQL |
| 时序数据库 | 5433 | PostgreSQL |
| 层次化数据库 | 5434 | PostgreSQL |
| 知识链数据库 | 5435 | PostgreSQL |
| 可解释性推理数据库 | 5436 | PostgreSQL |
| Schema版本管理数据库 | 5437 | PostgreSQL |

---

## 🔧 配置说明

### 数据库配置

```env
MULTIMODAL_DB_URL=postgresql://user:password@localhost:5432/multimodal_kg
TEMPORAL_DB_URL=postgresql://user:password@localhost:5432/temporal_kg
```

### LLM配置

```env
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
LLM_PROVIDER=openai  # 或 anthropic
```

### API配置

```env
MULTIMODAL_API_PORT=8000
TEMPORAL_API_PORT=8001
LLM_API_PORT=8002
USL_API_PORT=8003
DEBUG=False
```

---

## 🧪 测试

### 运行单元测试

```bash
# 运行所有测试
pytest code/tests/

# 运行特定测试
pytest code/tests/test_multimodal_kg.py

# 运行集成测试
pytest code/tests/test_integration.py

# 生成覆盖率报告
pytest --cov=code --cov-report=html
```

### 健康检查

```bash
# 检查统一API网关（推荐）
curl http://localhost:8080/api/v1/health

# 或检查各个服务
curl http://localhost:8000/api/v1/health  # 多模态KG
curl http://localhost:8001/api/v1/health  # 时序KG
curl http://localhost:8002/api/v1/health  # LLM推理
curl http://localhost:8003/api/v1/health  # USL
curl http://localhost:8004/api/v1/health  # 层次化KG
curl http://localhost:8005/api/v1/health  # 知识链
curl http://localhost:8006/api/v1/health  # 可解释性推理
curl http://localhost:8007/api/v1/health  # Schema版本管理
```

---

## 📝 使用示例

### 多模态知识图谱

```python
# 注意：需要将code目录添加到Python路径
import sys
sys.path.insert(0, 'code')

from multimodal_kg import TextModalityProcessor

processor = TextModalityProcessor()
processor.process_text(
    entity_id="schema_001",
    content="This is a test schema",
    content_type="schema_doc"
)

results = processor.search_similar("schema", top_k=10)
```

### 时序知识图谱

```python
# 注意：需要将code目录添加到Python路径
import sys
sys.path.insert(0, 'code')

from temporal_kg import TemporalKGStorage
from datetime import datetime

storage = TemporalKGStorage()
storage.add_entity(
    entity_id="schema_001",
    entity_type="schema",
    valid_from=datetime.now(),
    properties={"version": "1.0"}
)
```

### LLM推理

```python
# 注意：需要将code目录添加到Python路径
import sys
sys.path.insert(0, 'code')

from llm_reasoning import OpenAILLM

llm = OpenAILLM(api_key="your_key")
result = llm.reason(
    query="What is a schema?",
    context={"entities": [], "relations": []}
)
```

### USL

```python
# 注意：需要将code目录添加到Python路径
import sys
sys.path.insert(0, 'code')

from usl import USLParser, USLValidator

parser = USLParser()
ast = parser.parse(usl_code)

validator = USLValidator(ast)
result = validator.validate()
```

---

## 🔍 故障排查

### 数据库连接问题

1. 检查PostgreSQL是否运行
2. 检查数据库URL配置
3. 检查pgvector扩展是否安装

### API启动失败

1. 检查端口是否被占用
2. 检查依赖是否安装完整
3. 查看日志文件

### LLM API调用失败

1. 检查API密钥是否正确
2. 检查网络连接
3. 检查API配额

---

**创建时间**：2025-01-21
**最后更新**：2025-01-21
**维护者**：DSL Schema研究团队
