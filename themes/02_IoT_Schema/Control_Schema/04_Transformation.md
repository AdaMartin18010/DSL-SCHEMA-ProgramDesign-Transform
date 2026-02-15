# IoT控制Schema转换体系

## 📑 目录

- [IoT控制Schema转换体系](#iot控制schema转换体系)
  - [📑 目录](#-目录)
  - [1. 转换体系概述](#1-转换体系概述)
  - [2. 控制逻辑转换](#2-控制逻辑转换)
    - [2.1 采样控制转换](#21-采样控制转换)
    - [2.2 参数配置转换](#22-参数配置转换)
    - [2.3 事件管理转换](#23-事件管理转换)
    - [2.4 状态机转换](#24-状态机转换)
  - [3. 转换实例](#3-转换实例)
  - [4. 转换工具](#4-转换工具)
  - [5. 转换验证](#5-转换验证)
  - [6. 控制数据存储与分析](#6-控制数据存储与分析)
    - [6.1 PostgreSQL控制数据存储](#61-postgresql控制数据存储)
    - [6.2 控制数据分析查询](#62-控制数据分析查询)
  - [7. 参考文献](#7-参考文献)
    - [7.1 标准文档](#71-标准文档)
    - [7.2 技术文档](#72-技术文档)
    - [7.3 在线资源](#73-在线资源)

---

## 1. 转换体系概述

IoT控制Schema转换体系支持将控制Schema
转换为多种编程语言的控制代码。

**转换目标**：

1. **Python**：异步控制代码
2. **Rust**：实时控制代码
3. **C/C++**：嵌入式控制代码
4. **JavaScript**：Web控制代码

---

## 2. 控制逻辑转换

### 2.1 采样控制转换

**Schema到Python转换**：

```python
import asyncio

class SamplingController:
    """采样控制器"""

    def __init__(self, frequency: float, mode: str):
        self.frequency = frequency
        self.mode = mode
        self.interval = 1.0 / frequency

    async def continuous_sampling(self, sensor_read_func):
        """连续采样"""
        while True:
            data = await sensor_read_func()
            await self.process_data(data)
            await asyncio.sleep(self.interval)

    async def triggered_sampling(self, trigger_func, sensor_read_func):
        """触发采样"""
        while True:
            if await trigger_func():
                data = await sensor_read_func()
                await self.process_data(data)
```

### 2.2 参数配置转换

**Schema到Python转换**：

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class ParameterConfig:
    """参数配置"""
    temperature_threshold: float = 25.0
    humidity_threshold: float = 60.0
    sampling_rate: float = 1.0

    def validate(self):
        """验证参数"""
        if not (0.0 <= self.temperature_threshold <= 100.0):
            raise ValueError("Temperature threshold out of range")
        if not (0.0 <= self.humidity_threshold <= 100.0):
            raise ValueError("Humidity threshold out of range")
```

### 2.3 事件管理转换

**Schema到Python转换**：

```python
from enum import Enum
from typing import Callable, List

class EventType(Enum):
    ALARM = "alarm"
    WARNING = "warning"
    INFO = "info"

class EventManager:
    """事件管理器"""

    def __init__(self):
        self.handlers = {}

    def register_handler(self, event_type: EventType, handler: Callable):
        """注册事件处理器"""
        if event_type not in self.handlers:
            self.handlers[event_type] = []
        self.handlers[event_type].append(handler)

    async def trigger_event(self, event_type: EventType, data: dict):
        """触发事件"""
        if event_type in self.handlers:
            for handler in self.handlers[event_type]:
                await handler(data)
```

### 2.4 状态机转换

**Schema到Python转换**：

```python
from enum import Enum
from typing import Optional, Callable

class State(Enum):
    IDLE = "idle"
    RUNNING = "running"
    ERROR = "error"

class StateMachine:
    """状态机"""

    def __init__(self, initial_state: State):
        self.current_state = initial_state
        self.transitions = {}
        self.state_actions = {}

    def add_transition(self, source: State, target: State,
                      condition: Optional[Callable] = None,
                      action: Optional[Callable] = None):
        """添加状态转换"""
        if source not in self.transitions:
            self.transitions[source] = []
        self.transitions[source].append({
            'target': target,
            'condition': condition,
            'action': action
        })

    async def transition(self, event: Optional[dict] = None):
        """执行状态转换"""
        if self.current_state in self.transitions:
            for transition in self.transitions[self.current_state]:
                if transition['condition'] is None or transition['condition'](event):
                    if transition['action']:
                        await transition['action'](event)
                    self.current_state = transition['target']
                    break
```

---

## 3. 转换实例

**完整控制Schema转换示例**：

```python
# Schema定义的控制逻辑转换为Python代码
class IoTDeviceController:
    """IoT设备控制器"""

    def __init__(self, config: ParameterConfig):
        self.config = config
        self.sampling_controller = SamplingController(
            config.sampling_rate,
            "continuous"
        )
        self.event_manager = EventManager()
        self.state_machine = StateMachine(State.IDLE)

    async def run(self):
        """主控制循环"""
        await self.sampling_controller.continuous_sampling(
            self.read_sensors
        )
```

---

## 4. 转换工具

**工具列表**：

1. **代码生成器**：从Schema生成控制代码
2. **验证工具**：验证控制逻辑正确性
3. **仿真工具**：仿真控制逻辑执行

---

## 5. 转换验证

**验证方法**：

1. **语法验证**：验证代码语法
2. **语义验证**：验证控制逻辑语义
3. **实时性验证**：验证实时性要求

---

## 6. 控制数据存储与分析

### 6.1 PostgreSQL控制数据存储

**IoT控制逻辑数据存储方案**：

```python
import psycopg2
import json
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass

@dataclass
class ControlEvent:
    """控制事件"""
    device_id: str
    event_type: str
    event_data: Dict
    timestamp: datetime

@dataclass
class StateMachineState:
    """状态机状态"""
    device_id: str
    state_name: str
    previous_state: str
    transition_trigger: str
    timestamp: datetime

class IoTControlStorage:
    """IoT控制数据存储系统"""

    def __init__(self, connection_string: str):
        self.conn = psycopg2.connect(connection_string)
        self.cur = self.conn.cursor()
        self._create_tables()

    def _create_tables(self):
        """创建控制数据表"""
        # 控制配置表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS control_configs (
                id SERIAL PRIMARY KEY,
                device_id VARCHAR(200) NOT NULL,
                control_type VARCHAR(50) NOT NULL,
                configuration JSONB NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(device_id, control_type)
            )
        """)

        # 采样控制记录表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS sampling_controls (
                id BIGSERIAL PRIMARY KEY,
                device_id VARCHAR(200) NOT NULL,
                frequency FLOAT NOT NULL,
                mode VARCHAR(50) NOT NULL,
                sample_count INTEGER DEFAULT 0,
                last_sample_time TIMESTAMP,
                status VARCHAR(50) DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 状态机状态表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS state_machine_states (
                id BIGSERIAL PRIMARY KEY,
                device_id VARCHAR(200) NOT NULL,
                state_name VARCHAR(200) NOT NULL,
                previous_state VARCHAR(200),
                transition_trigger VARCHAR(200),
                timestamp TIMESTAMP NOT NULL,
                duration_ms INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 控制事件表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS control_events (
                id BIGSERIAL PRIMARY KEY,
                device_id VARCHAR(200) NOT NULL,
                event_type VARCHAR(100) NOT NULL,
                event_data JSONB NOT NULL,
                timestamp TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 参数配置历史表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS parameter_configs (
                id BIGSERIAL PRIMARY KEY,
                device_id VARCHAR(200) NOT NULL,
                parameter_name VARCHAR(200) NOT NULL,
                parameter_value TEXT NOT NULL,
                parameter_type VARCHAR(50) NOT NULL,
                timestamp TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 控制统计表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS control_statistics (
                id SERIAL PRIMARY KEY,
                device_id VARCHAR(200) NOT NULL,
                statistic_type VARCHAR(50) NOT NULL,
                time_window TIMESTAMP NOT NULL,
                statistics JSONB NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(device_id, statistic_type, time_window)
            )
        """)

        # 创建索引
        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_states_device_time
            ON state_machine_states(device_id, timestamp DESC)
        """)
        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_events_device_type_time
            ON control_events(device_id, event_type, timestamp DESC)
        """)
        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_params_device_name_time
            ON parameter_configs(device_id, parameter_name, timestamp DESC)
        """)

        self.conn.commit()

    def store_control_config(self, device_id: str, control_type: str,
                            configuration: Dict):
        """存储控制配置"""
        self.cur.execute("""
            INSERT INTO control_configs
            (device_id, control_type, configuration)
            VALUES (%s, %s, %s::jsonb)
            ON CONFLICT (device_id, control_type) DO UPDATE
            SET configuration = EXCLUDED.configuration,
                updated_at = CURRENT_TIMESTAMP
        """, (device_id, control_type, json.dumps(configuration)))
        self.conn.commit()

    def store_sampling_control(self, device_id: str, frequency: float,
                              mode: str, sample_count: int = 0,
                              last_sample_time: datetime = None,
                              status: str = 'active'):
        """存储采样控制记录"""
        self.cur.execute("""
            INSERT INTO sampling_controls
            (device_id, frequency, mode, sample_count, last_sample_time, status)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT DO NOTHING
        """, (device_id, frequency, mode, sample_count,
              last_sample_time, status))
        self.conn.commit()

    def store_state_transition(self, state: StateMachineState,
                              duration_ms: int = None):
        """存储状态转换"""
        self.cur.execute("""
            INSERT INTO state_machine_states
            (device_id, state_name, previous_state, transition_trigger,
             timestamp, duration_ms)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (state.device_id, state.state_name, state.previous_state,
              state.transition_trigger, state.timestamp, duration_ms))
        self.conn.commit()

    def store_control_event(self, event: ControlEvent):
        """存储控制事件"""
        self.cur.execute("""
            INSERT INTO control_events
            (device_id, event_type, event_data, timestamp)
            VALUES (%s, %s, %s::jsonb, %s)
        """, (event.device_id, event.event_type,
              json.dumps(event.event_data), event.timestamp))
        self.conn.commit()

    def store_parameter_config(self, device_id: str, parameter_name: str,
                              parameter_value: any, parameter_type: str,
                              timestamp: datetime = None):
        """存储参数配置"""
        if timestamp is None:
            timestamp = datetime.utcnow()

        self.cur.execute("""
            INSERT INTO parameter_configs
            (device_id, parameter_name, parameter_value, parameter_type, timestamp)
            VALUES (%s, %s, %s, %s, %s)
        """, (device_id, parameter_name, str(parameter_value),
              parameter_type, timestamp))
        self.conn.commit()

    def get_state_history(self, device_id: str,
                        start_time: datetime = None,
                        end_time: datetime = None,
                        limit: int = 1000) -> List[Dict]:
        """获取状态历史"""
        query = """
            SELECT state_name, previous_state, transition_trigger,
                   timestamp, duration_ms
            FROM state_machine_states
            WHERE device_id = %s
        """
        params = [device_id]

        if start_time:
            query += " AND timestamp >= %s"
            params.append(start_time)

        if end_time:
            query += " AND timestamp <= %s"
            params.append(end_time)

        query += " ORDER BY timestamp DESC LIMIT %s"
        params.append(limit)

        self.cur.execute(query, params)
        results = []
        for row in self.cur.fetchall():
            results.append({
                'state_name': row[0],
                'previous_state': row[1],
                'transition_trigger': row[2],
                'timestamp': row[3],
                'duration_ms': row[4]
            })
        return results

    def get_control_events(self, device_id: str = None,
                          event_type: str = None,
                          start_time: datetime = None,
                          end_time: datetime = None,
                          limit: int = 1000) -> List[Dict]:
        """获取控制事件"""
        query = """
            SELECT device_id, event_type, event_data, timestamp
            FROM control_events
            WHERE 1=1
        """
        params = []

        if device_id:
            query += " AND device_id = %s"
            params.append(device_id)

        if event_type:
            query += " AND event_type = %s"
            params.append(event_type)

        if start_time:
            query += " AND timestamp >= %s"
            params.append(start_time)

        if end_time:
            query += " AND timestamp <= %s"
            params.append(end_time)

        query += " ORDER BY timestamp DESC LIMIT %s"
        params.append(limit)

        self.cur.execute(query, params)
        results = []
        for row in self.cur.fetchall():
            results.append({
                'device_id': row[0],
                'event_type': row[1],
                'event_data': row[2],
                'timestamp': row[3]
            })
        return results

    def calculate_statistics(self, device_id: str,
                            time_window: timedelta = timedelta(hours=1)) -> Dict:
        """计算控制统计信息"""
        end_time = datetime.utcnow()
        start_time = end_time - time_window

        # 状态转换统计
        self.cur.execute("""
            SELECT
                COUNT(*) as transition_count,
                COUNT(DISTINCT state_name) as unique_states,
                AVG(duration_ms) as avg_duration_ms
            FROM state_machine_states
            WHERE device_id = %s
              AND timestamp >= %s
              AND timestamp <= %s
        """, (device_id, start_time, end_time))

        state_stats = self.cur.fetchone()

        # 事件统计
        self.cur.execute("""
            SELECT
                COUNT(*) as event_count,
                COUNT(DISTINCT event_type) as unique_event_types
            FROM control_events
            WHERE device_id = %s
              AND timestamp >= %s
              AND timestamp <= %s
        """, (device_id, start_time, end_time))

        event_stats = self.cur.fetchone()

        statistics = {
            'state_transitions': {
                'count': state_stats[0] if state_stats[0] else 0,
                'unique_states': state_stats[1] if state_stats[1] else 0,
                'avg_duration_ms': float(state_stats[2]) if state_stats[2] else 0
            },
            'events': {
                'count': event_stats[0] if event_stats[0] else 0,
                'unique_types': event_stats[1] if event_stats[1] else 0
            }
        }

        # 存储统计结果
        self.cur.execute("""
            INSERT INTO control_statistics
            (device_id, statistic_type, time_window, statistics)
            VALUES (%s, %s, %s, %s::jsonb)
            ON CONFLICT (device_id, statistic_type, time_window) DO UPDATE
            SET statistics = EXCLUDED.statistics
        """, (device_id, 'control_statistics', end_time,
              json.dumps(statistics)))
        self.conn.commit()

        return statistics

    def analyze_state_patterns(self, device_id: str,
                              time_window: timedelta = timedelta(hours=24)) -> Dict:
        """分析状态模式"""
        end_time = datetime.utcnow()
        start_time = end_time - time_window

        # 状态频率分析
        self.cur.execute("""
            SELECT
                state_name,
                COUNT(*) as frequency,
                AVG(duration_ms) as avg_duration_ms,
                MIN(duration_ms) as min_duration_ms,
                MAX(duration_ms) as max_duration_ms
            FROM state_machine_states
            WHERE device_id = %s
              AND timestamp >= %s
              AND timestamp <= %s
            GROUP BY state_name
            ORDER BY frequency DESC
        """, (device_id, start_time, end_time))

        patterns = []
        for row in self.cur.fetchall():
            patterns.append({
                'state_name': row[0],
                'frequency': row[1],
                'avg_duration_ms': float(row[2]) if row[2] else 0,
                'min_duration_ms': row[3],
                'max_duration_ms': row[4]
            })

        return {
            'device_id': device_id,
            'time_window': time_window,
            'patterns': patterns,
            'total_transitions': sum(p['frequency'] for p in patterns)
        }

    def close(self):
        """关闭连接"""
        self.cur.close()
        self.conn.close()

# 使用示例
if __name__ == "__main__":
    storage = IoTControlStorage(
        "postgresql://user:password@localhost/iot_control_db"
    )

    # 存储控制配置
    storage.store_control_config(
        device_id="device_001",
        control_type="sampling",
        configuration={
            "frequency": 10.0,
            "mode": "continuous",
            "threshold": 0.1
        }
    )

    # 存储状态转换
    state = StateMachineState(
        device_id="device_001",
        state_name="running",
        previous_state="idle",
        transition_trigger="start_command",
        timestamp=datetime.utcnow()
    )
    storage.store_state_transition(state, duration_ms=100)

    # 存储控制事件
    event = ControlEvent(
        device_id="device_001",
        event_type="threshold_exceeded",
        event_data={"value": 25.5, "threshold": 25.0},
        timestamp=datetime.utcnow()
    )
    storage.store_control_event(event)

    # 计算统计信息
    stats = storage.calculate_statistics("device_001")
    print(f"统计信息: {stats}")

    # 分析状态模式
    patterns = storage.analyze_state_patterns("device_001")
    print(f"状态模式: {patterns}")

    storage.close()
```

### 6.2 控制数据分析查询

**高级分析查询**：

```python
class IoTControlAnalyzer:
    """IoT控制数据分析器"""

    def __init__(self, storage: IoTControlStorage):
        self.storage = storage

    def analyze_control_efficiency(self, device_id: str,
                                  time_window: timedelta = timedelta(hours=24)) -> Dict:
        """分析控制效率"""
        stats = self.storage.calculate_statistics(device_id, time_window)
        patterns = self.storage.analyze_state_patterns(device_id, time_window)

        # 计算效率指标
        total_time = time_window.total_seconds() * 1000  # 转换为毫秒
        active_time = sum(p['avg_duration_ms'] * p['frequency']
                         for p in patterns['patterns']
                         if 'running' in p['state_name'].lower())
        efficiency = (active_time / total_time * 100) if total_time > 0 else 0

        return {
            'device_id': device_id,
            'efficiency_percent': efficiency,
            'total_transitions': patterns['total_transitions'],
            'active_states': len([p for p in patterns['patterns']
                                 if 'running' in p['state_name'].lower()]),
            'statistics': stats
        }
```

---

## 7. 参考文献

### 7.1 标准文档

- GB/T 34068-2017 物联网总体技术 智能传感器接口规范
- IEC 61131-3:2013 Programmable controllers

### 7.2 技术文档

- 控制逻辑转换最佳实践
- PostgreSQL JSONB文档

### 7.3 在线资源

- **IEC官网**：[https://www.iec.ch/](https://www.iec.ch/)
- **PostgreSQL官网**：[https://www.postgresql.org/](https://www.postgresql.org/)

---

**参考文档**：

- `01_Overview.md` - 概述
- `02_Formal_Definition.md` - 形式化定义
- `03_Standards.md` - 标准对标
- `05_Case_Studies.md` - 实践案例

**创建时间**：2025-01-21
**最后更新**：2025-01-21（扩展控制数据存储和分析功能，新增PostgreSQL存储方案）
