# DSL Schema API 文档索引

**版本**: v1.0  
**最后更新**: 2026-02-16  
**维护者**: DSL Schema研究团队

---

## 📚 API 文档导航

欢迎使用 DSL Schema API 文档索引！本文档提供所有 API 接口的快速导航和参考。

---

## 🚀 快速开始

| 文档 | 描述 | 链接 |
|------|------|------|
| 快速入门 | 5分钟快速上手 | [QUICK_START.md](../guides/QUICK_START.md) |
| API 参考 | 完整API接口文档 | [API_REFERENCE.md](../guides/API_REFERENCE.md) |
| 项目架构 | 系统架构图 | [PROJECT_ARCHITECTURE.md](../guides/PROJECT_ARCHITECTURE.md) |

---

## 📖 核心 API 模块

### 1. 统一API网关

| 端点 | 方法 | 描述 |
|------|------|------|
| `/` | GET | 服务列表首页 |
| `/api/v1/health` | GET | 健康检查（所有服务） |
| `/api/v1/services` | GET | 列出所有可用服务 |
| `/api/v1/{service}/{path}` | * | 代理请求到指定服务 |

**详细文档**: [API_REFERENCE.md](../guides/API_REFERENCE.md#-统一api网关)

---

### 2. 多模态知识图谱 API

**服务地址**: `http://localhost:8000`  
**网关路径**: `/api/v1/multimodal_kg/`

| 端点 | 方法 | 描述 |
|------|------|------|
| `/entity/add` | POST | 添加实体（文本/图像） |
| `/search/similar` | POST | 相似实体搜索 |
| `/entity/{id}` | GET | 获取实体详情 |
| `/entity/{id}` | DELETE | 删除实体 |

**详细文档**: [API_REFERENCE.md](../guides/API_REFERENCE.md#1-多模态知识图谱api)

---

### 3. 时序知识图谱 API

**服务地址**: `http://localhost:8001`  
**网关路径**: `/api/v1/temporal_kg/`

| 端点 | 方法 | 描述 |
|------|------|------|
| `/entity/add` | POST | 添加带时间戳的实体 |
| `/evolution/{id}` | GET | 查询实体演化历史 |
| `/snapshot` | GET | 获取时间点快照 |
| `/compare` | POST | 对比两个时间点状态 |

**详细文档**: [API_REFERENCE.md](../guides/API_REFERENCE.md#2-时序知识图谱api)

---

### 4. LLM推理引擎 API

**服务地址**: `http://localhost:8002`  
**网关路径**: `/api/v1/llm_reasoning/`

| 端点 | 方法 | 描述 |
|------|------|------|
| `/reason` | POST | 执行推理任务 |
| `/reasoning_chain` | POST | 执行推理链 |
| `/models` | GET | 列出可用模型 |
| `/health` | GET | 服务健康检查 |

**详细文档**: [API_REFERENCE.md](../guides/API_REFERENCE.md#3-llm推理引擎api)

---

### 5. 统一Schema语言 API

**服务地址**: `http://localhost:8003`  
**网关路径**: `/api/v1/usl/`

| 端点 | 方法 | 描述 |
|------|------|------|
| `/parse` | POST | 解析USL代码 |
| `/validate` | POST | 验证USL语法 |
| `/transform` | POST | 转换为其他格式 |
| `/format` | POST | 格式化USL代码 |

**详细文档**: [API_REFERENCE.md](../guides/API_REFERENCE.md#4-统一schema语言api)

---

### 6. 层次化知识表示 API

**服务地址**: `http://localhost:8005`  
**网关路径**: `/api/v1/hierarchical/`

| 端点 | 方法 | 描述 |
|------|------|------|
| `/entity/add` | POST | 添加层次化实体 |
| `/levels` | GET | 获取层次级别 |
| `/reasoning` | POST | 执行层次化推理 |
| `/abstraction` | POST | 创建知识抽象 |

**详细文档**: [API_REFERENCE.md](../guides/API_REFERENCE.md#5-层次化知识表示api)

---

### 7. 知识链方法 API

**服务地址**: `http://localhost:8006`  
**网关路径**: `/api/v1/knowledge_chain/`

| 端点 | 方法 | 描述 |
|------|------|------|
| `/chain/build` | POST | 构建知识链 |
| `/chain/{id}` | GET | 获取知识链详情 |
| `/chain/{id}/execute` | POST | 执行知识链 |
| `/chains` | GET | 列出所有知识链 |

**详细文档**: [API_REFERENCE.md](../guides/API_REFERENCE.md#6-知识链方法api)

---

### 8. 可解释性推理 API

**服务地址**: `http://localhost:8007`  
**网关路径**: `/api/v1/explainable/`

| 端点 | 方法 | 描述 |
|------|------|------|
| `/reason` | POST | 执行可解释推理 |
| `/explanation/{id}` | GET | 获取推理解释 |
| `/rules` | GET | 列出推理规则 |
| `/rules` | POST | 添加推理规则 |

**详细文档**: [API_REFERENCE.md](../guides/API_REFERENCE.md#7-可解释性推理api)

---

### 9. Schema版本管理 API

**服务地址**: `http://localhost:8004`  
**网关路径**: `/api/v1/schema_version/`

| 端点 | 方法 | 描述 |
|------|------|------|
| `/version` | POST | 创建新版本 |
| `/version/{id}` | GET | 获取版本详情 |
| `/versions` | GET | 列出所有版本 |
| `/compare` | POST | 比较两个版本 |
| `/migrate` | POST | 执行版本迁移 |
| `/compatibility` | POST | 检查兼容性 |

**详细文档**: [API_REFERENCE.md](../guides/API_REFERENCE.md#8-schema版本管理api)

---

## 📦 客户端 SDK

### Python SDK

```python
# 安装
pip install dsl-schema-client

# 使用示例
from dsl_schema import Client

client = Client(base_url="http://localhost:8080")

# 调用多模态知识图谱
result = client.multimodal_kg.search_similar(query="payment", top_k=5)

# 调用LLM推理
response = client.llm_reasoning.reason(prompt="分析Schema转换规则")
```

### JavaScript/TypeScript SDK

```javascript
// 安装
npm install dsl-schema-client

// 使用示例
import { DSLSchemaClient } from 'dsl-schema-client';

const client = new DSLSchemaClient({ baseURL: 'http://localhost:8080' });

// 调用API
const result = await client.usl.parse({ code: uslCode });
```

---

## 🔐 认证

API 支持以下认证方式：

### API Key 认证

```bash
curl -H "X-API-Key: your-api-key" \
     http://localhost:8080/api/v1/services
```

### JWT 认证

```bash
curl -H "Authorization: Bearer your-jwt-token" \
     http://localhost:8080/api/v1/services
```

---

## ⚠️ 错误码

| 状态码 | 描述 | 说明 |
|--------|------|------|
| 200 | OK | 请求成功 |
| 400 | Bad Request | 请求参数错误 |
| 401 | Unauthorized | 未授权访问 |
| 403 | Forbidden | 禁止访问 |
| 404 | Not Found | 资源不存在 |
| 429 | Too Many Requests | 请求频率超限 |
| 500 | Internal Server Error | 服务器内部错误 |
| 503 | Service Unavailable | 服务不可用 |

---

## 📊 限流策略

| 接口类型 | 限流策略 | 说明 |
|----------|----------|------|
| 公共接口 | 100 req/min | 无需认证 |
| 认证接口 | 1000 req/min | 需要API Key |
| LLM推理 | 10 req/min | 资源消耗大 |
| 批量操作 | 50 req/min | 大量数据处理 |

---

## 🧪 测试环境

```bash
# 启动测试环境
docker-compose -f docker/docker-compose.yml up -d

# 运行集成测试
pytest code/tests/integration/ -v

# 运行API测试
pytest code/tests/test_api.py -v
```

---

## 📚 相关文档

| 文档 | 描述 |
|------|------|
| [DEPLOYMENT_GUIDE.md](../guides/DEPLOYMENT_GUIDE.md) | 部署指南 |
| [DEVELOPMENT_GUIDE.md](../guides/DEVELOPMENT_GUIDE.md) | 开发指南 |
| [SECURITY_GUIDE.md](../guides/SECURITY_GUIDE.md) | 安全指南 |
| [TROUBLESHOOTING.md](../guides/TROUBLESHOOTING.md) | 故障排除 |

---

## 🆘 获取帮助

- 📧 邮件: dsl-schema@example.com
- 💬 论坛: [讨论区](../../docs/community/)
- 🐛 Issues: [GitHub Issues](https://github.com/example/dsl-schema/issues)

---

*最后更新: 2026-02-16*
