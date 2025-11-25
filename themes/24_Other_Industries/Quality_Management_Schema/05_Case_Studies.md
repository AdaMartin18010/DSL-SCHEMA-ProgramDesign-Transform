# 质量管理Schema实践案例

## 📑 目录

- [质量管理Schema实践案例](#质量管理schema实践案例)
  - [📑 目录](#-目录)
  - [1. 案例概述](#1-案例概述)
  - [2. 案例1：质量体系管理](#2-案例1质量体系管理)

---

## 1. 案例概述

本文档提供质量管理Schema在实际应用中的实践案例。

---

## 2. 案例1：质量体系管理

### 2.1 场景描述

**业务背景**：
管理ISO 9001质量管理体系，记录质量检验数据。

**解决方案**：
使用质量管理Schema管理质量体系，存储到PostgreSQL。

### 2.2 实现代码

```python
from quality_management_storage import QualityManagementStorage
from datetime import date

# 初始化存储
storage = QualityManagementStorage("postgresql://user:pass@localhost/quality_management")

# 创建质量体系
storage.store_quality_system(
    system_id="QS001",
    system_name="ABC公司质量管理体系",
    standard_type="ISO9001",
    certification_date=date(2024, 1, 1),
    expiry_date=date(2027, 1, 1)
)
```

---

**参考文档**：

- `01_Overview.md` - 概述
- `02_Formal_Definition.md` - 形式化定义
- `03_Standards.md` - 标准对标
- `04_Transformation.md` - 转换体系

**创建时间**：2025-01-21
**最后更新**：2025-01-21

