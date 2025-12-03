# 项目结构说明

## 📋 文档信息

**创建时间**：2025-01-21
**最后更新**：2025-01-21
**文档版本**：v2.0
**维护者**：DSL Schema研究团队

---

## 🎯 项目结构总览

```
DSL-SCHEMA-ProgramDesign-Transform/
├── README.md                    # 项目主文档
├── LICENSE                      # 许可证
├── CONTRIBUTING.md             # 贡献指南
├── QUICK_START_GUIDE.md         # 快速开始指南（链接到docs/guides/）
│
├── code/                       # 📦 代码目录
│   ├── api_gateway/            # API网关
│   ├── multimodal_kg/          # 多模态知识图谱
│   ├── temporal_kg/            # 时序知识图谱
│   ├── llm_reasoning/          # LLM推理引擎
│   ├── usl/                    # 统一Schema语言
│   ├── hierarchical_kg/        # 层次化知识表示
│   ├── knowledge_chain/        # 知识链方法
│   ├── explainable_reasoning/   # 可解释性推理
│   ├── schema_versioning/      # Schema版本管理
│   ├── tests/                  # 测试代码
│   ├── scripts/                # 脚本
│   ├── server/                 # TypeScript服务器
│   ├── transformers/           # TypeScript转换器
│   └── utils/                  # TypeScript工具
│
├── docs/                       # 📚 文档目录
│   ├── guides/                 # 指南文档
│   ├── reports/                # 报告文档
│   ├── plans/                  # 计划文档
│   ├── implementation/         # 实现指南
│   └── structure/              # 结构框架文档
│
├── themes/                     # 🎨 主题文档（64个Schema）
│   └── ... (33个主题目录)
│
├── view/                       # 🔍 视图理论
│   └── ... (理论分析、实践指南)
│
├── archive/                    # 📦 归档目录
│   └── ... (历史文档)
│
├── examples/                   # 💡 示例代码
│   └── quick_start.py
│
└── docker/                     # 🐳 Docker配置
    ├── docker-compose.yml
    └── Dockerfile.*
```

---

## 📦 代码目录（code/）

**定位**：所有源代码文件

### 核心模块

| 模块 | 说明 | 语言 |
|------|------|------|
| api_gateway | 统一API网关 | Python |
| multimodal_kg | 多模态知识图谱 | Python |
| temporal_kg | 时序知识图谱 | Python |
| llm_reasoning | LLM推理引擎 | Python |
| usl | 统一Schema语言 | Python |
| hierarchical_kg | 层次化知识表示 | Python |
| knowledge_chain | 知识链方法 | Python |
| explainable_reasoning | 可解释性推理 | Python |
| schema_versioning | Schema版本管理 | Python |
| server | MCP服务器 | TypeScript |
| transformers | Schema转换器 | TypeScript |

### 测试和脚本

- `tests/` - 单元测试和集成测试
- `scripts/` - 数据库初始化、服务启动脚本

---

## 📚 文档目录（docs/）

**定位**：所有文档文件

### 子目录说明

| 目录 | 说明 | 内容 |
|------|------|------|
| guides/ | 指南文档 | 部署指南、快速开始指南 |
| reports/ | 报告文档 | 实现阶段报告、项目完成报告 |
| plans/ | 计划文档 | 执行计划、设计计划 |
| implementation/ | 实现指南 | 各模块的实现指南 |
| structure/ | 结构框架 | 思维表征、模式总结、知识图谱框架 |

---

## 🎨 主题文档（themes/）

**定位**：64个Schema的完整文档集

- 33个主题目录
- 每个Schema包含5个标准文档（01-05）
- 总计320个文档

---

## 🔍 视图理论（view/）

**定位**：理论分析、实践指南、案例研究

- 理论分析文档
- 实践指南
- 案例研究

---

## 📦 归档目录（archive/）

**定位**：历史文档和已完成任务的文档

- plans/ - 历史计划文档
- reports/ - 历史报告文档
- analysis/ - 分析文档
- roadmaps/ - 路线图文档

---

## 💡 示例代码（examples/）

**定位**：使用示例和演示代码

- `quick_start.py` - 快速开始示例

---

## 🐳 Docker配置（docker/）

**定位**：Docker相关配置文件

- `docker-compose.yml` - 服务编排
- `Dockerfile.*` - 各服务的Dockerfile

---

## 🔍 查找指南

### 查找代码

- **Python代码**：`code/` 目录下各模块
- **TypeScript代码**：`code/server/`, `code/transformers/`
- **测试代码**：`code/tests/`

### 查找文档

- **部署指南**：`docs/guides/DEPLOYMENT_GUIDE.md`
- **实现指南**：`docs/implementation/`
- **项目报告**：`docs/reports/`
- **执行计划**：`docs/plans/`
- **结构框架**：`docs/structure/`

### 查找Schema文档

- **主题文档**：`themes/[主题编号]_[主题名称]/`
- **Schema文档**：`themes/[主题编号]_[主题名称]/[Schema名称]/`

---

**创建时间**：2025-01-21
**最后更新**：2025-01-21
**维护者**：DSL Schema研究团队
