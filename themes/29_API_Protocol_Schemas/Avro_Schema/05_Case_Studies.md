# Avro Schema实践案例

## 📑 目录

- [Avro Schema实践案例](#avro-schema实践案例)
  - [📑 目录](#-目录)
  - [1. 案例概述](#1-案例概述)
  - [2. 案例1：大数据平台数据序列化优化](#2-案例1大数据平台数据序列化优化)
    - [2.1 企业背景](#21-企业背景)
    - [2.2 业务痛点](#22-业务痛点)
    - [2.3 业务目标](#23-业务目标)
    - [2.4 技术挑战](#24-技术挑战)
    - [2.5 完整代码实现](#25-完整代码实现)
    - [2.6 效果评估与ROI](#26-效果评估与roi)

---

## 2. 案例1：大数据平台数据序列化优化

### 2.1 企业背景

**企业概况**：
"数智云科"（化名）是领先的大数据服务提供商，日均处理数据量超过500TB，服务于100+企业客户。公司大数据平台每天处理超过100亿条日志记录。

### 2.2 业务痛点

1. **JSON序列化性能瓶颈**
   - 数据体积大，网络传输成本高
   - 序列化/反序列化CPU占用高
   - 存储成本居高不下

2. **Schema管理混乱**
   - 数据格式频繁变化，兼容性问题多
   - 缺乏统一的Schema注册中心
   - 版本管理困难

3. **跨语言兼容性差**
   - Java、Python、Go服务间数据交换困难
   - 需要编写大量的数据转换代码
   - 容易出错且维护成本高

### 2.3 业务目标

1. **性能提升**
   - 序列化体积减少50%以上
   - 序列化速度提升3倍
   - 存储成本降低40%

2. **Schema管理**
   - 建立统一的Schema Registry
   - 实现Schema自动演进
   - 向后/向前兼容性保证

3. **跨语言支持**
   - 支持Java、Python、Go、Scala
   - 自动生成多语言代码
   - 统一的数据模型

### 2.4 技术挑战

1. **大数据量处理**
   - 日处理100亿+条记录
   - 峰值QPS超过100万
   - 需要流式处理能力

2. **Schema演进**
   - 新增/删除字段的处理
   - 字段类型变更的兼容性
   - 多版本Schema共存

3. **性能优化**
   - 内存使用优化
   - 批处理优化
   - 压缩算法选择

### 2.5 完整代码实现

```python
#!/usr/bin/env python3
"""
Avro Schema完整实现
数智云科大数据平台序列化系统
"""

import json
import fastavro
from fastavro import parse_schema, schemaless_writer, schemaless_reader
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from io import BytesIO
import hashlib
from datetime import datetime
import struct


class AvroSchemaManager:
    """Avro Schema管理器"""
    
    def __init__(self, registry_url: Optional[str] = None):
        self.schemas: Dict[str, Dict] = {}
        self.parsed_schemas: Dict[str, Any] = {}
        self.registry_url = registry_url
        
    def register_schema(self, name: str, schema: Dict, version: str = "1.0"):
        """注册Schema"""
        schema_id = f"{name}:{version}"
        self.schemas[schema_id] = schema
        self.parsed_schemas[schema_id] = parse_schema(schema)
        return schema_id
    
    def get_schema(self, name: str, version: str = "1.0") -> Optional[Dict]:
        """获取Schema"""
        schema_id = f"{name}:{version}"
        return self.schemas.get(schema_id)
    
    def get_parsed_schema(self, name: str, version: str = "1.0"):
        """获取解析后的Schema"""
        schema_id = f"{name}:{version}"
        return self.parsed_schemas.get(schema_id)


# 用户行为日志 Schema
user_behavior_schema = {
    "type": "record",
    "name": "UserBehavior",
    "namespace": "com.shuzhi",
    "fields": [
        {"name": "event_id", "type": "string"},
        {"name": "user_id", "type": "string"},
        {"name": "event_type", "type": "string"},
        {"name": "timestamp", "type": "long"},
        {"name": "properties", "type": {"type": "map", "values": "string"}, "default": {}},
        {"name": "device_info", "type": {
            "type": "record",
            "name": "DeviceInfo",
            "fields": [
                {"name": "device_id", "type": "string"},
                {"name": "os", "type": "string"},
                {"name": "app_version", "type": "string"}
            ]
        }},
        {"name": "location", "type": ["null", {
            "type": "record",
            "name": "Location",
            "fields": [
                {"name": "lat", "type": "double"},
                {"name": "lon", "type": "double"}
            ]
        }], "default": None}
    ]
}


# 交易记录 Schema（支持Schema演进）
transaction_schema_v1 = {
    "type": "record",
    "name": "Transaction",
    "namespace": "com.shuzhi",
    "fields": [
        {"name": "transaction_id", "type": "string"},
        {"name": "user_id", "type": "string"},
        {"name": "amount", "type": "double"},
        {"name": "currency", "type": "string"},
        {"name": "status", "type": "string"},
        {"name": "created_at", "type": "long"}
    ]
}

# V2版本：新增字段（带默认值，保证向后兼容）
transaction_schema_v2 = {
    "type": "record",
    "name": "Transaction",
    "namespace": "com.shuzhi",
    "fields": [
        {"name": "transaction_id", "type": "string"},
        {"name": "user_id", "type": "string"},
        {"name": "amount", "type": "double"},
        {"name": "currency", "type": "string"},
        {"name": "status", "type": "string"},
        {"name": "created_at", "type": "long"},
        {"name": "merchant_id", "type": ["null", "string"], "default": None},  # 新增
        {"name": "discount_amount", "type": ["null", "double"], "default": None}  # 新增
    ]
}


class AvroSerializer:
    """Avro序列化器"""
    
    def __init__(self, schema_manager: AvroSchemaManager):
        self.schema_manager = schema_manager
    
    def serialize(self, data: Dict, schema_name: str, version: str = "1.0") -> bytes:
        """序列化数据"""
        schema = self.schema_manager.get_parsed_schema(schema_name, version)
        if not schema:
            raise ValueError(f"Schema not found: {schema_name}:{version}")
        
        buf = BytesIO()
        schemaless_writer(buf, schema, data)
        return buf.getvalue()
    
    def deserialize(self, data: bytes, schema_name: str, version: str = "1.0") -> Dict:
        """反序列化数据"""
        schema = self.schema_manager.get_parsed_schema(schema_name, version)
        if not schema:
            raise ValueError(f"Schema not found: {schema_name}:{version}")
        
        buf = BytesIO(data)
        return schemaless_reader(buf, schema)
    
    def serialize_with_schema_id(self, data: Dict, schema_id: str) -> bytes:
        """带Schema ID的序列化（用于Schema Registry）"""
        schema = self.schema_manager.get_parsed_schema_by_id(schema_id)
        
        buf = BytesIO()
        # 写入Schema ID（8字节）
        buf.write(struct.pack('>Q', int(schema_id)))
        # 写入数据
        schemaless_writer(buf, schema, data)
        return buf.getvalue()


class AvroBatchProcessor:
    """Avro批处理器"""
    
    def __init__(self, serializer: AvroSerializer, batch_size: int = 1000):
        self.serializer = serializer
        self.batch_size = batch_size
        self.batch: List[bytes] = []
    
    def add_record(self, data: Dict, schema_name: str, version: str = "1.0"):
        """添加记录"""
        serialized = self.serializer.serialize(data, schema_name, version)
        self.batch.append(serialized)
        
        if len(self.batch) >= self.batch_size:
            self.flush()
    
    def flush(self):
        """刷新批次"""
        if not self.batch:
            return
        
        # 实际实现会写入Kafka/HDFS等
        print(f"Flushing {len(self.batch)} records")
        self.batch = []


# 使用示例
def main():
    # 创建Schema管理器
    schema_manager = AvroSchemaManager()
    schema_manager.register_schema("UserBehavior", user_behavior_schema, "1.0")
    schema_manager.register_schema("Transaction", transaction_schema_v1, "1.0")
    schema_manager.register_schema("Transaction", transaction_schema_v2, "2.0")
    
    # 创建序列化器
    serializer = AvroSerializer(schema_manager)
    
    # 示例数据
    user_behavior = {
        "event_id": "evt_123456",
        "user_id": "usr_789",
        "event_type": "click",
        "timestamp": int(datetime.now().timestamp() * 1000),
        "properties": {"page": "home", "button": "buy"},
        "device_info": {
            "device_id": "dev_abc123",
            "os": "iOS 17",
            "app_version": "3.5.0"
        },
        "location": {
            "lat": 39.9042,
            "lon": 116.4074
        }
    }
    
    # 序列化
    serialized = serializer.serialize(user_behavior, "UserBehavior", "1.0")
    print(f"Avro序列化后大小: {len(serialized)} bytes")
    
    # JSON对比
    json_bytes = json.dumps(user_behavior).encode('utf-8')
    print(f"JSON序列化后大小: {len(json_bytes)} bytes")
    print(f"压缩比: {len(json_bytes) / len(serialized):.2f}x")
    
    # 反序列化
    deserialized = serializer.deserialize(serialized, "UserBehavior", "1.0")
    print(f"反序列化结果: {deserialized['event_id']}")


if __name__ == '__main__':
    main()
```

### 2.6 效果评估与ROI

| 指标 | 改进前(JSON) | 改进后(Avro) | 提升幅度 |
|------|-------------|-------------|----------|
| 数据体积 | 100% | 35% | 65%减少 |
| 序列化速度 | 基准 | 3.5倍 | 250%提升 |
| 反序列化速度 | 基准 | 4倍 | 300%提升 |
| 存储成本 | 100% | 40% | 60%降低 |
| 网络带宽 | 100% | 35% | 65%节省 |

**ROI计算**：

```
项目投资：180万元
年度收益：680万元
  - 存储成本节省：380万元
  - 网络成本节省：180万元
  - 计算资源节省：120万元

第一年ROI = (680 - 180) / 180 = 278%
```

---

**创建时间**：2025-01-21
**最后更新**：2025-02-15
