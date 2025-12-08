# API文档

## 📋 文档信息

**创建时间**：2025-01-21
**最后更新**：2025-01-21
**文档版本**：v1.0
**维护者**：DSL Schema研究团队

---

## 🎯 API总览

项目提供**9个REST API服务**，通过统一API网关访问。

### 统一API网关

**地址**：`http://localhost:8080`

**功能**：

- 统一路由管理
- 请求转发
- 健康检查聚合
- 服务列表查询

---

## 📚 核心服务API

### 1. 多模态知识图谱API

**服务地址**：`http://localhost:8000`
**网关路径**：`/api/v1/multimodal_kg/`

#### 主要接口

- `POST /api/v1/multimodal_kg/entity/add` - 添加实体
- `POST /api/v1/multimodal_kg/search/similar` - 相似实体搜索
- `GET /api/v1/multimodal_kg/health` - 健康检查

### 2. 时序知识图谱API

**服务地址**：`http://localhost:8001`
**网关路径**：`/api/v1/temporal_kg/`

#### 主要接口

- `POST /api/v1/temporal_kg/entity/add` - 添加实体
- `GET /api/v1/temporal_kg/evolution/{entity_id}` - 查询演化历史
- `GET /api/v1/temporal_kg/health` - 健康检查

### 3. LLM推理引擎API

**服务地址**：`http://localhost:8002`
**网关路径**：`/api/v1/llm_reasoning/`

#### 主要接口

- `POST /api/v1/llm_reasoning/reason` - 执行推理
- `POST /api/v1/llm_reasoning/embed` - 文本嵌入
- `GET /api/v1/llm_reasoning/health` - 健康检查

### 4. 统一Schema语言API

**服务地址**：`http://localhost:8003`
**网关路径**：`/api/v1/usl/`

#### 主要接口

- `POST /api/v1/usl/parse` - 解析USL
- `POST /api/v1/usl/validate` - 验证USL
- `POST /api/v1/usl/convert` - 转换USL
- `GET /api/v1/usl/health` - 健康检查

### 5. 层次化知识表示API

**服务地址**：`http://localhost:8004`
**网关路径**：`/api/v1/hierarchical_kg/`

#### 主要接口

- `POST /api/v1/hierarchical_kg/entity/add` - 添加实体
- `POST /api/v1/hierarchical_kg/reasoning` - 层次化推理
- `GET /api/v1/hierarchical_kg/query/level/{level}` - 按层次查询
- `GET /api/v1/hierarchical_kg/health` - 健康检查

### 6. 知识链方法API

**服务地址**：`http://localhost:8005`
**网关路径**：`/api/v1/knowledge-chain/`

#### 主要接口

- `POST /api/v1/knowledge-chain/build` - 构建知识链
- `POST /api/v1/knowledge-chain/reasoning` - 知识链推理
- `GET /api/v1/knowledge-chain/{chain_id}` - 获取知识链
- `GET /api/v1/knowledge-chain/health` - 健康检查

### 7. 可解释性推理API

**服务地址**：`http://localhost:8006`
**网关路径**：`/api/v1/explainable-reasoning/`

#### 主要接口

- `POST /api/v1/explainable-reasoning/reason` - 可解释性推理
- `GET /api/v1/explainable-reasoning/path/{path_id}` - 获取推理路径
- `GET /api/v1/explainable-reasoning/rules` - 获取所有规则
- `GET /api/v1/explainable-reasoning/health` - 健康检查

### 8. Schema版本管理API

**服务地址**：`http://localhost:8007`
**网关路径**：`/api/v1/schema-versioning/`

#### 主要接口

- `POST /api/v1/schema-versioning/version/create` - 创建版本
- `GET /api/v1/schema-versioning/version/{schema_id}` - 获取当前版本
- `POST /api/v1/schema-versioning/compatibility/check` - 检查兼容性
- `POST /api/v1/schema-versioning/migration/migrate` - 执行迁移
- `GET /api/v1/schema-versioning/health` - 健康检查

---

## 🔗 统一API网关

**地址**：`http://localhost:8080`

### 网关接口

- `GET /` - 根路径（服务列表）
- `GET /api/v1/health` - 健康检查（所有服务）
- `GET /api/v1/services` - 列出所有服务
- `GET/POST/PUT/DELETE /api/v1/{service_name}/{path}` - 代理请求到指定服务

### 使用示例

```bash
# 通过网关访问多模态KG API
curl http://localhost:8080/api/v1/multimodal_kg/entity/add

# 检查所有服务健康状态
curl http://localhost:8080/api/v1/health
```

---

## 📝 API使用示例

详细的使用示例请查看：

- [快速开始指南](guides/QUICK_START_GUIDE.md)
- [示例代码](../../examples/quick_start.py)

---

**创建时间**：2025-01-21
**最后更新**：2025-01-21
**维护者**：DSL Schema研究团队
