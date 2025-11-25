# 消费者追溯Schema实践案例

## 📑 目录

- [消费者追溯Schema实践案例](#消费者追溯schema实践案例)
  - [📑 目录](#-目录)
  - [1. 案例概述](#1-案例概述)
  - [2. 案例1：消费者产品追溯查询](#2-案例1消费者产品追溯查询)
    - [2.1 场景描述](#21-场景描述)
    - [2.2 实现代码](#22-实现代码)

---

## 1. 案例概述

本文档提供消费者追溯Schema在实际应用中的实践案例。

---

## 2. 案例1：消费者产品追溯查询

### 2.1 场景描述

**业务背景**：
消费者通过产品GTIN查询产品追溯信息。

**解决方案**：
使用GS1标准标识产品，使用EPCIS记录追溯事件，提供消费者查询接口。

### 2.2 实现代码

```python
from consumer_traceability_storage import ConsumerTraceabilityStorage
from datetime import datetime

# 初始化存储
storage = ConsumerTraceabilityStorage("postgresql://user:pass@localhost/consumer_traceability")

# 创建产品
storage.store_product(
    product_id="PROD001",
    gtin="1234567890123",
    product_name="有机大米",
    batch_number="BATCH20250121",
    production_date=datetime(2025, 1, 15)
)

# 消费者查询产品追溯信息
def query_product_traceability(storage: ConsumerTraceabilityStorage, gtin: str):
    """查询产品追溯信息"""
    storage.cur.execute("""
        SELECT p.product_id, p.product_name, p.batch_number, p.production_date,
               tc.chain_status
        FROM products p
        LEFT JOIN traceability_chains tc ON p.product_id = tc.product_id
        WHERE p.gtin = %s
    """, (gtin,))

    result = storage.cur.fetchone()
    if result:
        return {
            "product_id": result[0],
            "product_name": result[1],
            "batch_number": result[2],
            "production_date": result[3],
            "chain_status": result[4]
        }
    return None
```

---

**参考文档**：

- `01_Overview.md` - 概述
- `02_Formal_Definition.md` - 形式化定义
- `03_Standards.md` - 标准对标
- `04_Transformation.md` - 转换体系

**创建时间**：2025-01-21
**最后更新**：2025-01-21
