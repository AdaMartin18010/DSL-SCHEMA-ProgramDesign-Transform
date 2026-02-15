# Schema验证器工具

**版本**: v1.0  
**创建日期**: 2026-02-15  

---

## 功能概述

Schema验证器是一个用于验证DSL Schema文档质量和一致性的自动化工具。

### 主要功能

1. **结构验证**
   - 检查必需文件是否存在
   - 验证文档格式正确性
   - 检查交叉引用完整性

2. **内容验证**
   - 术语一致性检查
   - 标准引用有效性
   - Mermaid图表语法检查

3. **质量评分**
   - 文档完整度评分
   - 形式化深度评分
   - 综合质量报告

---

## 使用方法

```bash
# 验证单个主题
python schema_validator.py --theme 01_Industrial_Automation

# 验证所有主题
python schema_validator.py --all

# 生成质量报告
python schema_validator.py --all --report report.html
```

---

## 验证规则

### 结构规则

| 规则ID | 描述 | 严重级别 |
|--------|------|---------|
| STRUCT-001 | README.md必须存在 | Error |
| STRUCT-002 | Mind_Map.md必须存在 | Error |
| STRUCT-003 | Knowledge_Matrix.md必须存在 | Error |
| STRUCT-004 | Formal_Proofs.md必须存在 | Error |
| STRUCT-005 | Decision_Trees.md必须存在 | Warning |
| STRUCT-006 | 子主题文档完整性检查 | Error |

### 内容规则

| 规则ID | 描述 | 严重级别 |
|--------|------|---------|
| CONTENT-001 | 术语必须使用统一术语表 | Warning |
| CONTENT-002 | 标准引用必须使用最新版本 | Warning |
| CONTENT-003 | Mermaid图表必须语法正确 | Error |
| CONTENT-004 | 交叉引用必须有效 | Warning |

---

## 输出格式

```json
{
  "validation_id": "val-20260215-001",
  "timestamp": "2026-02-15T21:00:00Z",
  "summary": {
    "total_files": 50,
    "passed": 48,
    "warnings": 2,
    "errors": 0
  },
  "results": [
    {
      "file": "01_Industrial_Automation/README.md",
      "status": "passed",
      "checks": [...]
    }
  ]
}
```

---

**维护者**: DSL Schema研究团队
