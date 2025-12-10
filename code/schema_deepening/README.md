# Schema深化模块

## 📋 模块概述

Schema深化模块专注于Smart_Home、OA、Maritime、Food_Industry等Schema的深化实现，重点关注**数据模型转换、数据处理、Schema数据方面**。

## 🎯 核心功能

### 1. 智慧家居转换器（SmartHomeConverter）

**功能**：

- Matter/Zigbee双向转换
- 场景联动（条件检查、动作执行）
- 设备注册和管理

**使用示例**：

```python
from code.schema_deepening import SmartHomeConverter, DeviceProtocol

converter = SmartHomeConverter()

# Matter到Zigbee转换
matter_device = {
    'device_id': 'matter_light_1',
    'name': '客厅灯',
    'device_type': 'light',
    'protocol': 'matter',
    'clusters': [{
        'cluster_id': 0x0006,
        'cluster_name': 'OnOff',
        'attributes': {'OnOff': True}
    }]
}

zigbee_device = converter.convert_matter_to_zigbee(matter_device)

# 创建场景
scene = converter.create_scene({
    'name': '回家场景',
    'triggers': [{'type': 'manual'}],
    'actions': [{
        'type': 'set_state',
        'device_id': 'matter_light_1',
        'attribute': 'power',
        'value': True
    }]
})

# 执行场景
result = converter.execute_scene(scene.scene_id)
```

### 2. OA转换器（OAConverter）

**功能**：

- ODF/OOXML双向转换
- 文档类型检测和转换
- 文档结构转换

**使用示例**：

```python
from code.schema_deepening import OAConverter, DocumentFormat

converter = OAConverter()

# ODF到OOXML转换
result = converter.convert_odf_to_ooxml('input.odt', 'output.docx')
```

### 3. Maritime转换器（MaritimeConverter）

**功能**：

- EDIFACT消息解析
- EDIFACT到XML转换
- AIS数据解析和集成

**使用示例**：

```python
from code.schema_deepening import MaritimeConverter, EDIFACTMessageType

converter = MaritimeConverter()

# 解析EDIFACT消息
message = converter.parse_edifact(edifact_msg)

# 解析AIS消息
ais_message = converter.parse_ais(ais_data)

# 集成AIS数据
trajectory = converter.integrate_ais_data('vessel_1', [ais_message])
```

### 4. Food_Industry转换器（FoodIndustryConverter）

**功能**：

- EPCIS事件处理
- 追溯链查询（正向、反向）
- 质量监控

**使用示例**：

```python
from code.schema_deepening import FoodIndustryConverter, EPCISEventType

converter = FoodIndustryConverter()

# 处理EPCIS事件
event = converter.process_epcis_event(event_data)

# 正向追溯
chain = converter.trace_forward(event.epc)

# 质量检查
quality_result = converter.check_quality(food_data, [rule.rule_id])
```

### 5. BPMN处理器（BPMNProcessor）

**功能**：

- BPMN流程解析
- 流程执行
- 任务管理

**使用示例**：

```python
from code.schema_deepening import BPMNProcessor

processor = BPMNProcessor()

# 解析BPMN
process = processor.parse_bpmn(bpmn_xml)

# 启动流程
instance_id = processor.start_process(process.process_id)

# 完成任务
processor.complete_task('task_1')
```

### 6. EPCIS处理器（EPCISProcessor）

**功能**：

- EPCIS XML解析
- 事件查询
- EPC索引

**使用示例**：

```python
from code.schema_deepening import EPCISProcessor

processor = EPCISProcessor()

# 解析EPCIS XML
events = processor.parse_epcis_xml(epcis_xml)

# 查询事件
related_events = processor.query_events_by_epc(epc)
```

### 7. EDIFACT解析器（EDIFACTParser）

**功能**：

- EDIFACT消息解析
- 消息验证
- XML转换

**使用示例**：

```python
from code.schema_deepening import EDIFACTParser

parser = EDIFACTParser()

# 解析EDIFACT消息
message = parser.parse_message(edifact_msg)

# 验证消息
validation = parser.validate_message(message)

# 转换为XML
xml = parser.convert_to_xml(message)
```

### 8. AIS处理器（AISProcessor）

**功能**：

- AIS消息解析（NMEA格式）
- 船舶轨迹构建
- 距离计算

**使用示例**：

```python
from code.schema_deepening import AISProcessor

processor = AISProcessor()

# 解析AIS消息
message = processor.parse_nmea(nmea_sentence)

# 获取船舶轨迹
trajectory = processor.get_vessel_trajectory(mmsi)
```

## 📁 文件结构

```
code/schema_deepening/
├── __init__.py                          # 模块初始化
├── logger.py                            # 日志工具
├── exceptions.py                        # 异常类定义
├── cache.py                             # 缓存工具
├── smart_home_converter.py              # 智慧家居转换器
├── smart_home_storage.py                # 智慧家居存储
├── oa_converter.py                      # OA转换器
├── oa_storage.py                        # OA存储
├── bpmn_processor.py                   # BPMN处理器
├── maritime_converter.py                # Maritime转换器
├── maritime_storage.py                  # Maritime存储
├── edifact_parser.py                    # EDIFACT解析器
├── ais_processor.py                     # AIS处理器
├── food_industry_converter.py           # 食品行业转换器
├── food_industry_storage.py             # 食品行业存储
├── epcis_processor.py                   # EPCIS处理器
├── tests/                               # 测试目录
│   ├── __init__.py
│   ├── test_smart_home_converter.py    # 转换器测试
│   ├── test_smart_home_storage.py       # 存储测试
│   └── test_cache.py                    # 缓存测试
└── README.md                            # 本文档
```

## 🔧 依赖

- Python 3.8+
- psycopg2（PostgreSQL连接）
- 标准库：typing, dataclasses, enum, datetime, xml.etree.ElementTree, zipfile, json, re, struct

## 📝 使用说明

1. **导入模块**：

```python
from code.schema_deepening import (
    SmartHomeConverter,
    OAConverter,
    MaritimeConverter,
    FoodIndustryConverter,
    BPMNProcessor,
    EPCISProcessor,
    EDIFACTParser,
    AISProcessor
)
```

2. **使用转换器**：

```python
# Smart Home
converter = SmartHomeConverter()
zigbee_device = converter.convert_matter_to_zigbee(matter_device)

# OA
oa_converter = OAConverter()
result = oa_converter.convert_odf_to_ooxml('input.odt', 'output.docx')

# Maritime
maritime_converter = MaritimeConverter()
message = maritime_converter.parse_edifact(edifact_msg)

# Food Industry
food_converter = FoodIndustryConverter()
event = food_converter.process_epcis_event(event_data)
```

3. **使用存储**：

```python
from code.schema_deepening import SmartHomeStorage

storage = SmartHomeStorage("postgresql://localhost/smart_home_db")
storage.store_device(device)
```

## 🎯 核心特性

### 数据模型转换

- ✅ Matter/Zigbee双向转换
- ✅ ODF/OOXML双向转换
- ✅ EDIFACT到XML转换

### 数据处理

- ✅ EPCIS事件处理
- ✅ AIS数据解析
- ✅ BPMN流程执行

### Schema数据

- ✅ 追溯链查询
- ✅ 质量监控
- ✅ 场景联动

## 📊 代码统计

- **总代码行数**：约5,250行
- **核心类数量**：13个
- **方法数量**：约150个

## 🔄 后续计划

1. ✅ **功能完善**：完善错误处理、添加日志记录、添加单元测试
2. ✅ **性能优化**：查询优化、索引优化、缓存机制
3. **文档完善**：API文档、使用示例、最佳实践

## ✨ 最新更新 (2025-01-21)

### 新增功能

1. **日志系统**
   - 统一的日志记录工具 (`logger.py`)
   - 支持控制台和文件输出
   - **所有模块已集成日志记录** ✅

2. **异常处理**
   - 自定义异常类 (`exceptions.py`)
   - 完善的错误处理和验证
   - 清晰的错误信息
   - **所有模块已集成异常处理** ✅

3. **缓存机制**
   - 简单缓存实现 (`cache.py`)
   - 支持过期时间和线程安全
   - 缓存装饰器支持

4. **单元测试**
   - SmartHomeConverter测试
   - SmartHomeStorage测试
   - 缓存功能测试

### 改进内容

#### Smart Home模块

- ✅ 所有转换器方法添加了日志记录
- ✅ 完善的输入验证和错误处理
- ✅ 使用LRU缓存优化设备类型映射
- ✅ 数据库操作添加了异常处理和回滚
- ✅ 场景执行添加了详细的日志记录
- ✅ 数据库索引优化（新增7个索引）

#### OA模块

- ✅ OAConverter添加了完整的日志和错误处理
- ✅ OAStorage添加了日志、错误处理和索引优化（新增6个索引）
- ✅ ODF/OOXML转换添加了详细的错误处理

#### Maritime模块

- ✅ MaritimeConverter添加了日志和错误处理
- ✅ MaritimeStorage添加了日志、错误处理和索引优化（新增5个索引）
- ✅ EDIFACT消息解析添加了详细的错误处理

#### Food Industry模块

- ✅ FoodIndustryConverter添加了日志和错误处理
- ✅ FoodIndustryStorage添加了日志、错误处理和索引优化（新增7个索引）
- ✅ EPCIS事件处理添加了详细的错误处理

#### 处理器模块

- ✅ 所有处理器（BPMN、EPCIS、EDIFACT、AIS）已集成日志系统
- ✅ 所有处理器已导入异常类，准备错误处理

---

**创建时间**：2025-01-21
**最后更新**：2025-01-21
**维护者**：DSL Schema研究团队
