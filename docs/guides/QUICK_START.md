# DSL Schema 快速入门指南

**版本**: v2.0  
**最后更新**: 2026-02-14

---

## 🚀 5分钟快速开始

### 1. 环境准备

```bash
# 克隆项目
git clone <repository-url>
cd DSL-SCHEMA-ProgramDesign-Transform

# 安装依赖
pip install -r requirements.txt

# 验证安装
python scripts/setup_environment.py --check-only
```

### 2. 运行第一个示例

```bash
# 运行完整工作流示例
python examples/complete_workflow_example.py
```

### 3. 运行测试

```bash
# 运行所有测试
pytest code/tests/ -v

# 运行特定模块测试
pytest code/tests/test_llm_reasoning.py -v
pytest code/tests/test_usl.py -v
```

---

## 📚 核心功能快速体验

### 功能1: USL解析

```python
from usl import USLParser

usl_code = """
schema UserSchema {
    field username: String {
        required: true
        minLength: 3
    }
    field email: String {
        required: true
        format: "email"
    }
}
"""

parser = USLParser()
ast = parser.parse(usl_code)
print(ast)
```

### 功能2: LLM推理

```python
from llm_reasoning import OpenAILLM, ReasoningChainBuilder

# 初始化LLM
llm = OpenAILLM(api_key="your-api-key")

# 构建推理链
builder = ReasoningChainBuilder(kg_processor=None, llm=llm)
chain = builder.build_reasoning_chain("分析Schema转换规则")
```

### 功能3: 增量转换

```python
from schema_transformation import IncrementalTransformer

transformer = IncrementalTransformer()
result = transformer.transform(source_schema, target_schema)
```

---

## 📖 学习路径

### 初学者 (1-2天)

1. 阅读 [项目概览](../../README.md)
2. 浏览 [examples/](../../examples/) 目录
3. 运行快速入门示例
4. 查看 [FAQ.md](../../FAQ.md)

### 进阶用户 (1周)

1. 深入学习 [themes/](../../themes/) 中的Schema定义
2. 研究 [code/](../../code/) 核心模块实现
3. 阅读理论文档 [docs/theory/](../theory/)
4. 实践Schema转换

### 专家用户 (持续)

1. 参与USL标准化提案 [docs/standards/](../standards/)
2. 开发新模块和扩展
3. 贡献代码和文档
4. 参与社区讨论

---

## 🛠️ 常用命令

```bash
# 环境检查
python scripts/setup_environment.py

# 运行测试
pytest code/tests/ -v --tb=short

# 生成进度报告
python scripts/project_progress_report.py

# 验证文档
python scripts/verify_documentation.py

# 最终检查
python scripts/final_100_percent_check.py
```

---

## 📞 获取帮助

- 📧 邮件支持: dsl-schema@example.com
- 💬 社区论坛: [讨论区](../../docs/community/)
- 🐛 问题反馈: [GitHub Issues](../../.github/ISSUE_TEMPLATE.md)
- 📚 完整文档: [DOCUMENT_INDEX.md](../../DOCUMENT_INDEX.md)

---

**🎉 恭喜！您已完成DSL Schema的快速入门！**
