# 开发指南

## 📋 文档信息

**创建时间**：2025-01-21
**最后更新**：2025-01-21
**文档版本**：v1.0
**维护者**：DSL Schema研究团队

---

## 🚀 开发环境设置

### 1. 环境要求

- Python 3.10+
- Node.js 18+（TypeScript代码）
- PostgreSQL 16+（带pgvector扩展）
- Docker和Docker Compose（可选）

### 2. 克隆项目

```bash
git clone <repository-url>
cd DSL-SCHEMA-ProgramDesign-Transform
```

### 3. 安装Python依赖

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

### 4. 安装TypeScript依赖

```bash
cd code
npm install
```

### 5. 配置环境变量

```bash
# 复制示例配置文件
cp .env.example .env

# 编辑配置文件
# 设置数据库连接、API密钥等
```

### 6. 初始化数据库

```bash
# 使用Makefile（推荐）
make init-db

# 或直接运行脚本
python code/scripts/init_databases.py
```

### 7. 使用Makefile（可选但推荐）

项目提供了Makefile，可以简化常用操作：

```bash
# 查看所有可用命令
make help

# 安装依赖
make install
make install-ts

# 运行测试
make test

# 代码检查
make lint

# 代码格式化
make format

# 运行所有检查
make check

# 项目统计
make stats
```

---

## 📝 代码结构

### Python代码

```
code/
├── api_gateway/          # API网关
├── multimodal_kg/       # 多模态知识图谱
├── temporal_kg/          # 时序知识图谱
├── llm_reasoning/        # LLM推理引擎
├── usl/                  # 统一Schema语言
├── hierarchical_kg/      # 层次化知识表示
├── knowledge_chain/      # 知识链方法
├── explainable_reasoning/ # 可解释性推理
├── schema_versioning/    # Schema版本管理
├── tests/                # 测试代码
└── scripts/              # 脚本
```

### TypeScript代码

```
code/
├── server/               # MCP服务器
├── transformers/         # Schema转换器
└── utils/                # 工具函数
```

---

## 🧪 测试

### 运行测试

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

### 测试覆盖率目标

- 单元测试覆盖率：80%+
- 集成测试覆盖率：60%+

---

## 🔧 开发工作流

### 1. 创建新功能

1. 在相应的模块目录下创建新文件
2. 编写代码和文档字符串
3. 编写单元测试
4. 运行测试确保通过
5. 提交代码

### 2. 代码规范

- 使用Python类型提示
- 遵循PEP 8代码风格
- 编写详细的文档字符串
- 添加适当的注释

### 3. 提交规范

- 使用清晰的提交信息
- 一个提交只做一件事
- 提交前运行测试

---

## 📚 相关文档

- [代码目录说明](../code/README.md)
- [部署指南](DEPLOYMENT_GUIDE.md)
- [API参考](API_REFERENCE.md)

---

**创建时间**：2025-01-21
**最后更新**：2025-01-21
**维护者**：DSL Schema研究团队
