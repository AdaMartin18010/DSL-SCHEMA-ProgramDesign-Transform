# 项目重组计划

## 📋 目标

将代码和文档明确分离，创建清晰的项目结构。

## 🎯 新目录结构

```
DSL-SCHEMA-ProgramDesign-Transform/
├── README.md                    # 项目主文档
├── LICENSE                      # 许可证
├── CONTRIBUTING.md             # 贡献指南
├── QUICK_START_GUIDE.md         # 快速开始指南
│
├── code/                       # 代码目录（原code/）
│   ├── api_gateway/            # API网关
│   ├── multimodal_kg/          # 多模态知识图谱
│   ├── temporal_kg/            # 时序知识图谱
│   ├── llm_reasoning/          # LLM推理引擎
│   ├── usl/                    # 统一Schema语言
│   ├── hierarchical_kg/        # 层次化知识表示
│   ├── knowledge_chain/        # 知识链方法
│   ├── explainable_reasoning/  # 可解释性推理
│   ├── schema_versioning/      # Schema版本管理
│   ├── tests/                  # 测试代码
│   ├── scripts/                # 脚本
│   ├── server/                 # TypeScript服务器代码
│   ├── transformers/           # TypeScript转换器
│   ├── utils/                  # TypeScript工具
│   ├── requirements.txt        # Python依赖
│   └── README.md              # 代码目录说明
│
├── docs/                       # 文档目录
│   ├── guides/                 # 指南文档
│   │   ├── DEPLOYMENT_GUIDE.md
│   │   └── QUICK_START_GUIDE.md
│   ├── reports/                # 报告文档
│   │   ├── IMPLEMENTATION_PHASE_*.md
│   │   ├── FINAL_*.md
│   │   └── PROJECT_*.md
│   ├── plans/                  # 计划文档
│   │   ├── PROJECT_COMPREHENSIVE_ADVANCEMENT_EXECUTION_PLAN.md
│   │   └── SCHEMA_DESIGN_*.md
│   ├── implementation/         # 实现指南
│   │   ├── MULTIMODAL_KG_IMPLEMENTATION_GUIDE.md
│   │   ├── TEMPORAL_KG_IMPLEMENTATION_GUIDE.md
│   │   ├── LLM_REASONING_IMPLEMENTATION_GUIDE.md
│   │   └── USL_IMPLEMENTATION_GUIDE.md
│   └── structure/              # 结构框架文档（从根目录移动）
│       ├── GLOBAL_MINDMAP.md
│       ├── MULTIDIMENSIONAL_MATRICES.md
│       └── ...
│
├── themes/                     # 主题文档（保持不变）
│   └── ...
│
├── view/                       # 视图理论（保持不变）
│   └── ...
│
├── archive/                    # 归档（保持不变）
│   └── ...
│
├── examples/                   # 示例代码
│   └── quick_start.py
│
├── docker/                     # Docker相关文件
│   ├── docker-compose.yml
│   ├── Dockerfile.multimodal
│   ├── Dockerfile.temporal
│   ├── Dockerfile.llm
│   ├── Dockerfile.usl
│   ├── Dockerfile.hierarchical
│   ├── Dockerfile.knowledge_chain
│   ├── Dockerfile.explainable
│   ├── Dockerfile.versioning
│   └── Dockerfile.gateway
│
└── .env.example                # 环境变量示例
```

---

**创建时间**：2025-01-21
**维护者**：DSL Schema研究团队

