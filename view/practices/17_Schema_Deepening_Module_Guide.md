# Schema深化模块实践指南

## 📚 文档信息

**创建时间**：2025-01-21
**最后更新**：2025-01-21
**文档版本**：v1.0
**维护者**：DSL Schema研究团队

---

## 🎯 概述

Schema深化模块（`code/schema_deepening`）是一个专注于Smart_Home、OA、Maritime、Food_Industry等Schema的深化实现模块，重点关注**数据模型转换、数据处理、Schema数据方面**。

### 核心功能

- ✅ Matter/Zigbee双向转换
- ✅ ODF/OOXML双向转换
- ✅ EDIFACT消息解析和转换
- ✅ EPCIS事件处理和追溯链查询
- ✅ BPMN流程处理
- ✅ AIS数据解析
- ✅ 完整的日志和错误处理系统
- ✅ 性能优化（缓存、数据库索引）

---

## 📁 模块结构

### 核心转换器（4个）

1. **SmartHomeConverter** - 智慧家居转换器
   - Matter/Zigbee双向转换
   - 场景联动（条件检查、动作执行）
   - 设备注册和管理

2. **OAConverter** - 办公自动化转换器
   - ODF/OOXML双向转换
   - 文档类型检测和转换
   - 文档结构转换

3. **MaritimeConverter** - 海运与航运转换器
   - EDIFACT消息解析
   - EDIFACT到XML转换
   - AIS数据解析和集成

4. **FoodIndustryConverter** - 食品行业转换器
   - EPCIS事件处理
   - 追溯链查询（正向、反向）
   - 质量监控

### 处理器（4个）

1. **BPMNProcessor** - BPMN流程处理器
2. **EPCISProcessor** - EPCIS处理器
3. **EDIFACTParser** - EDIFACT解析器
4. **AISProcessor** - AIS处理器

### 基础设施

- **logger.py** - 统一日志工具
- **exceptions.py** - 异常类定义
- **cache.py** - 缓存机制
- **utils.py** - 通用工具函数

---

## 🚀 快速开始

### 1. 导入模块

```python
from code.schema_deepening import (
    SmartHomeConverter,
    OAConverter,
    MaritimeConverter,
    FoodIndustryConverter,
    DeviceProtocol,
    DeviceType,
    DocumentFormat,
    DocumentType,
    EPCISEventType,
    TraceDirection
)
```

### 2. 使用示例

#### Smart Home转换

```python
from code.schema_deepening import SmartHomeConverter

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

#### OA转换

```python
from code.schema_deepening import OAConverter

converter = OAConverter()

# ODF到OOXML转换
result = converter.convert_odf_to_ooxml('input.odt', 'output.docx')
```

#### Maritime转换

```python
from code.schema_deepening import MaritimeConverter

converter = MaritimeConverter()

# 解析EDIFACT消息
message = converter.parse_edifact(edifact_msg)

# 解析AIS消息
ais_message = converter.parse_ais(ais_data)

# 集成AIS数据
trajectory = converter.integrate_ais_data('vessel_1', [ais_message])
```

#### Food Industry转换

```python
from code.schema_deepening import FoodIndustryConverter

converter = FoodIndustryConverter()

# 处理EPCIS事件
event = converter.process_epcis_event(event_data)

# 正向追溯
chain = converter.trace_forward(event.epc)

# 质量检查
quality_result = converter.check_quality(food_data, [rule.rule_id])
```

---

## 📊 数据库存储

### Smart Home存储

```python
from code.schema_deepening import SmartHomeStorage

storage = SmartHomeStorage("postgresql://localhost/smart_home_db")

# 存储设备
device = {
    'device_id': 'device_1',
    'name': '客厅灯',
    'device_type': 'light',
    'protocol': 'matter',
    'state': {'power': True, 'brightness': 80},
    'capabilities': ['on_off', 'dimming']
}

storage.store_device(device)

# 查询设备状态历史
history = storage.query_device_state_history('device_1')
```

### OA存储

```python
from code.schema_deepening import OAStorage

storage = OAStorage("postgresql://localhost/oa_db")

# 存储文档
document = {
    'document_id': 'doc_1',
    'name': '项目计划书',
    'document_type': 'text',
    'format': 'odf',
    'content_path': '/path/to/document.odt'
}

storage.store_document(document)
```

### Maritime存储

```python
from code.schema_deepening import MaritimeStorage

storage = MaritimeStorage("postgresql://localhost/maritime_db")

# 存储AIS数据
ais_data = {
    'mmsi': '123456789',
    'message_type': 1,
    'latitude': 39.9042,
    'longitude': 116.4074,
    'speed': 12.5,
    'course': 45.0,
    'timestamp': datetime.utcnow()
}

storage.store_ais_data(ais_data)
```

### Food Industry存储

```python
from code.schema_deepening import FoodIndustryStorage

storage = FoodIndustryStorage("postgresql://localhost/food_db")

# 存储EPCIS事件
event = {
    'event_id': 'event_1',
    'event_type': 'ObjectEvent',
    'epc': 'urn:epc:id:sgtin:0614141.107346.2017',
    'action': 'OBSERVE',
    'biz_step': 'receiving',
    'event_time': datetime.utcnow()
}

storage.store_epcis_event(event)
```

---

## 🔧 工具函数

### 数据验证

```python
from code.schema_deepening.utils import (
    validate_uuid,
    validate_email,
    is_valid_url
)

# 验证UUID
is_valid = validate_uuid("550e8400-e29b-41d4-a716-446655440000")

# 验证邮箱
is_valid = validate_email("test@example.com")

# 验证URL
is_valid = is_valid_url("https://example.com")
```

### 日期时间处理

```python
from code.schema_deepening.utils import parse_datetime

# 解析多种格式的日期时间
dt = parse_datetime("2024-01-21T10:00:00")
dt = parse_datetime("2024/01/21 10:00:00")
```

### JSON处理

```python
from code.schema_deepening.utils import safe_json_loads, safe_json_dumps

# 安全解析JSON
data = safe_json_loads(json_str, default={})

# 安全序列化
json_str = safe_json_dumps(obj, default="{}")
```

### 其他工具

```python
from code.schema_deepening.utils import (
    format_file_size,
    truncate_string,
    deep_merge_dict,
    generate_id
)

# 格式化文件大小
size = format_file_size(1024 * 1024 * 5)  # "5.00 MB"

# 截断字符串
text = truncate_string("很长的字符串...", max_length=10)

# 深度合并字典
merged = deep_merge_dict(dict1, dict2)

# 生成ID
id = generate_id("device", timestamp=True)
```

---

## 📝 日志和错误处理

### 日志记录

```python
from code.schema_deepening import logger

# 记录不同级别的日志
logger.debug("调试信息")
logger.info("操作成功")
logger.warning("警告信息")
logger.error("错误信息", exc_info=True)
```

### 错误处理

```python
from code.schema_deepening.exceptions import (
    ValidationError,
    ConversionError,
    StorageError
)

try:
    # 操作代码
    result = converter.convert_matter_to_zigbee(device)
except ValidationError as e:
    logger.error(f"验证失败: {str(e)}")
except ConversionError as e:
    logger.error(f"转换失败: {str(e)}")
except StorageError as e:
    logger.error(f"存储失败: {str(e)}")
```

---

## ⚡ 性能优化

### 缓存使用

```python
from code.schema_deepening.cache import cached, get_global_cache

# 使用装饰器缓存
@cached(ttl=300)  # 缓存5分钟
def expensive_function(x, y):
    return x + y

# 使用全局缓存
cache = get_global_cache()
cache.set('key', 'value', ttl=3600)
value = cache.get('key')
```

### 数据库索引

所有存储模块都已优化数据库索引：

- **Smart Home**: 7个索引
- **OA**: 6个索引
- **Maritime**: 5个索引
- **Food Industry**: 7个索引

**总计**: 25个优化索引

---

## 🧪 测试

### 运行测试

```bash
# 运行所有测试
python -m pytest code/schema_deepening/tests/ -v

# 运行特定测试
python -m pytest code/schema_deepening/tests/test_smart_home_converter.py -v
```

### 测试覆盖

- ✅ SmartHomeConverter测试
- ✅ SmartHomeStorage测试
- ✅ OAConverter测试
- ✅ MaritimeConverter测试
- ✅ FoodIndustryConverter测试
- ✅ 缓存功能测试

---

## 📖 相关文档

### 模块文档

- [README.md](../../code/schema_deepening/README.md) - 模块完整文档
- [BEST_PRACTICES.md](../../code/schema_deepening/BEST_PRACTICES.md) - 最佳实践指南
- [CHANGELOG.md](../../code/schema_deepening/CHANGELOG.md) - 更新日志
- [examples.py](../../code/schema_deepening/examples.py) - 使用示例代码

### 项目文档

- [行业Schema分析与转换](../analysis/themes/05-行业Schema分析与转换.md) - 行业Schema分析
- [DSL转换方案与技术分析](../analysis/themes/03-DSL转换方案与技术分析.md) - 转换技术分析

---

## 🎯 最佳实践

### 1. 错误处理

```python
try:
    result = converter.convert_matter_to_zigbee(device)
except ValidationError as e:
    # 处理验证错误
    logger.error(f"验证失败: {str(e)}")
    return {'success': False, 'error': str(e)}
except ConversionError as e:
    # 处理转换错误
    logger.error(f"转换失败: {str(e)}")
    return {'success': False, 'error': str(e)}
```

### 2. 日志记录

```python
# 在关键操作前后记录日志
logger.info(f"开始转换设备: {device_id}")
try:
    result = converter.convert_matter_to_zigbee(device)
    logger.info(f"转换成功: {device_id}")
    return result
except Exception as e:
    logger.error(f"转换失败: {device_id}, 错误: {str(e)}", exc_info=True)
    raise
```

### 3. 性能优化

```python
# 使用缓存减少重复计算
@cached(ttl=300)
def get_device_type_mapping(device_type):
    # 昂贵的计算
    return mapping

# 批量处理数据
def batch_process_devices(devices):
    results = []
    for device in devices:
        result = process_device(device)
        results.append(result)
    return results
```

---

## 📊 统计信息

### 代码统计

- **总代码行数**: 约8,500行
- **核心类数量**: 13个
- **方法数量**: 约200个
- **工具函数**: 20+个
- **单元测试**: 6个测试文件
- **数据库索引**: 25个优化索引

### 功能覆盖

- ✅ 4个核心转换器
- ✅ 4个处理器
- ✅ 4个存储模块
- ✅ 完整的日志系统
- ✅ 完善的错误处理
- ✅ 性能优化机制

---

## 🔄 后续计划

1. **扩展测试**: 为所有模块创建完整的单元测试
2. **性能监控**: 添加性能指标收集和分析
3. **API文档**: 生成完整的API文档
4. **集成测试**: 添加端到端集成测试

---

## 📝 更新日志

### v1.0 (2025-01-21)

- ✅ 所有核心模块完成
- ✅ 日志和错误处理系统
- ✅ 性能优化（索引、缓存）
- ✅ 单元测试框架
- ✅ 完整的文档体系

---

**维护者**: DSL Schema研究团队
**最后更新**: 2025-01-21
