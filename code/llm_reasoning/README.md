# LLM推理引擎实现

## 📋 目录结构

```
llm_reasoning/
├── README.md              # 本文件
├── llm_interface.py      # LLM接口抽象
├── embedding.py           # 知识图谱嵌入
├── chain_builder.py       # 推理链构建
├── validator.py           # 结果验证
├── models.py              # 数据模型
└── api.py                 # REST API接口
```

---

## 🎯 实现目标

- ✅ LLM接口抽象（支持OpenAI、Claude等）
- ✅ 知识图谱嵌入（实体、关系、子图）
- ✅ 推理链构建（多步推理）
- ✅ 结果验证（置信度、来源验证）
- ✅ REST API接口

---

## 📝 实现指南

参考：`../../implementation/LLM_REASONING_IMPLEMENTATION_GUIDE.md`

---

**创建时间**：2025-01-21
**维护者**：DSL Schema研究团队
