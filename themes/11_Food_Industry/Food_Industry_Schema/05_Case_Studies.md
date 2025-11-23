# 食品行业Schema实践案例

## 📑 目录

- [食品行业Schema实践案例](#食品行业schema实践案例)
  - [📑 目录](#-目录)
  - [1. 案例概述](#1-案例概述)
  - [2. 案例1：食品生产管理和批次追踪](#2-案例1食品生产管理和批次追踪)
    - [2.1 场景描述](#21-场景描述)
    - [2.2 Schema定义](#22-schema定义)
    - [2.3 实现代码](#23-实现代码)
  - [3. 案例2：食品安全全程追溯](#3-案例2食品安全全程追溯)
    - [3.1 场景描述](#31-场景描述)
    - [3.2 Schema定义](#32-schema定义)
    - [3.3 实现代码](#33-实现代码)
  - [4. 案例3：食品质量监控](#4-案例3食品质量监控)
    - [4.1 场景描述](#41-场景描述)
    - [4.2 Schema定义](#42-schema定义)
  - [5. 案例4：GS1到EPCIS消息转换](#5-案例4gs1到epcis消息转换)
    - [5.1 场景描述](#51-场景描述)
    - [5.2 实现代码](#52-实现代码)
  - [6. 案例5：食品行业数据分析和报表](#6-案例5食品行业数据分析和报表)
    - [6.1 场景描述](#61-场景描述)
    - [6.2 实现代码](#62-实现代码)
    - [6.3 数据分析示例](#63-数据分析示例)

---

## 1. 案例概述

本文档提供食品行业Schema在实际应用中的实践案例。

---

## 2. 案例1：食品生产管理和批次追踪

### 2.1 场景描述

**业务背景**：
食品加工厂需要管理食品生产批次，记录生产流程和质量检查点，
确保生产过程符合ISO 22000标准，并支持批次追溯。

**技术挑战**：

- 需要创建和管理生产批次
- 需要记录生产流程步骤
- 需要记录质量检查点
- 需要追踪原料来源

**解决方案**：
使用ProductionBatchManager创建生产批次，使用FoodTraceabilitySystem
记录生产事件，实现完整的生产批次管理。

### 2.2 Schema定义

详见第2.2节原始定义。

### 2.3 实现代码

**完整的食品生产管理实现**：

```python
from food_industry_storage import FoodIndustryStorage
from production_batch_manager import ProductionBatchManager
from food_traceability_system import FoodTraceabilitySystem
from datetime import datetime, date

# 初始化存储和管理器
storage = FoodIndustryStorage("postgresql://user:pass@localhost/food_industry")
batch_manager = ProductionBatchManager(storage)
traceability_system = FoodTraceabilitySystem(storage)

# 创建食品
food_data = {
    "food_id": "FOOD20250121001",
    "gtin": "12345678901234",
    "food_name": "有机面包",
    "food_category": "Grain",
    "food_type": "Bread",
    "brand_name": "健康品牌",
    "manufacturer": "食品加工厂",
    "country_of_origin": "CN",
    "food_description": "有机全麦面包",
    "production_date": date(2025, 1, 21),
    "expiry_date": date(2025, 1, 28),
    "shelf_life_days": 7,
    "storage_conditions": "常温干燥保存"
}

food_id = storage.store_food(food_data)
print(f"Created food: {food_id}")

# 创建生产批次
batch_data = {
    "batch_number": "BATCH20250121001",
    "batch_size": 1000,
    "production_date": date(2025, 1, 21),
    "production_time": datetime.now().time(),
    "production_location": "生产车间A",
    "production_facility": "食品加工厂",
    "production_line": "生产线1"
}

batch_number = batch_manager.create_production_batch("FOOD20250121001", batch_data)
print(f"Created production batch: {batch_number}")

# 记录生产事件
events = [
    {
        "event_type": "Production",
        "event_location": "生产车间A",
        "event_operator": "张三",
        "event_description": "食品生产完成"
    },
    {
        "event_type": "QualityCheck",
        "event_location": "质检实验室",
        "event_operator": "王五",
        "event_description": "质量检查通过"
    },
    {
        "event_type": "Packaging",
        "event_location": "包装车间",
        "event_operator": "李四",
        "event_description": "食品包装完成"
    }
]

for event in events:
    event_id = traceability_system.add_traceability_event(
        "FOOD20250121001",
        batch_number,
        event["event_type"],
        event["event_location"],
        event["event_operator"],
        event["event_description"]
    )
    print(f"Recorded event: {event_id} - {event['event_type']}")

# 获取批次信息
batch_info = batch_manager.get_batch_info(batch_number)
if batch_info:
    print(f"\nBatch information:")
    print(f"  Batch number: {batch_info['batch_number']}")
    print(f"  Batch size: {batch_info['batch_size']}")
    print(f"  Production date: {batch_info['production_date']}")
    print(f"  Production location: {batch_info['production_location']}")

# 查询批次质量摘要
quality_summary = storage.get_batch_quality_summary(batch_number)
print(f"\nQuality summary:")
print(f"  Event count: {quality_summary.get('event_count', 0)}")
print(f"  Quality checks: {quality_summary.get('quality_check_count', 0)}")
```

---

## 3. 案例2：食品安全全程追溯

### 3.1 场景描述

**业务背景**：
食品供应链需要实现全程追溯，从原料供应商到生产商、分销商、
零售商，确保食品安全和质量可追溯。

**技术挑战**：

- 需要建立完整的追溯链
- 需要记录所有追溯事件
- 需要支持正向追溯（来源）和反向追溯（去向）
- 需要符合ISO 22005标准

**解决方案**：
使用FoodTraceabilitySystem创建追溯链，记录所有追溯事件，
实现正向和反向追溯功能。

### 3.2 Schema定义

详见第3.2节原始定义。

### 3.3 实现代码

**完整的食品安全追溯实现**：

```python
from food_industry_storage import FoodIndustryStorage
from food_traceability_system import FoodTraceabilitySystem
from datetime import datetime

# 初始化存储和追溯系统
storage = FoodIndustryStorage("postgresql://user:pass@localhost/food_industry")
traceability_system = FoodTraceabilitySystem(storage)

# 创建追溯链
traceability_data = {
    "supplier_name": "面粉供应商",
    "supplier_gln": "1234567890123",
    "manufacturer_name": "食品加工厂",
    "manufacturer_gln": "9876543210987",
    "distributor_name": "食品分销商",
    "distributor_gln": "1111111111111",
    "retailer_name": "超市A",
    "retailer_gln": "2222222222222"
}

traceability_id = traceability_system.create_traceability_chain(
    "FOOD20250121001",
    "BATCH20250121001",
    traceability_data
)
print(f"Created traceability chain: {traceability_id}")

# 记录追溯事件
events = [
    {
        "event_type": "Production",
        "event_location": "生产车间A",
        "event_operator": "张三",
        "event_description": "食品生产完成"
    },
    {
        "event_type": "Packaging",
        "event_location": "包装车间",
        "event_operator": "李四",
        "event_description": "食品包装完成"
    },
    {
        "event_type": "Transportation",
        "event_location": "运输途中",
        "event_operator": "王五",
        "event_description": "食品运输开始"
    },
    {
        "event_type": "Distribution",
        "event_location": "分销中心A",
        "event_operator": "赵六",
        "event_description": "食品到达分销中心"
    },
    {
        "event_type": "Retail",
        "event_location": "门店A",
        "event_operator": "钱七",
        "event_description": "食品到达零售门店"
    }
]

for event in events:
    event_id = traceability_system.add_traceability_event(
        "FOOD20250121001",
        "BATCH20250121001",
        event["event_type"],
        event["event_location"],
        event["event_operator"],
        event["event_description"]
    )
    print(f"Recorded event: {event_id} - {event['event_type']}")

# 获取追溯链
chain = traceability_system.get_traceability_chain("FOOD20250121001", "BATCH20250121001")
if chain:
    print(f"\nTraceability chain:")
    print(f"  Supplier: {chain.get('supplier_name')}")
    print(f"  Manufacturer: {chain.get('manufacturer_name')}")
    print(f"  Distributor: {chain.get('distributor_name')}")
    print(f"  Retailer: {chain.get('retailer_name')}")

# 获取追溯历史
history = traceability_system.get_traceability_history("FOOD20250121001", "BATCH20250121001")
print(f"\nTraceability history ({len(history)} events):")
for event in history:
    print(f"  {event['event_time']}: {event['event_type']} - {event['event_location']}")

# 追溯食品来源
origin_info = traceability_system.trace_food_origin("FOOD20250121001", "BATCH20250121001")
print(f"\nFood origin:")
print(f"  Supplier: {origin_info['origin_info']['supplier']}")
print(f"  Manufacturer: {origin_info['origin_info']['manufacturer']}")
if origin_info['origin_info']['first_event']:
    print(f"  First event: {origin_info['origin_info']['first_event']['event_type']}")

# 追溯食品去向
destination_info = traceability_system.trace_food_destination("FOOD20250121001", "BATCH20250121001")
print(f"\nFood destination:")
print(f"  Distributor: {destination_info['destination_info']['distributor']}")
print(f"  Retailer: {destination_info['destination_info']['retailer']}")
if destination_info['destination_info']['last_event']:
    print(f"  Last event: {destination_info['destination_info']['last_event']['event_type']}")

# 查询追溯事件统计
event_stats = storage.get_traceability_event_statistics("FOOD20250121001", "BATCH20250121001")
print(f"\nEvent statistics:")
print(f"  Total events: {event_stats['event_count']}")
print(f"  Event types: {event_stats['event_type_count']}")
print(f"  Locations: {event_stats['location_count']}")
```

---

## 4. 案例3：食品质量监控

### 4.1 场景描述

**应用场景**：
使用HACCP标准监控食品质量，包括质量检测和质量证书管理。

### 4.2 Schema定义

**食品质量监控Schema**：

```json
{
  "food_id": "FOOD20250121001",
  "batch_number": "BATCH20250121001",
  "quality_records": [
    {
      "record_id": "RECORD001",
      "record_type": "Test",
      "record_time": "2025-01-21T11:00:00Z",
      "record_location": "质检实验室",
      "record_operator": "质检员A",
      "record_result": "Pass",
      "record_document": "质检报告001.pdf"
    },
    {
      "record_id": "RECORD002",
      "record_type": "Certificate",
      "record_time": "2025-01-21T12:00:00Z",
      "record_location": "证书办公室",
      "record_operator": "证书管理员",
      "record_result": "Pass",
      "record_document": "质量证书001.pdf"
    }
  ]
}
```

---

## 5. 案例4：GS1到EPCIS消息转换

### 5.1 场景描述

**业务背景**：
食品企业需要将GS1标准的食品信息转换为EPCIS事件格式，
以便与EPCIS系统集成，实现跨系统的食品追溯。

**技术挑战**：

- 需要解析GS1条码和应用标识符
- 需要转换为EPCIS事件格式
- 需要支持多种EPCIS事件类型
- 需要生成EPCIS XML格式

**解决方案**：
使用GS1Parser解析GS1条码，使用GS1ToEPCISConverter转换为EPCIS事件。

### 5.2 实现代码

**完整的GS1到EPCIS转换实现**：

```python
from gs1_parser import GS1Parser, GS1ToEPCISConverter

# 初始化解析器和转换器
parser = GS1Parser()
converter = GS1ToEPCISConverter()

# 解析GS1条码
gs1_barcode = "011234567890123410BATCH001111250121"
gs1_data = parser.parse_gs1_barcode(gs1_barcode)
print(f"Parsed GS1 barcode:")
print(f"  GTIN: {gs1_data.get('gtin')}")
print(f"  Batch number: {gs1_data.get('batch_number')}")
print(f"  Production date: {gs1_data.get('production_date')}")

# GS1食品信息
food_info = {
    "food_id": "FOOD20250121001",
    "gtin": "12345678901234",
    "food_name": "有机面包",
    "food_category": "Grain",
    "batch_number": "BATCH20250121001",
    "production_date": "2025-01-21",
    "expiry_date": "2025-01-28",
    "production_location": "生产车间A",
    "manufacturer_gln": "9876543210987"
}

# 转换为EPCIS ObjectEvent
object_event = converter.convert_food_info_to_object_event(food_info)
print(f"\nEPCIS ObjectEvent:")
print(f"  Event type: {object_event['eventType']}")
print(f"  EPC: {object_event['epcList'][0]}")
print(f"  Biz step: {object_event['bizStep']}")

# 转换为EPCIS XML
epcis_xml = converter.convert_to_epcis_xml(object_event)
print(f"\nEPCIS XML (first 500 chars):")
print(epcis_xml[:500])

# GS1生产信息
production_info = {
    "production_id": "PROD20250121001",
    "gtin": "12345678901234",
    "batch_number": "BATCH20250121001",
    "batch_size": 1000,
    "production_date": "2025-01-21",
    "production_location": "生产车间A",
    "production_facility": "食品加工厂",
    "production_line": "生产线1",
    "manufacturer_gln": "9876543210987"
}

# 转换为EPCIS AggregationEvent
aggregation_event = converter.convert_production_info_to_aggregation_event(production_info)
print(f"\nEPCIS AggregationEvent:")
print(f"  Event type: {aggregation_event['eventType']}")
print(f"  Parent ID: {aggregation_event['parentID']}")
print(f"  Child EPC: {aggregation_event['childEPCs'][0]}")

# GS1追溯信息
traceability_info = {
    "gtin": "12345678901234",
    "event_time": "2025-01-22T08:00:00Z",
    "event_type": "Transportation",
    "event_location": "运输途中",
    "location_gln": "1111111111111",
    "biz_step": "shipping",
    "transaction_type": "PO",
    "transaction_id": "PO20250122001",
    "from_location": "生产车间A",
    "to_location": "分销中心A",
    "transport_method": "Truck"
}

# 转换为EPCIS TransactionEvent
transaction_event = converter.convert_traceability_info_to_transaction_event(traceability_info)
print(f"\nEPCIS TransactionEvent:")
print(f"  Event type: {transaction_event['eventType']}")
print(f"  Biz step: {transaction_event['bizStep']}")
print(f"  Transaction ID: {transaction_event['bizTransactionList'][0]['bizTransaction']}")
```

---

## 6. 案例5：食品行业数据分析和报表

### 6.1 场景描述

**应用场景**：
使用PostgreSQL存储食品行业数据，支持食品追溯、质量查询、
生产统计和过期食品分析。

### 6.2 实现代码

详见 `04_Transformation.md` 第7章。

### 6.3 数据分析示例

**食品行业数据分析查询**：

```python
from food_industry_storage import FoodIndustryStorage
from datetime import datetime, timedelta

storage = FoodIndustryStorage("postgresql://user:pass@localhost/food_industry")

# 查询生产批次统计
production_stats = storage.get_production_statistics(
    datetime.now() - timedelta(days=30)
)
print("Production Statistics (30 days):")
for stat in production_stats:
    print(f"  {stat['food_category']}:")
    print(f"    Batches: {stat['batch_count']}")
    print(f"    Total quantity: {stat['total_quantity']:.2f}")
    print(f"    Avg batch size: {stat['avg_batch_size']:.2f}")

# 查询追溯事件统计
event_stats = storage.get_traceability_event_statistics(
    "FOOD20250121001",
    "BATCH20250121001"
)
print(f"\nTraceability Event Statistics:")
print(f"  Total events: {event_stats['event_count']}")
print(f"  Event types: {event_stats['event_type_count']}")
print(f"  Locations: {event_stats['location_count']}")

# 查询即将过期的食品
expiring_foods = storage.get_food_expiry_analysis(days_ahead=30)
print(f"\nExpiring Foods (next 30 days):")
for food in expiring_foods[:10]:  # 显示前10个
    print(f"  {food['food_name']} ({food['food_category']}):")
    print(f"    Expiry date: {food['expiry_date']}")
    print(f"    Days until expiry: {food['days_until_expiry']}")

# 查询批次质量摘要
quality_summary = storage.get_batch_quality_summary("BATCH20250121001")
print(f"\nBatch Quality Summary:")
print(f"  Batch number: {quality_summary.get('batch_number')}")
print(f"  Batch size: {quality_summary.get('batch_size')}")
print(f"  Event count: {quality_summary.get('event_count', 0)}")
print(f"  Quality checks: {quality_summary.get('quality_check_count', 0)}")
```

---

**参考文档**：

- `01_Overview.md` - 概述
- `02_Formal_Definition.md` - 形式化定义
- `03_Standards.md` - 标准对标
- `04_Transformation.md` - 转换体系

**创建时间**：2025-01-21
**最后更新**：2025-01-21
