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
  - [7. 案例6：完整追溯链（从原料到销售）](#7-案例6完整追溯链从原料到销售)
    - [7.1 场景描述](#71-场景描述)
    - [7.2 Schema定义](#72-schema定义)
    - [7.3 实现代码](#73-实现代码)
  - [8. 案例7：问题食品召回（反向追溯）](#8-案例7问题食品召回反向追溯)
    - [8.1 场景描述](#81-场景描述)
    - [8.2 Schema定义](#82-schema定义)
    - [8.3 实现代码](#83-实现代码)
  - [9. 案例8：质量检测流程](#9-案例8质量检测流程)
    - [9.1 场景描述](#91-场景描述)
    - [9.2 实现代码](#92-实现代码)
  - [10. 案例9：批次质量分析](#10-案例9批次质量分析)
    - [10.1 场景描述](#101-场景描述)
    - [10.2 实现代码](#102-实现代码)
  - [11. 案例10：供应商质量评估](#11-案例10供应商质量评估)
    - [11.1 场景描述](#111-场景描述)
    - [11.2 实现代码](#112-实现代码)

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

## 7. 案例6：完整追溯链（从原料到销售）

### 7.1 场景描述

**业务背景**：
食品公司需要实现从原料采购到最终销售的完整追溯链，记录每个环节的详细信息，确保食品安全和合规性。

**技术挑战**：

- 需要记录原料供应商信息
- 需要记录生产过程各环节
- 需要记录运输和分销过程
- 需要记录最终销售信息
- 需要支持正向追溯查询

**解决方案**：
使用FoodTraceabilitySystem创建完整的追溯链，使用trace_forward方法实现正向追溯。

### 7.2 Schema定义

**完整追溯链Schema**：

```json
{
  "food_id": "FOOD20250121001",
  "batch_number": "BATCH20250121001",
  "trace_path": [
    {
      "step": 1,
      "event_type": "RawMaterialReceived",
      "event_time": "2025-01-15T08:00:00Z",
      "location": "原料仓库A",
      "description": "接收原料"
    },
    {
      "step": 2,
      "event_type": "ProductionStarted",
      "event_time": "2025-01-16T09:00:00Z",
      "location": "生产车间A",
      "description": "开始生产"
    },
    {
      "step": 3,
      "event_type": "QualityCheck",
      "event_time": "2025-01-16T14:00:00Z",
      "location": "质检室A",
      "description": "质量检测"
    },
    {
      "step": 4,
      "event_type": "Packaging",
      "event_time": "2025-01-17T10:00:00Z",
      "location": "包装车间A",
      "description": "包装完成"
    },
    {
      "step": 5,
      "event_type": "Shipping",
      "event_time": "2025-01-18T08:00:00Z",
      "location": "物流中心A",
      "description": "发货"
    },
    {
      "step": 6,
      "event_type": "RetailSale",
      "event_time": "2025-01-20T10:00:00Z",
      "location": "零售店A",
      "description": "销售"
    }
  ]
}
```

### 7.3 实现代码

**完整的追溯链实现**：

```python
from food_traceability_system import FoodTraceabilitySystem
from food_industry_storage import FoodIndustryStorage
from datetime import datetime

def complete_traceability_chain():
    """完整追溯链示例"""
    storage = FoodIndustryStorage("postgresql://user:pass@localhost/food_industry")
    traceability_system = FoodTraceabilitySystem(storage)

    food_id = "FOOD20250121001"
    batch_number = "BATCH20250121001"

    # 创建追溯链
    traceability_data = {
        "supplier_name": "原料供应商A",
        "supplier_gln": "1111111111111",
        "manufacturer_name": "食品加工厂A",
        "manufacturer_gln": "2222222222222",
        "distributor_name": "分销商A",
        "distributor_gln": "3333333333333",
        "retailer_name": "零售店A",
        "retailer_gln": "4444444444444"
    }

    traceability_id = traceability_system.create_traceability_chain(
        food_id, batch_number, traceability_data
    )
    print(f"Created traceability chain: {traceability_id}")

    # 添加追溯事件
    events = [
        {"type": "RawMaterialReceived", "location": "原料仓库A", "description": "接收原料"},
        {"type": "ProductionStarted", "location": "生产车间A", "description": "开始生产"},
        {"type": "QualityCheck", "location": "质检室A", "description": "质量检测"},
        {"type": "Packaging", "location": "包装车间A", "description": "包装完成"},
        {"type": "Shipping", "location": "物流中心A", "description": "发货"},
        {"type": "RetailSale", "location": "零售店A", "description": "销售"}
    ]

    for i, event in enumerate(events):
        event_time = datetime(2025, 1, 15 + i, 8 + i, 0, 0)
        traceability_system.add_traceability_event(
            food_id,
            batch_number,
            event["type"],
            event["location"],
            event_operator=f"Operator{i+1}",
            event_description=event["description"]
        )
        print(f"Added event: {event['type']} at {event['location']}")

    # 正向追溯
    forward_trace = traceability_system.trace_forward(food_id, batch_number)
    print(f"\nForward Traceability:")
    print(f"  Origin: {forward_trace['origin']['manufacturer']}")
    print(f"  Destination: {forward_trace['destination']['retailer']}")
    print(f"  Total steps: {forward_trace['total_steps']}")
    print(f"\nTrace Path:")
    for step in forward_trace['trace_path']:
        print(f"  Step {step['step']}: {step['event_type']} at {step['location']} ({step['event_time']})")

    # 追溯路径可视化
    visualization = traceability_system.visualize_trace_path(food_id, batch_number, "forward")
    print(f"\nVisualization:")
    print(f"  Nodes: {len(visualization['visualization']['nodes'])}")
    print(f"  Edges: {len(visualization['visualization']['edges'])}")

    storage.close()

if __name__ == "__main__":
    complete_traceability_chain()
```

---

## 8. 案例7：问题食品召回（反向追溯）

### 8.1 场景描述

**业务背景**：
当发现食品存在质量问题时，需要快速反向追溯，找出所有受影响的产品批次，确定问题源头，并召回所有相关产品。

**技术挑战**：

- 需要快速反向追溯
- 需要找出所有受影响批次
- 需要确定问题源头
- 需要生成召回清单

**解决方案**：
使用trace_backward方法实现反向追溯，快速定位问题源头和所有受影响的产品。

### 8.2 Schema定义

**问题食品召回Schema**：

```json
{
  "recall_id": "RECALL20250121001",
  "food_id": "FOOD20250121001",
  "batch_number": "BATCH20250121001",
  "issue_description": "检测到细菌超标",
  "recall_reason": "QualityIssue",
  "trace_backward_result": {
    "origin": {
      "supplier": "原料供应商A",
      "manufacturer": "食品加工厂A",
      "first_event": {...}
    },
    "trace_path": [...],
    "affected_batches": ["BATCH20250121001", "BATCH20250121002"]
  }
}
```

### 8.3 实现代码

**问题食品召回实现**：

```python
from food_traceability_system import FoodTraceabilitySystem
from food_industry_storage import FoodIndustryStorage
from datetime import datetime

def food_recall_example():
    """问题食品召回示例"""
    storage = FoodIndustryStorage("postgresql://user:pass@localhost/food_industry")
    traceability_system = FoodTraceabilitySystem(storage)

    food_id = "FOOD20250121001"
    batch_number = "BATCH20250121001"

    # 反向追溯
    backward_trace = traceability_system.trace_backward(food_id, batch_number)
    print(f"Backward Traceability:")
    print(f"  Starting point: {backward_trace['starting_point']['retailer']}")
    print(f"  Origin: {backward_trace['origin']['manufacturer']}")
    print(f"  Total steps: {backward_trace['total_steps']}")

    print(f"\nTrace Path (backward):")
    for step in backward_trace['trace_path']:
        print(f"  Step {step['step']}: {step['event_type']} at {step['location']} ({step['event_time']})")

    # 查找所有受影响批次（简化：假设同一原料供应商的所有批次都受影响）
    origin = backward_trace['origin']
    supplier = origin.get('supplier')

    # 获取所有使用相同供应商的批次
    affected_batches = []
    if supplier:
        # 这里应该查询数据库，找到所有使用相同供应商的批次
        # 简化示例
        affected_batches = [
            {"food_id": food_id, "batch_number": batch_number},
            {"food_id": food_id, "batch_number": "BATCH20250121002"}
        ]

    print(f"\nAffected Batches:")
    for batch in affected_batches:
        print(f"  {batch['food_id']} - {batch['batch_number']}")

    # 生成召回清单
    recall_list = {
        "recall_id": f"RECALL_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "issue_description": "检测到细菌超标",
        "recall_reason": "QualityIssue",
        "origin": origin,
        "affected_batches": affected_batches,
        "recall_time": datetime.now()
    }

    print(f"\nRecall List:")
    print(f"  Recall ID: {recall_list['recall_id']}")
    print(f"  Issue: {recall_list['issue_description']}")
    print(f"  Affected batches: {len(recall_list['affected_batches'])}")

    storage.close()

if __name__ == "__main__":
    food_recall_example()
```

---

## 9. 案例8：质量检测流程

### 9.1 场景描述

**业务背景**：
食品公司需要建立完整的质量检测流程，包括定义质量检测规则、执行质量检测、触发质量预警、生成质量报告。

**技术挑战**：

- 需要定义多种质量检测规则
- 需要实时质量检测
- 需要自动触发预警
- 需要生成质量报告

**解决方案**：
使用QualityMonitor类实现质量检测流程，支持多种检测规则和自动预警。

### 9.2 实现代码

**质量检测流程实现**：

```python
from quality_monitor import QualityMonitor
from food_industry_storage import FoodIndustryStorage
from datetime import datetime

def quality_check_process():
    """质量检测流程示例"""
    storage = FoodIndustryStorage("postgresql://user:pass@localhost/food_industry")
    quality_monitor = QualityMonitor(storage)

    # 添加质量检测规则
    rules = [
        {
            "rule_id": "RULE001",
            "rule_name": "温度上限检测",
            "rule_type": "threshold",
            "parameter_name": "temperature_max",
            "threshold_value": 8.0,
            "severity": "high",
            "alert_message": "温度超过8°C，不符合冷藏要求"
        },
        {
            "rule_id": "RULE002",
            "rule_name": "湿度范围检测",
            "rule_type": "range",
            "parameter_name": "humidity",
            "min_value": 40.0,
            "max_value": 60.0,
            "severity": "medium",
            "alert_message": "湿度不在40%-60%范围内"
        },
        {
            "rule_id": "RULE003",
            "rule_name": "pH值检测",
            "rule_type": "range",
            "parameter_name": "ph_value",
            "min_value": 6.5,
            "max_value": 7.5,
            "severity": "critical",
            "alert_message": "pH值不在6.5-7.5范围内，可能存在质量问题"
        }
    ]

    for rule in rules:
        quality_monitor.add_quality_rule(rule["rule_id"], rule)
        print(f"Added quality rule: {rule['rule_name']}")

    # 执行质量检测
    food_id = "FOOD20250121001"
    batch_number = "BATCH20250121001"

    quality_data = {
        "temperature_max": 7.5,
        "humidity": 55.0,
        "ph_value": 7.0,
        "bacteria_count": 100
    }

    check_result = quality_monitor.check_quality(food_id, batch_number, quality_data)
    print(f"\nQuality Check Result:")
    print(f"  Passed: {check_result['passed']}")
    print(f"  Quality Score: {check_result['quality_score']:.2f}")
    print(f"  Violations: {len(check_result['violations'])}")
    print(f"  Warnings: {len(check_result['warnings'])}")

    if check_result['violations']:
        print(f"\nViolations:")
        for violation in check_result['violations']:
            print(f"  - {violation['rule_name']}: {violation['message']}")

    if check_result['warnings']:
        print(f"\nWarnings:")
        for warning in check_result['warnings']:
            print(f"  - {warning['rule_name']}: {warning['message']}")

    # 生成质量报告
    report = quality_monitor.generate_quality_report(
        food_id=food_id,
        batch_number=batch_number,
        start_date=datetime(2025, 1, 1),
        end_date=datetime.now()
    )

    print(f"\nQuality Report:")
    print(f"  Total checks: {report['summary']['total_checks']}")
    print(f"  Pass rate: {report['summary']['pass_rate']:.2f}%")
    print(f"  Average quality score: {report['summary']['average_quality_score']:.2f}")
    print(f"  Active alerts: {report['summary']['active_alerts']}")

    storage.close()

if __name__ == "__main__":
    quality_check_process()
```

---

## 10. 案例9：批次质量分析

### 10.1 场景描述

**业务背景**：
食品公司需要分析不同批次的质量数据，识别质量趋势，找出质量问题的根本原因，优化生产过程。

**技术挑战**：

- 需要分析多个批次的质量数据
- 需要识别质量趋势
- 需要找出质量问题模式
- 需要生成分析报告

**解决方案**：
使用质量检测数据和统计分析，实现批次质量分析和趋势识别。

### 10.2 实现代码

**批次质量分析实现**：

```python
from quality_monitor import QualityMonitor
from food_industry_storage import FoodIndustryStorage
from datetime import datetime, timedelta
from collections import defaultdict

def batch_quality_analysis():
    """批次质量分析示例"""
    storage = FoodIndustryStorage("postgresql://user:pass@localhost/food_industry")
    quality_monitor = QualityMonitor(storage)

    food_id = "FOOD20250121001"

    # 获取所有批次的质量检测记录
    quality_checks = storage.get_quality_checks(
        food_id=food_id,
        start_date=datetime.now() - timedelta(days=30)
    )

    if not quality_checks:
        print("No quality checks found")
        return

    # 按批次分组
    batch_quality = defaultdict(list)
    for check in quality_checks:
        batch_number = check.get("batch_number")
        batch_quality[batch_number].append(check)

    print(f"Batch Quality Analysis for {food_id}:")
    print(f"  Total batches: {len(batch_quality)}")

    # 分析每个批次
    batch_stats = []
    for batch_number, checks in batch_quality.items():
        passed_count = sum(1 for c in checks if c.get("passed", False))
        total_count = len(checks)
        avg_score = sum(c.get("quality_score", 0) for c in checks) / total_count if total_count > 0 else 0

        # 统计违规类型
        violation_types = defaultdict(int)
        for check in checks:
            for violation in check.get("violations", []):
                violation_types[violation.get("rule_name", "Unknown")] += 1

        batch_stats.append({
            "batch_number": batch_number,
            "total_checks": total_count,
            "passed_checks": passed_count,
            "pass_rate": (passed_count / total_count * 100) if total_count > 0 else 0,
            "avg_quality_score": avg_score,
            "violation_types": dict(violation_types)
        })

    # 排序（按质量得分）
    batch_stats.sort(key=lambda x: x["avg_quality_score"], reverse=True)

    print(f"\nBatch Quality Ranking:")
    for i, stat in enumerate(batch_stats, 1):
        print(f"  {i}. {stat['batch_number']}:")
        print(f"     Pass rate: {stat['pass_rate']:.2f}%")
        print(f"     Avg quality score: {stat['avg_quality_score']:.2f}")
        if stat['violation_types']:
            print(f"     Violations: {', '.join(stat['violation_types'].keys())}")

    # 识别质量趋势
    print(f"\nQuality Trends:")
    if len(batch_stats) >= 2:
        recent_batches = batch_stats[:5]
        avg_recent_score = sum(s["avg_quality_score"] for s in recent_batches) / len(recent_batches)

        older_batches = batch_stats[-5:] if len(batch_stats) > 5 else []
        if older_batches:
            avg_older_score = sum(s["avg_quality_score"] for s in older_batches) / len(older_batches)
            trend = "improving" if avg_recent_score > avg_older_score else "declining"
            print(f"  Quality trend: {trend}")
            print(f"  Recent avg score: {avg_recent_score:.2f}")
            print(f"  Older avg score: {avg_older_score:.2f}")

    # 找出常见问题
    all_violations = defaultdict(int)
    for stat in batch_stats:
        for violation_type, count in stat["violation_types"].items():
            all_violations[violation_type] += count

    if all_violations:
        print(f"\nCommon Issues:")
        sorted_violations = sorted(all_violations.items(), key=lambda x: x[1], reverse=True)
        for violation_type, count in sorted_violations[:5]:
            print(f"  {violation_type}: {count} occurrences")

    storage.close()

if __name__ == "__main__":
    batch_quality_analysis()
```

---

## 11. 案例10：供应商质量评估

### 11.1 场景描述

**业务背景**：
食品公司需要评估供应商的质量表现，根据供应商提供的原料质量数据，评估供应商的可靠性，优化供应商选择。

**技术挑战**：

- 需要收集供应商质量数据
- 需要评估供应商质量表现
- 需要生成供应商质量报告
- 需要支持供应商排名

**解决方案**：
使用质量检测数据和追溯链信息，实现供应商质量评估和排名。

### 11.2 实现代码

**供应商质量评估实现**：

```python
from food_traceability_system import FoodTraceabilitySystem
from food_industry_storage import FoodIndustryStorage
from quality_monitor import QualityMonitor
from datetime import datetime, timedelta
from collections import defaultdict

def supplier_quality_assessment():
    """供应商质量评估示例"""
    storage = FoodIndustryStorage("postgresql://user:pass@localhost/food_industry")
    traceability_system = FoodTraceabilitySystem(storage)
    quality_monitor = QualityMonitor(storage)

    # 获取所有追溯链
    # 简化：假设可以从数据库查询所有追溯链
    suppliers = {}

    # 模拟供应商数据
    suppliers = {
        "供应商A": {
            "gln": "1111111111111",
            "batches": ["BATCH20250121001", "BATCH20250121002"],
            "quality_checks": []
        },
        "供应商B": {
            "gln": "2222222222222",
            "batches": ["BATCH20250121003", "BATCH20250121004"],
            "quality_checks": []
        }
    }

    # 获取每个供应商的质量检测数据
    for supplier_name, supplier_data in suppliers.items():
        for batch_number in supplier_data["batches"]:
            checks = storage.get_quality_checks(batch_number=batch_number)
            supplier_data["quality_checks"].extend(checks)

    # 评估供应商质量
    supplier_assessments = []

    for supplier_name, supplier_data in suppliers.items():
        checks = supplier_data["quality_checks"]

        if not checks:
            continue

        total_checks = len(checks)
        passed_checks = sum(1 for c in checks if c.get("passed", False))
        avg_score = sum(c.get("quality_score", 0) for c in checks) / total_checks if total_checks > 0 else 0

        # 统计违规
        violation_count = sum(len(c.get("violations", [])) for c in checks)
        critical_violations = sum(
            1 for c in checks
            for v in c.get("violations", [])
            if v.get("severity") == "critical"
        )

        supplier_assessments.append({
            "supplier_name": supplier_name,
            "gln": supplier_data["gln"],
            "total_checks": total_checks,
            "passed_checks": passed_checks,
            "pass_rate": (passed_checks / total_checks * 100) if total_checks > 0 else 0,
            "avg_quality_score": avg_score,
            "violation_count": violation_count,
            "critical_violations": critical_violations,
            "batches_count": len(supplier_data["batches"])
        })

    # 排序（按质量得分）
    supplier_assessments.sort(key=lambda x: x["avg_quality_score"], reverse=True)

    print(f"Supplier Quality Assessment:")
    print(f"  Total suppliers: {len(supplier_assessments)}")

    print(f"\nSupplier Ranking:")
    for i, assessment in enumerate(supplier_assessments, 1):
        print(f"  {i}. {assessment['supplier_name']}:")
        print(f"     Pass rate: {assessment['pass_rate']:.2f}%")
        print(f"     Avg quality score: {assessment['avg_quality_score']:.2f}")
        print(f"     Violations: {assessment['violation_count']}")
        print(f"     Critical violations: {assessment['critical_violations']}")
        print(f"     Batches: {assessment['batches_count']}")

    # 生成供应商质量报告
    print(f"\nSupplier Quality Report:")
    for assessment in supplier_assessments:
        rating = "Excellent" if assessment["avg_quality_score"] >= 90 else \
                 "Good" if assessment["avg_quality_score"] >= 75 else \
                 "Fair" if assessment["avg_quality_score"] >= 60 else "Poor"

        print(f"  {assessment['supplier_name']}: {rating}")
        print(f"    Recommendation: {'Continue partnership' if assessment['avg_quality_score'] >= 75 else 'Review partnership'}")

    storage.close()

if __name__ == "__main__":
    supplier_quality_assessment()
```

---

**参考文档**：

- `01_Overview.md` - 概述
- `02_Formal_Definition.md` - 形式化定义
- `03_Standards.md` - 标准对标
- `04_Transformation.md` - 转换体系

**创建时间**：2025-01-21
**最后更新**：2025-01-21
