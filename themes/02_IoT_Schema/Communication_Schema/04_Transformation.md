# IoT通信Schema转换体系

## 📑 目录

- [IoT通信Schema转换体系](#iot通信schema转换体系)
  - [📑 目录](#-目录)
  - [1. 转换体系概述](#1-转换体系概述)
    - [1.1 转换目标](#11-转换目标)
    - [1.2 转换原则](#12-转换原则)
  - [2. 协议转换矩阵](#2-协议转换矩阵)
    - [2.1 有线协议转换](#21-有线协议转换)
    - [2.2 无线协议转换](#22-无线协议转换)
    - [2.3 跨协议转换](#23-跨协议转换)
  - [3. 数据格式转换](#3-数据格式转换)
    - [3.1 JSON转换](#31-json转换)
    - [3.2 XML转换](#32-xml转换)
    - [3.3 Protobuf转换](#33-protobuf转换)
  - [4. 协议网关实现](#4-协议网关实现)
    - [4.1 Modbus到MQTT网关](#41-modbus到mqtt网关)
    - [4.2 CAN到OPC UA网关](#42-can到opc-ua网关)
    - [4.3 LoRaWAN到HTTP网关](#43-lorawan到http网关)
  - [5. 转换实例](#5-转换实例)
    - [5.1 MQTT消息转换](#51-mqtt消息转换)
    - [5.2 CoAP资源转换](#52-coap资源转换)
    - [5.3 Modbus寄存器转换](#53-modbus寄存器转换)
  - [6. 转换工具](#6-转换工具)
    - [6.1 开源工具](#61-开源工具)
    - [6.2 商业工具](#62-商业工具)
  - [7. 转换验证](#7-转换验证)
    - [7.1 语义验证](#71-语义验证)
    - [7.2 性能验证](#72-性能验证)
    - [7.3 可靠性验证](#73-可靠性验证)
  - [8. 通信协议数据存储与分析](#8-通信协议数据存储与分析)
    - [8.1 PostgreSQL通信协议数据存储](#81-postgresql通信协议数据存储)
    - [8.2 通信协议数据分析查询](#82-通信协议数据分析查询)
  - [9. 参考文献](#9-参考文献)
    - [9.1 标准文档](#91-标准文档)
    - [9.2 技术文档](#92-技术文档)
    - [9.3 在线资源](#93-在线资源)

---

## 1. 转换体系概述

IoT通信Schema转换体系支持多种协议之间的
转换和数据格式之间的转换。

### 1.1 转换目标

**转换目标类型**：

1. **协议转换**：Modbus → MQTT, CAN → OPC UA
2. **数据格式转换**：JSON → XML, Binary → Protobuf
3. **传输方式转换**：TCP → UDP, HTTP → WebSocket

### 1.2 转换原则

**原则1（语义保持）**：
转换后的消息必须与原始消息语义等价。

**原则2（信息完整）**：
转换过程中应保持信息完整性。

**原则3（性能优化）**：
转换应尽可能高效。

---

## 2. 协议转换矩阵

### 2.1 有线协议转换

| 源协议 | 目标协议 | 转换复杂度 | 信息损失 |
|--------|---------|-----------|---------|
| Modbus RTU | Modbus TCP | 低 | 无 |
| Modbus RTU | MQTT | 中 | 低 |
| Modbus RTU | HTTP | 中 | 低 |
| CAN | MQTT | 中 | 低 |
| CAN | OPC UA | 高 | 无 |
| Profibus | OPC UA | 高 | 无 |

### 2.2 无线协议转换

| 源协议 | 目标协议 | 转换复杂度 | 信息损失 |
|--------|---------|-----------|---------|
| MQTT | CoAP | 低 | 无 |
| MQTT | HTTP | 低 | 无 |
| LoRaWAN | MQTT | 中 | 低 |
| LoRaWAN | HTTP | 中 | 低 |
| NB-IoT | MQTT | 中 | 低 |
| Zigbee | MQTT | 高 | 中 |

### 2.3 跨协议转换

**转换策略**：

1. **直接映射**：协议特性直接对应
2. **适配映射**：通过适配层转换
3. **网关转换**：通过协议网关转换

---

## 3. 数据格式转换

### 3.1 JSON转换

**JSON到其他格式**：

| 源格式 | 目标格式 | 转换方法 |
|--------|---------|---------|
| JSON | XML | 结构化映射 |
| JSON | Protobuf | Schema映射 |
| JSON | Binary | 序列化 |
| JSON | CSV | 扁平化 |

### 3.2 XML转换

**XML到其他格式**：

| 源格式 | 目标格式 | 转换方法 |
|--------|---------|---------|
| XML | JSON | 结构化映射 |
| XML | YAML | 结构化映射 |
| XML | Protobuf | Schema映射 |

### 3.3 Protobuf转换

**Protobuf到其他格式**：

| 源格式 | 目标格式 | 转换方法 |
|--------|---------|---------|
| Protobuf | JSON | 反序列化 |
| Protobuf | XML | 反序列化+转换 |
| Protobuf | Binary | 直接使用 |

---

## 4. 协议网关实现

### 4.1 Modbus到MQTT网关

**实现示例**：

```python
import pymodbus
from pymodbus.client.sync import ModbusSerialClient
import paho.mqtt.client as mqtt
import json
from datetime import datetime

class ModbusToMQTTGateway:
    """Modbus到MQTT协议网关"""

    def __init__(self, modbus_port: str, mqtt_broker: str):
        # Modbus客户端
        self.modbus_client = ModbusSerialClient(
            method='rtu',
            port=modbus_port,
            baudrate=9600
        )

        # MQTT客户端
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.connect(mqtt_broker, 1883)

    def read_modbus_register(self, slave_id: int, address: int):
        """读取Modbus寄存器"""
        result = self.modbus_client.read_holding_registers(
            address=address,
            count=1,
            unit=slave_id
        )
        return result.registers[0] if not result.isError() else None

    def publish_to_mqtt(self, topic: str, data: dict):
        """发布数据到MQTT"""
        payload = json.dumps(data)
        self.mqtt_client.publish(topic, payload, qos=1)

    def convert_and_publish(self, slave_id: int, modbus_address: int, mqtt_topic: str):
        """转换并发布"""
        value = self.read_modbus_register(slave_id, modbus_address)
        if value is not None:
            data = {
                "slave_id": slave_id,
                "address": modbus_address,
                "value": value,
                "timestamp": datetime.utcnow().isoformat()
            }
            self.publish_to_mqtt(mqtt_topic, data)
```

### 4.2 CAN到OPC UA网关

**实现示例**：

```python
import can
from opcua import Client, ua
import struct

class CANToOPCUAGateway:
    """CAN到OPC UA协议网关"""

    def __init__(self, can_interface: str, opcua_endpoint: str):
        # CAN总线
        self.can_bus = can.interface.Bus(
            channel=can_interface,
            bustype='socketcan'
        )

        # OPC UA客户端
        self.opcua_client = Client(opcua_endpoint)
        self.opcua_client.connect()

    def read_can_message(self):
        """读取CAN消息"""
        message = self.can_bus.recv(timeout=1.0)
        return message

    def write_opcua_node(self, node_id: str, value: float):
        """写入OPC UA节点"""
        node = self.opcua_client.get_node(node_id)
        node.set_value(value, ua.VariantType.Float)

    def convert_and_write(self, can_id: int, opcua_node_id: str):
        """转换并写入"""
        message = self.read_can_message()
        if message and message.arbitration_id == can_id:
            # 解析CAN数据（假设是4字节浮点数）
            value = struct.unpack('f', message.data[:4])[0]
            self.write_opcua_node(opcua_node_id, value)
```

### 4.3 LoRaWAN到HTTP网关

**实现示例**：

```python
import requests
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

class LoRaWANToHTTPGateway:
    """LoRaWAN到HTTP协议网关"""

    def __init__(self, app_key: bytes, http_endpoint: str):
        self.app_key = app_key
        self.http_endpoint = http_endpoint

    def decrypt_lorawan_payload(self, encrypted_payload: bytes, dev_addr: bytes, f_cnt: int):
        """解密LoRaWAN载荷"""
        # LoRaWAN AES-128解密逻辑
        try:
            from Crypto.Cipher import AES
            from Crypto.Util import Counter

            # 生成会话密钥（简化实现，实际应使用AppSKey）
            app_s_key = self.app_s_key  # 16字节密钥

            # 构建AES计数器（使用dev_addr和f_cnt）
            counter = Counter.new(32, prefix=dev_addr[:4] + f_cnt.to_bytes(4, 'big'))
            cipher = AES.new(app_s_key, AES.MODE_CTR, counter=counter)

            decrypted_payload = cipher.decrypt(encrypted_payload)
            return decrypted_payload
        except Exception as e:
            self.logger.error(f"LoRaWAN decryption error: {e}")
            raise ValueError(f"LoRaWAN decryption failed: {e}")

    def convert_to_http(self, lorawan_data: dict):
        """转换为HTTP请求"""
        payload = {
            "device_id": lorawan_data["dev_eui"],
            "data": lorawan_data["payload"],
            "timestamp": lorawan_data["timestamp"]
        }
        return payload

    def send_http_request(self, payload: dict):
        """发送HTTP请求"""
        response = requests.post(
            self.http_endpoint,
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        return response.status_code == 200
```

---

## 5. 转换实例

### 5.1 MQTT消息转换

**MQTT到JSON转换**：

```python
import json
import paho.mqtt.client as mqtt

class MQTTMessageConverter:
    """MQTT消息转换器"""

    def mqtt_to_json(self, topic: str, payload: bytes, qos: int):
        """MQTT消息转JSON"""
        try:
            # 尝试解析为JSON
            data = json.loads(payload.decode('utf-8'))
        except:
            # 如果不是JSON，转换为文本
            data = {"raw": payload.decode('utf-8')}

        return {
            "topic": topic,
            "payload": data,
            "qos": qos,
            "timestamp": datetime.utcnow().isoformat()
        }

    def json_to_mqtt(self, json_data: dict):
        """JSON转MQTT消息"""
        topic = json_data.get("topic", "")
        payload = json.dumps(json_data.get("payload", {}))
        qos = json_data.get("qos", 0)
        return topic, payload.encode('utf-8'), qos
```

### 5.2 CoAP资源转换

**CoAP到HTTP转换**：

```python
from coapthon.client.helperclient import HelperClient
import requests

class CoAPToHTTPConverter:
    """CoAP到HTTP转换器"""

    def coap_to_http(self, coap_uri: str, method: str, payload: bytes):
        """CoAP请求转HTTP请求"""
        # CoAP URI: coap://host:port/path
        # HTTP URI: http://host:port/path
        http_uri = coap_uri.replace("coap://", "http://")

        # CoAP方法映射到HTTP方法
        http_method = {
            "GET": "GET",
            "POST": "POST",
            "PUT": "PUT",
            "DELETE": "DELETE"
        }.get(method, "GET")

        return http_uri, http_method, payload

    def http_to_coap(self, http_uri: str, method: str, payload: bytes):
        """HTTP请求转CoAP请求"""
        coap_uri = http_uri.replace("http://", "coap://")
        return coap_uri, method, payload
```

### 5.3 Modbus寄存器转换

**Modbus寄存器到JSON转换**：

```python
class ModbusRegisterConverter:
    """Modbus寄存器转换器"""

    def __init__(self, register_map: dict):
        self.register_map = register_map

    def register_to_json(self, slave_id: int, address: int, value: int):
        """寄存器值转JSON"""
        register_info = self.register_map.get(address, {})

        # 数据类型转换
        data_type = register_info.get("type", "uint16")
        if data_type == "float32":
            # 假设两个寄存器组成一个浮点数
            # 需要读取相邻的两个寄存器来组成32位浮点数
            # 这里简化处理，实际需要读取两个寄存器值
            import struct
            # 假设value是16位值，需要组合两个寄存器
            # 实际实现需要读取address和address+1两个寄存器
            if isinstance(value, (list, tuple)) and len(value) >= 2:
                # 组合两个16位值为32位浮点数
                combined = (value[0] << 16) | value[1]
                value = struct.unpack('>f', struct.pack('>I', combined))[0]
            else:
                # 单个寄存器值，转换为浮点数
                value = float(value)

        return {
            "slave_id": slave_id,
            "address": address,
            "name": register_info.get("name", f"Register_{address}"),
            "value": value,
            "unit": register_info.get("unit", ""),
            "timestamp": datetime.utcnow().isoformat()
        }
```

---

## 6. 转换工具

### 6.1 开源工具

**工具列表**：

1. **Node-RED**：可视化流程编程，支持协议转换
2. **Eclipse Kura**：边缘计算框架，支持协议网关
3. **ThingsBoard**：IoT平台，支持协议转换
4. **Apache NiFi**：数据流处理，支持协议转换

### 6.2 商业工具

**工具列表**：

1. **AWS IoT Core**：AWS IoT平台，支持协议转换
2. **Azure IoT Hub**：Azure IoT平台，支持协议转换
3. **Google Cloud IoT**：Google IoT平台，支持协议转换

---

## 7. 转换验证

### 7.1 语义验证

**验证方法**：
比较转换前后的消息语义是否等价。

### 7.2 性能验证

**验证方法**：
测试转换的延迟和吞吐量。

### 7.3 可靠性验证

**验证方法**：
测试转换的可靠性和错误处理。

---

## 8. 通信协议数据存储与分析

### 8.1 PostgreSQL通信协议数据存储

**IoT通信协议数据存储方案**：

```python
import psycopg2
import json
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass

@dataclass
class MQTTMessage:
    """MQTT消息"""
    topic: str
    payload: bytes
    qos: int
    retain: bool
    timestamp: datetime
    client_id: str = None

@dataclass
class ModbusRegister:
    """Modbus寄存器"""
    slave_id: int
    address: int
    value: int
    function_code: int
    timestamp: datetime

class IoTCommunicationStorage:
    """IoT通信协议数据存储系统"""

    def __init__(self, connection_string: str):
        self.conn = psycopg2.connect(connection_string)
        self.cur = self.conn.cursor()
        self._create_tables()

    def _create_tables(self):
        """创建通信协议数据表"""
        # 协议配置表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS protocol_configs (
                id SERIAL PRIMARY KEY,
                protocol_type VARCHAR(50) NOT NULL,
                config_name VARCHAR(200) NOT NULL,
                configuration JSONB NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(protocol_type, config_name)
            )
        """)

        # MQTT消息表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS mqtt_messages (
                id BIGSERIAL PRIMARY KEY,
                topic VARCHAR(500) NOT NULL,
                payload BYTEA NOT NULL,
                payload_text TEXT,
                qos INTEGER NOT NULL,
                retain BOOLEAN DEFAULT FALSE,
                client_id VARCHAR(200),
                timestamp TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Modbus寄存器表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS modbus_registers (
                id BIGSERIAL PRIMARY KEY,
                slave_id INTEGER NOT NULL,
                address INTEGER NOT NULL,
                value INTEGER NOT NULL,
                function_code INTEGER NOT NULL,
                timestamp TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # CoAP资源表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS coap_resources (
                id BIGSERIAL PRIMARY KEY,
                uri_path VARCHAR(500) NOT NULL,
                method VARCHAR(10) NOT NULL,
                payload BYTEA,
                content_format INTEGER,
                timestamp TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 协议转换日志表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS protocol_conversions (
                id BIGSERIAL PRIMARY KEY,
                source_protocol VARCHAR(50) NOT NULL,
                target_protocol VARCHAR(50) NOT NULL,
                source_data JSONB NOT NULL,
                target_data JSONB NOT NULL,
                conversion_time_ms INTEGER,
                success BOOLEAN DEFAULT TRUE,
                error_message TEXT,
                timestamp TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 协议统计表
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS protocol_statistics (
                id SERIAL PRIMARY KEY,
                protocol_type VARCHAR(50) NOT NULL,
                statistic_type VARCHAR(50) NOT NULL,
                time_window TIMESTAMP NOT NULL,
                statistics JSONB NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(protocol_type, statistic_type, time_window)
            )
        """)

        # 创建索引
        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_mqtt_topic_time
            ON mqtt_messages(topic, timestamp DESC)
        """)
        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_mqtt_timestamp
            ON mqtt_messages(timestamp DESC)
        """)
        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_modbus_slave_addr_time
            ON modbus_registers(slave_id, address, timestamp DESC)
        """)
        self.cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_conversions_source_target
            ON protocol_conversions(source_protocol, target_protocol, timestamp DESC)
        """)

        self.conn.commit()

    def store_protocol_config(self, protocol_type: str, config_name: str,
                              configuration: Dict):
        """存储协议配置"""
        self.cur.execute("""
            INSERT INTO protocol_configs
            (protocol_type, config_name, configuration)
            VALUES (%s, %s, %s::jsonb)
            ON CONFLICT (protocol_type, config_name) DO UPDATE
            SET configuration = EXCLUDED.configuration,
                updated_at = CURRENT_TIMESTAMP
        """, (protocol_type, config_name, json.dumps(configuration)))
        self.conn.commit()

    def store_mqtt_message(self, message: MQTTMessage):
        """存储MQTT消息"""
        payload_text = None
        try:
            payload_text = message.payload.decode('utf-8')
        except UnicodeDecodeError:
            # 如果不是UTF-8编码，尝试其他编码或记录为二进制
            try:
                payload_text = message.payload.decode('latin-1')
            except:
                payload_text = None  # 无法解码，保持为None
        except Exception as e:
            self.logger.warning(f"Failed to decode payload: {e}")
            payload_text = None

        self.cur.execute("""
            INSERT INTO mqtt_messages
            (topic, payload, payload_text, qos, retain, client_id, timestamp)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (message.topic, message.payload, payload_text,
              message.qos, message.retain, message.client_id,
              message.timestamp))
        self.conn.commit()

    def store_modbus_register(self, register: ModbusRegister):
        """存储Modbus寄存器值"""
        self.cur.execute("""
            INSERT INTO modbus_registers
            (slave_id, address, value, function_code, timestamp)
            VALUES (%s, %s, %s, %s, %s)
        """, (register.slave_id, register.address, register.value,
              register.function_code, register.timestamp))
        self.conn.commit()

    def store_conversion_log(self, source_protocol: str, target_protocol: str,
                            source_data: Dict, target_data: Dict,
                            conversion_time_ms: int = None,
                            success: bool = True, error_message: str = None):
        """存储协议转换日志"""
        self.cur.execute("""
            INSERT INTO protocol_conversions
            (source_protocol, target_protocol, source_data, target_data,
             conversion_time_ms, success, error_message, timestamp)
            VALUES (%s, %s, %s::jsonb, %s::jsonb, %s, %s, %s, %s)
        """, (source_protocol, target_protocol,
              json.dumps(source_data), json.dumps(target_data),
              conversion_time_ms, success, error_message,
              datetime.utcnow()))
        self.conn.commit()

    def get_mqtt_messages(self, topic: str = None,
                         start_time: datetime = None,
                         end_time: datetime = None,
                         limit: int = 1000) -> List[Dict]:
        """获取MQTT消息"""
        query = """
            SELECT topic, payload, payload_text, qos, retain, client_id, timestamp
            FROM mqtt_messages
            WHERE 1=1
        """
        params = []

        if topic:
            query += " AND topic = %s"
            params.append(topic)

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
                'topic': row[0],
                'payload': bytes(row[1]),
                'payload_text': row[2],
                'qos': row[3],
                'retain': row[4],
                'client_id': row[5],
                'timestamp': row[6]
            })
        return results

    def get_modbus_registers(self, slave_id: int = None,
                            address: int = None,
                            start_time: datetime = None,
                            end_time: datetime = None,
                            limit: int = 1000) -> List[Dict]:
        """获取Modbus寄存器值"""
        query = """
            SELECT slave_id, address, value, function_code, timestamp
            FROM modbus_registers
            WHERE 1=1
        """
        params = []

        if slave_id:
            query += " AND slave_id = %s"
            params.append(slave_id)

        if address:
            query += " AND address = %s"
            params.append(address)

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
                'slave_id': row[0],
                'address': row[1],
                'value': row[2],
                'function_code': row[3],
                'timestamp': row[4]
            })
        return results

    def calculate_protocol_statistics(self, protocol_type: str,
                                     time_window: timedelta = timedelta(hours=1)) -> Dict:
        """计算协议统计信息"""
        end_time = datetime.utcnow()
        start_time = end_time - time_window

        if protocol_type == 'MQTT':
            self.cur.execute("""
                SELECT
                    COUNT(*) as message_count,
                    COUNT(DISTINCT topic) as unique_topics,
                    COUNT(DISTINCT client_id) as unique_clients,
                    AVG(LENGTH(payload)) as avg_payload_size,
                    SUM(CASE WHEN qos > 0 THEN 1 ELSE 0 END) as qos_messages
                FROM mqtt_messages
                WHERE timestamp >= %s AND timestamp <= %s
            """, (start_time, end_time))

            row = self.cur.fetchone()
            if row and row[0]:
                statistics = {
                    'message_count': row[0],
                    'unique_topics': row[1],
                    'unique_clients': row[2],
                    'avg_payload_size': float(row[3]) if row[3] else 0,
                    'qos_messages': row[4]
                }

                # 存储统计结果
                self.cur.execute("""
                    INSERT INTO protocol_statistics
                    (protocol_type, statistic_type, time_window, statistics)
                    VALUES (%s, %s, %s, %s::jsonb)
                    ON CONFLICT (protocol_type, statistic_type, time_window) DO UPDATE
                    SET statistics = EXCLUDED.statistics
                """, (protocol_type, 'message_statistics', end_time,
                      json.dumps(statistics)))
                self.conn.commit()

                return statistics

        elif protocol_type == 'Modbus':
            self.cur.execute("""
                SELECT
                    COUNT(*) as register_count,
                    COUNT(DISTINCT slave_id) as unique_slaves,
                    COUNT(DISTINCT address) as unique_addresses,
                    AVG(value) as avg_value,
                    MIN(value) as min_value,
                    MAX(value) as max_value
                FROM modbus_registers
                WHERE timestamp >= %s AND timestamp <= %s
            """, (start_time, end_time))

            row = self.cur.fetchone()
            if row and row[0]:
                statistics = {
                    'register_count': row[0],
                    'unique_slaves': row[1],
                    'unique_addresses': row[2],
                    'avg_value': float(row[3]) if row[3] else 0,
                    'min_value': row[4],
                    'max_value': row[5]
                }

                # 存储统计结果
                self.cur.execute("""
                    INSERT INTO protocol_statistics
                    (protocol_type, statistic_type, time_window, statistics)
                    VALUES (%s, %s, %s, %s::jsonb)
                    ON CONFLICT (protocol_type, statistic_type, time_window) DO UPDATE
                    SET statistics = EXCLUDED.statistics
                """, (protocol_type, 'register_statistics', end_time,
                      json.dumps(statistics)))
                self.conn.commit()

                return statistics

        return None

    def analyze_conversion_performance(self, source_protocol: str = None,
                                      target_protocol: str = None,
                                      time_window: timedelta = timedelta(hours=24)) -> Dict:
        """分析转换性能"""
        end_time = datetime.utcnow()
        start_time = end_time - time_window

        query = """
            SELECT
                source_protocol,
                target_protocol,
                COUNT(*) as conversion_count,
                AVG(conversion_time_ms) as avg_time_ms,
                MIN(conversion_time_ms) as min_time_ms,
                MAX(conversion_time_ms) as max_time_ms,
                SUM(CASE WHEN success THEN 1 ELSE 0 END) as success_count,
                SUM(CASE WHEN NOT success THEN 1 ELSE 0 END) as error_count
            FROM protocol_conversions
            WHERE timestamp >= %s AND timestamp <= %s
        """
        params = [start_time, end_time]

        if source_protocol:
            query += " AND source_protocol = %s"
            params.append(source_protocol)

        if target_protocol:
            query += " AND target_protocol = %s"
            params.append(target_protocol)

        query += " GROUP BY source_protocol, target_protocol"

        self.cur.execute(query, params)
        results = []
        for row in self.cur.fetchall():
            results.append({
                'source_protocol': row[0],
                'target_protocol': row[1],
                'conversion_count': row[2],
                'avg_time_ms': float(row[3]) if row[3] else 0,
                'min_time_ms': row[4],
                'max_time_ms': row[5],
                'success_count': row[6],
                'error_count': row[7],
                'success_rate': row[6] / row[2] * 100 if row[2] > 0 else 0
            })
        return results

    def close(self):
        """关闭连接"""
        self.cur.close()
        self.conn.close()

# 使用示例
if __name__ == "__main__":
    storage = IoTCommunicationStorage(
        "postgresql://user:password@localhost/iot_comm_db"
    )

    # 存储MQTT配置
    storage.store_protocol_config(
        protocol_type="MQTT",
        config_name="broker_config",
        configuration={
            "broker": "mqtt.example.com",
            "port": 1883,
            "keep_alive": 60
        }
    )

    # 存储MQTT消息
    message = MQTTMessage(
        topic="sensors/temperature/room1",
        payload=b'{"value": 23.5, "unit": "C"}',
        qos=1,
        retain=False,
        timestamp=datetime.utcnow(),
        client_id="sensor_001"
    )
    storage.store_mqtt_message(message)

    # 存储Modbus寄存器
    register = ModbusRegister(
        slave_id=1,
        address=40001,
        value=1234,
        function_code=3,
        timestamp=datetime.utcnow()
    )
    storage.store_modbus_register(register)

    # 存储转换日志
    storage.store_conversion_log(
        source_protocol="Modbus",
        target_protocol="MQTT",
        source_data={"slave_id": 1, "address": 40001, "value": 1234},
        target_data={"topic": "modbus/device1/register40001", "value": 1234},
        conversion_time_ms=5
    )

    # 计算统计信息
    mqtt_stats = storage.calculate_protocol_statistics("MQTT")
    print(f"MQTT统计: {mqtt_stats}")

    modbus_stats = storage.calculate_protocol_statistics("Modbus")
    print(f"Modbus统计: {modbus_stats}")

    # 分析转换性能
    conversion_perf = storage.analyze_conversion_performance()
    print(f"转换性能: {conversion_perf}")

    storage.close()
```

### 8.2 通信协议数据分析查询

**高级分析查询**：

```python
class IoTCommunicationAnalyzer:
    """IoT通信协议数据分析器"""

    def __init__(self, storage: IoTCommunicationStorage):
        self.storage = storage

    def analyze_topic_traffic(self, topic_pattern: str,
                             time_window: timedelta = timedelta(hours=1)) -> Dict:
        """分析主题流量"""
        end_time = datetime.utcnow()
        start_time = end_time - time_window

        self.storage.cur.execute("""
            SELECT
                topic,
                COUNT(*) as message_count,
                AVG(LENGTH(payload)) as avg_size,
                MIN(timestamp) as first_message,
                MAX(timestamp) as last_message
            FROM mqtt_messages
            WHERE topic LIKE %s
              AND timestamp >= %s
              AND timestamp <= %s
            GROUP BY topic
            ORDER BY message_count DESC
        """, (topic_pattern, start_time, end_time))

        topics = []
        for row in self.storage.cur.fetchall():
            topics.append({
                'topic': row[0],
                'message_count': row[1],
                'avg_size': float(row[2]) if row[2] else 0,
                'first_message': row[3],
                'last_message': row[4]
            })

        return {
            'topic_pattern': topic_pattern,
            'time_window': time_window,
            'topics': topics,
            'total_topics': len(topics)
        }

    def analyze_register_trends(self, slave_id: int, address: int,
                               time_window: timedelta = timedelta(hours=1)) -> Dict:
        """分析寄存器趋势"""
        registers = self.storage.get_modbus_registers(
            slave_id=slave_id,
            address=address,
            start_time=datetime.utcnow() - time_window
        )

        if not registers:
            return None

        values = [r['value'] for r in registers]

        return {
            'slave_id': slave_id,
            'address': address,
            'value_count': len(values),
            'current_value': values[0] if values else None,
            'avg_value': sum(values) / len(values) if values else None,
            'min_value': min(values) if values else None,
            'max_value': max(values) if values else None,
            'trend': (values[0] - values[-1]) / len(values) if len(values) > 1 else 0
        }
```

---

## 9. 参考文献

### 9.1 标准文档

- MQTT 5.0 Specification
- CoAP RFC 7252
- Modbus Protocol Specification
- LoRaWAN Specification

### 9.2 技术文档

- 协议转换最佳实践
- 数据格式转换指南
- PostgreSQL JSONB文档

### 9.3 在线资源

- **Node-RED官网**：<https://nodered.org/>
- **Eclipse Kura官网**：<https://www.eclipse.org/kura/>
- **ThingsBoard官网**：<https://thingsboard.io/>
- **PostgreSQL官网**：<https://www.postgresql.org/>

---

**参考文档**：

- `01_Overview.md` - 概述
- `02_Formal_Definition.md` - 形式化定义
- `03_Standards.md` - 标准对标
- `05_Case_Studies.md` - 实践案例

**创建时间**：2025-01-21
**最后更新**：2025-01-21（扩展通信协议数据存储和分析功能，新增PostgreSQL存储方案）
