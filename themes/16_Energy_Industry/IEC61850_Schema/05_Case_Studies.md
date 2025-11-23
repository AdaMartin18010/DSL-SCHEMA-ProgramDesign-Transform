# IEC61850 Schema实践案例

## 📑 目录

- [IEC61850 Schema实践案例](#iec61850-schema实践案例)
  - [📑 目录](#-目录)
  - [1. 案例概述](#1-案例概述)
  - [2. 案例1：变电站自动化系统](#2-案例1变电站自动化系统)
    - [2.1 场景描述](#21-场景描述)
    - [2.2 Schema定义](#22-schema定义)
    - [2.3 实现代码](#23-实现代码)
  - [3. 案例2：智能电网数据采集](#3-案例2智能电网数据采集)
    - [3.1 场景描述](#31-场景描述)
    - [3.2 Schema定义](#32-schema定义)
    - [3.3 实现代码](#33-实现代码)
  - [4. 案例3：GOOSE通信实现](#4-案例3goose通信实现)
    - [4.1 场景描述](#41-场景描述)
    - [4.2 实现代码](#42-实现代码)
  - [5. 案例4：SCL配置管理](#5-案例4scl配置管理)
    - [5.1 场景描述](#51-场景描述)
    - [5.2 实现代码](#52-实现代码)
  - [6. 案例5：IEC61850数据分析和监控](#6-案例5iec61850数据分析和监控)
    - [6.1 场景描述](#61-场景描述)
    - [6.2 实现代码](#62-实现代码)

---

## 1. 案例概述

本文档提供IEC61850 Schema在实际应用中的实践案例。

---

## 2. 案例1：变电站自动化系统

### 2.1 场景描述

**业务背景**：
变电站需要实现自动化监控和控制，包括断路器控制、
测量数据采集、保护功能实现等。

**技术挑战**：

- 需要解析SCL配置文件
- 需要实现MMS服务调用
- 需要实时数据采集
- 需要设备控制功能

**解决方案**：
使用SCLParser解析SCL配置，使用MMSClient实现
MMS服务调用，使用IEC61850Storage存储数据。

### 2.2 Schema定义

**变电站自动化Schema**：

```json
{
  "substation_id": "SUB001",
  "substation_name": "220kV变电站",
  "ieds": [
    {
      "ied_name": "IED001",
      "ied_type": "Protection",
      "logical_devices": [
        {
          "ld_inst": "LD0",
          "logical_nodes": [
            {
              "ln_name": "XCBR1",
              "ln_class": "XCBR",
              "data_objects": [
                {
                  "do_name": "Pos",
                  "do_type": "DPC",
                  "data_attributes": [
                    {
                      "da_name": "stVal",
                      "da_type": "Dbpos",
                      "da_fc": "ST"
                    }
                  ]
                }
              ]
            }
          ]
        }
      ]
    }
  ]
}
```

### 2.3 实现代码

**完整的变电站自动化实现**：

```python
from scl_parser import SCLParser, IEDConfigManager
from mms_client import MMSClient, MMSServiceManager
from iec61850_storage import IEC61850Storage

# 初始化组件
storage = IEC61850Storage("postgresql://user:pass@localhost/iec61850")
scl_parser = SCLParser()
ied_manager = IEDConfigManager(scl_parser)
mms_manager = MMSServiceManager(storage)

# 加载SCL配置
scl_file_path = "substation_config.scd"
ied_manager.load_scl_config(scl_file_path)
print(f"Loaded SCL configuration from {scl_file_path}")

# 创建MMS客户端
ied_name = "IED001"
mms_host = "192.168.1.100"
mms_port = 102

if mms_manager.create_client(ied_name, mms_host, mms_port):
    print(f"Created MMS client for {ied_name}")

# 获取逻辑节点列表
logical_nodes = ied_manager.get_logical_nodes(ied_name)
print(f"\nLogical nodes in {ied_name}:")
for ln in logical_nodes:
    print(f"  {ln['ln_name']} ({ln['ln_class']})")

# 读取断路器位置
breaker_pos_var = "IED001/LD0/XCBR1.Pos.stVal"
breaker_pos = mms_manager.read_data_object(ied_name, breaker_pos_var)
if breaker_pos is not None:
    print(f"\nBreaker position: {breaker_pos}")

# 控制断路器
breaker_ctl_var = "IED001/LD0/XCBR1.Pos.ctlVal"
if mms_manager.write_data_object(ied_name, breaker_ctl_var, "on"):
    print(f"Breaker control command sent")

# 存储IED信息
ied_config = ied_manager.get_ied_config(ied_name)
if ied_config:
    storage.store_ied({
        "ied_name": ied_config["ied_name"],
        "ied_desc": ied_config["ied_desc"],
        "ied_type": ied_config["ied_type"],
        "ied_manufacturer": ied_config["ied_manufacturer"],
        "ied_config_version": ied_config["ied_config_version"]
    })
    print(f"\nStored IED information: {ied_name}")

# 存储逻辑节点信息
for ln in logical_nodes:
    storage.store_logical_node({
        "ied_name": ied_name,
        "ld_inst": "LD0",
        "ln_name": ln["ln_name"],
        "ln_class": ln["ln_class"],
        "ln_inst": ln.get("ln_inst"),
        "ln_prefix": ln.get("ln_prefix"),
        "ln_desc": ln.get("ln_desc")
    })

# 查询IED统计信息
stats = storage.get_ied_statistics(ied_name)
print(f"\nIED Statistics:")
print(f"  Logical nodes: {stats['ln_count']}")
print(f"  Data objects: {stats['do_count']}")
print(f"  Total reads: {stats['total_reads']}")
```

---

## 3. 案例2：智能电网数据采集

### 3.1 场景描述

**业务背景**：
智能电网需要实时采集多个IED的测量数据，
包括电压、电流、功率等，用于电网监控和分析。

**技术挑战**：

- 需要同时连接多个IED
- 需要周期性数据采集
- 需要数据存储和分析
- 需要异常检测

**解决方案**：
使用MMSServiceManager管理多个MMS客户端，
实现周期性数据采集，使用IEC61850Storage存储数据。

### 3.2 Schema定义

**智能电网数据采集Schema**：

```json
{
  "grid_id": "GRID001",
  "grid_name": "区域电网",
  "data_collection": {
    "collection_interval": 1,
    "collection_units": "seconds",
    "ieds": [
      {
        "ied_name": "IED001",
        "ied_host": "192.168.1.100",
        "variables": [
          {
            "variable_name": "IED001/LD0/MMXU1.TotW.mag.f",
            "variable_desc": "总功率",
            "variable_unit": "W"
          },
          {
            "variable_name": "IED001/LD0/MMXU1.TotV.mag.f",
            "variable_desc": "总电压",
            "variable_unit": "V"
          }
        ]
      }
    ]
  }
}
```

### 3.3 实现代码

**完整的智能电网数据采集实现**：

```python
from mms_client import MMSServiceManager
from iec61850_storage import IEC61850Storage
import time
from datetime import datetime

# 初始化组件
storage = IEC61850Storage("postgresql://user:pass@localhost/iec61850")
mms_manager = MMSServiceManager(storage)

# 配置数据采集
ieds_config = [
    {
        "ied_name": "IED001",
        "host": "192.168.1.100",
        "port": 102,
        "variables": [
            "IED001/LD0/MMXU1.TotW.mag.f",
            "IED001/LD0/MMXU1.TotV.mag.f",
            "IED001/LD0/MMXU1.TotA.mag.f"
        ]
    },
    {
        "ied_name": "IED002",
        "host": "192.168.1.101",
        "port": 102,
        "variables": [
            "IED002/LD0/MMXU1.TotW.mag.f",
            "IED002/LD0/MMXU1.TotV.mag.f"
        ]
    }
]

# 创建MMS客户端
for ied_config in ieds_config:
    if mms_manager.create_client(
        ied_config["ied_name"],
        ied_config["host"],
        ied_config["port"]
    ):
        print(f"Connected to {ied_config['ied_name']}")

# 周期性数据采集
collection_interval = 1  # 秒
collection_duration = 60  # 秒

start_time = time.time()
while time.time() - start_time < collection_duration:
    for ied_config in ieds_config:
        ied_name = ied_config["ied_name"]

        for variable_name in ied_config["variables"]:
            value = mms_manager.read_data_object(ied_name, variable_name)
            if value is not None:
                print(f"{datetime.now()}: {variable_name} = {value}")

    time.sleep(collection_interval)

print(f"\nData collection completed. Duration: {collection_duration} seconds")

# 查询数据统计
for ied_config in ieds_config:
    stats = storage.get_ied_statistics(ied_config["ied_name"])
    print(f"\n{ied_config['ied_name']} Statistics:")
    print(f"  Total reads: {stats['total_reads']}")
    print(f"  Last read time: {stats['last_read_time']}")
```

---

## 4. 案例3：GOOSE通信实现

### 4.1 场景描述

**业务背景**：
变电站需要实现GOOSE（Generic Object Oriented
Substation Event）通信，用于快速事件传输和保护功能。

**技术挑战**：

- 需要接收GOOSE消息
- 需要解析GOOSE数据
- 需要存储GOOSE消息
- 需要GOOSE消息分析

**解决方案**：
使用GOOSEService实现GOOSE消息接收和解析，
使用IEC61850Storage存储GOOSE消息。

### 4.2 实现代码

**完整的GOOSE通信实现**：

```python
from goose_service import GOOSEService
from iec61850_storage import IEC61850Storage
import threading

# 初始化组件
storage = IEC61850Storage("postgresql://user:pass@localhost/iec61850")
goose_service = GOOSEService(storage)

# 启动GOOSE监听器
goose_service.start_listener("eth0")
print("GOOSE listener started")

# 接收GOOSE消息
def receive_goose_messages():
    message_count = 0
    while message_count < 100:
        goose_msg = goose_service.receive_goose_message()
        if goose_msg:
            message_count += 1
            print(f"Received GOOSE message {message_count}:")
            print(f"  GO CB Ref: {goose_msg.get('go_cb_ref')}")
            print(f"  GO ID: {goose_msg.get('go_id')}")
            print(f"  GO T: {goose_msg.get('go_t')}")

# 在后台线程中接收消息
goose_thread = threading.Thread(target=receive_goose_messages)
goose_thread.daemon = True
goose_thread.start()

# 等待一段时间
import time
time.sleep(60)

# 查询GOOSE消息统计
stats = storage.get_goose_message_statistics(hours=1)
print(f"\nGOOSE Message Statistics (last hour):")
print(f"  Message count: {stats['message_count']}")
print(f"  CB count: {stats['cb_count']}")
print(f"  Average GO T: {stats['avg_go_t']}")
```

---

## 5. 案例4：SCL配置管理

### 5.1 场景描述

**业务背景**：
变电站需要管理SCL配置文件，包括IED配置、
通信配置、数据模型配置等。

**技术挑战**：

- 需要解析SCL文件
- 需要验证SCL配置
- 需要存储SCL配置
- 需要配置版本管理

**解决方案**：
使用SCLParser解析SCL文件，使用IEDConfigManager
管理IED配置，使用IEC61850Storage存储配置信息。

### 5.2 实现代码

**完整的SCL配置管理实现**：

```python
from scl_parser import SCLParser, IEDConfigManager
from iec61850_storage import IEC61850Storage

# 初始化组件
storage = IEC61850Storage("postgresql://user:pass@localhost/iec61850")
scl_parser = SCLParser()
ied_manager = IEDConfigManager(scl_parser)

# 解析SCL文件
scl_file_path = "substation_config.scd"
scl_data = scl_parser.parse_scl_file(scl_file_path)

print(f"Parsed SCL file: {scl_file_path}")
print(f"  Header ID: {scl_data['header'].get('id')}")
print(f"  Header Version: {scl_data['header'].get('version')}")
print(f"  IED count: {len(scl_data['ieds'])}")

# 加载IED配置
ied_manager.load_scl_config(scl_file_path)

# 遍历所有IED
for ied_name in ied_manager.ied_configs.keys():
    ied_config = ied_manager.get_ied_config(ied_name)

    # 存储IED信息
    storage.store_ied({
        "ied_name": ied_config["ied_name"],
        "ied_desc": ied_config["ied_desc"],
        "ied_type": ied_config["ied_type"],
        "ied_manufacturer": ied_config["ied_manufacturer"],
        "ied_config_version": ied_config["ied_config_version"]
    })

    # 获取逻辑节点
    logical_nodes = ied_manager.get_logical_nodes(ied_name)
    print(f"\n{ied_name} Logical Nodes:")
    for ln in logical_nodes:
        print(f"  {ln['ln_name']} ({ln['ln_class']})")

        # 存储逻辑节点
        storage.store_logical_node({
            "ied_name": ied_name,
            "ld_inst": "LD0",
            "ln_name": ln["ln_name"],
            "ln_class": ln["ln_class"],
            "ln_inst": ln.get("ln_inst"),
            "ln_prefix": ln.get("ln_prefix"),
            "ln_desc": ln.get("ln_desc")
        })

        # 获取数据对象
        data_objects = ied_manager.get_data_objects(ied_name, ln["ln_name"])
        print(f"    Data Objects: {len(data_objects)}")
```

---

## 6. 案例5：IEC61850数据分析和监控

### 6.1 场景描述

**业务背景**：
变电站需要实时监控IED状态，分析数据趋势，
检测异常情况，生成监控报表。

**技术挑战**：

- 需要实时数据查询
- 需要数据趋势分析
- 需要异常检测
- 需要报表生成

**解决方案**：
使用IEC61850Storage实现数据查询和分析，
实现数据趋势分析和异常检测功能。

### 6.2 实现代码

**完整的IEC61850数据分析和监控实现**：

```python
from iec61850_storage import IEC61850Storage
from datetime import datetime, timedelta

# 初始化存储
storage = IEC61850Storage("postgresql://user:pass@localhost/iec61850")

# 查询IED统计信息
ied_name = "IED001"
stats = storage.get_ied_statistics(ied_name)
print(f"IED Statistics for {ied_name}:")
print(f"  Logical nodes: {stats['ln_count']}")
print(f"  Data objects: {stats['do_count']}")
print(f"  Data attributes: {stats['da_count']}")
print(f"  Total reads: {stats['total_reads']}")
print(f"  Last read time: {stats['last_read_time']}")

# 查询GOOSE消息统计
goose_stats = storage.get_goose_message_statistics(hours=24)
print(f"\nGOOSE Message Statistics (last 24 hours):")
print(f"  Message count: {goose_stats['message_count']}")
print(f"  CB count: {goose_stats['cb_count']}")
print(f"  Destination count: {goose_stats['dst_count']}")
print(f"  Average GO T: {goose_stats['avg_go_t']}")
print(f"  First message: {goose_stats['first_message']}")
print(f"  Last message: {goose_stats['last_message']}")

# 查询最近的MMS读取记录
storage.cur.execute("""
    SELECT variable_name, value, read_time
    FROM mms_reads
    WHERE ied_name = %s
    ORDER BY read_time DESC
    LIMIT 10
""", (ied_name,))

print(f"\nRecent MMS Reads for {ied_name}:")
for row in storage.cur.fetchall():
    print(f"  {row[0]}: {row[1]} at {row[2]}")

# 查询数据趋势（示例：每小时平均值）
storage.cur.execute("""
    SELECT
        DATE_TRUNC('hour', read_time) as hour,
        COUNT(*) as read_count,
        AVG((value->>'value')::numeric) as avg_value
    FROM mms_reads
    WHERE ied_name = %s
    AND read_time >= CURRENT_TIMESTAMP - INTERVAL '24 hours'
    GROUP BY hour
    ORDER BY hour
""", (ied_name,))

print(f"\nData Trends (hourly average):")
for row in storage.cur.fetchall():
    print(f"  {row[0]}: {row[1]} reads, avg value: {row[2]}")
```

---

**参考文档**：

- `01_Overview.md` - 概述
- `02_Formal_Definition.md` - 形式化定义
- `03_Standards.md` - 标准对标
- `04_Transformation.md` - 转换体系

**创建时间**：2025-01-21
**最后更新**：2025-01-21
