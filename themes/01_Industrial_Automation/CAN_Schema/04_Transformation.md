# CAN协议Schema转换体系

## 📑 目录

- [CAN协议Schema转换体系](#can协议schema转换体系)
  - [📑 目录](#-目录)
  - [1. 转换体系概述](#1-转换体系概述)
    - [1.1 转换方向](#11-转换方向)
    - [1.2 转换维度](#12-转换维度)
  - [2. 七维转换矩阵](#2-七维转换矩阵)
    - [2.1 CAN七维转换矩阵](#21-can七维转换矩阵)
    - [2.2 详细转换规则](#22-详细转换规则)
      - [2.2.1 类型映射](#221-类型映射)
      - [2.2.2 内存布局](#222-内存布局)
      - [2.2.3 控制流](#223-控制流)
  - [3. DBC到代码转换](#3-dbc到代码转换)
    - [3.1 转换函数定义](#31-转换函数定义)
    - [3.2 转换步骤](#32-转换步骤)
      - [步骤1：解析DBC文件](#步骤1解析dbc文件)
      - [步骤2：生成数据结构](#步骤2生成数据结构)
      - [步骤3：生成解析函数](#步骤3生成解析函数)
    - [3.3 转换示例](#33-转换示例)
  - [4. 代码到DBC转换](#4-代码到dbc转换)
    - [4.1 解析函数定义](#41-解析函数定义)
    - [4.2 解析步骤](#42-解析步骤)
      - [步骤1：代码分析](#步骤1代码分析)
      - [步骤2：DBC生成](#步骤2dbc生成)
    - [4.3 解析示例](#43-解析示例)
  - [5. DBC到DBC转换](#5-dbc到dbc转换)
    - [5.1 转换场景](#51-转换场景)
    - [5.2 转换规则](#52-转换规则)
      - [5.2.1 版本升级](#521-版本升级)
      - [5.2.2 格式转换](#522-格式转换)
  - [6. 转换工具链](#6-转换工具链)
    - [6.1 开源工具](#61-开源工具)
      - [6.1.1 cantools](#611-cantools)
      - [6.1.2 canmatrix](#612-canmatrix)
    - [6.2 商业工具](#62-商业工具)
      - [6.2.1 Vector CANoe](#621-vector-canoe)
      - [6.2.2 Peak PCAN](#622-peak-pcan)
    - [6.3 工具对比](#63-工具对比)
  - [7. 转换验证](#7-转换验证)
    - [7.1 验证方法](#71-验证方法)
      - [7.1.1 语法验证](#711-语法验证)
      - [7.1.2 语义验证](#712-语义验证)
      - [7.1.3 等价性验证](#713-等价性验证)
    - [7.2 验证工具](#72-验证工具)
  - [8. CAN数据存储与分析](#8-can数据存储与分析)
    - [8.1 PostgreSQL CAN数据存储](#81-postgresql-can数据存储)
    - [8.2 CAN数据分析查询](#82-can数据分析查询)
  - [9. 实践案例](#9-实践案例)
    - [9.1 案例1：DBC到C代码生成](#91-案例1dbc到c代码生成)
    - [9.2 案例2：多DBC文件合并](#92-案例2多dbc文件合并)

---

## 1. 转换体系概述

CAN Schema转换体系支持多维度、多方向的转换：

### 1.1 转换方向

1. **DBC → 代码**：
   从DBC文件生成代码（C、Rust、Python等）
2. **代码 → DBC**：
   从代码生成DBC文件
3. **DBC → DBC**：
   不同版本DBC文件之间的转换

### 1.2 转换维度

支持**七维转换**：

1. **类型映射**
2. **内存布局**
3. **控制流**
4. **错误模型**
5. **并发原语**
6. **二进制编码**
7. **安全边界**

---

## 2. 七维转换矩阵

### 2.1 CAN七维转换矩阵

| 转换维度 | DBC Schema | C代码 | Rust代码 | Protobuf | SQL |
|---------|-----------|-------|----------|----------|-----|
| **类型映射** | 信号类型 | `struct can_frame` | `struct CanFrame` | `message CanFrame` | 表结构 |
| **内存布局** | 位域定义 | 联合体+位域 | `Array<u8, N>` | `bytes data` | 行存储 |
| **控制流** | 消息发送 | ISR中断 | `async Receiver` | gRPC streaming | 事务 |
| **错误模型** | 错误计数器 | TEC/REC | `Result<Frame>` | `status`码 | 死信队列 |
| **并发原语** | 总线仲裁 | 关中断+自旋锁 | `Mutex<SocketCAN>` | Channel缓冲 | MVCC |
| **二进制编码** | 位流编码 | 原始位流 | `bincode`编码 | Base64 | 压缩编码 |
| **安全边界** | ID过滤器 | 硬件过滤器 | Capability | TLS+ACL | 行级安全 |

### 2.2 详细转换规则

#### 2.2.1 类型映射

**DBC信号类型** → **编程语言类型**：

```text
BOOL → bool / BOOL
UINT8 → uint8_t / u8
UINT16 → uint16_t / u16
UINT32 → uint32_t / u32
INT8 → int8_t / i8
INT16 → int16_t / i16
INT32 → int32_t / i32
FLOAT32 → float / f32
FLOAT64 → double / f64
```

#### 2.2.2 内存布局

**DBC位域定义** → **结构体定义**：

```text
信号起始位 → 结构体字段偏移
信号长度 → 结构体字段大小
字节序 → 结构体字节序
```

#### 2.2.3 控制流

**DBC消息发送** → **代码发送逻辑**：

```text
周期发送 → 定时器触发
事件发送 → 中断触发
条件发送 → 条件判断触发
```

---

## 3. DBC到代码转换

### 3.1 转换函数定义

**定义**：

```text
transform: DBC_Schema → Code
```

### 3.2 转换步骤

#### 步骤1：解析DBC文件

- 解析消息定义
- 解析信号定义
- 解析节点定义
- 解析属性定义

#### 步骤2：生成数据结构

- 生成消息结构体
- 生成信号结构体
- 生成节点枚举

#### 步骤3：生成解析函数

- 生成编码函数
- 生成解码函数
- 生成验证函数

### 3.3 转换示例

**DBC定义**：

```dbc
BO_ 123 EngineSpeed: 8 ECU
 SG_ Speed : 0|16@1+ (0.125,0) [0|8000] "rpm" Node1,Node2
```

**转换后的C代码**：

```c
struct EngineSpeed {
    uint16_t Speed;  // 0-8000 rpm, resolution 0.125
};

void encode_EngineSpeed(struct EngineSpeed* msg, uint8_t* data) {
    data[0] = (msg->Speed >> 0) & 0xFF;
    data[1] = (msg->Speed >> 8) & 0xFF;
}

void decode_EngineSpeed(uint8_t* data, struct EngineSpeed* msg) {
    msg->Speed = (data[1] << 8) | data[0];
    msg->Speed = (uint16_t)(msg->Speed * 0.125);
}
```

---

## 4. 代码到DBC转换

### 4.1 解析函数定义

**定义**：

```text
parse: Code → DBC_Schema
```

### 4.2 解析步骤

#### 步骤1：代码分析

- 分析结构体定义
- 分析函数定义
- 提取类型信息
- 提取位域信息

#### 步骤2：DBC生成

- 生成消息定义
- 生成信号定义
- 生成节点定义

### 4.3 解析示例

**C代码**：

```c
// 原始C代码结构体
struct EngineSpeed {
    uint16_t Speed;        // 注释：发动机速度，单位rpm
    uint8_t SpeedValid;   // 注释：有效性标志
};

// 编码函数（用于推断Schema）
void encode_engine_speed(
    const struct EngineSpeed* src,
    uint8_t* dst)
{
    dst[0] = (uint8_t)(src->Speed & 0xFF);
    dst[1] = (uint8_t)((src->Speed >> 8) & 0xFF);
    dst[2] = src->SpeedValid & 0x01;
}
```

**代码分析过程**：

```python
import ast
import re
from typing import Dict, List

def analyze_c_struct(c_code: str) -> Dict:
    """分析C结构体，提取Schema信息"""
    schema = {
        "messages": [],
        "signals": []
    }

    # 解析结构体定义
    struct_pattern = r'struct\s+(\w+)\s*\{([^}]+)\}'
    matches = re.finditer(struct_pattern, c_code, re.MULTILINE)

    for match in matches:
        struct_name = match.group(1)
        struct_body = match.group(2)

        # 解析字段
        field_pattern = r'(\w+)\s+(\w+);'
        fields = re.finditer(field_pattern, struct_body)

        signals = []
        start_bit = 0

        for field in fields:
            field_type = field.group(1)
            field_name = field.group(2)

            # 推断信号定义
            signal_size = get_type_size(field_type)
            signals.append({
                "name": field_name,
                "type": field_type,
                "start_bit": start_bit,
                "length": signal_size
            })
            start_bit += signal_size

        schema["messages"].append({
            "name": struct_name,
            "signals": signals
        })

    return schema

def get_type_size(c_type: str) -> int:
    """获取C类型大小（位）"""
    type_sizes = {
        "uint8_t": 8,
        "uint16_t": 16,
        "uint32_t": 32,
        "int8_t": 8,
        "int16_t": 16,
        "int32_t": 32,
    }
    return type_sizes.get(c_type, 8)

# 使用示例
c_code = """
struct EngineSpeed {
    uint16_t Speed;
    uint8_t SpeedValid;
};
"""

schema = analyze_c_struct(c_code)
print(f"解析结果: {schema}")
```

**生成的DBC**：

```dbc
VERSION ""

NS_ :
BS_:

BO_ 123 EngineSpeed: 8 ECU
 SG_ Speed : 0|16@1+ (1,0) [0|65535] "rpm" Node1
 SG_ SpeedValid : 16|1@1+ (1,0) [0|1] "" Node1

CM_ BO_ 123 "发动机速度消息";
CM_ SG_ 123 Speed "发动机速度，单位rpm";
CM_ SG_ 123 SpeedValid "有效性标志";
```

---

## 5. DBC到DBC转换

### 5.1 转换场景

1. **版本升级**：旧版本DBC到新版本DBC
2. **格式转换**：不同工具格式之间的转换
3. **合并**：多个DBC文件合并为一个

### 5.2 转换规则

#### 5.2.1 版本升级

**规则**：

- 保留兼容的消息和信号
- 转换不兼容的定义
- 添加新版本特性

#### 5.2.2 格式转换

**规则**：

- 统一消息ID格式
- 统一信号定义格式
- 统一属性定义格式

---

## 6. 转换工具链

### 6.1 开源工具

#### 6.1.1 cantools

- **功能**：DBC文件解析和代码生成
- **语言支持**：C、Python、Rust等
- **特点**：功能完整，易于使用

#### 6.1.2 canmatrix

- **功能**：CAN数据库转换工具
- **格式支持**：DBC、ARXML、XLSX等
- **特点**：支持多种格式转换

### 6.2 商业工具

#### 6.2.1 Vector CANoe

- **功能**：完整的CAN开发环境
- **Schema支持**：DBC、CANdb++格式
- **特点**：功能强大，广泛使用

#### 6.2.2 Peak PCAN

- **功能**：CAN总线分析工具
- **Schema支持**：DBC格式
- **特点**：性价比高

### 6.3 工具对比

| 工具 | DBC支持 | 代码生成 | 转换能力 | 开源 | 成熟度 |
|-----|--------|---------|---------|------|--------|
| **cantools** | ✅ 完整 | ✅ 多语言 | ✅ 强 | ✅ 是 | ⭐⭐⭐⭐ |
| **canmatrix** | ✅ 完整 | ⚠️ 部分 | ✅ 强 | ✅ 是 | ⭐⭐⭐ |
| **CANoe** | ✅ 完整 | ✅ 多语言 | ✅ 强 | ❌ 否 | ⭐⭐⭐⭐⭐ |
| **PCAN** | ✅ 完整 | ⚠️ 部分 | ⚠️ 中 | ❌ 否 | ⭐⭐⭐⭐ |

---

## 7. 转换验证

### 7.1 验证方法

#### 7.1.1 语法验证

- **DBC语法验证**：验证DBC文件语法正确性
- **代码语法验证**：验证生成代码语法正确性

#### 7.1.2 语义验证

- **类型检查**：验证类型正确性
- **范围检查**：验证信号范围正确性
- **引用检查**：验证引用完整性

#### 7.1.3 等价性验证

- **双向转换**：DBC → Code → DBC
- **语义等价**：验证语义一致性

### 7.2 验证工具

- **DBC验证器**：cantools validate
- **代码验证器**：编译器、静态分析工具
- **等价性验证器**：自定义验证脚本

---

## 8. CAN数据存储与分析

### 8.1 PostgreSQL CAN数据存储

**CAN数据存储方案**：

```python
import psycopg2
import json
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass

@dataclass
class CANMessage:
    """CAN消息"""
    can_id: int
    timestamp: datetime
    data: bytes
    dlc: int

@dataclass
class DBCSignal:
    """DBC信号定义"""
    name: str
    start_bit: int
    length: int
    byte_order: str
    value_type: str
    factor: float
    offset: float
    minimum: Optional[float]
    maximum: Optional[float]
    unit: str

class CANDatabaseStorage:
    """CAN数据存储系统"""

    def __init__(self, connection_string: str):
        self.conn = psycopg2.connect(connection_string)
        self.cur = self.conn.cursor()
        self._create_tables()

    def _create_tables(self):
        """创建CAN数据表"""
        # DBC定义表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS dbc_definitions (
                id SERIAL PRIMARY KEY,
                dbc_name VARCHAR(200) UNIQUE NOT NULL,
                version VARCHAR(50),
                definition JSONB NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 消息定义表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS message_definitions (
                id SERIAL PRIMARY KEY,
                dbc_name VARCHAR(200) NOT NULL,
                message_id INTEGER NOT NULL,
                message_name VARCHAR(200) NOT NULL,
                dlc INTEGER NOT NULL,
                signals JSONB NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (dbc_name) REFERENCES dbc_definitions(dbc_name),
                UNIQUE(dbc_name, message_id)
            )
        """)

        # 信号定义表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS signal_definitions (
                id SERIAL PRIMARY KEY,
                dbc_name VARCHAR(200) NOT NULL,
                message_id INTEGER NOT NULL,
                signal_name VARCHAR(200) NOT NULL,
                start_bit INTEGER NOT NULL,
                length INTEGER NOT NULL,
                byte_order VARCHAR(20) NOT NULL,
                value_type VARCHAR(20) NOT NULL,
                factor FLOAT NOT NULL,
                offset FLOAT NOT NULL,
                minimum FLOAT,
                maximum FLOAT,
                unit VARCHAR(50),
                FOREIGN KEY (dbc_name, message_id)
                REFERENCES message_definitions(dbc_name, message_id),
                UNIQUE(dbc_name, message_id, signal_name)
            )
        """)

        # CAN消息日志表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS can_message_logs (
                id BIGSERIAL PRIMARY KEY,
                can_id INTEGER NOT NULL,
                timestamp TIMESTAMP NOT NULL,
                data BYTEA NOT NULL,
                dlc INTEGER NOT NULL,
                decoded_data JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # CAN统计表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS can_statistics (
                id SERIAL PRIMARY KEY,
                can_id INTEGER NOT NULL,
                time_window TIMESTAMP NOT NULL,
                message_count BIGINT NOT NULL,
                avg_interval_ms FLOAT,
                bus_load_percent FLOAT,
                statistics JSONB NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(can_id, time_window)
            )
        """)

        # 创建索引
        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_logs_canid_time
            ON can_message_logs(can_id, timestamp DESC)
        """)
        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_stats_canid_time
            ON can_statistics(can_id, time_window DESC)
        """)

        self.conn.commit()

    def store_dbc_definition(self, dbc_name: str, version: str, definition: Dict):
        """存储DBC定义"""
        self.cur.execute("""
            INSERT INTO dbc_definitions (dbc_name, version, definition)
            VALUES (%s, %s, %s::jsonb)
            ON CONFLICT (dbc_name) DO UPDATE
            SET version = EXCLUDED.version,
                definition = EXCLUDED.definition
        """, (dbc_name, version, json.dumps(definition)))
        self.conn.commit()

    def store_message_definition(self, dbc_name: str, message_id: int,
                                message_name: str, dlc: int, signals: List[DBCSignal]):
        """存储消息定义"""
        signals_json = [{
            'name': s.name,
            'start_bit': s.start_bit,
            'length': s.length,
            'byte_order': s.byte_order,
            'value_type': s.value_type,
            'factor': s.factor,
            'offset': s.offset,
            'minimum': s.minimum,
            'maximum': s.maximum,
            'unit': s.unit
        } for s in signals]

        self.cur.execute("""
            INSERT INTO message_definitions
            (dbc_name, message_id, message_name, dlc, signals)
            VALUES (%s, %s, %s, %s, %s::jsonb)
            ON CONFLICT (dbc_name, message_id) DO UPDATE
            SET message_name = EXCLUDED.message_name,
                dlc = EXCLUDED.dlc,
                signals = EXCLUDED.signals
        """, (dbc_name, message_id, message_name, dlc, json.dumps(signals_json)))

        # 存储信号定义
        for signal in signals:
            self.cur.execute("""
                INSERT INTO signal_definitions
                (dbc_name, message_id, signal_name, start_bit, length,
                 byte_order, value_type, factor, offset, minimum, maximum, unit)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (dbc_name, message_id, signal_name) DO UPDATE
                SET start_bit = EXCLUDED.start_bit,
                    length = EXCLUDED.length,
                    byte_order = EXCLUDED.byte_order,
                    value_type = EXCLUDED.value_type,
                    factor = EXCLUDED.factor,
                    offset = EXCLUDED.offset,
                    minimum = EXCLUDED.minimum,
                    maximum = EXCLUDED.maximum,
                    unit = EXCLUDED.unit
            """, (dbc_name, message_id, signal.name, signal.start_bit,
                  signal.length, signal.byte_order, signal.value_type,
                  signal.factor, signal.offset, signal.minimum,
                  signal.maximum, signal.unit))

        self.conn.commit()

    def store_message_logs_batch(self, messages: List[CANMessage],
                                decoder_func=None):
        """批量存储CAN消息日志"""
        for msg in messages:
            decoded_data = None
            if decoder_func:
                decoded_data = decoder_func(msg)

            self.cur.execute("""
                INSERT INTO can_message_logs
                (can_id, timestamp, data, dlc, decoded_data)
                VALUES (%s, %s, %s, %s, %s::jsonb)
            """, (msg.can_id, msg.timestamp, msg.data, msg.dlc,
                  json.dumps(decoded_data) if decoded_data else None))

        self.conn.commit()

    def calculate_statistics(self, can_id: int,
                            time_window: timedelta = timedelta(minutes=1)) -> Dict:
        """计算CAN消息统计信息"""
        end_time = datetime.utcnow()
        start_time = end_time - time_window

        self.cur.execute("""
            SELECT
                COUNT(*) as message_count,
                AVG(EXTRACT(EPOCH FROM (timestamp - LAG(timestamp)
                    OVER (ORDER BY timestamp))) * 1000) as avg_interval_ms
            FROM can_message_logs
            WHERE can_id = %s
              AND timestamp >= %s
              AND timestamp <= %s
        """, (can_id, start_time, end_time))

        stats = self.cur.fetchone()

        message_count = stats[0] if stats[0] else 0
        avg_interval_ms = float(stats[1]) if stats[1] else 0

        # 计算总线负载（假设500kbps）
        bus_load = (message_count * 8 * 8) / (500000 * time_window.total_seconds()) * 100

        statistics = {
            'message_count': message_count,
            'avg_interval_ms': avg_interval_ms,
            'bus_load_percent': bus_load
        }

        # 存储统计结果
        self.cur.execute("""
            INSERT INTO can_statistics
            (can_id, time_window, message_count, avg_interval_ms, bus_load_percent, statistics)
            VALUES (%s, %s, %s, %s, %s, %s::jsonb)
            ON CONFLICT (can_id, time_window) DO UPDATE
            SET message_count = EXCLUDED.message_count,
                avg_interval_ms = EXCLUDED.avg_interval_ms,
                bus_load_percent = EXCLUDED.bus_load_percent,
                statistics = EXCLUDED.statistics
        """, (can_id, end_time, message_count, avg_interval_ms,
              bus_load, json.dumps(statistics)))
        self.conn.commit()

        return statistics

    def close(self):
        """关闭连接"""
        self.cur.close()
        self.conn.close()
```

### 8.2 CAN数据分析查询

**CAN数据分析查询功能**：

```python
class CANDataAnalyzer:
    """CAN数据分析器"""

    def __init__(self, storage: CANDatabaseStorage):
        self.storage = storage
        self.cur = storage.cur
        self.conn = storage.conn

    def analyze_message_frequency(self, can_id: int,
                                 time_window: timedelta) -> Dict:
        """分析消息频率"""
        end_time = datetime.utcnow()
        start_time = end_time - time_window

        self.cur.execute("""
            SELECT
                COUNT(*) as total_messages,
                MIN(timestamp) as first_message,
                MAX(timestamp) as last_message,
                COUNT(*) / EXTRACT(EPOCH FROM (%s - %s)) as messages_per_second
            FROM can_message_logs
            WHERE can_id = %s
              AND timestamp >= %s
              AND timestamp <= %s
        """, (end_time, start_time, can_id, start_time, end_time))

        result = self.cur.fetchone()
        return {
            'total_messages': result[0],
            'first_message': result[1],
            'last_message': result[2],
            'messages_per_second': float(result[3]) if result[3] else 0
        }

    def analyze_bus_load(self, time_window: timedelta) -> Dict:
        """分析总线负载"""
        end_time = datetime.utcnow()
        start_time = end_time - time_window

        self.cur.execute("""
            SELECT
                can_id,
                COUNT(*) as message_count,
                COUNT(*) * 8 * 8 / EXTRACT(EPOCH FROM (%s - %s)) / 500000 * 100 as load_percent
            FROM can_message_logs
            WHERE timestamp >= %s
              AND timestamp <= %s
            GROUP BY can_id
            ORDER BY load_percent DESC
        """, (end_time, start_time, start_time, end_time))

        results = []
        for row in self.cur.fetchall():
            results.append({
                'can_id': row[0],
                'message_count': row[1],
                'load_percent': float(row[2]) if row[2] else 0
            })

        return {'bus_loads': results}

    def detect_anomalies(self, can_id: int,
                        expected_interval_ms: float,
                        tolerance: float = 0.2) -> List[Dict]:
        """检测异常消息间隔"""
        self.cur.execute("""
            WITH intervals AS (
                SELECT
                    timestamp,
                    EXTRACT(EPOCH FROM (timestamp - LAG(timestamp)
                        OVER (ORDER BY timestamp))) * 1000 as interval_ms
                FROM can_message_logs
                WHERE can_id = %s
                ORDER BY timestamp DESC
                LIMIT 1000
            )
            SELECT timestamp, interval_ms
            FROM intervals
            WHERE interval_ms IS NOT NULL
              AND (interval_ms < %s OR interval_ms > %s)
        """, (can_id, expected_interval_ms * (1 - tolerance),
              expected_interval_ms * (1 + tolerance)))

        anomalies = []
        for row in self.cur.fetchall():
            anomalies.append({
                'timestamp': row[0],
                'interval_ms': float(row[1]) if row[1] else 0
            })

        return anomalies
```

---

## 9. 实践案例

### 9.1 案例1：DBC到C代码生成

**场景**：从DBC文件生成C代码用于嵌入式开发

**步骤**：

1. 使用cantools解析DBC文件
2. 生成C结构体定义
3. 生成编码/解码函数
4. 集成到嵌入式项目

**结果**：成功生成可用的C代码

### 9.2 案例2：多DBC文件合并

**场景**：将多个DBC文件合并为一个统一文件

**步骤**：

1. 解析所有DBC文件
2. 合并消息定义
3. 解决冲突
4. 生成统一DBC文件

**挑战**：消息ID冲突、信号定义冲突

---

**参考文档**：

- `01_Overview.md` - 概述
- `02_Formal_Definition.md` - 形式化定义
- `03_Standards.md` - 标准对标
- `05_Case_Studies.md` - 实践案例（包含数据存储案例）

**创建时间**：2025-01-21
**最后更新**：2025-01-21（扩展CAN数据存储和分析功能，新增PostgreSQL存储方案）
