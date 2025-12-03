# 知识链方法实现

## 📋 目录结构

```
knowledge_chain/
├── README.md              # 本文件
├── models.py              # 数据模型
├── storage.py             # PostgreSQL存储
├── extraction.py           # 低层次知识提取
├── abstraction.py          # 高层次概念抽象
├── builder.py              # 知识链构建
├── reasoning.py            # 知识链推理
└── api.py                  # REST API接口
```

---

## 🎯 实现目标

- ✅ 低层次知识提取（实体、关系、属性）
- ✅ 高层次概念抽象（模式抽象、概念抽象、原理抽象）
- ✅ 知识链构建
- ✅ 知识链推理（自底向上、自顶向下）
- ✅ REST API接口

---

## 📝 框架设计

参考：`../../structure/KNOWLEDGE_CHAIN_METHOD.md`

---

**创建时间**：2025-01-21
**维护者**：DSL Schema研究团队
